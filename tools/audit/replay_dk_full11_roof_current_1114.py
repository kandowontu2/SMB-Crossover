"""Exactf11 DK continues ordinary jumps on the qualified low-ceiling roof."""
from functools import lru_cache
from hashlib import sha256

import replay_dk_full11_all_latched_current_1114 as Previous

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN
Frozen,IDENTITIES,normalize,bindings=Previous.Frozen,Previous.IDENTITIES,Previous.normalize,Previous.bindings
OLD_LUA_SHA='bb51b57f672063f76b30f36cb5e0af46dd0d69879fe5f5d0a22011e192f2ba4d'


@lru_cache(maxsize=1)
def controller(raw,key='donkey_kong'):
    text=Previous.controller(raw,key);assert sha256(text.encode()).hexdigest()==OLD_LUA_SHA
    once=Previous.Previous.Base.once
    text=once(text,'local dkDelivery={active=false,admitted=false,age=0,requests=0,accepts=0}',
        'local dkDelivery={active=false,admitted=false,age=0,requests=0,accepts=0}\nlocal dkRoofRequests=0')
    marker='  local c=context();local wanted=controls(c)'
    text=once(text,marker,marker+"""
  -- Actual supported Y112 rows were observed through1739. Stay above the
  -- measured low-ceiling/Koopa corridor instead of dropping back under it.
  -- Koopa's measured right1698 is behind DK's left at world1728-13=1715.
  if dkLaunchInfo.landing and c.x<1728 and c.yHigh==1 and c.grounded and c.y<=112 and not c.lastA then
   wanted={right=true,b=true,a=true};dkRoofRequests=dkRoofRequests+1
  end""")
    text=once(text,'all_jump_delivery=dkDelivery,','supported_roof_A_decisions=dkRoofRequests,all_jump_delivery=dkDelivery,')
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='donkey_kong'):
    q=Previous.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        previous_all_admission_controller_SHA256=OLD_LUA_SHA,
        supported_roof_route='only after actual first guarded roof landing, fresh ordinary ground jumps atY<=112 until1728; native admission still required',
        source_roof_witnesses=[1487,1509,1527,1614,1701,1739],
        all_previous_true_geometry_guards_retained=True)
    return q
