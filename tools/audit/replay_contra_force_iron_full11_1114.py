"""Explicit Iron far-stair landing successor; grounded-v3 stays frozen."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import replay_contra_force_grounded_full11_1114 as Previous

PIN,ROM,R,W,N=Previous.PIN,Previous.ROM,Previous.R,Previous.W,Previous.N
Frozen,POLICY=Previous.Frozen,Previous.POLICY
IDENTITIES={'iron':Previous.IDENTITIES['iron']}
normalize=Previous.normalize
PREVIOUS_SOURCE='0d55648f367bfec47f5b272eb4eeff3efcfe86787b112a92dae7a3422c7bcd14'
LUA_SHA={'iron':'41b214df5fd7a8ffd5b8f5fba048b3cb10280ecf5fb6136fddfa7ca67f225b82'}


def bindings(raw,key='iron'):
    assert key=='iron'
    return Previous.bindings(raw,key)


@lru_cache(maxsize=1)
def controller(raw,key='iron'):
    assert key=='iron'
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PREVIOUS_SOURCE
    text=Previous.controller(raw,key)
    old=" if s and c.x>=s.peak-20 and c.x<s.far and solid(s.peak+8,145)and not solid(s.edge+8,145)then\n"
    assert text.count(old)==1
    text=text.replace(old,old+"  if c.grounded and c.y<=112 and c.x>=s.far-15 then return held({right=true}),'stair-'..stair..'-far-landing'end\n",1)
    Frozen.LuaRuntime().compile(text)
    assert sha256(text.encode()).hexdigest()==LUA_SHA[key]
    return text


def metadata(raw,key='iron'):
    assert key=='iron'
    q=Previous.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        previous_grounded_v3_Lua_SHA256=Previous.LUA_SHA[key],
        sole_additional_control='Continue right after actual ground on far ledge; never steer back toward near peak',
        genuine_source_ground_snapshot_and_original_box_right15_required=True,
        physics_cookies_observers_success_conditions_and_other_three_controllers_unchanged=True)
    return q
