"""Same failed standing-A inputs; first six actual raised-head query returns."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_supermaaa_flower_clear_head_91dc_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='eae8fe02acd47a41bda1bfffacc4f74ee1a24704fcdabf0fe65528b747218850'


@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key);b=Current.bundle(raw);extra={}
    for name in('BlockBuffer_X_Adder','BlockBuffer_Y_Adder','R3','CrouchingFlag'):extra[name]=W.address(b,name)
    pc,at=W.address(b,'BlockBufferColli_Head'),W.location(b,'BlockBufferColli_Head');bank=(at-16)//8192
    h=dict(pc=pc,offset=at-16,bank=bank,bytes=list(raw[at:at+8]),bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    marker="hook('GameLoop',function()"
    observer='for n,a in pairs('+Text.lua(extra)+')do C.ram[n]=a end\nC.hooks.ActualNativeHead='+Text.lua(h)+"\n"+"""local pendingHeadQuery
hook('MaaHead',function()
 if stock.phase~='head'or pendingHeadQuery then return end
 stock.head_queries=stock.head_queries or{};if#stock.head_queries>=6 then return end
 local cpu=emu.getState();local y=cpu['cpu.y'];local dx,dy=r('BlockBuffer_X_Adder',y),r('BlockBuffer_Y_Adder',y);local c=context();local s=state()
 local x=s.x+dx;local worldY=s.y+dy-r('MaaaLength')
 local q={entryPC=cpu['cpu.pc'],entrySP=cpu['cpu.sp'],state=s,yIndex=y,xAdder=dx,yAdder=dy,crouch=r('CrouchingFlag'),queryX=x,queryY=worldY,buffer_tile=c.block(x,worldY)}
 pendingHeadQuery=q;stock.head_queries[#stock.head_queries+1]=q
 returning(function(t)
  q.returned={pc=t.pc,sp=t.sp,A=emu.getState()['cpu.a'],P=emu.getState()['cpu.ps'],R3=r('R3'),restoredY=r('Player_Y_Position')};pendingHeadQuery=nil
  if#stock.head_queries==6 then finish(false,'Diagnostic six actual standing-A raised-head queries complete')end
 end)
end)
hook('ActualNativeHead',function()
 if not pendingHeadQuery then return end
 local cpu=emu.getState();pendingHeadQuery.native={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],Y=cpu['cpu.y'],temporary_playerY=r('Player_Y_Position')}
end)
"""
    assert text.count(marker)==1;text=text.replace(marker,observer+marker,1);LuaRuntime().compile(text);return text


def metadata(raw,key='flower'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),head_query_factory_SHA256=digest(Path(__file__).read_bytes()),
        controls_identical=True,scope='Six reached MaaHead/native head returns under retained standingA controls; diagnostic only')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
