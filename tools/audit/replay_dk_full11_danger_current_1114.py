"""Exactf11 DK all-live-forward64px jump successor, no game changes."""
from functools import lru_cache
from hashlib import sha256

import current_dk_f11_input_1114 as Input
import replay_dk_full11_current_1114 as Previous

R,ROM,W,N,PIN=Input.R,Input.ROM,Input.W,Input.N,Input.PIN
Frozen,IDENTITIES=Previous.Frozen,Previous.IDENTITIES
normalize,bindings=Input.normalize,Input.bindings
OLD_LUA_SHA='1dbddab40b17764b04841e72a170bf3fd0b89ef872b38e3081126b30c764dd8c'
OLD_POLICY_SHA='4637f7d0946c03cb46609873e159d3c449696d3c85da31eddd0dc1937cc96c5a'


@lru_cache(maxsize=1)
def controller(raw,key='donkey_kong'):
    parent=Input.parent(raw);text=Previous.controller(parent,key)
    assert sha256(text.encode()).hexdigest()==OLD_LUA_SHA
    assert sha256(Previous.POLICY.read_bytes()).hexdigest()==OLD_POLICY_SHA
    prefix='local C='+Frozen.lua(Previous.bindings(parent,key))+'\n'
    assert text.startswith(prefix)
    text='local C='+Frozen.lua(bindings(raw,key))+'\n'+text[len(prefix):]
    old=""" -- Use the existing ordinary horizontal barrel against a nearby Goomba.
 if c.grounded and e and e.id==6 and e.dx>40 and e.dx<=108 and math.abs(e.y-c.y)<40 then
  jumpAge=-1
  return{b=c.poll%28<2}
 end"""
    new=""" -- All live forward actors contribute; a nearer defeated actor cannot mask one.
 local danger=false
 for i=0,5 do
  local flag,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
  local dx=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)-c.x
  if flag>0 and flag<128 and st<32 and(id<0x15 or id==0x2d or id==0x33)
   and not(id==6 and st>=2)and c.r('Enemy_Y_HighPos',i)==1
   and dx>0 and dx<=64 and math.abs(c.r('Enemy_Y_Position',i)-c.y)<48 then danger=true end
 end"""
    text=Previous.once(text,old,new)
    text=Previous.once(text,'local enemy=e and e.dx>0 and e.dx<72 and math.abs(e.y-c.y)<48','local enemy=danger')
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='donkey_kong'):
    q=Previous.metadata(Input.parent(raw),key)
    q.update(ROM_SHA256=PIN,controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        typed_input=Input.KIND,model_parent_SHA256=Previous.PIN,baseline_controller_SHA256=OLD_LUA_SHA,
        reaction='all live forward native actors within64px; remove neutral barrel wait; ordinary native A jump',
        measured_contact='DK right29/enemy left3, fatal gap26; relative approach about3px/update, foot clearance about8updates',
        previous_BT52_Gimmick192_classic3_common29_prior176_exact=True)
    return q
