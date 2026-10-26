"""Same actual releases and whole audio: retain all current protocol CPU overhead."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_render_oa import load,address
from cv3_remaining_sfx_complete_cpu_v1 import init,sound,EVENTS
from cv3_dmc_complete_cpu_v1 import apu,regs
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);paths=[D/'cv3-remaining-current50b-v1/baseline.nes',a.rom.parent/'baseline.nes',a.rom];bs=[load(p)for p in paths];rows=[]
 for typ,mode,face in itertools.product(range(1,7),[0,1],[1,2]):
  qs=[init(b,2)for b in bs]
  for q in qs:q.put(CrossoverBehaviorVersion=mode,PlayerFacingDir=face)
  cs=[q.invoke('Cv3Spawn',a=typ)[0]for q in qs];assert regs(cs[0])==regs(cs[1])==regs(cs[2]);cost=[c.processorCycles for c in cs]
  rows.append(dict(type=typ,mode=mode,face=face,complete_Cv3Spawn_cycles=cost,extra_vs50b=cost[2]-cost[0],delta_vs0802=cost[2]-cost[1]))
 actual=[]
 for sub,mode in itertools.product([1,2,3],[0,1]):
  qs=[init(b,2)for b in bs]
  for q in qs:q.put(CrossoverBehaviorVersion=mode,Cv3AttackAge=14,Cv3AttackKind=2,Cv3Fresh=0,SavedJoypadBits=0);q.set('Cv3Subweapon',sub,1)
  cs=[q.invoke('Cv3WeaponsGate')[0]for q in qs];assert regs(cs[0])==regs(cs[1])==regs(cs[2]);maincost=[c.processorCycles for c in cs];audio=[]
  for frame in range(90):
   cc=[q.invoke('AudioUpdate')[0]for q in qs];assert apu(qs[1])==apu(qs[2]),('same-source APU',sub,mode,frame,apu(qs[1]),apu(qs[2]));audio.append(dict(frame=frame,cycles=[c.processorCycles for c in cc],delta_vs0802=cc[2].processorCycles-cc[1].processorCycles))
  actual.append(dict(subweapon=sub,mode=mode,actual_three_shot_release=sub in[2,3],whole_Cv3WeaponsGate_cycles=maincost,main_extra_vs50b=maincost[2]-maincost[0],main_delta_vs0802=maincost[2]-maincost[1],whole_audio=audio,total90_audio_delta_vs0802=sum(r['delta_vs0802']for r in audio),audio_delta_range=[min(r['delta_vs0802']for r in audio),max(r['delta_vs0802']for r in audio)]))
 # Existing1F, idle and generic flag controls share the exact source actions.
 controls=[]
 for event,mode,queue in itertools.product([None]+list(EVENTS),[0,1],[0,0x20,0x22,0x21]):
  qs=[init(b,2 if event in[0x24,0x21,0x1e]else 3)for b in bs[1:]]
  for q in qs:
   q.put(CrossoverBehaviorVersion=mode)
   if event:sound(q,event)
   q.put(Square1SoundQueue=queue)
  costs=[]
  for frame in range(100):
   cs=[q.invoke('AudioUpdate')[0]for q in qs];assert apu(qs[0])==apu(qs[1]),('generic Fireball',event,mode,queue,frame,apu(qs[0]),apu(qs[1]));assert regs(cs[0])==regs(cs[1]);costs.append(cs[1].processorCycles-cs[0].processorCycles)
  controls.append(dict(event=event,mode=mode,Square1SoundQueue=queue,frames=100,cycle_deltas=sorted(set(costs)),total_delta=sum(costs),raw_APU_and_outer_AXYP_exact=True))
 result=dict(passed=True,accepted=False,status='COSTS_RETAINED_NOT_CADENCE_ACCEPTANCE',ROM_sha256=sha(a.rom),adopted50b_sha256=sha(paths[0]),held0802_sha256=sha(paths[1]),actual_spawn_cases=rows,actual_delayed_releases=actual,controls=controls,all_same_source_effect_APU_register_outputs_exact=True,source_generic_Fireball_common_mixer_not_duplicated=True,scope='Actual assembled native ability and whole AudioUpdate costs in bounded initialized component fixtures. No native deadline/cadence, wall-frame, DMC-bus, PPU/OAM or lag-fixed claim. Actual native first-boundary phase must be requalified after optimization; idle and startup overheads are not waived.',tool_sha256=sha(__file__))
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,ROM_sha256=result['ROM_sha256'],spawn_delta_vs50b={t:sorted({r['extra_vs50b']for r in rows if r['type']==t})for t in range(1,7)},delayed_release=[dict(sub=r['subweapon'],mode=r['mode'],main_extra_vs50b=r['main_extra_vs50b'],audio_delta_range=r['audio_delta_range'],audio90_delta=r['total90_audio_delta_vs0802'])for r in actual],control_cases=len(controls)),indent=2))
if __name__=='__main__':main()
