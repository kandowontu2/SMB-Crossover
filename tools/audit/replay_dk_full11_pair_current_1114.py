"""Exactf11 scoped64px pair reaction; proven opening policy preserved."""
from functools import lru_cache
from hashlib import sha256

import replay_dk_full11_danger_current_1114 as Global

Input,Previous=Global.Input,Global.Previous
R,ROM,W,N,PIN=Global.R,Global.ROM,Global.W,Global.N,Global.PIN
Frozen,IDENTITIES,normalize,bindings=Global.Frozen,Global.IDENTITIES,Global.normalize,Global.bindings


@lru_cache(maxsize=1)
def controller(raw,key='donkey_kong'):
    parent=Input.parent(raw);text=Previous.controller(parent,key)
    assert sha256(text.encode()).hexdigest()==Global.OLD_LUA_SHA
    assert sha256(Previous.POLICY.read_bytes()).hexdigest()==Global.OLD_POLICY_SHA
    prefix='local C='+Frozen.lua(Previous.bindings(parent,key))+'\n'
    assert text.startswith(prefix)
    text='local C='+Frozen.lua(bindings(raw,key))+'\n'+text[len(prefix):]
    marker=' -- Use the existing ordinary horizontal barrel against a nearby Goomba.'
    extra=""" -- Preserve the successful prefix; react earlier at the measured pair.
 if c.x>=1440 and c.grounded and not c.lastA then
  local danger=false
  for i=0,5 do
   local flag,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
   local dx=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)-c.x
   if flag>0 and flag<128 and st<32 and(id<0x15 or id==0x2d or id==0x33)
    and not(id==6 and st>=2)and c.r('Enemy_Y_HighPos',i)==1
    and dx>0 and dx<=64 and math.abs(c.r('Enemy_Y_Position',i)-c.y)<48 then danger=true end
  end
  if danger then jumpAge=0;return{right=true,b=c.x<3104,a=true}end
 end
"""
    text=Previous.once(text,marker,extra+marker)
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='donkey_kong'):
    q=Global.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        reaction='retain complete baseline prefix below1440; all-live-forward64px ordinary ground jump at measured pair/later',
        frozen_global_negative_controller_SHA256='f22845fc6ab354bb171f79b2c646dc6c7d7ba2e3fc8cd586738ad29563871906')
    return q
