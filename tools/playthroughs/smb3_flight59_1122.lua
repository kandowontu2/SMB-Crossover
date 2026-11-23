-- Adapter after the frozen ordinary Raccoon acquisition checkpoints.
local acquire=assert(oldChoose)
local route=assert(SMB3_UPGRADE_BASE)
local F={phase='acquire',changes={},combat={}}
SMB3_FLIGHT_STATE=F
local combat
local function change(c,p)
 F.phase=p;F.at=c.motor
 F.changes[#F.changes+1]={phase=p,motor=c.motor,update=c.update,x=c.x,y=c.y}
 assert(#F.changes<=20,'Finite natural Raccoon flight phases')
end
local function steer(c,goal)
 local vx=c.vx>=128 and c.vx-256 or c.vx
 local dx=goal-c.x;local lead=vx*vx/24+8
 if vx>3 and dx<=lead then return {left=true}end
 if vx< -3 and -dx<=lead then return {right=true}end
 if dx>5 then return {right=true}end
 if dx< -5 then return {left=true}end
 return {left=vx>0,right=vx<0}
end
local function enemy(c)
 local best
 for i=0,5 do
  local flag=c.r('Enemy_Flag',i);local id=c.r('Enemy_ID',i);local state=c.r('Enemy_State',i)
  local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
  local y=c.r('Enemy_Y_Position',i);local dx=x-c.x
  if flag>0 and flag<128 and id<21 and state&32==0 and not(id==6 and state>=2)
     and c.r('Enemy_Y_HighPos',i)==1 and math.abs(y-c.y-8)<=20 and dx>=0 and dx<=160
     and(not best or dx<best.dx)then best={slot=i,id=id,state=state,x=x,y=y,dx=dx}end
 end
 return best
end
local function fight(c)
 local q=assert(combat)
 assert(c.motor-q.motor<360,'Finite stationary runway encounter')
 if q.defeat then
  q.finished={motor=c.motor,x=c.x,y=c.y};F.active_combat=nil;combat=nil
  return {}
 end
 local slot=q.enemy.slot
 local flag,id,state=c.r('Enemy_Flag',slot),c.r('Enemy_ID',slot),c.r('Enemy_State',slot)
 local ex=c.r('Enemy_X_Position',slot)+256*c.r('Enemy_PageLoc',slot)
 local gap=ex-c.x;local vx=c.vx>=128 and c.vx-256 or c.vx
 q.last={motor=c.motor,x=c.x,y=c.y,vx=vx,enemy_x=ex,gap=gap,tail=c.r('M3Native::Player_TailAttack')}
 assert(flag>0 and flag<128 and id==q.enemy.id and state&32==0,
  'Runway actor remains live until the authenticated native tail-defeat return')
 assert(gap>=16,'Stop before unsafe runway body contact')
 if q.phase=='brake'then
  if vx>0 then return {left=true}end
  if vx<0 then return {right=true}end
  q.phase='face';q.stopped=q.last
 end
 if q.phase=='face'then
  if c.r('PlayerFacingDir')~=1 then return {right=true}end
  if vx~=0 then return {}end
  q.phase='wait';q.stationary=q.last
 end
 if q.phase=='wait'then
  if vx~=0 then return {}end
  if gap>30 or c.r('M3Native::Player_TailAttack')~=0 or c.r('M3Previous')&64~=0 then return {}end
  assert(c.grounded and gap>=22,'Safe grounded actual tail-entry distance')
  q.phase='await-tail';q.attack=q.last;return {b=true}
 elseif q.phase=='await-tail'then
  assert(c.motor-q.attack.motor<8,'Bounded actual fresh-B acceptance while stationary')
  if c.r('M3Native::Player_TailAttack')==0 then return {b=true}end
  q.phase='swing';q.accepted=q.last
 end
 assert(c.r('M3Native::Player_TailAttack')~=0,
  'Stationary tail swing ended without a qualified native defeat')
 return {}
end
return function(c)
 if not SMB3_ACTION_STATE.acquired then return acquire(c)end
 assert(c.r('M3Form')==3,'Naturally acquired Raccoon remains owned')
 if F.phase=='acquire'then change(c,'travel-to-runway')end
 if F.phase=='travel-to-runway'then
  if c.x>=1440 and c.grounded and c.y>=160 then
   F.runway={x=c.x,y=c.y,motor=c.motor};change(c,'earn-P')
  else return route(c)end
 end
 if F.phase=='earn-P'then
  assert(c.x<2112,'Natural P-meter runway ends before the first staircase')
  if combat then return fight(c)end
  local e=enemy(c)
  if c.grounded and e then
   assert(#F.combat<12,'Bounded actual runway enemies')
   combat={phase='brake',motor=c.motor,enemy=e};F.combat[#F.combat+1]=combat;F.active_combat=combat
   return fight(c)
  end
  if c.x>=1912 and c.grounded and c.y==176 and c.r('M3Native::Player_Power')==127
      and c.r('M3Previous')&128==0 then
   F.launch_input={motor=c.motor,update=c.update,x=c.x,y=c.y,vx=c.vx}
   change(c,'launch-flight');return {right=true,b=true,a=true}
  end
  return {right=true,b=true}
 elseif F.phase=='launch-flight'then
  assert(c.motor-F.at<12,'Real fresh A launches the naturally charged flight')
  if c.r('M3Native::Player_FlyTime')>0 and c.r('M3Native::Player_InAir')~=0 then
   change(c,'controlled-flight')
  else return {right=true,b=true,a=true}end
 end
 local b=steer(c,2080)
 if F.phase=='controlled-flight'then
  assert(c.y>=24 and c.y<=208,'Bounded visible native flight height')
  if c.r('M3Native::Player_FlyTime')==0 then change(c,'slow-descent')
  else
   local vy=c.r('M3Native::Player_YVel');if vy>=128 then vy=vy-256 end
   local flap=c.y>=80 or(c.y>=64 and vy>0)
   b.a=flap and c.r('M3Previous')&128==0
   return b
  end
 end
 if F.phase=='slow-descent'then
  if(F.slow_steps or 0)>=8 then change(c,'land')
  else b.a=c.r('M3Previous')&128==0;return b end
 end
 if F.phase=='land'and F.ground_verified then
  local vx=c.vx>=128 and c.vx-256 or c.vx
  if vx~=0 then return {left=vx>0,right=vx<0}end
  assert(c.grounded and c.r('M3Native::Player_InAir')==0 and c.r('M3Previous')&128==0,
   'Stationary grounded release before an ordinary fresh follow-up jump')
  F.followup_request={motor=c.motor,x=c.x,y=c.y,wag=c.r('M3Native::Player_WagCount')}
  change(c,'followup-jump')
 end
 if F.phase=='followup-jump'then
  assert(c.motor-F.at<12,'Bounded actual fresh-A follow-up acceptance')
  if F.followup and F.followup.launch then change(c,'followup-land');return{}end
  return {a=true}
 elseif F.phase=='followup-land'then
  assert(c.motor-F.at<240,'Bounded released-A follow-up and retained-suit landing')
  return {}
 end
 return b
end
