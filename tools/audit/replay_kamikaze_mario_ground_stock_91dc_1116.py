"""Ordinary fourth-cap walkoff and grounded first-pit jump for Source Mario."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_kamikaze_mario_stock_91dc_1116 as Previous
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
KINDS=Previous.KINDS
BASE_SHA='ed01181c4632387428875b980841bf549aefdd26ef1b519a3b9bef08b70ce212'

CONTROL="""local function sourceGroundRoute(c)
 local q=stock.ground_route
 if not q and stock.phase=='travel'and c.x>=896 and c.x<944 and c.grounded and c.y<=128 then
  q={phase='drop',since=guestReturns,cap=state(),cap_feet={c.block(c.x+3,c.y+32),c.block(c.x+12,c.y+32)}};stock.ground_route=q
 end
 if not q or q.phase=='done'then return end
 assert(guestReturns-q.since<400,'One ordinary cap drop and first-pit crossing')
 if q.phase=='drop'then
  if c.grounded and c.y>=160 and c.x>=944 then q.landing=state();q.phase='ground'else return{right=true}end
 end
 if C.stock_type==3 then q.phase='done';return end
 if q.phase=='ground'then
  if c.x<1072 then return{right=true,b=true}end
  assert(c.x<1088 and c.grounded and not lastA,'Fresh grounded takeoff before actual first pit')
  assert(c.block(1104,208)==0 and c.block(1120,208)==0 and c.block(1136,208)~=0,'Actual first pit and far bank')
  q.takeoff=state();q.phase='cross';return{right=true,b=true,a=true}
 elseif q.phase=='cross'then
  if c.x<1148 then return{right=true,b=true,a=true}end
  q.clear=state();q.phase='land'
 end
 assert(q.phase=='land','Ordinary first-pit landing phase')
 local v=c.vx<128 and c.vx or c.vx-256;local stop=c.x+v*math.abs(v)/32
 if c.grounded and c.y>=160 and c.x>=1136 and c.x<1216 and math.abs(v)<=1 then
  q.ground=state();q.phase='done';return{}
 end
 return{right=stop<1160,left=stop>1164}
end
local function chooseStock(c)
 local crossing=sourceGroundRoute(c);if crossing then return crossing end
"""


@lru_cache(maxsize=3)
def controller(raw,key='flower'):
    assert key in KINDS and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key);marker='local function chooseStock(c)\n'
    assert text.count(marker)==1;text=text.replace(marker,CONTROL,1)
    LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'))
    return text


def metadata(raw,key='flower'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),ground_route_factory_SHA256=digest(Path(__file__).read_bytes()),
        retained_early_cap_jump_negative='fe4f9ba426579b52a0ba637a222f55c46ccb25c0eb9454bb85347dc891b70f5d',
        actual_pit_causal_receipt='27720b449ebd2949deafce7a3c995a0356e1f9bb7c8623c479b37dbe1c61ddd8',
        ordinary_change='Walk off real fourth cap without A; fresh grounded jump before1104..1135 pit; land on actual far-bank ground before Flower row')
    return q


def family(kind='flower'):return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,kind),metadata=lambda raw,key:metadata(raw,kind))
