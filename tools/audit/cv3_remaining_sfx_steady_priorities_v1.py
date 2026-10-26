"""Full-state same-work fallback/priority costs versus exact held0c45."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_render_oa import load,address
from cv3_remaining_sfx_queue256_support_v1 import init,sound,EVENTS
from cv3_remaining_sfx_steady_cpu_v4 import invoke,writable_equal
from cv3_dmc_complete_cpu_v1 import apu,regs
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);bs=[load(a.prepared/(n+'.nes'))for n in['baseline','candidate']];rows=[]
 for current,incoming,age,mode in itertools.product(EVENTS,EVENTS,[0,1,5,12,27,42,88],[0,1]):
  qs=[init(b,2 if current in[0x24,0x21,0x1e]else 3)for b in bs]
  for q in qs:
   q.put(CrossoverBehaviorVersion=mode);sound(q,current)
   for _ in range(age):invoke(q,'AudioUpdate')
   sound(q,incoming)
  frames=[]
  for frame in range(4):
   cs=[invoke(q,'AudioUpdate',a=0x55,x=0x71,y=0xa5,flags=0x69)for q in qs];assert regs(cs[0])==regs(cs[1]);assert apu(qs[0])==apu(qs[1]);writable_equal(qs,[address(bs[1],'Cv3FxSavedA')]);frames.append(dict(old=cs[0].processorCycles,new=cs[1].processorCycles,delta=cs[1].processorCycles-cs[0].processorCycles))
  rows.append(dict(current=current,incoming=incoming,age=age,mode=mode,frames=frames))
  if len(rows)%14==0:(a.output/'progress.json').write_text(json.dumps(dict(cases=len(rows)))+'\n')
 (a.output/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n');r=dict(passed=True,native_executed=False,accepted=False,ROM_sha256=sha(a.prepared/'candidate.nes'),parent_ROM_sha256=sha(a.prepared/'baseline.nes'),strict_full_state_priority_schedules=len(rows),whole_audio_updates=len(rows)*4,all_complete_raw_APU_AXYP_SP_banks_final_actual_written_RAM_except_dead52_exact=True,cost_delta_range=[min(f['delta']for r in rows for f in r['frames']),max(f['delta']for r in rows for f in r['frames'])],scope='Original source priority is independently asserted by queue suite; this is complete output/state/ABI equivalence to its exact0c45 implementation plus honest actual whole-audio fallback costs. Scratch52 is the sole declared dead private exception. Not native deadline/cadence acceptance.',tool_sha256=sha(__file__));(a.output/'proof.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
