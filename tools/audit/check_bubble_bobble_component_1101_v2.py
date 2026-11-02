"""Original ROM vs relocated/private-state component; no host ROM execution."""
import collections,json
from py65.devices.mpu6502 import MPU
import check_bubble_bobble_closure_1101_v1 as T
import prepare_bubble_bobble_component_1101_v2 as P

O=P.O;layout=json.loads((O/'component-layout.json').read_text());lab=P.labels(O/'component.lbl');blob=(O/'component.bin').read_bytes()
oldpair=T.pair;original_calls=collections.Counter();relocated_calls=collections.Counter();cycle_delta=collections.defaultdict(list);private_writes_checked=0
return_words={pc+2:lab[f'BbOriginal_{pc:04X}']+2 for bank,pc,c in json.loads((O/'instruction-index.json').read_text())['rows']if c[0]==0x20 and f'BbOriginal_{pc:04X}'in lab}
unwind=None;normalized_dead_A=0


def pair():
 a,_=oldpair();b=MPU();b.memory[0xa000:0xc000]=blob
 for start,end in [(0,256),(0x200,0x300),(0x400,0x500)]:
  at=P.ram(start);b.memory[at:at+end-start]=a.memory[start:end]
 b.tilemap=list(a.memory[0x500:0x800]);b.imports={}
 for i,row in enumerate(layout['imports']):
  at=0xf000+i*4;vector=row['vector'];b.memory[vector:vector+3]=[76,at&255,at>>8];b.memory[at]=96;b.imports[at]=row['name']
 for at in list(range(256))+list(range(0x200,0x800)):b.memory[at]=(at*37+0xa5)&255
 b.guard=bytes(b.memory[:256]+b.memory[0x200:0x800])
 return a,b


def put(p,at,data):
 if isinstance(data,int):data=[data]
 a,b=p;a.memory[at:at+len(data)]=data
 if 0x500<=at<0x800:b.tilemap[at-0x500:at-0x500+len(data)]=data
 else:
  target=P.ram(at);b.memory[target:target+len(data)]=data


def setup(m,pc,x,y,a,flags):
 m.pc=pc;m.x=x;m.y=y;m.a=a;m.p=flags;m.sp=255;m.stPushWord(T.RET-1)


def compare(a,b,tag):
 global private_writes_checked,normalized_dead_A
 if a.a!=b.a:
  assert tag=='trap_contact' and unwind is not None and a.a==unwind[0]>>8 and b.a==unwind[1]>>8,(tag,'A',a.a,b.a,unwind)
  assert return_words[unwind[0]]==unwind[1];normalized_dead_A+=1
 assert(a.x,a.y,a.p,a.sp)==(b.x,b.y,b.p,b.sp),(tag,'ABI',(a.a,a.x,a.y,a.p,a.sp),(b.a,b.x,b.y,b.p,b.sp))
 for lo,hi in [(0,256),(0x200,0x300),(0x400,0x500)]:
  target=P.ram(lo);expect=a.memory[lo:hi];actual=b.memory[target:target+hi-lo]
  assert expect==actual,(tag,'state',[(hex(lo+i),v,actual[i])for i,v in enumerate(expect)if v!=actual[i]][:8])
 assert bytes(b.memory[:256]+b.memory[0x200:0x800])==b.guard,(tag,'host RAM changed')
 private_writes_checked+=1


def run(p,pc,x=0,y=0,a=0,flags=0x30,stop=T.RET,tag='component'):
 global unwind
 unwind=None;old_unwind=None;new_unwind=None
 original,component=p;target=lab.get(f'BbOriginal_{pc:04X}');assert target is not None,hex(pc)
 stop_new=stop if stop==T.RET else lab.get(f'BbOriginal_{stop:04X}',lab.get('BbImport'+P.IMPORTS.get(stop,'')))
 assert stop_new is not None,hex(stop)
 setup(original,pc,x,y,a,flags);setup(component,target,x,y,a,flags)
 oldcycles=original.processorCycles;newcycles=component.processorCycles;n=0
 while original.pc!=stop:
  at=original.pc;assert at in T.STUBS or any(s['start']<=at<s['end_exclusive']for s in T.manifest['source_ranges']),(tag,'original outside',hex(at))
  if at in T.STUBS:T.bridges[f'{at:04X}']+=1
  else:T.pcs.add(at)
  if at==0xdf39:old_unwind=original.memory[0x100+((original.sp+1)&255)]+256*original.memory[0x100+((original.sp+2)&255)]
  original.step();n+=1;assert n<20000
 m=component;j=0
 while m.pc!=stop_new:
  at=m.pc;assert 0xa000<=at<lab['BbCodeEnd'] or at in m.imports,(tag,'component outside',hex(at))
  if at in m.imports:
   name=m.imports[at];relocated_calls[name]+=1
   if name in ['Tile23','Tile84']:
    cur=0x23 if name=='Tile23'else 0x84;ptr=m.memory[P.STATE+cur]+256*m.memory[P.STATE+cur+1]
    assert 0x500<=ptr<0x800,(name,hex(ptr));v=m.tilemap[ptr-0x500];m.a=v;m.p=(m.p&~0x82)|(v&0x80)|(2 if not v else 0)
  if at==lab['BbOriginal_DF39']:new_unwind=m.memory[0x100+((m.sp+1)&255)]+256*m.memory[0x100+((m.sp+2)&255)]
  m.step();j+=1;assert j<30000,(tag,hex(m.pc))
 if old_unwind is not None:
  assert new_unwind is not None and return_words[old_unwind]==new_unwind;unwind=(old_unwind,new_unwind)
 compare(original,component,tag);T.counts[tag]+=1;T.max_steps=max(T.max_steps,n);T.cycles[tag].append(original.processorCycles-oldcycles)
 cycle_delta[tag].append(component.processorCycles-newcycles-(original.processorCycles-oldcycles))
 return original


class Output:
 def __truediv__(self,name):return O/('component-CPU.json'if name=='CPU-closure.json'else name)


def main():
 T.pair=pair;T.put=put;T.run=run;T.O=Output();T.main()
 q=json.loads((O/'component-CPU.json').read_text());reject=0;timing={}
 def clock(p):return run(p,0xce30,stop=0xce4d,tag='original_post_update_clock')
 # Twenty-four real source epochs, including the original NMI's isolated
 # clock tail. PPU/controller/coroutine/audio code is deliberately not copied.
 p=pair();put(p,0x464,0x80);growth=[]
 for frame in range(24):
  run(p,0xd887,stop=0xd8fd,tag='timed_bubble_update');clock(p)
  if frame in [6,7,14,15,22,23]:growth.append(dict(update=frame+1,state=p[0].memory[0x88],phase=p[0].memory[0x8a],phase_timer=p[0].memory[0x8b]))
 assert p[0].memory[0x88]==2 and p[0].memory[0x1f]==24;timing['bubble_growth']=growth
 # A fixture deadline is intentionally120, not a claim that every original
 # stage/rank supplies120. It must survive119 genuine enemy updates and expire
 # on exactly the120th when original stop flag0491 is clear.
 p=pair();put(p,0x68,[1,0,16,0]);put(p,0x210,[100,0,0,100,100,0,0,108]);put(p,0x413,120);put(p,0x444,1);put(p,0x26,0x68);deadline=[]
 for frame in range(120):
  run(p,0x9528,x=0x68,y=0x10,stop=0x9603 if frame==119 else T.RET,tag='timed_trap_deadline');clock(p)
  assert bool(p[0].memory[0x6a]&16)==(frame<119)
  if frame in [0,118,119]:deadline.append(dict(update=frame+1,timer=p[0].memory[0x413],enemy_flags=p[0].memory[0x6a]))
 timing['fixture_trap_deadline']=deadline
 eligibility=[]
 for actor,oy in [(0x2e,0),(0x42,8)]:
  for vertical in [0,1,2,3,0x80]:
   for held in [0,0x80]:
    p=pair();put(p,actor+1,held);put(p,actor+3,vertical);put(p,actor+9,1)
    run(p,0xd2c1,x=actor,y=oy,tag='ride_eligibility');starts=vertical in[2,3]and bool(held)
    assert p[0].memory[actor+4]==(28 if starts else 0) and p[0].memory[actor+9]==0
    eligibility.append(dict(actor=actor,vertical=vertical,heldA=bool(held),jump_restarted=starts))
 timing['ride_eligibility']=eligibility
 p=pair();put(p,0x461,1);put(p,0x31,2);put(p,0x2f,0x80);put(p,0x37,1);put(p,0x200,[100,0,3,100,100,10,3,108])
 run(p,0xd2c1,x=0x2e,y=0,tag='timed_ride_start');rise=[]
 for frame in range(28):
  run(p,0xd1e7,x=0x2e,y=0,tag='timed_ride_player');clock(p)
  if frame in[0,26,27]:rise.append(dict(update=frame+1,y=p[0].memory[0x200],vertical=p[0].memory[0x31],jump_index=p[0].memory[0x32]))
 assert p[0].memory[0x200]==57 and p[0].memory[0x31]==2;timing['ridden_jump']=rise
 for row in range(37):
  for flags in [0x30,0xff]:
   a,b=pair();setup(b,0xa000+row*3,17,29,123,flags);n=0
   while b.pc!=T.RET:b.step();n+=1;assert n<10
   assert(b.a,b.x,b.y,b.p,b.sp)==(123,17,29,flags&~1,255)
   assert bytes(b.memory[:256]+b.memory[0x200:0x800])==b.guard;reject+=1
 # Exercise the actual new bounded return, rather than stopping at its seam.
 a,b=pair();put((a,b),0x464,0x80);run((a,b),0xd887,stop=0xd8fd,tag='bounded_return_seam')
 a.pc=a.stPopWord()+1;b.step();compare(a,b,'bounded_return');assert b.pc==T.RET and b.sp==255
 q.update(passed=True,relocated_component_sha256=layout['sha256'],exact_instruction_lockstep=False,original_semantics_and_private_state_equal=True,all_host_zero_page_and_nonstack_RAM_preserved=True,compared_calls=private_writes_checked,reject_native_services=reject,real_bounded_tick_return=True,private_helper_dead_A_return_address_normalizations=normalized_dead_A,imports_called=dict(relocated_calls),timing_sequences=timing,full_call_counts=dict(T.counts),source_vs_component_cycle_delta={k:dict(min=min(v),max=max(v))for k,v in cycle_delta.items()},scope='Original ROM against independently assembled relocated A000 code/private C000..C3FF state. XY/status/SP/all768 state bytes match; A matches except the private DA00 trap helper deliberately discards its caller return word into A. Those cases verify exact original-to-relocated JSR return-token correspondence; the public player/bubble APIs overwrite this dead value. Host ZP/nonstack RAM stays guarded.1930 original fixtures plus sequential original clock/growth/deadline/ride cases,74 rejecting services and actual bounded return. Tile imports read source-format fixture map with original LDA flags; other used imports are typed RTS fixtures. No native terrain/camera, host transport/loader/ISR, ROM/menu admission or emulator proof.')
 (O/'component-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,compared_calls=private_writes_checked,native_reject_cases=reject,host_RAM_preserved=True,relocated_sha256=layout['sha256'])))


if __name__=='__main__':main()
