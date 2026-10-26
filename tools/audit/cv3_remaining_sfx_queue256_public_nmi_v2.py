"""Actual full lagNMI at every genuine compatibility-wrapper boundary."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_render_oa import load,address
from cv3_dmc_complete_cpu_v1 import apu,regs
from cv3_remaining_sfx_queue256_cpu_v1 import setup,start,finish,nmi,memory
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=load(a.rom);rows=[]
 for event,age,counter,typ,world in itertools.product([None,0x21],[0,12],[0,255],[0,1,4,6,7],[0,21]):
  def make():
   q=setup(b,age,event,counter);q.put(AvAudioRequest=world);return q
  probe=make();c=start(probe,name='Cv3FxSpawn',a=typ);trace=[];published=False
  for _ in range(300):
   if c.pc==0x5b00:break
   at=len(probe.m.writes);pc=c.pc;c.step();published|=any(ad==address(b,'Cv3FxQueueHead')for ad,v in probe.m.writes[at:]);trace.append(dict(pc=pc,published=published))
  else:raise AssertionError('trace timeout')
  for boundary in range(len(trace)+1):
   q=make();c=start(q,name='Cv3FxSpawn',a=typ)
   for _ in range(boundary):c.step()
   committed=trace[boundary-1]['published']if boundary else False;before=regs(c);actual=nmi(q,c);assert regs(c)==before;finish(c)
   r=make();d=start(r,name='Cv3FxSpawn',a=typ)
   if committed:finish(d);expected=nmi(r,d)
   else:expected=nmi(r,d);finish(d)
   assert actual['APU']==expected['APU']and memory(q)==memory(r)and q.m.banks==r.m.banks
   assert(c.a,c.x,c.y,c.p&0xcf,c.sp)==(typ,3,0x71,0x69&0xcf,253)
   q.invoke('AudioUpdate');r.invoke('AudioUpdate');assert apu(q)==apu(r)and memory(q)==memory(r)
   rows.append(dict(current=event,age=age,counter=counter,type=typ,world=world,boundary=boundary,published=committed,NMIcycles=actual['cycles']))
 result=dict(passed=True,accepted=False,ROM_sha256=sha(a.rom),actual_full_lag_NMI_genuine_checked_public_boundaries=len(rows),all_instruction_boundaries_AXYP_SP_banks_nonstack_RAM_and_following_APU_exact=True,scope='Actual original NMI/RTI interrupt at each compatibility-wrapper boundary, including preserved originalA/actor write and private checked producer. Invalid-type/world branches included. Native/PPU/DMC timing remains unqualified.',tool_sha256=sha(__file__))
 (a.output/'boundaries.json').write_text(json.dumps(rows,separators=(',',':'))+'\n');(a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
