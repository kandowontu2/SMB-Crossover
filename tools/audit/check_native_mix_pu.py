"""Compare the entire linked mixer, including actual world SFX advancement."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_audio_fallback_oc import execute,result
from check_tmnt_render_oa import load,address,location
def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.baseline),load(a.rom)
 mixbank=(location(old,'GuestAudioFinish')-16)//8192
 assert mixbank==(location(new,'GuestAudioFinish')-16)//8192 and 0xa000<=address(old,'GuestAudioFinish')<0xc000
 cases=0
 for previous,queues,dirty,scenario,flags in itertools.product(range(16),[(0,0,0),(1,0,0),(0,1,0),(0,0,1),(128,0,0),(0,32,0),(0,0,2),(1,32,2)],[0,1],range(4),[0x30,0x71]):
  seed=dict(SelectedCharacter=19,OperMode=0 if scenario==3 else 1,GamePauseStatus=1 if scenario==2 else 0,GuestMixPreviousMask=previous,GuestNativeEnable=15,GuestCombinedEnable=15,CurrentBank=mixbank|128)
  seed[0x5115]=mixbank|128
  for i in range(3):seed[address(old,'GuestWorldQueues')+i]=queues[i]
  for i in range(16):
   val=(i*17+19)&255
   seed[address(old,'GuestNativeApu')+i]=val;seed[address(old,'GuestApuLast')+i]=val if scenario==0 else 0
   seed[address(old,'GuestNativeDirty')+i]=dirty;seed[address(old,'GuestFxDirty')+i]=dirty
  x,m=execute(old,'GuestAudioFinish',seed,flags=flags);y,n=execute(new,'GuestAudioFinish',seed,flags=flags)
  assert result(x,m)==result(y,n),(previous,queues,dirty,scenario,flags,(x.a,x.x,x.y,x.p),(y.a,y.x,y.y,y.p),[(hex(i),m[i],n[i])for i in range(0x8000)if m[i]!=n[i]and not 0x1a0<=i<0x200][:20])
  cases+=1
 q=dict(passed=True,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),complete_mixer_cases=cases,
  scope='Actual GuestAudioFinish including shared SFX/expansion updates, all16previous-owner masks, eight valid effect queue patterns, dirty/unchanged images, pause/title and two flag states. Exact final registers/P/SP, all ordinary RAM and ordered hardware writes, including source timer retriggers. No waveform/performance/campaign claim.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q),flush=True)
if __name__=='__main__':main()
