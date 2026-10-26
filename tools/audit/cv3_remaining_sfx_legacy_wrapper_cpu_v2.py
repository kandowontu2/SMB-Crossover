"""Whole AudioUpdate differential/cost gate for finite private legacy wrapper."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_render_oa import load,address
from cv3_remaining_sfx_queue256_support_v1 import init,sound
from cv3_remaining_sfx_steady_cpu_v4 import invoke,writable_equal
from cv3_dmc_complete_cpu_v1 import apu,regs

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def compare(qs,flags=0x30):
 cs=[invoke(q,'AudioUpdate',flags=flags)for q in qs];assert regs(cs[0])==regs(cs[1]),('Full AXYP/SP',regs(cs[0]),regs(cs[1]));assert apu(qs[0])==apu(qs[1]),('Hardware',apu(qs[0]),apu(qs[1]));writable_equal(qs)
 return cs[1].processorCycles-cs[0].processorCycles

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=[load(a.prepared/(n+'.nes'))for n in['baseline','candidate']];rows=[]
 for event,mode in itertools.product([0x13,0x15,0x24,0x21,0x1e,0x1f,0x2f],[0,1]):
  qs=[init(b,2 if event in[0x24,0x21,0x1e]else 3)for b in[old,new]]
  for q in qs:q.put(CrossoverBehaviorVersion=mode);sound(q,event)
  for frame in range(100):
   before=(qs[0].get('Cv3NoiseActive'),qs[0].get('Cv3NoiseIndex'));delta=compare(qs);rows.append(dict(event=event,mode=mode,frame=frame,before=before,delta=delta))
 target=[]
 for index,dirty,flags in itertools.product(range(256),range(8),[0x20,0x69]):
  qs=[init(b)for b in[old,new]]
  for q in qs:
   q.put(Cv3NoiseActive=1,Cv3NoiseIndex=index,AvAudioRequest=0)
   for i,reg in enumerate([12,14,15]):q.set('GuestNativeDirty',(dirty>>i)&1,reg)
  delta=compare(qs,flags);target.append(dict(index=index,dirty=dirty,flags=flags,delta=delta))
 (a.output/'schedules.json').write_text(json.dumps(rows,indent=2)+'\n');(a.output/'phases.json').write_text(json.dumps(target,indent=2)+'\n');t=[r for r in target if r['index']==25];assert all(r['delta']<=-27 for r in t),t
 result=dict(passed=True,native_executed=False,ROM_sha256=sha(a.prepared/'candidate.nes'),parent_ROM_sha256=sha(a.prepared/'baseline.nes'),whole_audio_schedules=len(rows),all256legacy_phases_dirty_flags=len(target),schedule_cost_range=[min(r['delta']for r in rows),max(r['delta']for r in rows)],actual_target_index25_min_delta=min(r['delta']for r in t),actual_target_index25_max_delta=max(r['delta']for r in t),complete_RAM_APU_AXYP_SP_banks_equal=True,tool_sha256=sha(__file__),scope='Assembled fullAudioUpdate differential only, all original legacy index bytes retained including0..28 source phases. No native grant/deadline/campaign verdict; full caller liveness/IRQ/DMC/source readiness remains required.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
