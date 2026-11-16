"""Place the original jump's measured peak near real enemy body contact."""
from functools import lru_cache
import replay_prince_oneup_five1_67_1115 as Previous
from replay_prince_natural_stock_40a_1115 import LuaRuntime

C,PIN=Previous.C,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    text=Previous.controller(raw,mode,jump)
    assert C.digest(text.encode())=='142659ce8e86e27632e6b25bea582368069e21bbd9f5728e6728fcb92c786bb2'
    old='gap>=110 and gap<=142';assert text.count(old)==1
    text=text.replace(old,'gap>=70 and gap<=90',1)
    old="  pad=129;local j=stock.travel.jumps[#stock.travel.jumps];j.minimum_y=math.min(j.minimum_y,s.y)"
    new="  pad=s.lock~=0 and 129 or 1;local j=stock.travel.jumps[#stock.travel.jumps];j.minimum_y=math.min(j.minimum_y,s.y)"
    assert text.count(old)==1;text=text.replace(old,new,1)
    LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    q=Previous.metadata(raw,mode,jump);q.update(Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),
        previous_early_jump_Lua_SHA256='142659ce8e86e27632e6b25bea582368069e21bbd9f5728e6728fcb92c786bb2',
        actual_enemy_gap70_to90_after_measured_early_landing=True,release_A_after_original_jump_lock_clears=True)
    return q
