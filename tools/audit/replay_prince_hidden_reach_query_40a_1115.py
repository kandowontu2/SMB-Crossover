"""One genuine pose78 head query; shared feet entry is explicitly excluded."""
from functools import lru_cache
import replay_prince_natural_stock_fast_40a_1115 as Previous

C,N,W,PIN=Previous.C,Previous.N,Previous.W,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    assert mode=='oneup'and jump==8 and C.digest(raw)==PIN
    text=Previous.controller(raw,mode,jump);b=dict(W.Symbols.bundle(),raw=raw)
    index=W.address(b,'BlockBufferAdderData')+6
    old=" if s.pose~=78 and vy<128 then return end"
    new=f" if stock.phase~='jump'or s.pose~=78 or cpu['cpu.y']~=read({index})then return end"
    assert text.count(old)==1;text=text.replace(old,new,1)
    old="q.return_PC=ret.pc;q.return_SP=ret.sp\n"
    assert text.count(old)==1;text=text.replace(old,"q.return_PC=ret.pc;q.return_SP=ret.sp;stock.query_complete=true\n",1)
    old='local function naturalStockTick()\n'
    new=old+" if stock.query_complete then final=stockState();finish(false,'Diagnostic complete: one actual pose78 head query, not item acquisition');return true end\n"
    assert text.count(old)==1;text=text.replace(old,new,1)
    Previous.LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        scope='One genuine pose78 head query, explicit diagnostic; no acquisition qualification',
        feet_shared_entry_excluded=True,no_gameplay_seeds=True,native_ready=False,outputs=0,Mesen=False)
