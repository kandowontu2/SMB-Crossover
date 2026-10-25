"""Interrupt each real noise-helper instruction with the unchanged mapper IRQ/RTI."""
from pathlib import Path
import argparse,hashlib,itertools,json
from cv3_dmc_complete_cpu_v1 import LaneArena
from check_tmnt_render_oa import load,address,location
from verify_native_relocation import NesMPU
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=load(a.rom);rows=[]
 cases=[]
 for name,cue,y,flags in itertools.product(['Cv3NoiseCueFlags','Cv3NoiseCuePeriods','Cv3NoiseCueVolumes'],[0,0x13,0x15],[0,11,15,27],[0x20,0x21,0x60,0x61]):cases.append(dict(name=name,cue=cue,y=y,flags=flags,request=0,typ=1,character=5,pause=0))
 for request,flags in itertools.product([26,27,28],[0x20,0x21,0x60,0x61]):cases.append(dict(name='Cv3NoiseCueReset',cue=0,y=23,flags=flags,request=request,typ=1,character=5,pause=0))
 for typ,request in itertools.product([1,2,6],[0,21,26,27,28]):cases.append(dict(name='Cv3NoiseCueSpawn',cue=0,y=23,flags=0x20,request=request,typ=typ,character=5,pause=0))
 for char,pause in itertools.product([3,4,5],[0,1]):cases.append(dict(name='Cv3NoiseCueOwnerInit',cue=0x13,y=23,flags=0x21,request=0,typ=0,character=char,pause=pause))
 for rec,ebank in itertools.product(cases,[125,127]):
  q=LaneArena(b,rec['character']);q.put(Cv3NoiseCue=rec['cue'],AvAudioRequest=rec['request'],GamePauseStatus=rec['pause'],Cv3NoiseIndex=15,IrqPPUCTRL=1,IrqNewScroll=0x53)
  pc=address(b,rec['name']);window=(pc-0x8000)//8192;bank=(location(b,rec['name'])-16)//8192;q.m.page(window,bank);q.set('CurrentBank'if window==1 else'CurrentBankC',bank|128);q.m.page(3,ebank)
  c=NesMPU(memory=q.m,pc=pc);c.a,c.x,c.y,c.p,c.sp=rec['typ'],0,rec['y'],rec['flags'],0xfd;c.stPushWord(0x5aff);steps=0
  while c.pc!=0x5b00:
   assert steps<1000
   before=(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,list(q.m.banks),q.get('CurrentBank'),q.get('CurrentBankC'))
   c.irq();assert c.pc==address(b,'IrqScrollSplit')
   for _ in range(100):
    c.step()
    if c.pc==before[5]and c.sp==before[4]:break
   else:raise AssertionError(('No real RTI',rec,hex(c.pc)))
   after=(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,list(q.m.banks),q.get('CurrentBank'),q.get('CurrentBankC'));assert before==after
   c.step();steps+=1
  assert c.sp==253;rows.append(dict(**rec,E_bank=ebank,actual_IRQ_RTI_boundaries=steps))
 result=dict(passed=True,ROM_sha256=hashlib.sha256(a.rom.read_bytes()).hexdigest(),cases=len(rows),actual_IRQ_RTI_boundaries=sum(r['actual_IRQ_RTI_boundaries']for r in rows),actual_A_C_E_register_flags_stack_shadows_exact=True,scope='Real assembled IRQ/RTI at every helper instruction boundary under both fixed125/127 windows. No NMI timing, physical DMC stealing, native PPU/OAM/CHR/cadence or waveform claim.')
 (a.output/'cases.json').write_text(json.dumps(rows,indent=2)+'\n');(a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
