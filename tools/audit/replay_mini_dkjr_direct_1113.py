"""Strict read-only Mini769 controller adapter; root owns all native runs."""
from hashlib import sha256
import json

import compose_dkjr_direct_platform_1113 as T
import replay_mini_platform_regression_1113 as Base

PARENT_LUA='c0e8e04a37eb7921a29ff1d019b63093b702348468802ec2da056d8070590468'


def controller(raw):
    assert sha256(raw).hexdigest()==T.PIN
    parent=T.reverse(raw)
    assert sha256(parent).hexdigest()==T.PARENT
    start=16+128*8192+962*1024
    assert raw[start:start+5120]==parent[start:start+5120]
    text=Base.controller(parent,descending_candidate=True)
    assert sha256(text.encode()).hexdigest()==PARENT_LUA
    assert text.count(T.PARENT)==1
    text=text.replace(T.PARENT,T.PIN,1)
    Base.LuaRuntime().compile(text)
    return text


if __name__=='__main__':
    _,raw=T.load_inputs();text=controller(raw)
    print('MINI_DKJR_DIRECT_CONTROLLER '+json.dumps(dict(ROM_SHA256=T.PIN,
        inverse_parent_SHA256=T.PARENT,parent_Lua_SHA256=PARENT_LUA,
        Lua_SHA256=sha256(text.encode()).hexdigest(),Lua_bytes=len(text.encode()),
        Mini_carrier_equal=True,only_ROM_identity_rebound=True,Lua_compiled=True,
        emulator_launched=False,outputs_written=0),separators=(',',':')),flush=True)
