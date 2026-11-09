"""Retest Thomas at the last supported takeoff window with bounded gap tracing."""

import argparse
import json
from pathlib import Path

from prepare_selected_native_packet_v1 import R, prepare, sha


BASE=R/'build/helper-camera-thomas-gap-1110'
PIN='5444f3e3bcb07c8314ba6f17b067f2e678eb4ec668786456e4f26d56ba8d75a2'


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new)


def transform(text):
    text=once(text,'local gapProbe={}','local gapProbe={rows={}}')
    text=once(text,
              '    pad.up=x>=1370 and leftSupport and not support',
              '''    -- V3 first rose at X1373. The successful floor route first rose at X1374.
    pad.up=x>=1371 and leftSupport and not support''')
    return once(text,
                '''  if updates%10==0 then csv:write''',
                '''  if x>=1364 and x<1432 and #gapProbe.rows<96 then
   local _,left=solid(x+3,208)
   local _,right=solid(x+12,208)
   gapProbe.rows[#gapProbe.rows+1]={frame=frame,Main=updates,x=x,y=py,
    state=r('Player_State'),vx=peek(0x46),vy=peek(0x8e),input=r('SavedJoypadBits'),
    next_up=not not pad.up,left_floor=left,right_floor=right}
  end
  if updates%10==0 then csv:write''')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    old_ready=BASE/'ready.json'
    controller=BASE/'controller.lua'
    failure=BASE/'capture/result.json'
    binding=BASE/'capture/binding.json'
    old=json.loads(old_ready.read_text())
    outcome=json.loads(failure.read_text())
    captured=json.loads(binding.read_text())
    rom=Path(old['ROM'])
    assert sha(rom)==old['ROM_sha256']==outcome['ROM_sha256']==captured['ROM_sha256']==PIN
    assert captured['exit_code']==1 and sha(old_ready)==captured['ready_sha256']
    assert not outcome['passed'] and outcome['maximum_X']==1418
    gap=outcome['first_floor_gap']
    assert (gap['trigger']['x'],gap['trigger']['left_tile'],gap['trigger']['right_tile'])==(1370,84,0)
    assert (gap['airborne']['x'],gap['airborne']['y'])==(1373,173) and 'landing' not in gap
    for path,digest in old['bindings'].items():
        assert sha(Path(path))==digest,path
    scope=('Cold controller-only Thomas full 1-1 into active 1-2, retaining all six offscreen '
           'constructors, native contacts, assisted crossings, and interrupt assertions. Retest '
           'the first floor gap using the last trailing-foot support at X1371–1372. At most '
           '96 extra rows inside the existing result, with the same capture set.')
    prepare(args.output,rom,transform(controller.read_text()),
            [Path(__file__),old_ready,controller,failure,binding],expected=PIN,timeout=240,
            scope=scope,allow_interactive=True)
    ready=args.output/'ready.json'
    data=json.loads(ready.read_text())
    data['timeout']=old['timeout']
    ready.write_text(json.dumps(data,indent=2)+'\n')


if __name__=='__main__':
    main()
