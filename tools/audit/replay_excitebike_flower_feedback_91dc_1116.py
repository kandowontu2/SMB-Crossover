"""Actual-state runway feedback; preserve frozen source/native F divergence."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_excitebike_flower_runway_91dc_1116 as Previous

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='6d2c572479aea47772e8bc69cfe738a749c89aece65b744d8bc50c91e5f3f470'

@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key);once=Previous.Previous.Previous.Previous.Previous.once
    helper="""local function originalCoastStop(s)
 -- Exact existing ground-coast CE58 and fractional-X DA58 rules. This only
 -- predicts controller braking; it writes no emulated state or game code.
 assert(s.native==0 and s.air==0 and s.crash==0 and s.recovery==0 and s.heat==0 and ram2(0x52)==0,'Original flat coast domain')
 assert(ram2(0x804)==1 and ram3(0xa905)==56 and ram3(0xa910)==1,'Current original ground-deceleration table/facing')
 local v,tick,f,x=s.speed,ram2(0x3f),ram2(0x394),s.x
 for _=1,256 do
  if v==0 then return x end
  tick=(tick+1)&255
  if tick&3==0 then v=math.max(0,v-56)end
  f=f+(v&255);x=x+(v>>8)+(f>=256 and 1 or 0);f=f&255
 end
 error('Original coast projection bound')
end
"""
    text=once(text,'local function stockDrive()\n',helper+'local function stockDrive()\n')
    old="""   buttons=65
   if s.x>=C.target_x+64 then q.phase='coast';q.release=state();buttons=0 end"""
    new="""   if s.crash~=0 or s.recovery~=0 or s.air~=0 or s.native~=0 then return end
   local projected=originalCoastStop(s);q.projected_stand=projected
   assert(projected<1380,'Actual original stopping distance stays before pit1392')
   for x=(s.x//16)*16,(projected//16)*16,16 do assert(solid(x,208),'Actual authored flat runway support')end
   buttons=65
   if projected>=C.target_x+100 then q.phase='coast';q.release=state();q.predicted_release_stand=projected;buttons=0 end"""
    text=once(text,old,new)
    old="if s.speed==0 and s.native==0 and s.air==0 and s.crash==0 then q.phase='back';q.stand=state();buttons=66 end"
    new="""if s.speed==0 and s.native==0 and s.air==0 and s.crash==0 then
    q.stand=state();q.prediction_error=s.x-q.predicted_release_stand
    if s.x<C.target_x+94 then
     q.refund=(q.refund or 0)+1;assert(q.refund<=2,'Finite actual obstruction/refunding');q.phase='out';buttons=65
    else q.phase='back';buttons=66 end
   end"""
    text=once(text,old,new)
    Previous.Previous.Previous.Previous.Previous.Previous.LuaRuntime().compile(text);return text

def metadata(raw,key='flower'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),feedback_factory_SHA256=digest(Path(__file__).read_bytes()),
        retained_native_fixed_runway_negative='dba8d124c9cd14bcff1879c127a1eb4233f22a05fcb2823d1306bf3cdfa3f925',
        runway_feedback='Actual current speed/private quarter-step/fraction; exact original56-per4 coast and fractional-X projection, real floor/pit and original speed/collector/60/25 gates retained')
    return q

def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
