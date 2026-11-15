"""Exactf11 DK real far-pit landing and early coin-row jump, ordinary input."""
from functools import lru_cache
from hashlib import sha256

import replay_dk_full11_danger_current_1114 as Binding

Input,Previous=Binding.Input,Binding.Previous
R,ROM,W,N,PIN=Binding.R,Binding.ROM,Binding.W,Binding.N,Binding.PIN
Frozen,IDENTITIES,normalize,bindings=Binding.Frozen,Binding.IDENTITIES,Binding.normalize,Binding.bindings


@lru_cache(maxsize=1)
def controller(raw,key='donkey_kong'):
    parent=Input.parent(raw);text=Previous.controller(parent,key)
    assert sha256(text.encode()).hexdigest()==Binding.OLD_LUA_SHA
    assert sha256(Previous.POLICY.read_bytes()).hexdigest()==Binding.OLD_POLICY_SHA
    prefix='local C='+Frozen.lua(Previous.bindings(parent,key))+'\n'
    assert text.startswith(prefix)
    text='local C='+Frozen.lua(bindings(raw,key))+'\n'+text[len(prefix):]
    text=Previous.once(text,'local lastX,still=0,0','local lastX,still=0,0\nlocal pairPhase,pairAge="approach",0')
    marker=' if c.world~=0 or c.level~=0 then return{}end'
    extra="""
 local function floorCell(x)
  local tile=c.block(x,208)
  return tile~=0 and tile~=0x23 and tile~=0x26 and tile~=0xc2 and tile~=0xc3
 end
 -- The far floor begins1424. Lead foot has reached it by native1408.
 -- Release A and countersteer while falling, retaining ordinary integration.
 if pairPhase=='approach'and c.x>=1408 and c.x<1472 and floorCell(1424)then pairPhase='land'end
 if pairPhase=='land'then
  if not c.grounded then return{left=c.vx>0 and c.vx<128,right=c.vx>=128}end
  if c.x<1437 then return{right=true}end
  if c.x>1458 then return{left=true}end
  if c.lastA then return{}end
  assert(c.x-13>=1424 and floorCell(c.x-13)and floorCell(c.x+29),'Actual whole DK body on far floor before fresh jump')
  pairPhase='rise';pairAge=0;jumpAge=0
  return{right=true,b=true,a=true}
 elseif pairPhase=='rise'then
  pairAge=pairAge+1
  assert(pairAge<100,'Bounded ordinary early coin-row jump')
  local brick=c.block(1504,144)
  if brick~=0 and brick~=0x23 and c.x+29>=1504 and c.x-13<=1519 then
   assert(c.y<=144 or c.y>=160,'True right-head clearance before entering coin brick')
  end
  if c.grounded and pairAge>1 then
   assert(c.y<=112,'Actual landing above the low ceiling before crossing live Goombas')
   pairPhase='done'
  else return{right=true,b=true,a=pairAge<40}end
 end
"""
    text=Previous.once(text,marker,marker+extra)
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='donkey_kong'):
    q=Binding.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        reaction='after lead foot passes second-pit far floor1424, release A/countersteer, actual grounded launch1437..1458, preserve coin-brick head guard',
        true_floor_and_head_clearance_required=True,helper_changes=0)
    return q
