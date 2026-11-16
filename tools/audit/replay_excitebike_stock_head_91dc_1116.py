"""Separate mirrored positive-M head policy; preserve coast/pit negative."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_excitebike_stock_91dc_1116 as Previous

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
PREVIOUS_SHA='27c077a48a789ccc41e8866f9712c48a15c84734481a03e0e8783cedec8cc445'
KINDS=('flower','star')

@lru_cache(maxsize=2)
def controller(raw,key='flower'):
    assert key in KINDS and digest(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    text=Previous.controller(raw,key);once=Previous.once
    old="""  phase='stock-travel';buttons=bits(travel())
  if s.x>=C.target_x+64 then stock.phase='recover';phase='stock-recover';buttons=0;stock.approach=state();travelJump=nil end"""
    new="""  phase='stock-travel'
  if s.x<C.target_x-128 then buttons=bits(travel())else buttons=65;travelJump=nil end
  if s.x>=C.target_x-29 and s.native==0 and s.air==0 and s.crash==0 and s.heat==0 then
   stock.phase='prelean';phase='stock-prelean';stock.prelean=mainReturns;stock.prelean_request=state();buttons=73;travelJump=nil
  end"""
    text=once(text,old,new)
    text=once(text,"  phase='stock-prelean';buttons=74","  phase='stock-prelean';buttons=73")
    text=once(text,"   buttons=202\n  end\n elseif stock.phase=='head'", "   buttons=201\n  end\n elseif stock.phase=='head'")
    text=once(text,"  buttons=mainReturns-stock.head<8 and 202 or 0", "  buttons=mainReturns-stock.head<8 and 201 or 0")
    text=once(text,'local function stockDrive()\n',"local function stockDrive()\n assert(r('GameEngineSubroutine')~=11,'Ordinary stock policy entered actual death engine')\n")
    Previous.Previous.LuaRuntime().compile(text)
    return text

def metadata(raw,key='flower'):
    q=Previous.metadata(raw,key);text=controller(raw,key)
    q.update(controller_SHA256=digest(text.encode()),head_factory_SHA256=digest(Path(__file__).read_bytes()),
        retained_coast_policy_negative='8ae058337fd92b1dc820d0845bde236ac510c8271951e0f9f2dc676d96a10263',
        ordinary_head_policy='Mirror genuine M:4 Up+Right+B then8 freshA near target; no coast beyond block')
    return q

def family(kind='flower'):return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,kind),metadata=lambda raw,key:metadata(raw,kind))
