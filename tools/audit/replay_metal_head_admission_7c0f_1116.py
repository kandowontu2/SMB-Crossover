"""Unchanged ordinary M controls; latch the real accepted head and jump state."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_metal_stock_7c0f_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest


@lru_cache(maxsize=1)
def controller(raw,key='oneup'):
    assert key=='oneup';c=Previous.bindings(raw,key);actor,_,_,_=Current.payload(raw)
    pc=Current.labels()['Ms_B798'];assert pc==0xad54 and actor[pc-0xa000:pc-0xa000+3]==bytes.fromhex('20c0bf')
    hook=dict(pc=pc,space='wram',bank=3,offset=3*8192+(pc&8191),bytes=list(actor[pc-0xa000:pc-0xa000+8]))
    _,body=Previous.controller(raw,key).split('\n',1)
    observer="C.hooks.RealAcceptedHead="+Text.lua(hook)+"\n"+"""local function admission()
 local q={state=state(),pad=src(0x31),clock=src(0x53),jump=src(0x5b8),jumpLatch=src(0x735),action=src(0x4e0),source_x=src(0x480)+256*src(0x498),source_y=src(0x4b0),source_vy=src(0x570),query_x=src(0x59)+256*src(0x5a),query_y=src(0x5b)}
 q.packet={};for i=0,7 do q.packet[#q.packet+1]=src(0x880+i)end;return q
end
hook('RealAcceptedHead',function()
 if not M.head_request then return end;M.accepted_head=M.accepted_head or{};if#M.accepted_head>=4 then return end
 local q=admission();local cpu=emu.getState();q.pc=cpu['cpu.pc'];q.sp=cpu['cpu.sp'];q.A=cpu['cpu.a'];q.P=cpu['cpu.ps'];M.accepted_head[#M.accepted_head+1]=q
 returning(function(t)q.returned=admission();q.returnPC=t.pc;q.returnSP=t.sp end)
end)
"""
    marker="hook('GameLoop',function()";assert body.count(marker)==1;body=body.replace(marker,observer+marker,1)
    marker=" assert(frame<18000 and mainEntries<6500,'Bounded natural Metal S/L controls')"
    replacement=""" if M.head_request and mainReturns-M.head_request.Main<=48 and(mainReturns-M.head_request.Main)%3==0 then
  M.admission=M.admission or{};if#M.admission<17 then M.admission[#M.admission+1]=admission()end
 end
 if mainReturns>=340 then finish(false,'Same-controls firstM accepted-head/jump diagnostic bound');return end
"""+marker
    assert body.count(marker)==1;body=body.replace(marker,replacement,1)
    text='local C='+Text.lua(c)+'\n'+body;LuaRuntime().compile(text);return text


def metadata(raw,key='oneup'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),probe_factory_SHA256=digest(Path(__file__).read_bytes()),controls_identical=True,
        scope='Actual7c0f same M inputs; real AD54 accepted-head seam and <=17 jump samples, diagnostic only')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
