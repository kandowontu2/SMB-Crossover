"""Exactf11 DK early roof route; release ordinary A during native descent."""
from functools import lru_cache
from hashlib import sha256

import replay_dk_full11_landing_current_1114 as Previous

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN
Frozen,IDENTITIES,normalize,bindings=Previous.Frozen,Previous.IDENTITIES,Previous.normalize,Previous.bindings
OLD_LUA_SHA='bda650a11629d48f49c27171690ff213d6274eaf66618a3b04b4a8564328ca17'


@lru_cache(maxsize=1)
def controller(raw,key='donkey_kong'):
    text=Previous.controller(raw,key);assert sha256(text.encode()).hexdigest()==OLD_LUA_SHA
    text=Previous.Previous.once(text,'b.a=jumpAge<40','b.a=jumpAge<40 and(c.x<1408 or c.vy>=128)')
    text=Previous.Previous.once(text,'a=pairAge<40}','a=pairAge<40 and c.vy>=128}')
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='donkey_kong'):
    q=Previous.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        previous_landing_controller_SHA256=OLD_LUA_SHA,
        A_release='after1408 keep A while actual native VY is negative; release during descent to permit fresh ground jump',
        native_vertical_contract='MovePlayerVertically sign/carry integration: integerVY0 has no upward displacement; no private JR fractional projection involved')
    return q
