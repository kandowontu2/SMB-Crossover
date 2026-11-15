"""Exactf11 DK near/far terrain control; no physics/helper changes."""
from functools import lru_cache
from hashlib import sha256

import replay_dk_full11_release_current_1114 as Previous

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN
Frozen,IDENTITIES,normalize,bindings=Previous.Frozen,Previous.IDENTITIES,Previous.normalize,Previous.bindings
OLD_LUA_SHA='f02d262022b46fb11f30742b2e498218ddf702665b38a539dfff29ef82d004c6'


@lru_cache(maxsize=1)
def controller(raw,key='donkey_kong'):
    text=Previous.controller(raw,key);assert sha256(text.encode()).hexdigest()==OLD_LUA_SHA
    old='local obstacle=solid(c.x+48,c.y+8)or solid(c.x+48,c.y+24)'
    new=old+"""
  -- DK body ends at+29. Do not skip the real16px rise before a lower far cell.
  if c.x>=2100 then
   for offset=30,46,8 do obstacle=obstacle or solid(c.x+offset,c.y+8)or solid(c.x+offset,c.y+24)end
  end"""
    text=Previous.Previous.Previous.once(text,old,new)
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='donkey_kong'):
    q=Previous.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        previous_released_A_controller_SHA256=OLD_LUA_SHA,
        terrain_reaction='after2100 sample near/far30/38/46/48; actual cap2240/Y144 was missed by far2265/Y152',
        ordinary_jump_and_all_previous_guards_preserved=True)
    return q
