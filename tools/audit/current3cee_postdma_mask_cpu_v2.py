"""Complete assembled NMI/input comparisons; only one mask write changes order."""
from pathlib import Path
import argparse, hashlib, itertools, json, traceback
from check_tmnt_render_oa import Memory, address, location
from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load
from verify_native_relocation import NesMPU
from parodius_visibility_hud_cancel_cpu_v2 import setup
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):Path(p).write_text(json.dumps(z,indent=2)+'\n')
class Bus(Memory):
 def __init__(self,b,initial,pads=(0xa5,0x5a)):
  self.stamps=[];self.cpu=None;self.pending_dma=False;super().__init__(b);list.__setitem__(self,slice(0,0x8000),initial);self.page(1,87);self.page(2,13);self.pads=pads;self.serial=[0,0];self.palette_reads=[];self.pending_dma=False;self.stamps=[];self.cpu=None
 def __getitem__(self,at):
  if at==0x2002:return 0x80
  if at==0x2007:
   v=(len(self.palette_reads)*17+3)&63;self.palette_reads.append(v);return v
  if at in [0x4016,0x4017]:
   p=at-0x4016;n=self.serial[p];self.serial[p]+=1;assert n<8;return(self.pads[p]>>(7-n))&1
  return super().__getitem__(at)
 def __setitem__(self,at,v):
  super().__setitem__(at,v)
  if at==0x4014:self.pending_dma=True
  if isinstance(at,int)and not 0x100<=at<0x200:self.stamps.append((self.cpu.processorCycles if self.cpu else 0,at,v))
def app(m):return bytes(m[:0x100])+bytes(m[0x200:0x800])+bytes(m[0x5c00:0x8000])
def run(b,q,stall=None,inject_index=None,trace=False):
 m=Bus(b,bytes(q.m[:0x8000]));m[address(b,'CurrentBank')]=215;m[address(b,'CurrentBankC')]=141
 smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2]
 before=[m[x]for x in smc];c=NesMPU(memory=m,pc=0x5b00);c.a,c.x,c.y,c.p,c.sp=0xa7,73,19,0x71,0xfd;m.cpu=c;c.nmi();m.writes=[];m.stamps=[];pcs=[];irqs=0
 for step in range(100000):
  if c.pc==0x5b00 and c.sp==0xfd:break
  if inject_index==step:
   assert not c.p&4;regs=(c.a,c.x,c.y,c.p,c.sp,c.pc);saved=([m[x]for x in smc],m.banks[:],m[address(b,'CurrentBank')],m[address(b,'CurrentBankC')]);c.irq()
   for k in range(2000):
    if(c.a,c.x,c.y,c.p,c.sp,c.pc)==regs:break
    c.step()
   else:raise AssertionError('IRQ did not restore complete foreground state')
   assert saved==([m[x]for x in smc],m.banks[:],m[address(b,'CurrentBank')],m[address(b,'CurrentBankC')]);irqs+=1
  pcs.append((c.pc,c.p,c.processorCycles));c.step()
  if m.pending_dma:
   if stall is not None:c.processorCycles+=513+((c.processorCycles+stall)&1)
   m.pending_dma=False
 else:raise AssertionError(('NMI timeout',hex(c.pc),m.banks))
 assert c.sp==0xfd and(c.a,c.x,c.y)==(0xa7,73,19)
 assert [m[x]for x in smc]==before
 writes=[(at,v)for at,v in m.writes if not 0x100<=at<0x200]
 masks=[i for i,(at,v)in enumerate(writes)if at==0x2001]
 regular=q.get('NmiDisable')<128
 assert len(masks)==(2 if regular else 0)
 canonical=writes[:]
 if regular:
  target=masks[-1];removed=canonical.pop(target);assert removed==(0x2001,m[address(b,'Mirror_PPUMASK')])
  dma=next(i for i,(at,v)in enumerate(writes)if at==0x4014);strobe=next(i for i,(at,v)in enumerate(writes)if at==0x4016)
  if 'PostDmaMaskEnable'in b['syms']:assert dma<target<strobe
  else:assert target<dma
 assert m.serial==([8,8]if regular else[0,0])
 return dict(regs=[c.a,c.x,c.y,c.p,c.sp],ram=app(m),banks=m.banks[:],writes=canonical,reads=m.palette_reads,cycles=c.processorCycles,trace=pcs if trace else[],irqs=irqs,stamps=m.stamps,serial=m.serial)
def seed(b,char,oper,lag,blank,reload,packet):
 q=Arena(b,char);q.put(OperMode=oper,NmiDisable=255 if lag else 0,DisableScreenFlag=blank,Mirror_PPUCTRL=0xa8,Mirror_PPUMASK=30,Sprite0HitDetectFlag=1,ReloadCHRBank=reload,X5WideChrActive=1,SsChrActive=0,VRAM_Buffer_AddrCtrl=0,SmFreezePalettePending=0,PnBombCapturePending=0,PnBombPaletteReady=0,InvHudActive=0,X5HudChrUpper=0)
 for n in ['CurrentCHRBank','X5ChrMode']:q.array(n,[0]*12)
 data=[0]if not packet else[0x3f,0x10,4,15,48,21,8,0x20,0x40,1,7,0]
 q.array('VRAM_Buffer1',data);q.set('VRAM_Buffer1_Offset',len(data)-1);return q
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 try:
  bs=[scoped_load(a.prepared/(s+'.nes'))for s in ['baseline','candidate']];proof=json.loads((a.prepared/'proof.json').read_text());assert proof['passed'];rows=[]
  def compare(kind,spec,states,stall=None):
   out=[run(b,q,stall)for b,q in zip(bs,states)]
   for field in ['regs','ram','banks','writes','reads','serial']:assert out[0][field]==out[1][field],(kind,spec,field,out[0][field]if field not in['ram','writes']else'first mismatch',out[1][field]if field not in['ram','writes']else'first mismatch')
   rows.append(dict(kind=kind,spec=spec,stall_model=stall,before_cycles=out[0]['cycles'],after_cycles=out[1]['cycles'],delta=out[1]['cycles']-out[0]['cycles']));return out
  for char,oper,lag,blank,reload,packet in itertools.product(range(24),[0,1],[0,1],[0,1],[0,1],[0,1]):
   compare('complete-NMI',[char,oper,lag,blank,reload,packet],[seed(b,char,oper,lag,blank,reload,packet)for b in bs])
  print(json.dumps(dict(complete_NMI=len(rows))),flush=True)
  for buttons,stall in itertools.product(range(256),[0,1]):
   out=[]
   for b in bs:
    q=seed(b,0,0,0,0,1,0);m=Bus(b,bytes(q.m[:0x8000]),(buttons,buttons^255));c=NesMPU(memory=m,pc=address(b,'OAMandReadJoypad'));c.sp=0xfd;c.stPushWord(0x5aff);m.cpu=c;m.writes=[]
    while c.pc!=0x5b00:
     c.step()
     if m.pending_dma:c.processorCycles+=513+((c.processorCycles+stall)&1);m.pending_dma=False
    out.append((m[address(b,'SavedJoypad1Bits')],m[address(b,'SavedJoypad2Bits')],c.sp,c.processorCycles))
   assert out[0][:3]==out[1][:3]==(buttons,buttons^255,0xfd)and out[1][3]-out[0][3]==8
  for char,oper,lag,reload,stall in itertools.product([0,3,11,18,19],[0,1],[0,1],[0,1],[0,1]):compare('complete-NMI-DMA-parity',[char,oper,lag,reload],[seed(b,char,oper,lag,0,reload,1)for b in bs],stall)
  for variant,kind,ctrl in itertools.product([1,2,3],['full','attr','new-life','death','capture'],[0,6,4]):
   qs=[]
   for b in bs:
    q=setup(b,0,variant,3 if kind=='attr'else 0);q.put(InvHudActive=variant*2+1 if kind=='attr'else 0,Mirror_PPUCTRL=0xa8,Mirror_PPUMASK=30,Sprite0HitDetectFlag=1,ReloadCHRBank=1,X5WideChrActive=1,VRAM_Buffer_AddrCtrl=ctrl)
    q.invoke('PnHud')
    if kind=='new-life':q.invoke('PnHudNewLife')
    if kind=='death':q.invoke('VvDeathStart')
    if kind=='capture':q.put(PnBombPaletteReady=0,PnBombCapturePending=1)
    q.array('VRAM_Buffer2',[0x20,0x80,0x81,5,0]);q.set('VRAM_Buffer2_Offset',4);q.set('NmiDisable',0);qs.append(q)
   compare('complete-NMI-HUD-lifecycle',[variant,kind,ctrl],qs)
  # Actual compiled IRQ at every enabled instruction boundary from scanline
  # setup through the input return, on both real linked routines separately.
  irq_rows=[]
  for bi,b in enumerate(bs):
   q=seed(b,18,1,0,0,1,1);reference=run(b,q,trace=True);start=address(b,'BankSwitchCHR');end=address(b,'NonMaskableInterrupt::InitBuffer');active=False
   for index,(pc,flags,clock)in enumerate(reference['trace']):
    if pc==start:active=True
    if pc==end:active=False
    if active and not flags&4:
     r=run(b,seed(b,18,1,0,0,1,1),inject_index=index);assert r['regs']==reference['regs']and r['ram']==reference['ram']and r['banks']==reference['banks'];irq_rows.append(dict(ROM='baseline'if bi==0 else'candidate',boundary=index,PC=pc,cycles=r['cycles'],fiveSMC_AXYP_SP_banks_resumed_exact=True))
  put(a.output/'cases.json',rows);put(a.output/'IRQ-cases.json',irq_rows)
  put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,candidate_ROM_sha256=sha(a.prepared/'candidate.nes'),baseline_ROM_sha256=sha(a.prepared/'baseline.nes'),complete_NMI_cases=len(rows),input_all_bytes_both_DMA_parities=512,actual_IRQ_cases=len(irq_rows),all_complete_return_AXYP_SP_application_RAM_5SMC_banks_input_and_other_IO_exact=True,intended_IO_delta='Only the last regular-NMI PPUMASK write is moved from before CHR/DMA to immediately after DMA and before input strobe. Its value and all other ordered writes/reads are exact.',cycle_delta=[min(r['delta']for r in rows),max(r['delta']for r in rows)],cases_sha256=sha(a.output/'cases.json'),IRQ_sha256=sha(a.output/'IRQ-cases.json'),tool_sha256=sha(__file__),limits='Synthetic complete-NMI and source-produced HUD controls. No physical PPU/DMA/DMC scheduling, native IRQ31 or universal late-NMI verdict. Mouse source control is separate.'))
  print(json.dumps(json.loads((a.output/'proof.json').read_text()),indent=2))
 except BaseException as ex:put(a.output/'failure.json',dict(passed=False,native_run=False,error=repr(ex),traceback=traceback.format_exc(),completed=rows if 'rows'in locals()else[]));(a.output/'failed-tool.py').write_bytes(Path(__file__).read_bytes());raise
if __name__=='__main__':main()
