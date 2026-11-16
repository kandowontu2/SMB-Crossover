"""Same failed F controls; stop at first mapped Y/status/death cause only."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_kamikaze_mario_stock_91dc_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='ed01181c4632387428875b980841bf549aefdd26ef1b519a3b9bef08b70ce212'


@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    _,body=Previous.controller(raw,key).split('\n',1);c=deepcopy(Current.bindings(raw));h=c['hooks']['MarioSourceMovement'];b=Current.bundle(raw)
    c.update(kind='flower',stock_type=1,target_x=1248,target_y=144,movement_hex=raw[16+h['offset']:16+h['offset']+64].hex())
    for name in('ObjectOffset','Enemy_MovingDir','Enemy_Y_HighPos','SavedJoypadBits'):c['ram'][name]=W.address(b,name)
    for name in('MarioSourceInjuryStart','KillPlayer'):
        pc,at=W.address(b,name),W.location(b,name);bank=(at-16)//8192
        c['hooks'][name]=dict(pc=pc,offset=at-16,bank=bank,bytes=list(raw[at:at+8]),bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    observer="""local function causalState()
 local s=state();local x=s.x;local c=context();s.pad=r('SavedJoypadBits');s.cells={}
 for _,dx in ipairs({3,12})do for _,y in ipairs({144,176,192,208})do s.cells[#s.cells+1]={x=x+dx,y=y,tile=c.block(x+dx,y)}end end
 s.source_vx={r('MmVX'),r('MmVX',1),r('MmVX',2)};s.source_vy={r('MmVY'),r('MmVY',1),r('MmVY',2)}
 return s
end
local function cause(kind,value)
 if not food.M_scope_passed or stock.cause then return end
 local cpu=emu.getState();local pc=cpu['cpu.pc'];local sp=cpu['cpu.sp'];local mapped=emu.convertAddress(pc)
 stock.cause={kind=kind,value=value,pc=pc,sp=sp,mapped=mapped,state=causalState(),
  stackPC=(read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1)&65535}
 finish(false,'Diagnostic actual first '..kind)
end
hook('MarioSourceMovement',function()
 if not food.M_scope_passed or guestReturns%4~=0 then return end
 stock.causal_last=stock.causal_last or{};stock.causal_last[#stock.causal_last+1]=causalState()
 if#stock.causal_last>24 then table.remove(stock.causal_last,1)end
end)
hook('KillPlayer',function()cause('KillPlayer',0)end)
hook('MarioSourceInjuryStart',function()cause('MarioSourceInjuryStart',r('PlayerStatus'))end)
emu.addMemoryCallback(guard(function(_,v)
 if v>1 and r('Player_Y_HighPos')<=1 then cause('high-Y boundary write',v)end
end),emu.callbackType.write,C.ram.Player_Y_HighPos)
emu.addMemoryCallback(guard(function(_,v)
 if v==0 and r('PlayerStatus')==1 then cause('tier1-to0 writer',v)end
end),emu.callbackType.write,C.ram.PlayerStatus)
"""
    marker="hook('GameLoop',function()";assert body.count(marker)==1;body=body.replace(marker,observer+marker,1)
    text='local C='+Text.lua(c)+'\n'+body;LuaRuntime().compile(text);return text


def metadata(raw,key='flower'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),causal_factory_SHA256=digest(Path(__file__).read_bytes()),
        controls_identical=True,scope='First actual mapped Y/status/death writer under frozen failedF controls; never item qualification')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
