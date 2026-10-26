"""Actual initial menu caller/PPU continuation and lag-NMI/IRQ boundary models."""
from pathlib import Path
import argparse,hashlib,itertools,json
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import Memory,address,location
from verify_native_relocation import NesMPU
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


class Ports(Memory):
 def __init__(self,b,t,w,mirror):
  self.t,self.v,self.w,self.x=t,t,w,5;self.control=mirror;self.mask=6;self.io=[];self.data_port=[];self.vram=bytearray((i*17+3)&63 for i in range(16384));super().__init__(b)
 def norm(self,a):
  a&=0x3fff
  if a>=0x3f00:
   a=0x3f00+(a&31)
   if a in [0x3f10,0x3f14,0x3f18,0x3f1c]:a-=16
  return a
 def __getitem__(self,a):
  v=super().__getitem__(a)
  if a==0x2002:self.w=0;self.io.append(('r',a,v))
  return v
 def __setitem__(self,a,v):
  if isinstance(a,int)and 0x2000<=a<=0x2007:
   self.io.append(('w',a,v))
   if a==0x2000:self.control=v;self.t=(self.t&~0xc00)|((v&3)<<10)
   elif a==0x2001:self.mask=v
   elif a==0x2005:
    if self.w:self.t=(self.t&~0x73e0)|((v&7)<<12)|((v&0xf8)<<2)
    else:self.t=(self.t&~31)|(v>>3);self.x=v&7
    self.w^=1
   elif a==0x2006:
    self.t=((self.t&255)|((v&63)<<8))if not self.w else((self.t&0x7f00)|v);self.w^=1
    if not self.w:self.v=self.t
   elif a==0x2007:
    self.data_port.append((self.norm(self.v),v));self.vram[self.norm(self.v)]=v;self.v=(self.v+(32 if self.control&4 else 1))&0x7fff
  super().__setitem__(a,v)
 def state(self):return dict(t=self.t,v=self.v,w=self.w,fineX=self.x,control=self.control,mask=self.mask)


def setup(b,mode=0,variant=1,mirror=0xa8,t=0x5b3f,w=1):
 q=Arena(b,18);old=q.m;q.m=Ports(b,t,w,mirror)
 for i in range(0x8000):list.__setitem__(q.m,i,list.__getitem__(old,i))
 q.put(OperMode=0,OperMode_Task=3,GameEngineSubroutine=0,CrossoverMenuState=1,CrossoverMenuIndex=17,CrossoverMenuPressed=0,CrossoverMenuButtons=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,VvVariant=variant,CrossoverBehaviorVersion=mode,DisableScreenFlag=1,NmiDisable=255,Mirror_PPUMASK=6,Mirror_PPUCTRL=mirror,ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,Player_PageLoc=0,PlayerStatus=0,Sprite0HitDetectFlag=0)
 list.__setitem__(q.m,0x2002,0x80);q.m.io=[];q.m.data_port=[];return q


def nmi_prefix(q):
 q.put(NmiDisable=0,DisableScreenFlag=0);c=NesMPU(memory=q.m,pc=0x5b00);c.sp=0xfd;c.a,c.x,c.y,c.p=0x55,37,193,0x30;c.nmi();before=len(q.m.io)
 for steps in range(100000):
  if c.pc==address(q.b,'OAMandReadJoypad'):break
  c.step()
 else:raise AssertionError(('NMI prefix timeout',c.pc))
 return dict(regs=[c.a,c.x,c.y,c.p,c.sp],cycles=c.processorCycles,ppu=q.m.state(),banks=q.m.banks[:],io=q.m.io[before:])


def foreground(q,name='CrossoverMenuInput'):
 c,_=q.invoke(name);return dict(regs=[c.a,c.x,c.y,c.p,c.sp],cycles=c.processorCycles,ram=bytes(q.m[:0x8000]),ppu=q.m.state(),io=q.m.io[:],port=q.m.data_port[:],banks=q.m.banks[:])


def direct_cpu(q):
 q.m.page(1,66);q.set('CurrentBank',194);q.m.io=[];q.m.data_port=[]
 c=NesMPU(memory=q.m,pc=address(q.b,'CrossoverMenuInput'));c.sp=0xfd;c.a,c.x,c.y,c.p=0x55,73,19,0x30;c.stPushWord(0x5aff)
 for _ in range(100000):
  if c.pc==address(q.b,'QueueVariantHint')and q.m.banks[1]==66:break
  c.step()
 else:raise AssertionError('Actual BuildScreen did not reach its hint owner')
 return c


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['baseline','candidate','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);bs=[scoped_load(a.baseline),scoped_load(a.candidate)];rows=[];case=None
 try:
  for mode,variant,mirror,w in itertools.product([0,1],range(4),[0xa8,0xa9,0xac,0xaf],[0,1]):
   case=dict(kind='full-buildscreen',mode=mode,variant=variant,mirror=mirror,initial_w=w);outs=[]
   for b in bs:
    q=setup(b,mode,variant,mirror,w=w);f=foreground(q);n=nmi_prefix(q);outs.append((q,f,n))
   (q,f,n),(r,g,k)=outs;assert f['regs']==g['regs']and f['banks']==g['banks'],('Full initial caller ABI',case)
   allowed=set(range(address(bs[0],'VRAM_Buffer1'),address(bs[0],'VRAM_Buffer1')+84))|{address(bs[0],'VRAM_Buffer1_Offset')}
   apps=list(range(0x100))+list(range(0x200,0x800))+list(range(0x5c00,0x8000));diff=[i for i in apps if f['ram'][i]!=g['ram'][i]]
   assert set(diff)<=allowed,('Full caller RAM/OAM',case,[(hex(i),f['ram'][i],g['ram'][i])for i in diff if i not in allowed])
   assert len(g['port'])==len(f['port'])+20
   expected=list(bs[0]['raw'][location(bs[0],'QueueVariantHint::ProtoHint'):location(bs[0],'QueueVariantHint::ProtoHint')+20])
   assert g['port'][-20:]==list(zip(range(0x2346,0x235a),expected)),('Correct address/increment/art',case)
   assert n['regs']==k['regs']and n['banks']==k['banks']and n['ppu']==k['ppu']and q.m.vram==r.m.vram,('Following full NMI pre-DMA PPU/register state',case,n,k)
   rows.append(dict(case,full_AXYP_SP_banks_RAM_OAM_exact=True,intended20_original_tiles_published_while_off=True,foreground_delta=g['cycles']-f['cycles'],NMI_prefix_delta=k['cycles']-n['cycles'],final_PPU_t_v_w_fineX_control_exact=True,final_all16384_modeled_PPU_bytes_exact=True))
  # True exclusive-owner guards: unsafe/missing private context must retain
  # the literal old queued writer rather than touching PPUDATA.
  for char,state,disable,mask,private in [(18,2,1,30,255),(18,2,0,6,255),(18,2,1,6,0),(18,1,1,6,255),(17,2,1,6,255)]:
   case=dict(kind='exclusive-owner-fallback',char=char,state=state,disable=disable,mask=mask,private=private)
   out=[]
   for b in bs:
    q=setup(b);q.put(SelectedCharacter=char,CrossoverMenuState=state,DisableScreenFlag=disable,Mirror_PPUMASK=mask,NmiDisable=private);foreground(q,'QueueVariantHint');out.append(q)
   assert out[0].m.io==out[1].m.io==[]and out[0].m.vram==out[1].m.vram
   assert bytes(out[0].m[address(bs[0],'VRAM_Buffer1'):address(bs[0],'VRAM_Buffer1')+84])==bytes(out[1].m[address(bs[1],'VRAM_Buffer1'):address(bs[1],'VRAM_Buffer1')+84])
   rows.append(dict(case,no_foreground_PPU_access=True,original_queued_hint_exact=True))
  b=bs[1];q=setup(b);c=direct_cpu(q);trace=[];helper_return=q.m[0x101+c.sp]+256*q.m[0x102+c.sp]+1;helper_sp=c.sp+2
  while not(c.pc==helper_return and c.sp==helper_sp):trace.append(c.pc);assert len(trace)<1000;c.step()
  while c.pc!=0x5b00:c.step()
  baseline_vram=bytes(q.m.vram);smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2]
  for kind,boundary in itertools.product(['nmi','irq'],range(len(trace))):
   case=dict(kind='interrupt',interrupt=kind,boundary=boundary);q=setup(b);c=direct_cpu(q)
   for _ in range(boundary):c.step()
   deferred=kind=='irq'and bool(c.p&c.INTERRUPT)
   # Pending IRQ is delivered only after the actual SEI region ends.
   while kind=='irq'and c.p&c.INTERRUPT:c.step()
   pc,sp,regs=c.pc,c.sp,(c.a,c.x,c.y,c.p);five=[q.m[i]for i in smc];banks=q.m.banks[:];shadow=(q.get('CurrentBank'),q.get('CurrentBankC'));ppu=q.m.state();io=len(q.m.io)
   if kind=='irq':q.m[0x5204]=128
   getattr(c,kind)();steps=0
   while not(c.pc==pc and c.sp==sp):
    assert steps<60000,('Interrupt timeout',case,hex(c.pc));c.step();steps+=1
   assert steps>0 and(c.a,c.x,c.y,c.p)==regs and q.m.banks==banks and(q.get('CurrentBank'),q.get('CurrentBankC'))==shadow and[q.m[i]for i in smc]==five
   if kind=='nmi':assert q.m.state()==ppu and len(q.m.io)==io,'Private lag NMI must not touch PPU transaction'
   while c.pc!=0x5b00:c.step()
   assert bytes(q.m.vram)==baseline_vram,'No lost/interleaved direct tile on interrupt'
   # Compare same post-NMI scroll/control policy against a no-interrupt copy.
   z=setup(b);d=direct_cpu(z)
   while d.pc!=0x5b00:d.step()
   x=nmi_prefix(q);y=nmi_prefix(z);assert x['ppu']==y['ppu']and q.m.vram==z.m.vram,('Post-NMI mismatch',case,hex(pc),deferred,x['ppu'],y['ppu'],[(hex(i),u,v)for i,(u,v)in enumerate(zip(q.m.vram,z.m.vram))if u!=v][:12])
   rows.append(dict(case,deferred_under_SEI=deferred,actual_handler_steps=steps,fiveSMC_AXYP_SP_actual_banks_restored=True,lag_NMI_PPU_untouched=kind=='nmi',direct_tiles_and_following_NMI_PPU_exact=True))
 except Exception as ex:
  (a.output/'failure.json').write_text(json.dumps(dict(passed=False,native_run=False,error=repr(ex),case=case,completed_cases=len(rows)),indent=2)+'\n');raise
 (a.output/'cases.json').write_text(json.dumps(rows,indent=2)+'\n');proof=dict(passed=True,native_run=False,baseline_ROM_sha256=sha(a.baseline),candidate_ROM_sha256=sha(a.candidate),cases=len(rows),full_BuildScreen_cases=sum(r['kind']=='full-buildscreen'for r in rows),exclusive_owner_controls=5,interrupt_cases=sum(r['kind']=='interrupt'for r in rows),tool_sha256=sha(Path(__file__)),cases_sha256=sha(a.output/'cases.json'),limits='Actual assembled full BuildScreen caller, whole regular NMI prefix to OAM entry and real compiled lag-NMI/IRQ instruction-boundary handlers under explicit PPU t/v/w/fineX/address/increment/palette model. IRQ waits for actual I clear. No real raster/DMA/DMC/controller/visible-pixel or global timing verdict. Synthetic CPU mode values are not native difficulty coverage.')
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))


if __name__=='__main__':main()
