"""Read-only target popup timing diagnosis after a genuine ordinary Star."""
from functools import lru_cache
import replay_prince_star_facing_40a_1115 as Previous

C,N,W,PIN=Previous.C,Previous.N,Previous.W,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='star',jump=8):
    text=Previous.controller(raw,mode,jump)
    def change(a,b):
        nonlocal text
        assert text.count(a)==1,a[:100];text=text.replace(a,b,1)
    b=dict(W.Symbols.bundle(),raw=raw);timer=W.address(b,'FloateyNum_Timer')
    change(" if not stock.collected or stock.credit or cpu['cpu.x']~=stock.collector.actor.slot then return end",
        " if stock.collector and cpu['cpu.x']==stock.collector.actor.slot then\n"
        "  stock.core_trace=stock.core_trace or{};if #stock.core_trace<12 then stock.core_trace[#stock.core_trace+1]={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],X=cpu['cpu.x'],timer=read("+str(timer)+"+cpu['cpu.x']),control=read(STOCK.ram.FloateyNum_Control+cpu['cpu.x']),score=stockScore(),state=stockState()}end\n end\n"
        " if not stock.collected or stock.credit or cpu['cpu.x']~=stock.collector.actor.slot then return end")
    change(' if stock.collected then\n  pad=0',
        ' if stock.collected then\n  stock.post_collect=stock.post_collect or{};if #stock.post_collect<12 then stock.post_collect[#stock.post_collect+1]={state=s,score=stockScore(),timer=read('+str(timer)+'+stock.collector.actor.slot),control=read(STOCK.ram.FloateyNum_Control+stock.collector.actor.slot)}end\n'
        "  if stock.prince_returns-stock.collected.state.Prince_returns>=40 then final=s;finish(false,'Read-only actual Star popup timing observation complete');return true end\n  pad=0")
    Previous.Previous.Previous.LuaRuntime().compile(text);return text

def metadata(raw,mode='star',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        ordinary_Star_controls_unchanged=True,diagnostic_only=True,no_gameplay_seeds=True,native_ready=False,outputs=0,Mesen=False)
