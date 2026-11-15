"""One genuine hidden1UP approach after the prefix's complete fourth cap."""
from functools import lru_cache
import replay_prince_hidden_running_40a_1115 as Previous

C,N,W,PIN=Previous.C,Previous.N,Previous.W,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    assert mode=='oneup'and jump==8 and C.digest(raw)==PIN
    text=Previous.controller(raw,mode,jump,start='cap');b=dict(W.Symbols.bundle(),raw=raw)
    old='STOCK.kind==3 and late.fourth_practical_cap and s.x>=899'
    assert text.count(old)==1;text=text.replace(old,'STOCK.kind==3 and late.fourth_full_cap',1)
    old="stock.active=true;stock.start=s;stock.score_before=stockScore();"
    new="stock.active=true;stock.start=s;stock.cap_actors={};for i=0,5 do local a=stockActor(i);if a.flag~=0 then stock.cap_actors[#stock.cap_actors+1]={actor=a,direction=read("+str(W.address(b,'Enemy_MovingDir'))+"+i)}end end;stock.score_before=stockScore();"
    assert text.count(old)==1;text=text.replace(old,new,1)
    # Bind delayed credit to the actual current timer DEC, not an unused
    # declared entry. This changes only an observer; all buttons are ordinary.
    pc=W.address(b,'FloateyNumbersCore');at=W.location(b,'FloateyNumbersCore')
    timer=W.address(b,'FloateyNum_Timer');assert raw[at+24:at+29]==bytes((0xde,timer&255,timer>>8,0xc9,43))
    old=dict(pc=pc,address=at-16,bytes=list(raw[at:at+8]),private=False)
    new=dict(pc=pc+24,address=at+8,bytes=list(raw[at+24:at+32]),private=False)
    encode=Previous.Previous.Base.lua
    needle='stockHook('+encode(old)+',function(cpu)';assert text.count(needle)==1
    text=text.replace(needle,'stockHook('+encode(new)+',function(cpu)',1)
    Previous.Previous.LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        genuine_both_feet_supported_fourth_cap_before_override=True,ordinary_running_A_then_Up=True,
        actual_timer43_delayed_life_cue64_required=True,no_gameplay_seeds=True,native_ready=False,outputs=0,Mesen=False)
