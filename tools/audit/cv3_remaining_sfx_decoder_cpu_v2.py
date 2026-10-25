"""WholeAudioUpdate held-versus-indexed-decoder exact RAM/APU/state differential."""
from pathlib import Path
import argparse,hashlib,itertools,json,random
from check_tmnt_render_oa import load,address
from cv3_remaining_sfx_complete_cpu_v1 import init,sound,EVENTS
from cv3_dmc_complete_cpu_v1 import apu,regs
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def compare(qs,cs):
 new=qs[1].b;allowed=set(range(0x100,0x200))|{address(new,n)+i for n in['Cv3FxNoisePtr','Cv3FxPulsePtr']for i in[0,1]}
 differences=[(hex(i),qs[0].m[i],qs[1].m[i])for i in range(0x8000)if i not in allowed and qs[0].m[i]!=qs[1].m[i]];assert not differences,differences[:12]
 assert apu(qs[0])==apu(qs[1])and qs[0].m.banks==qs[1].m.banks and regs(cs[0])==regs(cs[1])
 delta=address(new,'Cv3Fx1FNoise')-address(qs[0].b,'Cv3Fx1FNoise')
 for name in['Cv3FxNoisePtr','Cv3FxPulsePtr']:
  ptrs=[q.get(name)+256*q.get(name,1)for q in qs];assert ptrs==[0,0]or ptrs[1]-ptrs[0]==delta,(name,ptrs,delta)
  if ptrs[0]:
   bounds=sorted(address(qs[0].b,n)for n in['Cv3Fx1FNoise','Cv3Fx13Noise','Cv3Fx15Noise','Cv3Fx24Noise','Cv3Fx24Pulse','Cv3Fx21Noise','Cv3Fx21Pulse','Cv3Fx2FNoise','Cv3Fx2FPulse','Cv3FxNoiseLo']);end=next(v for v in bounds if v>ptrs[0]);length=min(16,end-ptrs[0]);samples=[]
   for q,ptr in zip(qs,ptrs):
    pos=16+82*8192+ptr-0xa000;samples.append(q.b['raw'][pos:pos+length])
   assert samples[0]==samples[1],(name,ptrs,samples)
 return cs[1].processorCycles-cs[0].processorCycles

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old=load(D/'cv3-remaining-current50b-v1/candidate.nes');new=load(a.rom);rows=[]
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
   cs=[q.invoke('AudioUpdate')[0]for q in qs];delta=compare(qs,cs);rows.append(dict(event=event,mode=mode,life=life,tick=tick,delta=delta))
 rng=random.Random(0xd3c0);qs=[init(b)for b in[old,new]];mixed=[]
 for tick in range(1024):
  requests=[]
  if tick==0 or rng.randrange(4)==0:
   for _ in range(1+rng.randrange(3)):
    e=rng.choice(list(EVENTS));requests.append(e)
    for q in qs:sound(q,e)
  for q in qs:q.put(GamePauseStatus=int(tick%97 in[7,8]))
  cs=[q.invoke('AudioUpdate')[0]for q in qs];mixed.append(dict(tick=tick,requests=requests,delta=compare(qs,cs)))
 result=dict(passed=True,accepted=False,ROM_sha256=sha(a.rom),held_ROM_sha256=sha(D/'cv3-remaining-current50b-v1/candidate.nes'),complete_event_mode_lifecycle_updates=len(rows),strict_continued_mixed_updates=len(mixed),ordered_raw_APU_writes_equal=True,whole_nonstack_RAM_registers_flags_mapper_equal=True,declared_private_pointer_normalization='Only four pointer bytes differ by exact common shift of the genuinely new source streams. Logical next up-to16 bytes inside the original stream are exact from actual physical82, regardless of restored A-window; no arbitrary private RAM exclusions.',cycle_delta_min=min(r['delta']for r in rows+mixed),cycle_delta_max=max(r['delta']for r in rows+mixed),scope='Actual assembled wholeAudioUpdate and genuine source lifecycle; existing music/source APUs exact. CPU excludes hardware DMA and native cadence; no adoption.')
 (a.output/'cases.json').write_text(json.dumps(rows+mixed,separators=(',',':'))+'\n');(a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
