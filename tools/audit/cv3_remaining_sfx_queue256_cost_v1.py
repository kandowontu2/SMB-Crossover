"""Actual full release/audio costs against50b,0802 and frozen64-ring7b0."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_render_oa import load
from cv3_remaining_sfx_queue256_support_v1 import init,sound,EVENTS
from cv3_dmc_complete_cpu_v1 import apu,regs
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 paths=[D/'cv3-remaining-current50b-v1/baseline.nes',D/'cv3-remaining-resident-v4/candidate.nes',D/'cv3-remaining-queue-v8/candidate.nes',a.rom];bs=[load(p)for p in paths];rows=[]
 for typ,mode,face in itertools.product(range(1,7),[0,1],[1,2]):
  qs=[init(b,2)for b in bs]
  for q in qs:q.put(CrossoverBehaviorVersion=mode,PlayerFacingDir=face)
  cs=[q.invoke('Cv3Spawn',a=typ)[0]for q in qs];assert len(set(regs(c)for c in cs))==1;cost=[c.processorCycles for c in cs]
  rows.append(dict(type=typ,mode=mode,face=face,cycles=cost,delta_vs50b=cost[3]-cost[0],delta_vs0802=cost[3]-cost[1],delta_vs7b0=cost[3]-cost[2]))
 actual=[]
 for sub,mode in itertools.product([1,2,3],[0,1]):
  qs=[init(b,2)for b in bs]
  for q in qs:q.put(CrossoverBehaviorVersion=mode,Cv3AttackAge=14,Cv3AttackKind=2,Cv3Fresh=0,SavedJoypadBits=0);q.set('Cv3Subweapon',sub,1)
  cs=[q.invoke('Cv3WeaponsGate')[0]for q in qs];assert len(set(regs(c)for c in cs))==1;maincost=[c.processorCycles for c in cs];audio=[]
  for frame in range(90):
   cc=[q.invoke('AudioUpdate')[0]for q in qs];assert apu(qs[1])==apu(qs[2])==apu(qs[3]),('unchanged ordinary release fullAPU',sub,mode,frame,[apu(q)for q in qs[1:]])
   costs=[c.processorCycles for c in cc];audio.append(dict(frame=frame,cycles=costs,delta_vs0802=costs[3]-costs[1],delta_vs7b0=costs[3]-costs[2]))
  actual.append(dict(subweapon=sub,mode=mode,main_cycles=maincost,main_delta_vs50b=maincost[3]-maincost[0],main_delta_vs0802=maincost[3]-maincost[1],audio=audio,total90_delta_vs0802=sum(r['delta_vs0802']for r in audio),total90_delta_vs7b0=sum(r['delta_vs7b0']for r in audio)))
 controls=[]
 for event,mode,queue in itertools.product([None]+list(EVENTS),[0,1],[0,0x20,0x22,0x21]):
  qs=[init(b,2 if event in[0x24,0x21,0x1e]else 3)for b in bs[1:]]
  for q in qs:
   q.put(CrossoverBehaviorVersion=mode)
   if event:sound(q,event)
   q.put(Square1SoundQueue=queue)
  costs=[]
  for frame in range(100):
   cs=[q.invoke('AudioUpdate')[0]for q in qs];assert apu(qs[0])==apu(qs[1])==apu(qs[2]),('common world fullAPU',event,mode,queue,frame,[apu(q)for q in qs]);assert len(set(regs(c)for c in cs))==1
   costs.append([c.processorCycles for c in cs])
  controls.append(dict(event=event,mode=mode,Square1SoundQueue=queue,frames=100,cycles=costs,delta_vs0802=sorted(set(c[2]-c[0]for c in costs)),delta_vs7b0=sorted(set(c[2]-c[1]for c in costs))))
 result=dict(passed=True,accepted=False,status='SOURCE_COMPONENT_COST_NOT_NATIVE_BUDGET_ACCEPTANCE',ROM_sha256=sha(a.rom),ordered_ROMs=[dict(path=str(p),sha256=sha(p))for p in paths],actual_spawn=rows,actual_delayed_release=actual,generic_controls=controls,scope='Actual full assembled release and AudioUpdate. Source sample/rawAPU retained on ordinary release controls; pause/cold new-admission correction separate. No native deadline or waveform claim.',tool_sha256=sha(__file__))
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,ROM_sha256=result['ROM_sha256'],releases=[dict(sub=r['subweapon'],mode=r['mode'],main_delta=r['main_delta_vs50b'],audio0=r['audio'][0],audio90delta=r['total90_delta_vs0802'])for r in actual],controls=len(controls)),indent=2))
if __name__=='__main__':main()
