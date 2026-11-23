local charge={tiers={}}
local limits={47,48,87}

local function chargeStarted(p,requested)
 local t=charge.active
 if not t then return end
 p.buster={requested=requested,frames=r('MmChargeFrames'),holding=mask&64~=0,
           x=pos('Player_X_Position','Player_PageLoc'),direction=r('PlayerFacingDir')}
end

local function chargeSpawned(p,slot)
 local t=assert(charge.active,'Spawn belongs to an active Buster trial')
 local shot=p.buster
 assert(slot<4 and r('MmBulletType',slot)==shot.requested,'Real Buster projectile occupies its slot')
 assert(r('MmBulletAge',slot)==0,'New shot starts at age zero')
 assert(r('MmBulletDir',slot)==shot.direction and (shot.direction==1 or shot.direction==2),
        'New shot follows the actual facing direction')
 shot.slot=slot
 shot.spawn_x=pos('MmBulletX','MmBulletPage',slot)
 assert(shot.spawn_x==shot.x+(shot.direction==1 and 27 or -11),'Real Buster muzzle position')
 shot.cue=r('Square1SoundQueue')
 assert(shot.cue==C.buster_cue and r('MmAudioShotType')==shot.requested,'Actual Buster sound cue and type')
 local normal=t.power*3-2
 if shot.holding then
  assert(not t.pellet and shot.requested==normal and shot.frames==0,'Fresh B spawns one standard shot')
  t.pellet=shot
 else
  assert(t.phase=='released' and t.target>=48 and not t.shot,'Only the expected release spawns a charged shot')
  assert(shot.frames==t.target and shot.requested==normal+(t.target==48 and 1 or 2),'Native charge threshold and tier select the right shot')
  t.shot=shot
 end
end

local function chargeControl(s)
 local power=s.status
 if power==0 or s.growth~=0 or not scope() then return end
 local pickup=checks[tostring(power-1)]
 if not pickup.grant then return end
 local tier=charge.tiers[power]
 if not tier then tier={power=power,trials={},start=s};charge.tiers[power]=tier end
 if tier.complete then return end
 assert(s.lives==2 and s.yHigh==1 and math.abs(s.x-tier.start.x)<20,'Keep the earned power on its natural firing ledge')
 local t=tier.trials[#tier.trials]
 if not t or t.done then
  if #tier.trials==#limits then tier.complete=s;return {}end
  if s.state~=0 or mask&64~=0 or r('MmChargeFrames')~=0 then return {}end
  t={power=power,target=limits[#tier.trials+1],phase='hold',start=s}
  tier.trials[#tier.trials+1]=t;charge.active=t
  return {b=true}
 end
 assert(s.motor-t.start.motor<=140,'Bounded Buster hold and release')
 if t.phase=='hold'then
  local frames=r('MmChargeFrames')
  if frames<t.target then return {b=true}end
  assert(frames==t.target and t.pellet and mask&64~=0,'Natural held B reached its exact release threshold')
  t.phase='released';t.release=s;t.counter=frames
  return {}
 end
 if s.motor-t.release.motor<3 then return {}end
 assert(r('MmChargeFrames')==0 and r('MmCharging')==0 and mask&64==0,'Released B resets the native charge')
 if t.target==47 then
  assert(not t.shot,'Releasing on frame47 spawns no charged shot')
 else
  assert(t.shot,'Releasing on frame48 or87 spawns a live charged shot')
  local shot=t.shot;local slot=shot.slot
  if r('MmBulletType',slot)==shot.requested and r('MmBulletAge',slot)>=2 then
   shot.after_x=pos('MmBulletX','MmBulletPage',slot);shot.age=r('MmBulletAge',slot)
   assert((shot.after_x-shot.spawn_x)*(shot.direction==1 and 1 or -1)>0,'The charged projectile moves in its launch direction')
  else
   assert(s.motor-t.release.motor<16,'The charged projectile persists long enough to move')
   return {}
  end
 end
 t.done=s;charge.active=nil
 return {}
end
