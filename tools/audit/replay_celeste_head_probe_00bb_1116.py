"""Unchanged L controls; capped actual small-head point and flight trace."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_celeste_stock_00bb_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest


@lru_cache(maxsize=1)
def controller(raw,key='oneup'):
    assert key=='oneup';c=deepcopy(Previous.bindings(raw,key));b=Current.bundle(raw)
    for n in('BlockBuffer_X_Adder','BlockBuffer_Y_Adder','CmPreviousAB','CmState','CmVelYFrac','CmJumpTime'):c['ram'][n]=W.address(b,n)
    c['head_add']=[raw[W.location(b,n)+14]for n in('BlockBuffer_X_Adder','BlockBuffer_Y_Adder')];assert c['head_add']==[8,18]
    _,body=Previous.controller(raw,key).split('\n',1)
    probe="""hook('BlockBufferColli_Head',function()
 if not stock.head_request or stock.born then return end;local cpu=emu.getState()
 if cpu['cpu.y']~=14 or r('Player_Y_Speed')<128 then return end
 assert(read(C.ram.BlockBuffer_X_Adder+14)==8 and read(C.ram.BlockBuffer_Y_Adder+14)==18)
 local qx=pos('Player_X_Position','Player_PageLoc')+8;local qy=r('Player_Y_Position')+18
 stock.minimum_head_y=math.min(stock.minimum_head_y or qy,qy)
 if qy>160 or(stock.last_sample_y and qy>=stock.last_sample_y)then return end
 stock.head_samples=stock.head_samples or{};if#stock.head_samples>=12 then return end;stock.last_sample_y=qy
 local q={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],Y=cpu['cpu.y'],state=state(),query_x=qx,query_y=qy,cell_x=(qx//16)*16,cell_y=(qy//16)*16,source_state=r('CmState'),previousAB=r('CmPreviousAB'),fraction=r('CmVelYFrac'),jumpTime=r('CmJumpTime')}
 stock.head_samples[#stock.head_samples+1]=q
 returning(function(t)q.returned={PC=t.pc,SP=t.sp,A=emu.getState()['cpu.a'],P=emu.getState()['cpu.ps'],R2=read(2),R3=read(3),R4=read(4),R6=read(6),R7=read(7)}end)
end)
"""
    marker="hook('GameLoop',function()";assert body.count(marker)==1;body=body.replace(marker,probe+marker,1)
    marker=" assert(frame<14000 and mainEntries<4500,'Bounded ordinary Celeste S/L')"
    extra=""" if stock.head_request then
  stock.minimum_player_y=math.min(stock.minimum_player_y or 255,r('Player_Y_Position'))
  stock.flight_samples=stock.flight_samples or{};local elapsed=moves-stock.headAt
  if elapsed<=72 and elapsed%6==0 and#stock.flight_samples<13 then stock.flight_samples[#stock.flight_samples+1]={state=state(),previousAB=r('CmPreviousAB'),source_state=r('CmState'),fraction=r('CmVelYFrac'),jumpTime=r('CmJumpTime')}end
 end
"""+marker
    assert body.count(marker)==1;body=body.replace(marker,extra,1)
    text='local C='+Text.lua(c)+'\n'+body;LuaRuntime().compile(text);return text


def metadata(raw,key='oneup'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw).encode()),probe_factory_SHA256=digest(Path(__file__).read_bytes()),
        controls_identical=True,scope='Same first L controls; actual native head row14/adders8,18/returned tile and minY, diagnostic only')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
