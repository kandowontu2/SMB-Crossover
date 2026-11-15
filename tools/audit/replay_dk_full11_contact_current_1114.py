"""Classic DK ordinary-barrel reaction successor; frozen1dbd preserved."""
from functools import lru_cache
from hashlib import sha256

import replay_dk_full11_current_1114 as Previous

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN
Frozen,IDENTITIES,normalize=Previous.Frozen,Previous.IDENTITIES,Previous.normalize
bindings=Previous.bindings
POLICY=R/'tools/playthroughs/dk_full11_contact_controls_1114.lua'
OLD_POLICY_SHA='4637f7d0946c03cb46609873e159d3c449696d3c85da31eddd0dc1937cc96c5a'
OLD_LUA_SHA='1dbddab40b17764b04841e72a170bf3fd0b89ef872b38e3081126b30c764dd8c'


@lru_cache(maxsize=1)
def controller(raw,key='donkey_kong'):
    text=Previous.controller(raw,key);old=Previous.POLICY.read_text()
    assert sha256(text.encode()).hexdigest()==OLD_LUA_SHA
    assert sha256(Previous.POLICY.read_bytes()).hexdigest()==OLD_POLICY_SHA
    replacement='local base=(function()\n'+old+'\nend)()\n'+POLICY.read_text()
    text=Previous.once(text,old,replacement)
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='donkey_kong'):
    q=Previous.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        baseline_controller_SHA256=OLD_LUA_SHA,contact_policy_SHA256=sha256(POLICY.read_bytes()).hexdigest(),
        measured_contact='DK right29 versus Goomba left3; first fatal gap26 while rising, before feet cleared head',
        reaction='countersteer, retreat to112px front gap, actual right-facing, fresh ordinary B while grounded')
    return q
