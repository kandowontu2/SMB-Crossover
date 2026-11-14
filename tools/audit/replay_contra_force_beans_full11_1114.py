"""Separate Beans controller: confirm real stair landing before waiting."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import replay_contra_force_full11_v2_1114 as Previous

PIN,ROM,R,W,N=Previous.PIN,Previous.ROM,Previous.R,Previous.W,Previous.N
Frozen,POLICY=Previous.Frozen,Previous.POLICY
IDENTITIES={'beans':Previous.IDENTITIES['beans']}
normalize=Previous.normalize
PREVIOUS_SOURCE='8330845efee9e4a7eb800e457f3c3c55a28590159d274b6d7d49b699500a08c4'
LUA_SHA={'beans':'ef3bff39831d008c967b0da0dd946e869798df743b1c4849be4e281a96b29b21'}


def bindings(raw,key='beans'):
    assert key=='beans'
    return Previous.bindings(raw,key)


@lru_cache(maxsize=1)
def controller(raw,key='beans'):
    assert key=='beans'
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PREVIOUS_SOURCE
    text=Previous.controller(raw,key)
    old="if stairPhase=='climb'and c.y<=112 then"
    new="if stairPhase=='climb'and c.grounded and c.y<=112 then"
    assert text.count(old)==1
    text=text.replace(old,new,1)
    Previous.Frozen.LuaRuntime().compile(text)
    assert sha256(text.encode()).hexdigest()==LUA_SHA[key]
    return text


def metadata(raw,key='beans'):
    assert key=='beans'
    q=Previous.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        previous_v2_Lua_SHA256=Previous.LUA_SHA[key],
        sole_control_change='Require genuine ground before stair climb->land phase',
        source_physics_and_all_observers_unchanged=True)
    return q
