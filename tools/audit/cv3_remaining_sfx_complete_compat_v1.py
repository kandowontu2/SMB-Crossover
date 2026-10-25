"""All37 ordinary full-AudioUpdate, real CV1 cross and unrelated death ownership."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_render_oa import load,address
from cv3_dmc_complete_cpu_v1 import LaneArena,apu,regs
from final_item_matrix import ROSTER
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def exact(qs):
 allowed=set(range(0x100,0x200))|set(range(address(qs[1].b,'RgAudioZp')+36,address(qs[1].b,'RgAudioZp')+55))
 delta=[(hex(i),qs[0].m[i],qs[1].m[i])for i in range(0x8000)if i not in allowed and qs[0].m[i]!=qs[1].m[i]]
 assert not delta,delta[:20]
 assert apu(qs[0])==apu(qs[1])and qs[0].m.banks==qs[1].m.banks
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
    cs=[q.invoke('AudioUpdate')[0]for q in qs];exact(qs);assert regs(cs[0])==regs(cs[1]);costs.append(cs[1].processorCycles-cs[0].processorCycles)
  rows.append(dict(identity=name,cases=len(costs),cycle_deltas=sorted(set(costs))));(a.output/'progress.json').write_text(json.dumps(rows,indent=2)+'\n')
 cross=[]
 for mode in[0,1]:
  qs=[LaneArena(b,5)for b in bs]
  for q in qs:q.put(Cv3Variant=0,CrossoverBehaviorVersion=mode,AreaMusicQueue=1);q.invoke('AudioUpdate');q.put(AreaMusicQueue=0,AvPending=5);q.invoke('AvSimonRelease');assert q.get('AvAudioRequest')==5 and any(q.get('RgShotType',i)==38 for i in range(10))
  for tick in range(40):
   cs=[q.invoke('AudioUpdate')[0]for q in qs];exact(qs);assert regs(cs[0])==regs(cs[1])
  cross.append(dict(mode=mode,source_CV1_typed_request=5,actor_type=38,whole_updates=40))
 deaths=[]
 for char,variant,mode in itertools.product([2,3,4,5,6,9,15,18,19],[0,1,2,3],[0,1]):
  if char!=5 and variant:continue
  if char==5 and variant:continue # CV3 deliberately gains source effect cancellation
  qs=[LaneArena(b,char)for b in bs]
  for q in qs:q.put(CrossoverBehaviorVersion=mode,Cv3Variant=variant);q.invoke('KillPlayer')
  exact(qs);deaths.append(dict(character=char,variant=variant,mode=mode,actual_KillPlayer_RAM_APU_banks_exact=True))
 result=dict(passed=True,accepted=False,ROM_sha256=sha(a.prepared/'candidate.nes'),baseline_ROM_sha256=sha(a.prepared/'baseline.nes'),identities=len(rows),ordinary_whole_AudioUpdate_cases=sum(r['cases']for r in rows),rows=rows,CV1_Simon_cross=cross,unrelated_actual_KillPlayer_cases=deaths,scope='Whole assembled ordinary audio and real cross/death chains. Direct numeric modes; exact old APU/RAM/register/bank results except unused new-family state. No native cadence, bus, audible waveform or campaign certification.',tool_sha256=sha(__file__))
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='rows'},indent=2))
if __name__=='__main__':main()
