"""Exactf11 DK all later ground requests latch until actual native admission."""
from functools import lru_cache
from hashlib import sha256

import replay_dk_full11_latched_current_1114 as Previous

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN
Frozen,IDENTITIES,normalize,bindings=Previous.Frozen,Previous.IDENTITIES,Previous.normalize,Previous.bindings
OLD_LUA_SHA='947e402f6efcff2a4abbdd0c9e77e4365bd26aeee5a6a136b3c66fc661ee4280'


@lru_cache(maxsize=1)
def controller(raw,key='donkey_kong'):
    text=Previous.controller(raw,key);assert sha256(text.encode()).hexdigest()==OLD_LUA_SHA
    text=Previous.Base.once(text,'local dkInput,dkDecide={},nil',
        'local dkInput,dkDecide={},nil\nlocal dkDelivery={active=false,admitted=false,age=0,requests=0,accepts=0}')
    old=""" if menuDone and active()and identity()and r('LevelNumber')==0 then dkInput=controls(context())else dkInput={}end"""
    new=""" if menuDone and active()and identity()and r('LevelNumber')==0 then
  local c=context();local wanted=controls(c)
  local function copyPad(p)local q={};for k,v in pairs(p)do q[k]=v end;return q end
  if c.x>=1408 then
   if dkDelivery.active then
    dkDelivery.age=dkDelivery.age+1
    if not dkDelivery.admitted then
     assert(dkDelivery.age<32,'Bounded native admission of every requested ground jump')
     if c.state==1 and c.vy>=128 then
      assert((r('SavedJoypadBits')&128)~=0 and(r('A_B_Buttons')&128)~=0
       and(r('PreviousA_B_Buttons')&128)~=0 and(r('DkPrevious')&128)~=0,'Actual native A admission for later jump')
      assert(c.y+256*c.yHigh<dkDelivery.requestY,'Actual upward world displacement for later jump')
      dkDelivery.admitted=true;dkDelivery.accepts=dkDelivery.accepts+1
     end
     wanted=copyPad(dkDelivery.pad);wanted.a=true
    elseif c.grounded then
     dkDelivery.active=false;dkDelivery.admitted=false
    else
     assert(dkDelivery.age<160,'Bounded actual native jump/landing lifecycle')
     wanted.a=c.vy>=128
    end
   end
   if not dkDelivery.active and c.grounded and wanted.a and not c.lastA then
    dkDelivery.active=true;dkDelivery.admitted=false;dkDelivery.age=0
    dkDelivery.requests=dkDelivery.requests+1;dkDelivery.requestY=c.y+256*c.yHigh
    dkDelivery.pad=copyPad(wanted)
   end
  end
  dkInput=wanted
 else dkInput={};dkDelivery.active=false;dkDelivery.admitted=false end"""
    text=Previous.Base.once(text,old,new)
    text=Previous.Base.once(text,'jump_launch=dkLaunchInfo,',
        'all_jump_delivery=dkDelivery,jump_launch=dkLaunchInfo,')
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='donkey_kong'):
    q=Previous.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        previous_first_admission_controller_SHA256=OLD_LUA_SHA,
        later_jump_contract='after1408 latch requested ordinary pad until actual native admission, hold A during actual ascent, release during descent',
        original_opening_inputs_and_all_floor_head_roof_guards_retained=True)
    return q
