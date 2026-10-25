"""Exact whole-audio C28 resident differential versus frozen2e, no pointer exclusions."""
from pathlib import Path
import argparse, hashlib, itertools, json, random
from check_tmnt_render_oa import load, address
from cv3_remaining_sfx_complete_cpu_v1 import init, sound, EVENTS
from cv3_dmc_complete_cpu_v1 import apu, regs

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def compare(qs,cs):
 differences=[(hex(i),qs[0].m[i],qs[1].m[i])for i in range(0x8000)if not 0x100<=i<0x200 and qs[0].m[i]!=qs[1].m[i]]
 assert not differences,differences[:12]
 assert apu(qs[0])==apu(qs[1]),('APU',apu(qs[0]),apu(qs[1]))
 assert qs[0].m.banks==qs[1].m.banks and regs(cs[0])==regs(cs[1])
 return cs[1].processorCycles-cs[0].processorCycles

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.rom.parent/'baseline.nes'),load(a.rom);rows=[]
 assert sha(a.rom.parent/'baseline.nes')=='2e005c8e2acde44bc184459d92b2966ee488b92819dd91151577fdf444b751df'
 for event,mode,life in itertools.product(EVENTS,[0,1],['natural','pause','scene','death','music']):
  qs=[init(b)for b in[old,new]]
  for q in qs:q.put(CrossoverBehaviorVersion=mode);sound(q,event)
  for tick in range(100):
   for q in qs:
    if life=='pause':q.put(GamePauseStatus=int(7<=tick<12))
    if tick==12:
     if life=='scene':q.invoke('Cv3NoiseSceneReset')
     elif life=='death':q.invoke('KillPlayer')
     elif life=='music':q.put(AreaMusicQueue=2)
   before={n:qs[1].get(n)for n in['Cv3FxOwned','Cv3FxNoiseID','Cv3FxPulseID','Cv3NoiseIndex','AvAudioRequest','Cv3FxPendingNoise','Cv3FxPendingPulse']}
   cs=[q.invoke('AudioUpdate')[0]for q in qs];delta=compare(qs,cs);rows.append(dict(event=event,mode=mode,life=life,tick=tick,delta=delta,before=before))
 rng=random.Random(0xd3c0);qs=[init(b)for b in[old,new]];mixed=[]
 for tick in range(1024):
  requests=[]
  if tick==0 or rng.randrange(4)==0:
   for _ in range(1+rng.randrange(3)):
    e=rng.choice(list(EVENTS));requests.append(e)
    for q in qs:sound(q,e)
  for q in qs:q.put(GamePauseStatus=int(tick%97 in[7,8]))
  before={n:qs[1].get(n)for n in['Cv3FxOwned','Cv3FxNoiseID','Cv3FxPulseID','Cv3NoiseIndex','AvAudioRequest','Cv3FxPendingNoise','Cv3FxPendingPulse']}
  cs=[q.invoke('AudioUpdate')[0]for q in qs];mixed.append(dict(tick=tick,requests=requests,delta=compare(qs,cs),before=before))
 cases=rows+mixed;(a.output/'cases.json').write_text(json.dumps(cases,separators=(',',':'))+'\n')
 result=dict(passed=all(r['delta']<=0 for r in cases),accepted=False,ROM_sha256=sha(a.rom),parent_ROM_sha256=sha(a.rom.parent/'baseline.nes'),whole_updates=len(rows),continued_mixed_updates=len(mixed),ordered_raw_APU_and_all_nonstack_RAM_registers_flags_mapper_exact=True,pointer_exclusions=0,cycle_delta_min=min(r['delta']for r in cases),cycle_delta_max=max(r['delta']for r in cases),regressions=[r for r in cases if r['delta']>0],tool_sha256=sha(__file__),scope='Actual assembled wholeAudioUpdate; all private pointers retain exact same physical A82 frame PC. No native cadence or hardware bus certification.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='regressions'},indent=2));assert result['passed'],result['regressions'][:10]
if __name__=='__main__':main()
