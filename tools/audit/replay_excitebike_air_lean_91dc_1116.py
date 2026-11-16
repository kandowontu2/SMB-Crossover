"""Retain intended original airborne Up after fresh-A release."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_excitebike_stock_head_91dc_1116 as Previous

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='63fe0e36186e0714609cf4698a3d451c88a25eb1ad545db8cf134cb780887e01'
KINDS=('flower',)

def air_lean(text):
    once=Previous.Previous.once
    text=once(text,"  buttons=mainReturns-stock.head<8 and 201 or 0",
        "  local n=mainReturns-stock.head;buttons=n<8 and 201 or n<36 and 8 or 0")
    return once(text,"   elseif n>=24 and s.native==0 and s.air==0 then stock.chase=nil end",
        "   elseif n<36 then buttons=8 elseif s.native==0 and s.air==0 then stock.chase=nil end")

@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=air_lean(Previous.controller(raw,key));Previous.Previous.Previous.LuaRuntime().compile(text);return text

def metadata(raw,key='flower'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),air_lean_factory_SHA256=digest(Path(__file__).read_bytes()),
        retained_head_negative='19727af528ba21743d083100bfa16c2c13a2438ae121b1061ef3fd9d0e9ab468',
        authentic_control='Original sourceUp bit2 retains24 air acceleration instead neutral52; established full-route36-Up hold, freshA only8')
    return q

def family(kind='flower'):return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,kind),metadata=lambda raw,key:metadata(raw,kind))
