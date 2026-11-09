"""Repeat the exact camera ROM with Karnov's crouch attack on the fatal approach."""

import argparse
import json
from pathlib import Path

from prepare_selected_native_packet_v1 import R, prepare, sha


BASE=R/'build/helper-camera-native-1110/karnov'
PIN='5444f3e3bcb07c8314ba6f17b067f2e678eb4ec668786456e4f26d56ba8d75a2'


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new)


def transform(text):
    text=once(text,'local passedLift=false',
              'local passedLift=false\nlocal corridorGuard,corridorFire,firstFightX,firstFightDx=0,0,-1,-1')
    old="""   if wx>=1140 and flag>0 and flag<128 and id<21 and state&32==0 and ex>wx and ex-wx<100 then
    pad.right=false;pad.a=false;pad.down=true;pad.b=gameFrames%12<6;jumpAge=0;release=8;break
   end"""
    new="""   local dx=ex-wx
   -- Stay grounded and clear the landing corridor before advancing to lift2.
   -- The earlier camera spawn changes when the first pipe crossing releases us.
   local corridor=wx>=776 and wx<872 and dx<160 and math.abs(ey-r('Player_Y_Position'))<=32
   local target=flag>0 and flag<128 and id<21 and state&32==0 and dx>0
   if target and (corridor or (wx>=1140 and dx<100)) then
    pad.right=false;pad.a=false;pad.down=true;pad.b=gameFrames%12<6;jumpAge=0;release=8
    if corridor then
     if corridorGuard==0 then firstFightX=wx;firstFightDx=dx end
     corridorGuard=corridorGuard+1
     if pad.b then corridorFire=corridorFire+1 end
    end
    break
   end"""
    text=once(text,old,new)
    old="""'{"passed":%s,"stage_complete":%s,"died":%s,"max_world_x":%d,"game_frames":%d,"controller_only":true}\\n',tostring(won),tostring(won),tostring(dead),maxX,gameFrames"""
    new="""'{"passed":%s,"stage_complete":%s,"died":%s,"max_world_x":%d,"game_frames":%d,"controller_only":true,"corridor_guard_polls":%d,"corridor_fire_held_polls":%d,"corridor_first_x":%d,"corridor_first_dx":%d}\\n',tostring(won),tostring(won),tostring(dead),maxX,gameFrames,corridorGuard,corridorFire,firstFightX,firstFightDx"""
    return once(text,old,new)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    old_ready=BASE/'ready.json'
    controller=BASE/'controller.lua'
    failure=BASE/'capture/result.json'
    observation=BASE/'capture/helper-camera.json'
    ready=json.loads(old_ready.read_text())
    old=json.loads(failure.read_text())
    receipts=json.loads(observation.read_text())
    rom=Path(ready['ROM'])
    assert sha(rom)==ready['ROM_sha256']==receipts['ROM_sha256']==PIN
    assert old['died'] and old['max_world_x']==853 and old['game_frames']==2295
    assert [q['relative_left'] for q in receipts['placements']]==[287,287]
    assert [q['crossed'] for q in receipts['placements']]==[True,False]
    for path,digest in ready['bindings'].items():
        assert sha(Path(path))==digest,path
    scope=('Cold controller-only Karnov full 1-1 into active 1-2. Retain both offscreen native '
           'constructors and verify actual boarding and crossings. Reuse crouch combat on the '
           'specific landing corridor where the previous unarmed approach died. Same capture set.')
    prepare(args.output,rom,transform(controller.read_text()),
            [Path(__file__),old_ready,controller,failure,observation],expected=PIN,timeout=240,
            scope=scope,allow_interactive=True)
    out_ready=args.output/'ready.json'
    data=json.loads(out_ready.read_text())
    data['timeout']=ready['timeout']
    out_ready.write_text(json.dumps(data,indent=2)+'\n')


if __name__=='__main__':
    main()
