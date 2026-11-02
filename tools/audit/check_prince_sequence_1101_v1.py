"""Replace recovered entries inside natural donor NMI/foreground sequencing."""
from pathlib import Path
import copy,hashlib,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prince_original_cpu_1101_v1 as P
import recover_prince_core_1101_v1 as B
O=B.O


def main():
 step=P.T.NesMPU.step
 def tracked(c):
  c.stack_low=min(getattr(c,'stack_low',c.sp),c.sp)
  z=step(c);c.stack_low=min(c.stack_low,c.sp);return z
 P.T.NesMPU.step=tracked
 labels=P.T.labels(O/'prince-core.lbl');blob=(O/'prince-core.bin').read_bytes()
 callbacks={labels[n]:(k,n)for k,n in B.CALLBACKS.items()}
 mapping={(7,0xf158):'PpAdvanceActor',(7,0xeff2):'PpControls',(5,0x8730):'PpSetAction',(5,0x8133):'PpFall',(5,0x839f):'PpDecodeInput'}
 relocs={int(v[1],16):labels[f'PpN_{v[0]}_{int(v[1],16):04X}']for v in json.loads((O/'core-recovery.json').read_text())['dynamic_command_targets'].values()}
 counts={};native={};states=set();frames=set();actions=set();control_continues=0
 def normalize(ram):
  ram=bytearray(ram);v=ram[0x23]|ram[0x24]<<8
  if v in relocs:ram[0x23:0x25]=relocs[v].to_bytes(2,'little')
  return ram
 def equal_ram(a,b,low,context):
  a=normalize(a);b=normalize(b)
  for lo,hi in [(0,0x101+low),(512,2048)]:
   assert a[lo:hi]==b[lo:hi],(context,[(hex(k),a[k],b[k])for k in range(lo,hi)if a[k]!=b[k]][:12])
 def relay(c):
  nonlocal control_continues
  key=(7 if c.pc>=0xc000 else c.memory.bank,c.pc)
  if key not in mapping:return
  name=mapping[key];counts[name]=counts.get(name,0)+1
  # Reference runs the exact same reached source boundary and real peripheral
  # state; no manufactured terrain return values or seeded action outcomes.
  ref=copy.deepcopy(c);ref.stack_low=ref.sp;entrysp=c.sp
  ret=((c.memory[0x101+entrysp]|c.memory[0x102+entrysp]<<8)+1)&65535
  end=0xf1a2 if name=='PpAdvanceActor'else(0xf090 if name=='PpControls'else None)
  n=0
  while not(ref.pc==ret and ref.sp==(entrysp+2)&255)and not(end is not None and ref.pc==end and ref.sp==entrysp):
   ref.step();n+=1;assert n<100000,(name,'reference bound',hex(ref.pc))
  p=P.T.NesMPU(memory=[0]*65536,pc=labels[name]);p.memory[0xa000:0xa000+len(blob)]=blob;p.memory[0xc000:0xc800]=c.memory[:2048]
  p.memory[0x100:0x200]=c.memory[0x100:0x200];p.a,p.x,p.y,p.p,p.sp=c.a,c.x,c.y,c.p,c.sp
  model=copy.deepcopy(c.memory);n=0;continuation=False
  while not(p.pc==ret and p.sp==(entrysp+2)&255):
   if p.sp==entrysp and p.pc==labels['PpFrameComplete'if name=='PpAdvanceActor'else 'PpControlComplete']:
    continuation=True;break
   if p.pc in callbacks:
    (bank,target),tag=callbacks[p.pc];donor=copy.deepcopy(c);donor.memory=copy.deepcopy(model)
    list.__setitem__(donor.memory,slice(0,2048),p.memory[0xc000:0xc800]);donor.memory.switch(bank if target<0xc000 else p.memory[0xc6d1]);donor.stack_low=0xfd
    prior={tag:copy.deepcopy(getattr(model,tag))for tag in ['apu','ppuwrites','writes']}
    result=P.call(donor,target,a=p.a,x=p.x,y=p.y,p=p.p,limit=100000)
    for stream_name,stream in prior.items():setattr(donor.memory,stream_name,stream+getattr(donor.memory,stream_name))
    for lo,hi in [(0,0x101+donor.stack_low),(512,2048)]:p.memory[0xc000+lo:0xc000+hi]=donor.memory[lo:hi]
    p.a,p.x,p.y,p.p=result[:4];p.pc=(p.stPopWord()+1)&65535;model=donor.memory;native[tag]=native.get(tag,0)+1;continue
   p.step();n+=1;assert n<12000,(name,'replacement bound',hex(p.pc))
  equal_ram(ref.memory[:2048],p.memory[0xc000:0xc800],ref.stack_low,('reached component',name))
  assert(ref.a,ref.x,ref.y,ref.p&0xef,ref.sp)==(p.a,p.x,p.y,p.p&0xef,p.sp),(name,'AXYPSP')
  for attr in ['ppu','oam','apu','ctrl','mask','v','w','hi','buffer','oamaddr','status_reads']:
   assert getattr(ref.memory,attr)==getattr(model,attr),(name,'peripheral',attr)
  for lo,hi in [(0,0x101+ref.stack_low),(512,2048)]:list.__setitem__(c.memory,slice(lo,hi),p.memory[0xc000+lo:0xc000+hi])
  # The relocated command-vector pointer is scratch only. Re-export the
  # genuine source pointer because subsequent donor code retains its ABI.
  inv={v:k for k,v in relocs.items()};v=c.memory[0x23]|c.memory[0x24]<<8
  if v in inv:list.__setitem__(c.memory,slice(0x23,0x25),list(inv[v].to_bytes(2,'little')))
  c.a,c.x,c.y,c.p,c.sp=p.a,p.x,p.y,p.p,p.sp
  c.pc=end if continuation else ret
  if continuation and name=='PpControls':control_continues+=1
  # Bank adapters retain the original private bank shadow. Actual donor
  # continuation now resumes in precisely that physical low window.
  c.memory.switch(p.memory[0xc6d1])
  for attr in ['ppu','oam','apu','ppuwrites','ctrl','mask','v','w','hi','buffer','oamaddr','status_reads']:
   setattr(c.memory,attr,copy.deepcopy(getattr(model,attr)))
 old=P.boot();new=copy.deepcopy(old);segments=[('natural-start',900,None),('run-right',150,1),('running-A',45,0x81),('release',50,0),('up',45,8),('careful-right',90,0x41),('run-left',120,2),('running-A-left',45,0x82),('release',80,0),('up-left',45,0x0a)]
 total=0;rows=[];positions=[];stack_floor=min(old.stack_low,new.stack_low)
 for title,n,pad in segments:
  for i in range(n):
   actual=0x10 if pad is None and(120<=total<123 or 300<=total<303 or 600<=total<603)else(pad or 0)
   old.stack_low=old.sp;new.stack_low=new.sp;P.frame(old,actual);P.frame(new,actual,relay)
   stack_floor=min(stack_floor,old.stack_low,new.stack_low)
   equal_ram(old.memory[:2048],new.memory[:2048],stack_floor,('whole source frame',total))
   assert bytes(old.memory[0x101+old.sp:0x200])==bytes(new.memory[0x101+new.sp:0x200]),('Live original stack',total)
   assert(old.a,old.x,old.y,old.sp,old.p&0xef)==(new.a,new.x,new.y,new.sp,new.p&0xef),('frame CPU',total)
   for attr in ['bank','ppu','oam','apu','ctrl','mask','v','w','hi','buffer','oamaddr','status_reads']:
    assert getattr(old.memory,attr)==getattr(new.memory,attr),('frame peripheral',total,attr)
   if total>=900:
    states.add(old.memory[0x618]);actions.add(old.memory[0x616]);frames.add(old.memory[0x617]);positions.append([old.memory[0x60f]|old.memory[0x610]<<8,old.memory[0x611]])
   total+=1
  rows.append(dict(segment=title,frames=n,x=old.memory[0x60f]|old.memory[0x610]<<8,y=old.memory[0x611],action=old.memory[0x616],source_frame=old.memory[0x617],state=old.memory[0x618]))
 q=dict(passed=True,donor_sha256=P.SHA,source_CPU_only=True,native_host=False,installed=False,frames=total,natural_startup_frames=900,reached_replacements=counts,control_prefix_continues_to_original_combat=control_continues,actual_donor_callbacks=native,actions=sorted(actions),source_frames=sorted(frames),actor_states=sorted(states),x_range=[min(v[0]for v in positions),max(v[0]for v in positions)],y_range=[min(v[1]for v in positions),max(v[1]for v in positions)],segments=rows,application_RAM_AXYP_SP_physical_bank_PPU_OAM_APU_exact=True,minimum_original_SP=stack_floor,stack_comparison='All original RAM except ever-reached discarded stack-write interval tracked by minimumSP; each frame also compares its actual live source stack. Low stack-page application buffers included.',limits=['Untimed donor NMI/main CPU sequencing only; not native Mesen/host cadence/1-1.','Original world/combat/render/audio consumers remain actual donor instructions.','Recovered animation/control prefixes continue before F1A2/F090; no hidden original combat recovery claim.'],bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),Path(P.__file__),Path(B.__file__),O/'prince-core.bin',O/'prince-core.lbl']})
 (O/'source-sequencing-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
