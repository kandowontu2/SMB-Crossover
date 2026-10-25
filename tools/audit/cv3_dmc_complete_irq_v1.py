"""Interrupt every assembled source-start instruction with the real mapper IRQ."""
from pathlib import Path
import argparse,hashlib,itertools,json
from robots_weapon_cpu_v1 import Arena
from check_tmnt_render_oa import load,address
from verify_native_relocation import NesMPU
from cv3_dmc_complete_cpu_v1 import LaneArena
def interrupted(q,name,a):
 b=q.b;c=NesMPU(memory=q.m,pc=address(b,name));c.a,c.x,c.y,c.p,c.sp=a,7,0xfd,0x30,0xfd;c.stPushWord(0x5aff);count=0;mainsteps=0
 while c.pc!=0x5b00:
  assert mainsteps<1000
  before=(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,list(q.m.banks),q.get('CurrentBankC'),q.get('IrqNewScroll'))
  c.irq();assert c.pc==address(b,'IrqScrollSplit')
  for _ in range(100):
   c.step()
   if c.pc==before[5]and c.sp==before[4]:break
  else:raise AssertionError(('IRQ failed to RTI',hex(before[5]),hex(c.pc)))
  after=(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,list(q.m.banks),q.get('CurrentBankC'),q.get('IrqNewScroll'));assert before==after,(before,after)
  assert q.m[0x2005]==0x53 and q.m[0x5128]==0 and q.m[0x5204]==0
  count+=1;c.step();mainsteps+=1
 assert c.sp==253
 return count,mainsteps
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=load(a.rom);rows=[]
 raw=b['raw'];fixed=raw[16+127*8192:16+128*8192];mirror=raw[16+125*8192:16+126*8192];assert fixed[0x1ffa:]==mirror[0x1ffa:]
 for request,current,status,bank in itertools.product((0x72,0x74,0x75,0x76),(0,5,9),(15,31),(28,88)):
  q=Arena(b,5);q.put(Cv3DmcPriority=current,Cv3DmcPending=request,BassDmcActive=3 if current else 0,GuestCombinedEnable=31,CurrentBankC=bank|128,IrqPPUCTRL=1,IrqNewScroll=0x53);q.m.page(2,bank);q.m.page(3,125 if current else 127);q.m[0x4015]=status
  count,mainsteps=interrupted(q,'Cv3DmcStartGate',request);assert q.m.banks[2]==bank and q.get('CurrentBankC')==bank|128
  rows.append(dict(kind='start',request=request,current=current,hardware_status=status,prior_C=bank,IRQ_RTI_boundaries=count,main_instructions=mainsteps))
 for request,bank,kind in itertools.product((0x72,0x74,0x75,0x76),(28,88),('complete','preempt')):
  q=LaneArena(b,5);q.put(GuestCombinedEnable=31,CurrentBankC=bank|128,IrqPPUCTRL=1,IrqNewScroll=0x53);q.m.page(2,bank);q.invoke('Cv3DmcStartGate',a=request);q.m[0x4015]=15 if kind=='complete'else 31
  count,mainsteps=interrupted(q,'GuestDmcStatus'if kind=='complete'else'Cv3DmcOwnerWrite',31 if kind=='complete'else 2);assert q.m.banks[2]==bank and q.get('CurrentBankC')==bank|128 and q.m.banks[3]==127
  rows.append(dict(kind=kind,request=request,prior_C=bank,IRQ_RTI_boundaries=count,main_instructions=mainsteps))
 result=dict(passed=True,ROM_sha256=hashlib.sha256(raw).hexdigest(),cases=len(rows),actual_IRQ_RTI_boundaries=sum(r['IRQ_RTI_boundaries']for r in rows),IRQ_regs_flags_SP_A_C_E_and_shadows_exact=True,fixed_NMI_reset_IRQ_vectors_identical=True,scope='Assembled CPU actual IRQ at every start/preemption instruction boundary. No emulated PPU timing, DMA clocks, NMI-overrun behavior, live hardware, visible IRQ split or native cadence certification.')
 (a.output/'cases.json').write_text(json.dumps(rows,indent=2)+'\n');(a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
