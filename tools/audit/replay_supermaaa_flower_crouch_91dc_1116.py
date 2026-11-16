"""Ordinary crouch-jump puts the actual raised head below the Flower block."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_supermaaa_flower_clear_head_91dc_1116 as Previous
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='eae8fe02acd47a41bda1bfffacc4f74ee1a24704fcdabf0fe65528b747218850'


@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key)
    old='   b={a=true}';assert text.count(old)==1;text=text.replace(old,'   b={a=true,down=true}',1)
    old='  return{a=guestReturns-stock.headAt<24}';assert text.count(old)==1
    text=text.replace(old,'  return{a=guestReturns-stock.headAt<24,down=guestReturns-stock.headAt<24}',1)
    b=Current.bundle(raw);table=W.address(b,'BlockBuffer_Y_Adder');crouch=W.address(b,'CrouchingFlag');r3=W.address(b,'R3')
    marker="hook('GameLoop',function()"
    observer=f"local actualHeadYAdder={table};local actualCrouch={crouch};local actualHeadResult={r3}\n"+"""hook('MaaHead',function()
 if stock.phase~='head'or stock.crouch_head then return end
 local cpu=emu.getState();local dy=read(actualHeadYAdder+cpu['cpu.y']);local s=state();local worldY=s.y+dy-r('MaaaLength');local tile=context().block(s.x+8,worldY)
 assert(read(actualCrouch)~=0 and cpu['cpu.y']==14 and dy==18,'Actual native crouch head table selected')
 assert(worldY>=144 and worldY<160 and tile==stock.authored_tile,'Actual crouch head inside real Flower block')
 stock.crouch_head={state=s,pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],yIndex=cpu['cpu.y'],yAdder=dy,queryX=s.x+8,queryY=worldY,tile=tile}
 returning(function(t)
  assert(read(actualHeadResult)==tile and emu.getState()['cpu.a']==tile,'Actual MaaHead returns original native block')
  stock.crouch_head.returned={pc=t.pc,sp=t.sp,A=emu.getState()['cpu.a'],P=emu.getState()['cpu.ps'],restoredY=r('Player_Y_Position')}
 end)
end)
"""
    assert text.count(marker)==1;text=text.replace(marker,observer+marker,1);LuaRuntime().compile(text);return text


def metadata(raw,key='flower'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),crouch_factory_SHA256=digest(Path(__file__).read_bytes()),
        retained_standing_head_negative='8d9211650156cf8ad47847ebc397fd4bed5272c4f594433b2fded2397d433490',
        standing_query_diagnostic='e6135f4bad0243acc231e4b12f6c08d8eb94060d7a70a67c60d0d63a8d704e22',
        ordinary_change='Hold native Down during freshA/head hold; original crouch table+18 instead of standing+4, actual tile/return proved; no game changes')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
