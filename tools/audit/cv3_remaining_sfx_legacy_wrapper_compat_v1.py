"""Fresh all37 ordinary audio identities and the real base-Simon cross release."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_render_oa import load,address
from cv3_dmc_complete_cpu_v1 import LaneArena,apu,regs
from final_item_matrix import ROSTER
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def same(qs):
 allowed=set(range(0x100,0x200))
 assert all(qs[0].m[i]==qs[1].m[i]for i in range(0x8000)if i not in allowed)
 assert qs[0].m.banks==qs[1].m.banks and apu(qs[0])==apu(qs[1])
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);bs=[load(a.prepared/(n+'.nes'))for n in['baseline','candidate']];rows=[]
 for name,slot,char,variant,value,family in ROSTER:
  costs=[]
  for mode,request in itertools.product([0,1],[(1,0),(2,0),(0,4),(1,8)]):
   qs=[LaneArena(b,char)for b in bs]
   for q in qs:
    q.put(CrossoverBehaviorVersion=mode,AreaMusicQueue=request[0],EventMusicQueue=request[1])
    if variant:q.set(variant,value)
   for tick in range(32):
    for q in qs:q.put(GamePauseStatus=int(tick in[16,17]),AvAudioRequest=21 if tick==8 else 22 if tick==12 else 0)
    if tick==20:
     for q in qs:q.m[0x4015]=15
    cs=[q.invoke('AudioUpdate')[0]for q in qs];same(qs);assert regs(cs[0])==regs(cs[1]);costs.append(cs[1].processorCycles-cs[0].processorCycles)
  rows.append(dict(identity=name,character=char,variant=variant,value=value,cases=len(costs),cycle_delta=[min(costs),max(costs)]));(a.output/'progress.json').write_text(json.dumps(rows,indent=2)+'\n')
 cross=[]
 for mode in(0,1):
  qs=[LaneArena(b,5)for b in bs]
  for q in qs:q.put(Cv3Variant=0,CrossoverBehaviorVersion=mode,AreaMusicQueue=1);q.invoke('AudioUpdate');q.put(AreaMusicQueue=0,AvPending=5);q.invoke('AvSimonRelease');assert q.get('AvAudioRequest')==5 and any(q.get('RgShotType',i)==38 for i in range(10))
  for tick in range(40):
   cs=[q.invoke('AudioUpdate')[0]for q in qs];same(qs);assert regs(cs[0])==regs(cs[1])
  cross.append(dict(mode=mode,release='AvSimonRelease',actor_type=38,source_request=5,source_family='existing Crossover2.02 CV1 SimonCross NSF',full_AudioUpdate_cases=40,exact_old_hardware_RAM_regs_banks=True))
 assert len(rows)==37
 result=dict(passed=True,baseline_sha256=sha(a.prepared/'baseline.nes'),ROM_sha256=sha(a.prepared/'candidate.nes'),identities=len(rows),ordinary_full_AudioUpdate_cases=sum(r['cases']for r in rows),rows=rows,real_existing_cross_release_cases=cross,tool_sha256=sha(__file__),scope='Fresh eaa3/private legacy-wrapper actual assembled whole ordinary AudioUpdate, both directly seeded modes, four area/event requests, typed injury, pause and hardware-ended controls. BaseSimon cross release and complete40-update original-family SFX preserved; originalCV3cross14 is not substituted into the CV1 family. No native/campaign or new pulse-SFX certification.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='rows'},indent=2))
if __name__=='__main__':main()
