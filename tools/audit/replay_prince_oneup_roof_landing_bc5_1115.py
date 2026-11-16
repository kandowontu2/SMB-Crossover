"""Keep original fall/grab live until an actual landing17 admission."""
from functools import lru_cache
import replay_prince_oneup_roof_fall_grip_bc5_1115 as Previous
from replay_prince_natural_stock_40a_1115 import LuaRuntime

C,PIN=Previous.C,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    text=Previous.controller(raw,mode,jump)
    assert C.digest(text.encode())=='a651194bf577e547a269c5c13e47465c5ab46f6dc3a25a94bd499f0f6e35ff82'
    old='  elseif age>=45 and s.action~=3 and s.action~=4 then'
    new='  elseif age>=45 and s.action==17 and s.mode==5 then'
    assert text.count(old)==1;text=text.replace(old,new,1)
    LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    q=Previous.metadata(raw,mode,jump);q.update(Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),
        actual_landing17_mode5_required_before_releasing_flight=True,
        fall7_is_not_misclassified_as_landing=True)
    return q
