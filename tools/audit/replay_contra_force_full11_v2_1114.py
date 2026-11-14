"""CF route observer successor: authentic C2 cookie and zero C3 tail."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import replay_contra_force_full11_1114 as Previous

PIN,ROM,R,W,N=Previous.PIN,Previous.ROM,Previous.R,Previous.W,Previous.N
IDENTITIES=Previous.IDENTITIES
Frozen,POLICY=Previous.Frozen,Previous.POLICY
normalize=Previous.normalize
bindings=Previous.bindings
PREVIOUS_SOURCE='1505edae84d0264be23a8ba48fbce7c8ee992931eb73dee5e515b68847e64c13'
LUA_SHA={'burns':'93028d0999787c6eebf6ca46b19898a6b2452d45e8c8957af4ec3d52b0c7b1e0',
    'smith':'e108ceacb8ddca9d86c52abda547576348b60109853497c178265a290d042c1c',
    'iron':'9d8e2d714bf5deec13f36b24530ac40305c773fea345167c90019b03486a5edc',
    'beans':'74f91e095f47813de185f003a6e12e40e3cfa9b51df533b63c248ccada073270'}


@lru_cache(maxsize=4)
def controller(raw,key):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PREVIOUS_SOURCE
    text=Previous.controller(raw,key)
    assert sha256(text.encode()).hexdigest()==Previous.LUA_SHA[key]
    old="  for bank=2,3 do for i,v in ipairs(C.cf.cookie)do assert(emu.read(bank*8192+0x1fe0+i-1,emu.memType.nesWorkRam)==v,'Actual complete CF cookie')end end"
    new="  for i,v in ipairs(C.cf.cookie)do assert(emu.read(2*8192+0x1fe0+i-1,emu.memType.nesWorkRam)==v,'Actual complete CF C2 cookie')end\n  for i=0,31 do assert(emu.read(3*8192+0x1fe0+i,emu.memType.nesWorkRam)==0,'Actual source-declared zero C3 cookie tail')end"
    assert text.count(old)==1
    text=text.replace(old,new,1)
    Previous.Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    assert sha256(text.encode()).hexdigest()==LUA_SHA[key]
    return text


def metadata(raw,key):
    q=Previous.metadata(raw,key)
    b=dict(W.Symbols.bundle(),raw=raw)
    loader=W.location(b,'CfLoaderExpectedCookie');outer=W.location(b,'CfExternalCookie')
    assert raw[loader:loader+16]==raw[outer:outer+16]
    del q['complete_C2_C3_cookies_and_real_movement_export_assertions_in_controller']
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        previous_unqualified_observer_Lua_SHA256=Previous.LUA_SHA[key],
        complete_C2_cookie_and_source_declared_zero_C3_tail_assertions=True,
        previous_gameplay_controls_identical=True,source_movement_export_signatures_exact=True)
    return q
