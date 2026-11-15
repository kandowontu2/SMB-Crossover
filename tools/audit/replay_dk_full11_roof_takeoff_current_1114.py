"""Exactf11 DK ordinary re-jump before the measured first roof support ends."""
from functools import lru_cache
from hashlib import sha256

import replay_dk_full11_roof_edge_current_1114 as Previous

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN
Frozen,IDENTITIES,normalize,bindings=Previous.Frozen,Previous.IDENTITIES,Previous.normalize,Previous.bindings
OLD_LUA_SHA='eae8b13647143d1a3fef1346e303af338c43e0952ce888ec9e9487227cc3af48'


@lru_cache(maxsize=1)
def controller(raw,key='donkey_kong'):
    text=Previous.controller(raw,key);assert sha256(text.encode()).hexdigest()==OLD_LUA_SHA
    once=Previous.Previous.Previous.Previous.Base.once
    text=once(text,'if c.x<1527 then','if c.x<1506 then')
    text=once(text,"assert(c.x<=1532 and not c.lastA,'Actual supported roof edge and fresh A before upper-brick clearance jump')",
        "assert(c.x<=1510 and not c.lastA,'Actual supported first roof and fresh A before support ends')")
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='donkey_kong'):
    q=Previous.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        previous_unsupported_edge_controller_SHA256=OLD_LUA_SHA,
        supported_roof_route='real A-released first roof run-up to1506..1510, fresh ordinary native-admitted jump before observed1512 support loss',
        source_supported_launch_witness=[1506,1510],
        upper_solid_cells_observed=[1456,1472,1488,1504],upper_row_y=80,
        head_clearance_is_observed_by_actual_collision_not_assumed=True)
    return q
