"""Same-input causal launch/head observer, not a new navigation policy."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import replay_excitebike_stock_head_91dc_1116 as Previous

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='63fe0e36186e0714609cf4698a3d451c88a25eb1ad545db8cf134cb780887e01'

@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    config=deepcopy(Previous.Previous.bindings(raw,key));b=Current.bundle(raw)
    for name in('BlockBuffer_X_Adder','BlockBuffer_Y_Adder'):
        config['ram'][name]=W.address(b,name)
    for name in('ExAirLaunch','BlockBufferColli_Head'):
        pc=W.address(b,name);work=name.startswith('Ex');at=Current.START+(pc&8191)if work else W.location(b,name);bank=(at-16)//8192
        config['hooks'][name]=dict(pc=pc,offset=3*8192+(pc&8191)if work else at-16,work=work,bytes=list(raw[at:at+8]))
        if not work:config['hooks'][name].update(bank=bank,bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    text=Previous.controller(raw,key);_,body=text.split('\n',1);text='local C='+Previous.Previous.Previous.Text.lua(config)+'\n'+body
    observer="""food.head_trace={launches={},queries={},seen={},minY={}}
local function tracePhase()
 if not food.M_scope_passed and(phase=='jump'or phase=='wait')and mainReturns<400 then return'M-positive'end
 if food.M_scope_passed and stock.head and mainReturns-stock.head<48 then return'stock-negative'end
end
hook('ExAirLaunch',function()
 local k=tracePhase();if not k then return end;local cpu=emu.getState()
 food.head_trace.launches[#food.head_trace.launches+1]={case=k,state=state(),pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],A=cpu['cpu.a'],X=cpu['cpu.x'],Y=cpu['cpu.y'],
  pad=r('SavedJoypadBits'),previous=ram2(0x803),source_input=ram2(0x5c),source_y=ram2(0x8c),source_facing=ram2(0x804)}
end)
hook('BlockBufferColli_Head',function()
 local k=tracePhase();if not k then return end;local cpu=emu.getState();local i=cpu['cpu.y']
 local x=pos('Player_X_Position','Player_PageLoc')+r('BlockBuffer_X_Adder',i);local y=r('Player_Y_Position')+r('BlockBuffer_Y_Adder',i)
 local q={case=k,entry=state(),entryPC=cpu['cpu.pc'],entrySP=cpu['cpu.sp'],adder_index=i,point_x=x,point_y=y}
 returning(function(t)
  local c=emu.getState();q.raw=c['cpu.a'];q.returnPC=t.pc;q.returnSP=t.sp;q.P=c['cpu.ps'];q.row=read(5);q.probe_low_x=read(8);q.buffer=read(9)+256*read(10)
  local tag=k..':'..(x//16)..':'..(y//16)..':'..q.raw
  if not food.head_trace.seen[tag]then
   food.head_trace.seen[tag]=true;if#food.head_trace.queries<24 then food.head_trace.queries[#food.head_trace.queries+1]=q end
  end
 end)
end)
hook('ExHostMovement',function()
 local k=tracePhase();if not k then return end
 returning(function(t)local s=state();local q=food.head_trace.minY[k]
  if not q or s.y<q.state.y then food.head_trace.minY[k]={state=s,pc=t.pc,sp=t.sp,pad=r('SavedJoypadBits'),source_y=ram2(0x8c),source_input=ram2(0x5c)}end
 end)
end)
"""
    text=Previous.Previous.once(text,"hook('GameLoop',function()",observer+"hook('GameLoop',function()")
    Previous.Previous.Previous.LuaRuntime().compile(text);return text

def metadata(raw,key='flower'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),trace_factory_SHA256=digest(Path(__file__).read_bytes()),
        controls_identical_to_frozen_negative=True,scope='Read-only actual launch/head-point cause; source-positive M and negative stock kept distinct')
    return q
