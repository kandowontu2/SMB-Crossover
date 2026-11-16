"""Genuine Flower birth retained; original speed-powered collection run-up."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_excitebike_air_lean_91dc_1116 as Previous

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='aa6f42671d55647f2dd421b5825d26e8ab76b3860b0389da7674f71de0aeb0de'

@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key);a=text.index(' if a then\n  if a.state<128 then return end\n');b=text.index(" if stock.phase=='travel'then",a)
    text=text[:a]+""" if a then
  if a.state<128 then return end
  phase='stock-collect';stock.phase='collect'
  if not stock.runup then stock.runup={phase='out',since=mainReturns,start=state()}end
  local q=stock.runup
  assert(mainReturns-q.since<700,'One bounded real collection run-up')
  assert(s.x<1380,'Remain before real second pit1392')
  if q.phase=='out'then
   buttons=65
   if s.x>=C.target_x+48 then q.phase='coast';q.release=state();buttons=0 end
  elseif q.phase=='coast'then
   if s.speed==0 and s.native==0 and s.air==0 and s.crash==0 then q.phase='back';q.stand=state();buttons=66 end
  elseif q.phase=='back'then
   buttons=66
   if s.x<=C.target_x+55 and s.speed>=630 and s.native==0 and s.air==0 and s.crash==0 then
    q.phase='prelean';q.prelean=mainReturns;q.prelean_request=state();buttons=74
   end
   assert(s.x>=C.target_x+38,'Source-speed run-up must qualify before launch column')
  elseif q.phase=='prelean'then
   buttons=74
   if mainReturns-q.prelean>=4 then q.phase='jump';q.jump=mainReturns;q.request=state();q.minimum_y=s.y;buttons=202 end
  elseif q.phase=='jump'then
   local n=mainReturns-q.jump;q.minimum_y=math.min(q.minimum_y,s.y)
   buttons=n<8 and 202 or n<36 and 8 or 0
   assert(n<120,'One ordinary original airborne collection must reach the mature Flower')
  else error('Unknown source collection run-up '..q.phase)end
  return
 end
"""+text[b:]
    Previous.Previous.Previous.Previous.LuaRuntime().compile(text);return text

def metadata(raw,key='flower'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),runup_factory_SHA256=digest(Path(__file__).read_bytes()),
        retained_low_speed_chase_negative='d2901c25090158505e0b4e29f1082602e6e6ae89b55d737948803c65414b2abd',
        original_runup='Actual throttle/coast/reverse, matched positiveM speed630 minimum, freshA+airborneUp; no movement grants')
    return q

def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
