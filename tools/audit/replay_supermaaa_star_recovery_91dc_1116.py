"""Frozen ground/head inputs; genuine injury60, then unpowered mature Star."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_supermaaa_star_ground_takeoff_91dc_1116 as Previous
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='a73c1f30defa6c4d2bb02b35cb705d4ec361c6d1e0b7835acc9a8799a5d40bfe'


@lru_cache(maxsize=1)
def controller(raw,key='star'):
    assert key=='star'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key)
    old=" assert(r('PlayerStatus')==1,'Genuine firstM tier retained before stock')"
    new=" assert(r('PlayerStatus')==1 or(r('PlayerStatus')==0 and stock.shrink_done),'Retained M or actual completed injury60')"
    assert text.count(old)==1;text=text.replace(old,new,1)
    old="assert(stock.native_effect and stock.star35_writer and r('StarInvincibleTimer')>0 and r('PlayerStatus')==1 and r('NumberofLives')==2,'Actual StarC0/35writer, retainedM and life2')"
    new="assert(stock.injury and stock.shrink_ticks==60 and stock.shrink_done and stock.collector.state.power==0 and stock.native_effect and stock.star35_writer and r('StarInvincibleTimer')>0 and r('PlayerStatus')==0 and r('NumberofLives')==2,'Actual injury60 then unpowered StarC0/35writer/life2')"
    assert text.count(old)==1;text=text.replace(old,new,1)
    old=" stock.injury={pc=cpu['cpu.pc']"
    new=" assert(r('PlayerStatus')==1 and r('NumberofLives')==2,'Actual first powered native injury');stock.shrink_ticks=0\n"+old
    assert text.count(old)==1;text=text.replace(old,new,1)
    observer="""hook('MarioSourcePowerupUpdate',function()
 if not stock.injury or stock.shrink_done or r('GuestPowerupActive')==0 then return end
 assert(r('GuestPowerupOld')==1 and r('GuestPowerupTarget')==0 and r('GuestLegacyHurt')~=0 and r('GuestPowerupAge')==stock.shrink_ticks,'Actual old1/target0 injury transaction')
 stock.shrink_ticks=stock.shrink_ticks+1;assert(stock.shrink_ticks<=60,'Actual sixty injury updates')
 returning(function(t)
  if stock.shrink_ticks==60 then
   assert(r('PlayerStatus')==0 and r('GuestPowerupActive')==0 and r('GuestPowerupAge')==60 and r('TimerControl')==0 and active(),'Actual original injury60 returned')
   stock.shrink_done={pc=t.pc,sp=t.sp,state=state()}
  end
 end)
end)
"""
    marker="hook('GameLoop',function()";assert text.count(marker)==1;text=text.replace(marker,observer+marker,1);LuaRuntime().compile(text);return text


def metadata(raw,key='star'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),recovery_factory_SHA256=digest(Path(__file__).read_bytes()),
        retained_powered_head_negative='b1e2ffc657b364f5442365f428ae4e01f86a29c73ac4a920a72c7618ef1aca47',controls_identical=True,
        scope='Genuine M/ground/head/Star birth/full128, actual injury+60shrink, unpowered physical StarC0/35/1000 then25Source/life2; not poweredStar')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
