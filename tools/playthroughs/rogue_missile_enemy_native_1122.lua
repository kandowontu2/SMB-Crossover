-- Catch the naturally falling roof Goomba before its feet reach the floor.
local function missileShot(i)
 return {slot=i,action=r('RdWAction',i),x=pos('RdWX','RdWHi',i),y=r('RdWY',i),
  vx=r('RdWVX',i),vy=r('RdWVY',i),frame=r('RdWFrame',i),reset=r('RdWReset',i),
  rx=r('RdWRadiusX',i),ry=r('RdWRadiusY',i),onScreen=r('RdWOnScreen',i)}
end
local function missileCounts(suffix)
 local q=snapshot(suffix);q.RdControlDispatch=counts['RdControlDispatch'..suffix]or 0;return q
end
local function missilePhase(f,name)
 f.phase=name;f.entered=updates
 assert(#f.steps<20,'Bounded missile route phases')
 f.steps[#f.steps+1]={phase=name,player=state()}
end
local function missileReturned(n,p)
 local f=gear.missile;if not f then return end
 if n=='RdWxSpawn'and f.phase=='fire'then
  local s=missileShot(p.weapon_slot)
  assert(not f.birth and s.action==11 and s.vx==4 and s.vy==0 and s.y==187,
         'One genuine rightward missile11 at the original floor muzzle')
  assert(r('RdMissiles')==4 and r('RdMaxMissiles')==5 and r('RdMissileMode')==1,
         'Exactly one naturally earned missile spent')
  assert(f.request and f.ammo,'Actual original missile request and ammo writer')
  f.slot=s.slot;f.birth={shot=s,player=state()}
 elseif n=='RdWxUpdateSlot'and f.birth and p.weapon_slot==f.slot then
  local s=missileShot(f.slot)
  if p.weapon_before.action==11 and s.x~=p.weapon_before.x then
   assert(s.x==p.weapon_before.x+4 and s.y==p.weapon_before.y,
          'Original horizontal missile speed4')
   f.moves=(f.moves or 0)+1
  end
  if p.weapon_before.action==11 and s.action==4 then
   assert(f.hit and s.reset==0x91,'Actual enemy contact enters original impact animation')
   f.impact={before=p.weapon_before,after=s,player=state()}
  end
  if s.action==0 and not f.expiry then
   assert(f.hit and f.impact,'Contact and original impact before missile removal')
   f.expiry={player=state(),entered=missileCounts('_entered'),returned=missileCounts('_returned')}
  end
 end
end
local function missileEnemyDrive(c)
 local f=gear.missile
 assert(c.level==1 and c.areaType==2 and r('AreaAddrsLOffset')==f.areaOffset
        and updates-f.started<2200,'Bounded ordinary 1-2 missile encounter')
 assert(identity()and active()and r('NumberofLives')==2 and r('RdTanks')==1
        and r('RdGear')==1 and r('RdMaxMissiles')==5,'Earned resources and live identity')
 if f.baseline then
  assert(r('RdHealthLo')==f.baseline.health_raw[1]and r('RdHealthHi')==f.baseline.health_raw[2],
         'Captured actual health preserved through missile contact and cleanup')
  assert(r('RdMissiles')==(f.birth and 4 or 5),'Exact earned ammo before and after the single missile')
 end
 if c.x>=1000 and updates%12==0 then
  if #f.approach==20 then table.remove(f.approach,1)end
  local actors={};for i=0,4 do local a=actor(i);if a.flag==1 then actors[#actors+1]=a end end
  f.approach[#f.approach+1]={player=state(),actors=actors}
 end
 local grounded=c.yHigh==1 and bombReady(c)
 if f.phase=='unmorph'then
  if r('RdAction')==3 then return{up=true}end
  missilePhase(f,'travel')
 end
 if f.phase=='travel'then
  if c.x>=832 and not f.passedLowCeiling then missilePhase(f,'low-ceiling')
  elseif c.x>=1052 and grounded and c.y>=170 then
   f.baseline=state();missilePhase(f,'release')
  else return gearTravel(setmetatable({area=f.areaOffset},{__index=c}))end
 end
 if f.phase=='low-ceiling'then
  if r('RdAction')~=3 then return{down=grounded}end
  if c.x<900 then return{right=true}end
  missilePhase(f,'stand-after-ceiling')
 end
 if f.phase=='stand-after-ceiling'then
  if r('RdAction')==3 then return{up=true}end
  f.passedLowCeiling=true;missilePhase(f,'walk-under')
 end
 if f.phase=='walk-under'then
  if not grounded or c.y<170 then return{}end
  if c.x<1052 then return{right=true}end
  missilePhase(f,'travel')
 end
 if f.phase=='align'then
  if c.x<1086 then return{right=true}end
  if c.x>1089 then return{left=true}end
  assert(grounded and c.y==177,'Real floor before the falling-enemy pocket')
  missilePhase(f,'wait-target');return{}
 end
 if f.phase=='release'then
  if updates-f.entered<2 or r('RdHeld')&96~=0 then return{}end
  missilePhase(f,'select')
 end
 if f.phase=='select'then
  if r('RdMissileMode')~=1 then return{select=true}end
  missilePhase(f,'rearm');return{}
 end
 if f.phase=='rearm'then
  if updates-f.entered<2 or r('RdHeld')&96~=0 then return{}end
  missilePhase(f,'align');return{}
 end
 if f.phase=='wait-target'then
  for i=0,4 do local a=actor(i)
   if a.flag==1 and a.id==6 and a.state==1 and a.x>=1118 and a.x<=1144
      and a.y>=150 and a.y<=160 and r('MmEnemyHealthLo',i)==2 then
    f.target={actor=a,player=state()};missilePhase(f,'fire');return{b=true}
   end
  end
  assert(updates-f.entered<180,'Natural roof Goomba must descend into the original missile lane')
  return{}
 end
 if f.phase=='fire'then
  if not f.birth then
   assert(updates-f.entered<12,'Fresh B admits the earned missile')
   return{b=true}
  end
  missilePhase(f,'retreat')
 end
 if f.phase=='retreat'and c.x>1052 then return{left=true}end
 if f.expiry then
  local er,rr=missileCounts('_entered'),missileCounts('_returned');local enough=true
  f.postexpiry_returned={}
  for n,v in pairs(er)do
   f.postexpiry_returned[n]=rr[n]-f.expiry.returned[n]
   if v-f.expiry.entered[n]<25 or f.postexpiry_returned[n]<25 then enough=false end
  end
  if enough then
   assert(#pending==0 and f.moves>0 and f.hit and f.impact and r('RdWAction',f.slot)==0
          and r('RdMissiles')==4,'Actual damage, original cleanup, and 25 more completed workers')
   f.complete=true;finish('natural-missile-damages-Goomba');return{}
  end
 end
 return{}
end
