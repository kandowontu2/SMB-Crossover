local impact={}

local function witnessBrick(cpu)
 local t=charge.active
 if t and t.phase=='released' and r('MmBlockAttack')==1 then
  local x,y=pos('MmProbeX','MmProbePage'),r('MmProbeY')
  impact.probe={x=x,y=y,tile=cpu['cpu.a']}
  assert(t.shot and t.shot.requested==3,'The released full charge owns the block attack')
  if impact.contact then
   assert(not impact.question and x//16*16==368 and y//16*16==144 and cpu['cpu.a']==0xc0,
          'Full charge pierces the brick and reaches its neighboring coin block')
   assert(r('MmBreakBlock')==0,'The neighboring coin block bumps intact')
   impact.question={x=x,y=y,slot=r('SprDataOffset_Ctrl'),motor=motor,coins=r('CoinTally')}
   return
  end
  assert(x//16*16==384 and y//16*16==144 and cpu['cpu.a']==0x51,
         'Full charge selects the authored brick at X384/Y144')
  assert(r('MmBreakBlock')==1,'The released full charge breaks the actual brick')
  impact.contact={x=x,y=y,tile=cpu['cpu.a'],shot=t.shot.slot,motor=motor}
 end
end

local function observeBrickNoise(_,cue)
 if impact.contact and not impact.noise and cue==1 then impact.noise={motor=motor,cue=cue}end
end

chargeControl=function(s)
 if s.status==0 or s.growth~=0 or not scope()then return end
 if not checks['0'].grant then return {}end
 assert(s.status==1 and s.lives==2 and s.x>=398 and s.x<=422,'Powered robot stays beside the brick during the firing test')
 local c=context();local tier=charge.tiers[1]
 if not tier then
  assert(c.block(384,144)==0x51,'Real brick is intact before the shot')
  tier={power=1,trials={},start=s};charge.tiers[1]=tier
 end
 local t=tier.trials[1]
 if not t then
  if not impact.aligned and s.x<414 then return {right=true}end
  impact.aligned=true
  if r('PlayerFacingDir')~=2 then return {left=true}end
  if s.state~=0 or s.vx>4 and s.vx<252 or mask&64~=0 or r('MmChargeFrames')~=0 then return {}end
  assert(s.x>=406,'Buster muzzle will probe the rightmost brick first')
  t={power=1,target=87,phase='hold',start=s};tier.trials[1]=t;charge.active=t
  return {b=true}
 end
 assert(s.motor-t.start.motor<=195,'Bounded real charge, jump and recovery')
 if t.phase=='hold'then
  if r('MmChargeFrames')<87 then return {b=true}end
  assert(t.pellet and t.pellet.direction==2 and s.state==0,'Earned full charge and a real grounded launch')
  t.phase='lift';t.jump=s;return {b=true,a=true}
 end
 if t.phase=='lift'then
  assert(s.motor-t.jump.motor<22,'Fresh A lifts the shooter beside the brick')
  if s.y>146 then return {b=true,a=true}end
  assert(s.state~=0 and s.y>=135 and r('MmChargeFrames')==87,'Release full charge while rising next to the brick')
  t.phase='released';t.release=s
  return {a=true}
 end
 if s.motor-t.release.motor>=7 then
  assert(impact.contact and impact.noise and impact.question,'The released shot shatters the brick and bumps the coin block')
  local q=impact.question
  if r('Block_State',q.slot)~=0 and r('Block_Metatile',q.slot)==0xc4 then
   assert(pos('Block_X_Position','Block_PageLoc',q.slot)==368,'Bouncing coin block keeps its authored horizontal origin')
   q.bounces=(q.bounces or 0)+1
  end
  assert(r('MmChargeFrames')==0 and r('MmCharging')==0,'Charge returns cleanly after the hit')
  if s.motor-impact.contact.motor>=25 and s.state==0 and s.y==176 then
   assert(c.block(384,144)==0 and c.block(368,144)==0xc4,'Brick clears and the coin block changes at its original cell')
   assert(q.bounces and (r('CoinTally')-q.coins)%100==1,'The bumped block stays aligned and awards exactly one coin')
   t.done=s;tier.complete=s;charge.active=nil
  end
 end
 return {}
end
