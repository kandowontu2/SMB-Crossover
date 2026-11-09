"""Hold the last-supported Thomas takeoff until the game reads and uses Up."""

import argparse
import json
from pathlib import Path

from prepare_selected_native_packet_v1 import R, prepare, sha


BASE=R/'build/helper-camera-thomas-gap-v4-1110'
PIN='5444f3e3bcb07c8314ba6f17b067f2e678eb4ec668786456e4f26d56ba8d75a2'


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new)


def transform(text):
    text=once(text,'local gapProbe={rows={}}','local gapProbe,gapUpPending={rows={}},false')
    old="""  local grounded=r('Player_State')==0
  if gapProbe.trigger and x>=1360 and x<1450 then
   if not grounded and not gapProbe.airborne then
    gapProbe.airborne={frame=frame,Main=updates,x=x,y=py}
   elseif grounded and x>=1412 and gapProbe.airborne and not gapProbe.landing then
    gapProbe.landing={frame=frame,Main=updates,x=x,y=py}
   end
  end"""
    new="""  local state=r('Player_State')
  local grounded=state==0
  if gapProbe.trigger and x>=1360 and x<1450 then
   local input=r('SavedJoypadBits')
   if input&8~=0 and not gapProbe.readback then
    gapProbe.readback={frame=frame,Main=updates,x=x,y=py,state=state,input=input}
   end
   if state==1 and peek(0x8e)&128~=0 and not gapProbe.airborne then
    gapProbe.airborne={frame=frame,Main=updates,x=x,y=py,input=input}
    gapUpPending=false
   elseif grounded and x>=1412 and gapProbe.airborne and not gapProbe.landing then
    gapProbe.landing={frame=frame,Main=updates,x=x,y=py}
   elseif gapUpPending and (state==2 or x>=1378 or updates-gapProbe.trigger.Main>6)then
    gapProbe.expired={frame=frame,Main=updates,x=x,y=py,state=state,input=input}
    gapUpPending=false
   end
  end"""
    text=once(text,old,new)
    text=once(text,
              '    pad.up=x>=1371 and leftSupport and not support',
              '    pad.up=not gapProbe.trigger and x>=1371 and leftSupport and not support')
    old="""   if gap and pad.up and not gapProbe.trigger then
    gapProbe.trigger={frame=frame,Main=updates,x=x,y=py,left_tile=leftTile,right_tile=supportTile}
   end
  end
  if x>=1364"""
    new="""   if gap and pad.up and not gapProbe.trigger then
    gapProbe.trigger={frame=frame,Main=updates,x=x,y=py,left_tile=leftTile,right_tile=supportTile}
    gapUpPending=true
   end
  end
  -- A logical Main can finish between two genuine controller polls. Keep
  -- the supported takeoff request live until Up is consumed and we rise.
  if gapUpPending and not pad.down then pad.up=true end
  if x>=1364"""
    text=once(text,old,new)
    return once(text,
                '    next_up=not not pad.up,left_floor=left,right_floor=right}',
                '    next_up=not not pad.up,pending_up=gapUpPending,left_floor=left,right_floor=right}')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    old_ready=BASE/'ready.json'
    controller=BASE/'controller.lua'
    failed=BASE/'capture/result.json'
    binding=BASE/'capture/binding.json'
    old=json.loads(old_ready.read_text())
    outcome=json.loads(failed.read_text())
    captured=json.loads(binding.read_text())
    rom=Path(old['ROM'])
    assert sha(rom)==old['ROM_sha256']==outcome['ROM_sha256']==captured['ROM_sha256']==PIN
    assert captured['exit_code']==1 and sha(old_ready)==captured['ready_sha256']
    assert not outcome['passed'] and outcome['maximum_X']==1396
    gap=outcome['first_floor_gap']
    trigger=gap['trigger']
    assert (trigger['Main'],trigger['x'],trigger['left_tile'],trigger['right_tile'])==(3047,1372,84,0)
    rows={row['Main']:row for row in gap['rows']}
    assert rows[3047]['next_up'] and not rows[3048]['next_up']
    assert rows[3048]['state']==0 and rows[3049]['state']==2
    assert all(row['input']&8==0 for row in gap['rows'])
    for path,digest in old['bindings'].items():
        assert sha(Path(path))==digest,path
    scope=('Cold controller-only Thomas full 1-1 into active 1-2, preserving all six offscreen '
           'constructors, native contacts, assisted crossings, and interrupt assertions. The '
           'X1371–1372 takeoff request remains latched across missed polls until a genuine '
           'rising jump or a bounded expired attempt. Same capture set.')
    prepare(args.output,rom,transform(controller.read_text()),
            [Path(__file__),old_ready,controller,failed,binding],expected=PIN,timeout=240,
            scope=scope,allow_interactive=True)
    ready=args.output/'ready.json'
    data=json.loads(ready.read_text())
    data['timeout']=old['timeout']
    ready.write_text(json.dumps(data,indent=2)+'\n')


if __name__=='__main__':
    main()
