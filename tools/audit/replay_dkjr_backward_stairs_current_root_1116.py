"""Ordinary original backward jumps with acknowledged left facing on stairs."""
from hashlib import sha256
from pathlib import Path

import inspect_dkjr_stair_queries_current_root_1116 as Previous

H=lambda value:sha256(value).hexdigest()
ABILITY=Previous.C.R/'tools/audit/plan_dkjr_backward_stair_input_1116.py'
ABILITY_SHA='2ede0a2fcd5bd2314c6e7dd3b40b8794e0acce5fa4e1eb355eade097c8c77cf4'


def controller(raw,*,source=False):
    assert H(ABILITY.read_bytes())==ABILITY_SHA
    text=Previous.controller(raw,source=source)
    old='    if player>q.x then bits=2;return end\n    q.stopped=updates'
    new="""    -- Original facing0 keeps jump right-edge24, matching ground24.
    -- A fresh Right+A latches rightward motion before GroundMove can turn.
    if player>q.x or ram(2,0x6d)~=0 then bits=2;return end
    assert(ram(2,0x71)~=2,'Authenticated normal backward-jump mode')
    q.stopped=updates
    if riserTrace then
     riserTrace.left_ack={Main=updates,x=player,y=y,facing=ram(2,0x6d),source=ram(2,0x6b)}
    end"""
    assert text.count(old)==1
    result=text.replace(old,new,1)
    assert result.replace(new,old,1)==text
    Previous.Controls.Previous.Frozen.Frozen.Frozen.Prior.Ground.LuaRuntime().compile(result)
    return result


if __name__=='__main__':
    from check_dkjr_backward_stairs_current_root_1116 import main
    main()
