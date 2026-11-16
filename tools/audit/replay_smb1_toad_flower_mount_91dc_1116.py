"""Genuine Flower birth retained; ordinary jump beside the actual brick row."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_smb1_toad_native_stock_91dc_1116 as Previous

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='1acaa08a55128dbf10d4cbfeb92d5d5611f183492c732b4dc060f19c5f8a7e1b'


@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key)
    a=text.index("  stock.phase='collect';local dx=a.x-c.x;");b=text.index('\n  return b',a)+len('\n  return b')
    text=text[:a]+"""  stock.phase='collect'
  if not stock.mount then
   local edge=C.target_x;local row={}
   for _=1,8 do
    local tile=c.block(edge-16,C.target_y);row[#row+1]={x=edge-16,tile=tile}
    if tile==0 then break end;edge=edge-16
   end
   local clear=edge-24;assert(clear>c.camera,'Actual left-side head clearance remains visible')
   stock.mount={phase='back',edge=edge,clear=clear,row=row,since=guestReturns,request=state()}
  end
  local q=stock.mount;assert(guestReturns-q.since<220,'One ordinary real-row Flower mount')
  if q.phase=='back'then
   local v=c.vx<128 and c.vx or c.vx-256;local stop=c.x+v*math.abs(v)/32
   if c.grounded and c.y>=160 and math.abs(c.x-q.clear)<=2 and math.abs(v)<=1 and not lastA then
    q.settle=(q.settle or 0)+1
    if q.settle>=8 then q.phase='rise';q.takeoff=guestReturns;q.stand=state();return{a=true}end
   else q.settle=0 end
   return{right=stop<q.clear-1,left=stop>q.clear+1}
  elseif q.phase=='rise'then
   if c.y<=C.target_y-32 then q.phase='onto';q.clearance=state()else return{a=guestReturns-q.takeoff<32}end
  end
  assert(q.phase=='onto','Actual mount phase')
  return{right=c.x<a.x-3,left=c.x>a.x+3,a=guestReturns-q.takeoff<32,b=true}"""+text[b:]
    Previous.Previous.Previous.LuaRuntime().compile(text);return text


def metadata(raw,key='flower'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),mount_factory_SHA256=digest(Path(__file__).read_bytes()),
        retained_under_block_negative='8e11904f1d344f0a1715a5b271699133bcf4ed65e974db1bfd780a6015da6f6e',
        ordinary_mount='Actual row edge/visible head-clear ground column, fresh verticalA then native horizontal movement onto row')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
