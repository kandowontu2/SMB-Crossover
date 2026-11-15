"""Strict40a natural Star route with the actual target timer/caller witness."""
from functools import lru_cache
import replay_prince_star_facing_40a_1115 as Previous

C,N,W,PIN=Previous.C,Previous.N,Previous.W,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='star',jump=8):
    assert mode=='star'and jump==8 and C.digest(raw)==PIN
    text=Previous.controller(raw,mode,jump);b=dict(W.Symbols.bundle(),raw=raw)
    pc=W.address(b,'FloateyNumbersCore');at=W.location(b,'FloateyNumbersCore')
    old=dict(pc=pc,address=at-16,bytes=list(raw[at:at+8]),private=False)
    # Actual native path reaches this DEC with the original core caller stack.
    # Timer43 is sampled before DEC; the actual FarCall tail returns to that
    # caller only after the target popup's score/life effect has completed.
    delta=24;timer=W.address(b,'FloateyNum_Timer')
    assert pc+delta==0x897c and raw[at+delta:at+delta+5]==bytes((0xde,timer&255,timer>>8,0xc9,43))
    new=dict(pc=pc+delta,address=at+delta-16,bytes=list(raw[at+delta:at+delta+8]),private=False)
    encode=Previous.Previous.Previous.Base.lua
    before='stockHook('+encode(old)+',function(cpu)';after='stockHook('+encode(new)+',function(cpu)'
    assert text.count(before)==1;text=text.replace(before,after,1)
    Previous.Previous.Previous.LuaRuntime().compile(text)
    assert not any(token in text for token in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    return text

def metadata(raw,mode='star',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        immutable_E161_prefix=True,ordinary_controls_only=True,actual_target_timer_DEC_PC=0x897c,
        actual_timer43_caller_return_and_1000_points_required=True,birth_mature_physical_collector_erase_cue_and_25_returns_required=True,
        no_gameplay_seeds=True,native_ready=False,outputs=0,Mesen=False)
