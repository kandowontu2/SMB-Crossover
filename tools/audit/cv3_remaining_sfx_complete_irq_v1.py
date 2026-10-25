"""Actual original mapper IRQ/RTI at each complete roster/audio CPU boundary."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_render_oa import load,address,location
from cv3_dmc_complete_cpu_v1 import LaneArena,apu,regs
from cv3_remaining_sfx_complete_cpu_v1 import init,sound,EVENTS
from verify_native_relocation import NesMPU
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=load(a.rom);rows=[]
 for event,age,ebank in itertools.product(EVENTS,[0,5,27],[125,127]):
  q=init(b,2 if event in[0x24,0x21,0x1e]else 3);sound(q,event)
  for _ in range(age):q.invoke('AudioUpdate')
  q.put(IrqPPUCTRL=1,IrqNewScroll=0x53);q.m.page(3,ebank);pc=address(b,'RosterAudioUpdate');c=NesMPU(memory=q.m,pc=pc);c.a,c.x,c.y,c.p,c.sp=0x55,3,7,0x20,0xfd;c.stPushWord(0x5aff);steps=0;voices={}
  while c.pc!=0x5b00:
   assert steps<30000
   before=(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,list(q.m.banks),q.get('CurrentBank'),q.get('CurrentBankC'),q.m[address(b,'R0')],q.m[address(b,'R1')]);c.irq();assert c.pc==address(b,'IrqScrollSplit')
   for _ in range(100):
    c.step()
    if c.pc==before[5]and c.sp==before[4]:break
   else:raise AssertionError(('No actual RTI',event,age,hex(c.pc)))
   after=(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,list(q.m.banks),q.get('CurrentBank'),q.get('CurrentBankC'),q.m[address(b,'R0')],q.m[address(b,'R1')]);assert before==after
   c.step();steps+=1
  assert c.sp==253;rows.append(dict(event=event,age=age,E_window_code_alias=ebank,actual_IRQ_RTI_boundaries=steps));(a.output/'progress.json').write_text(json.dumps(rows,indent=2)+'\n')
 result=dict(passed=True,ROM_sha256=hashlib.sha256(a.rom.read_bytes()).hexdigest(),cases=len(rows),actual_IRQ_RTI_boundaries=sum(r['actual_IRQ_RTI_boundaries']for r in rows),actual_AXYP_SP_PC_R0_R1_A_C_E_mapper_shadows_exact=True,scope='Real assembled RosterAudioUpdate Save/Play/private A82 service/restore and actual IRQ/RTI at every instruction. E125/127 are code-alias controls. No NMI scheduling, physical DMC bus, PPU/OAM/CHR, native cadence or audible waveform certification.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
