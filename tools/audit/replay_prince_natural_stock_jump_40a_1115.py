"""Ordinary A jump with brake calibrated from the retained reach-only probe."""
from functools import lru_cache
import replay_prince_natural_stock_returns_40a_1115 as Previous

C,N,W,PIN=Previous.C,Previous.N,Previous.W,Previous.PIN

@lru_cache(maxsize=2)
def controller(raw,mode='oneup',jump=128):
    assert jump==128 and mode in('oneup','star')and C.digest(raw)==PIN
    text=Previous.controller(raw,mode,jump)
    old='  local target=STOCK.x-8'
    new=old+";if stock.attempts==0 then target=target-28 end -- measured normal running brake displacement"
    assert text.count(old)==1;text=text.replace(old,new,1)
    old="if age>=8 and floor(s)and idle(s)then stock.attempts=stock.attempts+1;"
    new="if age>=8 and floor(s)and idle(s)then assert(s.x>=STOCK.x-14 and s.x<=STOCK.x+8,'Measured brake at authored head span');stock.attempts=stock.attempts+1;"
    assert text.count(old)==1;text=text.replace(old,new,1)
    Previous.LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=128):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),mode=mode,jump_mask=128,
        required_native_variant=3,ordinary_A_jump_and_measured_brake=True,actual_016E_and_popup_credit_witnesses=True,
        no_gameplay_seeds=True,native_ready=False,outputs=0,Mesen=False)
