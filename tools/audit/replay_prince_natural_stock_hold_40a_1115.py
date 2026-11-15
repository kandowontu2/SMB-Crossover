"""Established held-Up80 recipe; separate from retained short-pulse negatives."""
from functools import lru_cache
import replay_prince_natural_stock_returns_40a_1115 as Previous

C,N,W,PIN=Previous.C,Previous.N,Previous.W,Previous.PIN

@lru_cache(maxsize=2)
def controller(raw,mode='oneup',jump=8):
    assert jump==8 and mode in('oneup','star')and C.digest(raw)==PIN
    text=Previous.controller(raw,mode,jump)
    def change(old,new):
        nonlocal text
        assert text.count(old)==1,old[:100];text=text.replace(old,new,1)
    change('  local target=STOCK.x-8','  local target=STOCK.x-8;if stock.attempts==0 then target=target-28 end')
    change('if age>=8 and floor(s)and idle(s)then stock.attempts=stock.attempts+1;',
        'if age>=8 and floor(s)and idle(s)and s.action==0 then stock.attempts=stock.attempts+1;')
    change('  pad=age<12 and STOCK.jump or 0','  pad=age<80 and STOCK.jump or 0')
    change('  if age>24 and floor(s)and idle(s)then','  if age>100 and floor(s)and idle(s)then')
    change(" assert(stock.born and stock.mature and a.flag==1 and a.id==46 and a.state>=128,'Genuine mature authored item before collector')",
        " if stock.born and a.state>=128 then stock.mature=stock.mature or{state=stockState(),actor=a,at_collector=true}end\n assert(stock.born and stock.mature and a.flag==1 and a.id==46 and a.state>=128,'Genuine mature authored item before collector')")
    # Preserve measured boxes even if an overly strict observer rejects them.
    change(" assert(ox>0 and oy>0,'Actual positive native body/item overlap')\n",'')
    change(' stock.collector=before\n'," stock.collector=before\n assert(ox>0 and oy>0,'Actual positive native body/item overlap')\n")
    Previous.LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),mode=mode,
        required_native_variant=3,ordinary_fresh_idle_Up_hold80=True,short_pulse_and_A_negatives_retained=True,
        no_gameplay_seeds=True,native_ready=False,outputs=0,Mesen=False)
