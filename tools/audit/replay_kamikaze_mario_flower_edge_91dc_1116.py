"""Stand beside the actual row edge for Source Mario's powered jump height."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_kamikaze_mario_ground_stock_91dc_1116 as Previous
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='58e1680356c1a30ea16d8beba9dd5305362b28222bf38b71b2de35f6025fdf01'


@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key);old='   local clear=edge+16'
    assert text.count(old)==1;text=text.replace(old,'   local clear=edge',1)
    old="if q.settle>=8 then q.phase='rise';q.takeoff=guestReturns;q.stand=state();return{a=true}end"
    new="""if q.settle>=8 then
     assert(c.block(c.x+2,C.target_y)==0 and c.block(c.x+13,C.target_y)==0,'Actual head-clear footprint beside right row edge')
     q.phase='rise';q.takeoff=guestReturns;q.stand=state();q.head_feet={c.block(c.x+2,C.target_y),c.block(c.x+13,C.target_y)};return{a=true}
    end"""
    assert text.count(old)==1;text=text.replace(old,new,1);LuaRuntime().compile(text);return text


def metadata(raw,key='flower'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),edge_factory_SHA256=digest(Path(__file__).read_bytes()),
        ordinary_change='Head-clear actual edge1280 rather than16px-away1296; same real birth/maturity/collection/growth/25 gates',
        retained_distant_mount_negative='f2590e67e621678323de3bc7adac158dc74b3b47f5192fe0355b1e7a02d94db3')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
