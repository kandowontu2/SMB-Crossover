"""Ordinary reflected-star braking successor on strict private7a80."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import replay_gimmick_empty_side_current_1115 as Previous

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN
Frozen,normalize=Previous.Frozen,Previous.normalize
IDENTITIES={'mr_gimmick':Previous.IDENTITIES['flower']}
PARENT_SOURCE='5c5a77a49f34af37bc2f90f51efa342ecbed6badf79590b639526c1967963e00'
PARENT_LUA='cce79facd3c60f504c06df43c32d18cae932b135334600d10e6fc5a9e5c7dfbc'


def bindings(raw,key='mr_gimmick'):
    assert key=='mr_gimmick';return Previous.bindings(raw,'flower')


@lru_cache(maxsize=1)
def controller(raw,key='mr_gimmick'):
    assert key=='mr_gimmick'and sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT_SOURCE
    old=Previous.controller(raw,'flower');assert sha256(old.encode()).hexdigest()==PARENT_LUA
    before='  return{left=true,a=vy>=128}\n elseif phase==\'flower-jump\'then'
    after="""  -- Brake existing left momentum once the real star wall reflection occurs.
  -- No inferred support: the unchanged exact RideStar/poll/consumption gate
  -- still admits the next jump only from a current real flagged ride.
  if flower.wall_reflection and not flower.reflected_braking then
   flower.reflected_braking=gmTravel.snapshot();mark(c,'actual-reflection-right-brake')
  end
  return{left=not flower.wall_reflection,right=not not flower.wall_reflection,a=vy>=128}
 elseif phase=='flower-jump'then"""
    assert old.count(before)==1;result=old.replace(before,after,1)
    Frozen.LuaRuntime().compile(result)
    assert not any(s in result for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return result


def metadata(raw,key='mr_gimmick'):
    q=Previous.metadata(raw,'flower');q.update(identity=key,controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        parent_factory_SHA256=PARENT_SOURCE,parent_Lua_SHA256=PARENT_LUA,unchanged_control_and_observer_body=False,
        diagnostic_hooks={name:bindings(raw,key)['hooks'][name]for name in('TravelPadRead','TravelFreshRead','TravelJumpAccepted','GmRideStar','GmRideStarReturn')},
        ordinary_navigation_change='After actual star reflection, hold Right to brake existing left momentum before the unchanged current-real-support jump gate',
        scope='New ordinary reflected-star braking continuation on strict7a80; first M/reflection/currentRideStar/realFlower inventory-code2/cue/erase/score/25 movements required; pending source/native')
    return q
