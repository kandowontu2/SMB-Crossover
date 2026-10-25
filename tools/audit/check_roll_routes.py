"""Bind independent Roll1-1 replays, camera follow and update/draw counts."""
from pathlib import Path
import argparse,csv,hashlib,json


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);args=p.parse_args();root=args.root.resolve()
 sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
 rom=root/'roll-empty-v4.nes';result=dict(passed=True,ROM_sha256=sha(rom),modes={})
 for mode,folder in(('easy','replay-easy-v4-r2'),('hard','replay-hard-v4')):
  path=root/folder;m=json.loads((path/'manifest.json').read_text());assert m['exit']==0 and m['fixed_replay']and m['result']['cleared']and m['result']['deaths']==0 and m['ROM_sha256']==result['ROM_sha256']
  assert m['controller_only']and not m['memory_writes']and set(m['result']['stage_entries'])=={'0-0','0-1'}
  trace=list(csv.DictReader((path/'trace.csv').open()));live=[r for r in trace if r['world']=='0'and r['level']=='0'and r['engine']=='8'and r['mode']=='1'and r['task']=='3']
  steps=[];source_steps=[]
  for before,after in zip(live,live[1:]):
   if int(after['frame'])!=int(before['frame'])+1:continue
   delta=int(after['camera'])-int(before['camera']);steps.append(delta)
   assert 0<=delta<=3,('Camera goes backwards or jumps beyond native motion',mode,after)
   if delta==3:
    # Source Hard StepTick moves2 pixels on a new direction press. Pressing
    # jump in that update also admits Walk202's165/120 velocity. Its integer
    # result can be3. Keep that requested source behavior; camera must follow
    # the same player displacement, with neither drift nor an independent leap.
    assert mode=='hard'and before['state']=='0'and before['vx']=='0'
    assert int(before['buttons'])&1==0 and int(after['buttons'])&0x81==0x81
    assert int(after['x'])-int(before['x'])==3
    assert int(after['x'])-int(after['camera'])==int(before['x'])-int(before['camera'])
    source_steps.append(int(after['frame']))
  screen=[int(r['x'])-int(r['camera'])for r in live];assert max(screen)<=112
  profile=list(csv.DictReader((path/'roll-performance-frames.csv').open()));active=[r for r in profile if r['world']=='0'and r['level']=='0'and r['engine']=='8']
  assert(path/'inputs.csv').read_bytes()==(root/f'route-{mode}-v4/inputs.csv').read_bytes(),'Fixed replay matches saved controller input'
  result['modes'][mode]=dict(gameplay_video_frames=len(live),camera_step_min=min(steps),camera_step_max=max(steps),native_hard_step_plus_jump_frames=source_steps,maximum_player_screen_x=max(screen),native_movement_updates=sum(int(r['updates'])for r in active),native_sprite_draws=sum(int(r['draws'])for r in active),lag_nmis=sum(int(r['lagNmis'])for r in active),profile_video_frames=len(active),trace_sha256=sha(path/'trace.csv'),profile_sha256=sha(path/'roll-performance-frames.csv'),inputs_identical_to_discovery=True)
 result['scope']='Independent saved-input1-1 replays through playable1-2. Ordinary1-1 camera follow; native movement/update/draw counts. A source Hard direction-step plus jump can move3 pixels, followed equally by the camera. No zero-lag/full-scanline-visibility claim.'
 (root/'camera-route-proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
