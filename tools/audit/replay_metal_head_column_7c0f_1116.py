"""Measured ordinary head alignment; current Metal owning code stays unchanged."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_metal_stock_7c0f_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
KINDS=Previous.KINDS


@lru_cache(maxsize=4)
def controller(raw,key='oneup',prefix=False):
    c=Previous.bindings(raw,key);_,body=Previous.controller(raw,key).split('\n',1)
    old="elseif M.phase==2 then b.right=c.x<336;if c.x>=336 then"
    new="elseif M.phase==2 then b.right=c.x<340;if c.x>=340 then"
    assert body.count(old)==1;body=body.replace(old,new,1)
    actor=Current.payload(raw)[0];pc=Current.labels()['Ms_B798'];assert pc==0xad54
    h=dict(pc=pc,space='wram',bank=3,offset=3*8192+(pc&8191),bytes=list(actor[pc-0xa000:pc-0xa000+8]))
    observer='C.hooks.RealAcceptedHead='+Text.lua(h)+'\n'+"""hook('RealAcceptedHead',function()
 local q=M.scope_passed and stock or M;if not q.head_request then return end
 q.accepted_head=q.accepted_head or{};if#q.accepted_head>=4 then return end
 local cpu=emu.getState();local a={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],state=state(),source_x=src(0x480)+256*src(0x498),source_y=src(0x4b0),source_vy=src(0x570),query_x=src(0x59)+256*src(0x5a),query_y=src(0x5b)}
 q.accepted_head[#q.accepted_head+1]=a
 returning(function(t)a.packet={};for i=0,7 do a.packet[#a.packet+1]=src(0x880+i)end;a.returnPC=t.pc;a.returnSP=t.sp end)
end)
"""
    marker="hook('GameLoop',function()";assert body.count(marker)==1;body=body.replace(marker,observer+marker,1)
    marker="M.scope_passed=true;M.earned=state();stock.since=stepOK;buttons={}"
    if prefix:
        assert body.count(marker)==1;body=body.replace(marker,marker+";M.actual_Main_return={pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp']};finish(true,'Genuine aligned Metal M and25 accepted movement+HostStep at completedMain')",1)
    marker=" assert(frame<18000 and mainEntries<6500,'Bounded natural Metal S/L controls')"
    extra=" if mainReturns>=1200 and not M.scope_passed then finish(false,'Aligned firstM bound');return end\n"+marker
    assert body.count(marker)==1;body=body.replace(marker,extra,1)
    text='local C='+Text.lua(c)+'\n'+body;LuaRuntime().compile(text)
    assert not any(n in text for n in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'))
    return text


def metadata(raw,key='oneup',prefix=False):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key,prefix).encode()),factory_SHA256=digest(Path(__file__).read_bytes()),
        scope='Actual7c0f measured head-column alignment340; real mature M/credit/25 prefix'+(' only'if prefix else' then natural '+key),
        prefix_only=prefix,controls_change='Approach340 instead336: prior actual head query334 hit adjacent cell; desired original head query>=336',game_bytes_changed=0)
    return q


def family(kind='oneup',prefix=False):return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,kind,prefix),metadata=lambda raw,key:metadata(raw,kind,prefix))
