"""Fresh ordinary crouch-A on reaching supported head column, no idle delay."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_supermaaa_star_ground_91dc_1116 as Previous
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='ad5ebd04aa9f78c106d7b1654ad418b694169cb6adb1eb68bf1f90b105ada884'


@lru_cache(maxsize=1)
def controller(raw,key='star'):
    assert key=='star'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key)
    old=""" if c.grounded and c.y>=160 and math.abs(c.x-center)<=2 and math.abs(v)<=1 and not lastA then
  q.stand=state();q.phase='done';stock.phase='align';stock.phaseStart=guestReturns;stock.settle=0;return{}
 end"""
    new=""" if c.grounded and c.y>=160 and math.abs(c.x-center)<=2 and not lastA then
  assert(c.block(c.x+3,208)~=0 and c.block(c.x+12,208)~=0,'Actual ground-supported fresh Star jump')
  q.stand=state();q.phase='done';stock.phase='head';stock.headAt=guestReturns;stock.request=state();stock.authored_tile=c.block(C.target_x,C.target_y)
  return{a=true,down=true}
 end"""
    assert text.count(old)==1;text=text.replace(old,new,1)
    b=Current.bundle(raw);table=W.address(b,'BlockBuffer_Y_Adder');r3=W.address(b,'R3')
    observer=f"local headYTable={table};local headTileResult={r3}\n"+"""hook('MaaHead',function()
 if stock.phase~='head'or stock.crouch_head then return end
 local cpu=emu.getState();local dy=read(headYTable+cpu['cpu.y']);local s=state();local y=s.y+dy-r('MaaaLength');local x=s.x+8
 stock.crouch_head={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],state=s,yIndex=cpu['cpu.y'],yAdder=dy,queryX=x,queryY=y,tile=context().block(x,y)}
 returning(function(t)stock.crouch_head.returned={pc=t.pc,sp=t.sp,A=emu.getState()['cpu.a'],P=emu.getState()['cpu.ps'],R3=read(headTileResult),restoredY=r('Player_Y_Position')}end)
end)
hook('MaaStomp',function()
 if not food.M_scope_passed then return end
 stock.actual_stomps=stock.actual_stomps or{};if#stock.actual_stomps>=4 then return end
 local q={before=state(),pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp']};stock.actual_stomps[#stock.actual_stomps+1]=q
 returning(function(t)q.after=state();q.returnPC=t.pc;q.returnSP=t.sp end)
end)
"""
    marker="hook('GameLoop',function()";assert text.count(marker)==1;text=text.replace(marker,observer+marker,1)
    LuaRuntime().compile(text);return text


def metadata(raw,key='star'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),takeoff_factory_SHA256=digest(Path(__file__).read_bytes()),
        retained_idle_enemy_negative='3a3279d63b3d610a007ba9e441cad96598557aa8376a38ad27695e152d662a99',
        ordinary_change='Fresh crouch-A as soon as grounded inside real head column; omit fixture-only zeroVX/eight-neutral wait, actual head/stomp witnesses')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
