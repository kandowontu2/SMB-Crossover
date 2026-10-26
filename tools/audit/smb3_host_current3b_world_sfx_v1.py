"""Actual common mixer capture/finish with SMB3 source active, compared to current3b."""
from pathlib import Path
import argparse,json,traceback
from smb3_host_current3b_cpu_v1 import D,Fixture,sha,put
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from check_tmnt_render_oa import address

def snapshot(q,b):
 out={}
 for name,n in [('GuestWorldQueues',3),('GuestFxApu',16),('GuestFxDirty',16),('Square1SoundBuffer',1),('Square2SoundBuffer',1),('NoiseSoundBuffer',1),('GuestMixMask',1),('GuestMixPreviousMask',1)]:
  at=address(b,name);out[name]=list(q.m[at:at+n])
 return out
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old=scoped_load(D/'root-current-roster-composition-v1/candidate.nes');new=scoped_load(a.packet/'candidate.nes');rows=[]
 try:
  cues=[tuple((1<<bit)if c==channel else 0 for c in range(3))for channel in range(3)for bit in range(8)]+[(1,1,1),(128,128,128),(255,255,255),(0,0,0)]
  for mode in [0,1]:
   for cue in cues:
    ref=Arena(old,17);ref.put(CrossoverBehaviorVersion=mode,OperMode=1,AreaMusicQueue=1,GuestAudioCharacter=255,XgAudioCharacter=255)
    f=Fixture(new,mode,0);ref.invoke('AudioUpdate');f.invoke(('AreaMusicQueue',1))
    for key,value in zip(['Square1SoundQueue','Square2SoundQueue','NoiseSoundQueue'],cue):ref.set(key,value);f.q.set(key,value)
    for tick in range(5):
     ref.invoke('AudioUpdate');f.invoke();assert snapshot(ref,old)==snapshot(f.q,new),('Shared SFX state/capture changed',mode,cue,tick)
     if tick==0:assert snapshot(f.q,new)['GuestWorldQueues']==list(cue)
    rows.append(dict(mode=mode,cue=cue,ticks=5))
  put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,parent_ROM_sha256=sha(D/'root-current-roster-composition-v1/candidate.nes'),candidate_ROM_sha256=sha(a.packet/'candidate.nes'),profiles=len(rows),whole_AudioUpdate_ticks=len(rows)*6,original_source_RAM_AXYP_SP_ordered_logical_APU_and_sample_checks=True,shared_SFX_capture_image_dirty_buffer_and_mix_ownership_exact=True,world_cue_combinations=cues,checker_sha256=sha(__file__),limits='Arranged whole-AudioUpdate sourceCPU states. Logical source stores and actual common mixer RAM ownership are checked separately; this is not source waveform, original ordered physical4000..0F hardware equivalence, native controller cue timing, DMA or visible deadline qualification.'))
  print(json.dumps(dict(passed=True,profiles=len(rows),ticks=len(rows)*6)))
 except Exception as e:put(a.output/'failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc(),profiles_done=len(rows)));raise
if __name__=='__main__':main()
