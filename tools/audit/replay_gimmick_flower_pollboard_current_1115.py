"""Current590 ordinary Flower boarding with actual input/admission handshakes."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import replay_gimmick_flower_polltravel_current_1115 as Previous

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN
Frozen,IDENTITIES,normalize,bindings=Previous.Frozen,Previous.IDENTITIES,Previous.normalize,Previous.bindings
PARENT_SOURCE='40cf3d34f7b1e48519bec38e7f165f08d882713e5f4b68057ab4b253566965d3'
PARENT_LUA='a948946485989b29ce3334cadfa23a8fbf67b291aa4e27288dfc2668dd0d2208'

POLICY=r'''
local phase,age='align',0
local gate,press,releaseA
local function nativeStar(c)return c.r('GmRam0091')end
local function epoch(c)return{poll=gmTravel.polls,read=gmTravel.reads,Main=c.frame}end
local function cleared(g,bit)
 return g and gmTravel.polls-g.poll>=2 and(gmTravel.last_clear[tostring(bit)]or 0)>g.read
end
local function mark(c,name)
 local q=gmTravel.snapshot();q.phase=name
 flower.control_events=flower.control_events or{}
 assert(#flower.control_events<24,'Bounded Flower control witnesses')
 flower.control_events[#flower.control_events+1]=q
end
return function(c)
 if not firstMReady then return oldPolicy(c)end
 if flower.after then return{}end
 local mature=false
 for i=0,5 do if c.r('Enemy_Flag',i)==1 and c.r('Enemy_ID',i)==46 then
  assert(c.r('PowerUpType',i)==1,'Ordinary final Flower kind')
  mature=c.r('Enemy_State',i)>=128
 end end
 if not mature then return oldPolicy(c)end
 local v=c.r('GmRam00CC');if v>=128 then v=v-256 end
 local vy=c.r('GmRam00C2')
 local stopping=c.x+v*math.abs(v)/32
 flower.control_phase=phase
 if phase=='align'then
  if not(c.grounded and c.x>=1242 and c.x<=1246 and math.abs(v)<=2)then return{right=stopping<1243,left=stopping>1245}end
  if nativeStar(c)~=0 then return{}end
  phase='charge';age=0;gate=epoch(c)
  flower.boarding_policy_start={frame=c.frame,x=c.x,y=c.y,VX=c.r('GmRam00CC')};mark(c,'stationary-charge')
 end
 if phase=='charge'then
  age=age+1;assert(age<180,'Bounded ordinary charge')
  if nativeStar(c)>=169 and cleared(gate,128)and c.r('GmPrevious')&128==0 then
   phase='right-runup';mark(c,'right-charged-runup')
  else return{b=true}end
 end
 if phase=='right-runup'then
  if c.x<1270 then return{right=true,b=true}end
  phase='left-runup';mark(c,'left-charged-runup')
 end
 if phase=='left-runup'then
  if c.x>1245 or v>=0 then return{left=true,b=true}end
  assert(c.grounded and c.r('GmPrevious')&128==0,'Actual grounded released-A takeoff')
  phase='left-air-charge';age=0;press=epoch(c);press.admissions=gmTravel.flower_admissions or 0
  flower.boarding_takeoff={frame=c.frame,x=c.x,y=c.y,VX=c.r('GmRam00CC')};mark(c,'request-left-jump')
  return{left=true,a=true,b=true}
 elseif phase=='left-air-charge'then
  age=age+1;assert(age<48,'Bounded real left-jump input admission')
  if(gmTravel.flower_admissions or 0)<=press.admissions then
   if gmTravel.polls-press.poll>=2 and(gmTravel.last_set['128']or 0)>press.read and(gmTravel.last_fresh_read or 0)>press.read then
    phase='right-runup';flower.takeoff_retries=(flower.takeoff_retries or 0)+1;mark(c,'retry-unadmitted-left-jump')
    return{right=true,b=true}
   end
   return{left=true,a=true,b=true}
  end
  if not flower.left_jump_admitted then flower.left_jump_admitted={frame=c.frame,x=c.x,y=c.y,VY=vy};mark(c,'actual-left-jump-admitted')end
  if vy>=128 and vy<204 then return{left=true,a=true,b=true}end
  assert(vy>=128,'Actual original rising jump before release')
  phase='release-right';age=0;flower.support_baseline=flower.support_count or 0
  flower.launch_baseline=flower.opposite_launch and flower.opposite_launch.state.Main or-1
  mark(c,'request-right-facing-star-release');return{right=true,a=true}
 elseif phase=='release-right'then
  age=age+1;assert(age<12,'Bounded real star release consumption')
  if not flower.opposite_launch or flower.opposite_launch.state.Main<=flower.launch_baseline then return{right=true,a=true}end
  phase='left-chase';age=0;mark(c,'actual-star-launched')
 end
 if phase=='left-chase'then
  age=age+1;assert(age<100,'Bounded reflected-star support')
  if vy<128 and not releaseA then releaseA=epoch(c);mark(c,'descending-release-A')end
  local current=gmTravel.last_support and gmTravel.last_support.read==gmTravel.reads
  if flower.wall_reflection and(flower.support_count or 0)>flower.support_baseline and current and c.r('GmRam036E')==128 and vy==0 and cleared(releaseA,128)and c.r('GmPrevious')&128==0 then
   phase='flower-jump';age=0;press=epoch(c);mark(c,'request-current-ride-fresh-right-jump')
   return{right=true,a=true}
  end
  assert(nativeStar(c)~=0 and c.x>=1152,'Real star remains active before support')
  return{left=true,a=vy>=128}
 elseif phase=='flower-jump'then
  age=age+1;assert(age<100,'Bounded ordinary post-support Flower jump')
  if not flower.support_jump then
   assert(c.frame-press.Main<16,'Fresh ride jump must be actually admitted')
   return{right=true,a=true}
  end
  return{right=c.x<1243,left=c.x>1247,a=vy>=128}
 end
 error('Unknown polled Flower boarding phase '..phase)
end
'''


@lru_cache(maxsize=1)
def controller(raw,key='mr_gimmick'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT_SOURCE
    text=Previous.controller(raw,key);assert sha256(text.encode()).hexdigest()==PARENT_LUA
    old=Previous.Flower.Previous.policy();start=old.index("local phase,age='align',0")
    text=Previous.Pipe.once(text,old[start:],POLICY.lstrip('\n'))
    text=Previous.Pipe.once(text,'if flower.boarding_policy_start then gmTravel.request=nil end',
        "if pos('Player_X_Position','Player_PageLoc')>=1212 then gmTravel.request=nil end")
    text=Previous.Pipe.once(text,"   gmTravel.record('actual-Flower-phase-jump',gmTravel.snapshot())\n  end",
        "   gmTravel.record('actual-Flower-phase-jump',gmTravel.snapshot())\n  else gmTravel.flower_head_admissions=(gmTravel.flower_head_admissions or 0)+1 end")
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='mr_gimmick'):
    q=Previous.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        parent_full_setup_negative_factory_SHA256=PARENT_SOURCE,parent_full_setup_negative_Lua_SHA256=PARENT_LUA,
        measured_Flower_boarding_input_policy_unchanged=False,
        scope='Current590 genuine M, polled/consumed travel and actual-admission/launch/current-reflected-star support/fresh-jump Flower collector; inventory2/next2/cue1c/erase/1000score/25moves. Source-only pending root native; no fullstage/audio/visual claim')
    return q
