"""Wait for the real row Goomba to clear SuperMaaa's raised head column."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_supermaaa_stock_91dc_1116 as Previous
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='97c8f76baba1e0ed133de8fac75b6aeb1a0e37d284852d8dfec311e19e5bbb1b'


@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key);old=" if stock.settle>=8 then\n   stock.phase='head'"
    new=""" if stock.settle>=8 then
   for i=0,4 do
    local e=actor(i)
    if e.flag==1 and e.id<21 and e.state<32 and e.x>c.x-32 and e.x<c.x+32 and e.y<c.y-16 then
     stock.head_enemy_wait=stock.head_enemy_wait or{first=state(),first_actor=e};stock.head_enemy_wait.last=state();stock.head_enemy_wait.last_actor=e
     return{}
    end
   end
   if stock.head_enemy_wait then stock.head_enemy_wait.clear=state()end
   stock.phase='head'"""
    assert text.count(old)==1;text=text.replace(old,new,1);LuaRuntime().compile(text);return text


def metadata(raw,key='flower'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),clear_head_factory_SHA256=digest(Path(__file__).read_bytes()),
        retained_raised_box_injury_negative='160e3384c42e0e3b7aeb28cc80bfb56a264dd9436a45800a7bbae6f79244ba03',
        ordinary_change='Neutral at supported standing head column until live upper enemy clears horizontal32px; same freshA, tier1/F60/credit/25 gates')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
