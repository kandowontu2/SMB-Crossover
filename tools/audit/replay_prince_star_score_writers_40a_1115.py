"""Actual native popup/score writer diagnosis; ordinary Star route unchanged."""
from functools import lru_cache
import replay_prince_star_credit_trace_40a_1115 as Previous

C,N,W,PIN=Previous.C,Previous.N,Previous.W,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='star',jump=8):
    text=Previous.controller(raw,mode,jump);b=dict(W.Symbols.bundle(),raw=raw)
    timer=W.address(b,'FloateyNum_Timer');fp=W.address(b,'FloateyNumbersCore')
    install=r'''
stock.native_writers={};stock.raw_popup_entries={}
local function stockWriter(at,value)
 if not stock.collected or #stock.native_writers>=8 then return end
 local cpu=emu.getState();local pc=cpu['cpu.pc'];local mapped=emu.convertAddress(pc);local bytes={}
 for i=0,7 do bytes[#bytes+1]=read(pc+i)end
 stock.native_writers[#stock.native_writers+1]={at=at,before=read(at),value=value,PC=pc,SP=cpu['cpu.sp'],X=cpu['cpu.x'],Y=cpu['cpu.y'],map=mapped,bytes=bytes,score=stockScore(),state=stockState()}
end
emu.addMemoryCallback(guarded(function(at,value)
 if stock.collector and at==@TIMER@+stock.collector.actor.slot then stockWriter(at,value)end
end),emu.callbackType.write,@TIMER@,@TIMER@+6)
emu.addMemoryCallback(guarded(stockWriter),emu.callbackType.write,STOCK.ram.Player1ScoreDisplay,STOCK.ram.Player1ScoreDisplay+5)
emu.addMemoryCallback(guarded(function()
 if not stock.collector or #stock.raw_popup_entries>=2 then return end
 local cpu=emu.getState();local pc=cpu['cpu.pc'];local a=emu.convertAddress(pc)
 stock.raw_popup_entries[#stock.raw_popup_entries+1]={PC=pc,SP=cpu['cpu.sp'],X=cpu['cpu.x'],map=a,state=stockState()}
end),emu.callbackType.exec,@FP@)
'''.replace('@TIMER@',str(timer)).replace('@FP@',str(fp))
    old='local function naturalStockTick()\n';assert text.count(old)==1
    text=text.replace(old,install+'\n'+old,1)
    Previous.Previous.Previous.Previous.LuaRuntime().compile(text);return text

def metadata(raw,mode='star',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        ordinary_Star_inputs_unchanged=True,at_most_eight_native_writes=True,diagnostic_only=True,
        no_gameplay_seeds=True,native_ready=False,outputs=0,Mesen=False)
