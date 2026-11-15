"""Exactf11 DK uses the observed real roof edge before the next ordinary jump."""
from functools import lru_cache
from hashlib import sha256

import replay_dk_full11_roof_current_1114 as Previous

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN
Frozen,IDENTITIES,normalize,bindings=Previous.Frozen,Previous.IDENTITIES,Previous.normalize,Previous.bindings
OLD_LUA_SHA='1c76fe83bdc1815218af27d2d39dd5c2258941e5f89eeeb5b24fd5c2a29c8606'


@lru_cache(maxsize=1)
def controller(raw,key='donkey_kong'):
    text=Previous.controller(raw,key);assert sha256(text.encode()).hexdigest()==OLD_LUA_SHA
    once=Previous.Previous.Previous.Base.once
    text=once(text,'local dkRoofRequests=0','local dkRoofRequests=0\nlocal dkRoofBridgeDone=false')
    old="""  if dkLaunchInfo.landing and c.x<1728 and c.yHigh==1 and c.grounded and c.y<=112 and not c.lastA then
   wanted={right=true,b=true,a=true};dkRoofRequests=dkRoofRequests+1
  end"""
    new="""  if dkLaunchInfo.landing and not dkRoofBridgeDone then
   assert(c.yHigh==1 and c.y<=112 and c.grounded,'Retain actual first roof support until its qualified edge')
   if c.x<1527 then
    wanted={right=true,b=false,a=false}
   else
    assert(c.x<=1532 and not c.lastA,'Actual supported roof edge and fresh A before upper-brick clearance jump')
    dkRoofBridgeDone=true;wanted={right=true,b=true,a=true};dkRoofRequests=dkRoofRequests+1
   end
  elseif dkRoofBridgeDone and c.x<1728 and c.yHigh==1 and c.grounded and c.y<=112 and not c.lastA then
   wanted={right=true,b=true,a=true};dkRoofRequests=dkRoofRequests+1
  end"""
    text=once(text,old,new)
    text=once(text,'supported_roof_A_decisions=dkRoofRequests,',
        'qualified_roof_edge_requested=dkRoofBridgeDone,supported_roof_A_decisions=dkRoofRequests,')
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='donkey_kong'):
    q=Previous.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        previous_immediate_roof_controller_SHA256=OLD_LUA_SHA,
        supported_roof_route='after guarded landing retain realY112 ground to observed1527..1532 support, then fresh native-admitted ordinary jump; continue high corridor',
        source_supported_launch_witness=1527,all_floor_head_and_admission_guards_retained=True)
    return q
