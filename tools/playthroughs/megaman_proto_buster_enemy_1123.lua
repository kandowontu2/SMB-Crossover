local combat={}

local function enemyHP(slot)
 return r('MmEnemyHealthLo',slot)+256*r('MmEnemyHealthHi',slot)
end

local function witnessDamage(p,slot)
 local t=charge.active
 if not t or not combat.target or combat.target.slot~=slot or combat.defeat then return end
 local shotSlot=r('MmSlot');local shot=r('MmBulletType',shotSlot);local e=actor(slot)
 if not (t.shot and shot==3 and shotSlot==t.shot.slot or t.followup and shot==1 and shotSlot==t.followup.slot) then return end
 assert(e.id==6 and e.flag>0 and e.flag<128 and e.state<2,'The Buster contacts the tracked living Goomba')
 p.buster_hit={actor=e,hp=enemyHP(slot),shot=shot,shot_slot=shotSlot,
               player=state(),score=score()}
end

local function witnessDamageReturn(p)
 local hit=p.buster_hit;local slot=hit.actor.slot
 local e=actor(slot);local hp=enemyHP(slot)
 hit.after={actor=e,hp=hp,cue=r('Square1SoundQueue'),player=state()}
 assert(hit.after.cue==C.enemy_smack,'Native enemy-hit sound')
 if hit.shot==3 then
  assert(not combat.full and hit.hp==0,'The full charge is the first damage to the live Goomba')
  combat.full=hit
  if C.mode_value==0 then
   assert(hp==25 and e.state<2,'Full charge leaves 25 of the Easy Goomba’s 100 HP')
   return
  end
 else
  assert(C.mode_value==0 and combat.full and hit.hp==25,'Follow-up pellet hits the same damaged Easy Goomba')
 end
 assert(hp==0 and e.state&32~=0,'The tracked Goomba enters its native defeat state')
 local popup=r('FloateyNum_Control',slot);local x,y=r('FloateyNum_X_Pos',slot),r('FloateyNum_Y_Pos',slot)
 assert(popup==1 and x==(e.x-hit.after.player.camera)&255 and y==e.y,'The 100-point popup starts at the defeated Goomba')
 hit.popup={x=x,y=y,kind=popup}
 combat.defeat=hit
end

local originalChargeSpawned=chargeSpawned
chargeSpawned=function(p,slot)
 local t=charge.active
 if t and t.phase=='tap' then
  local shot=p.buster
  assert(not t.followup and shot.requested==1 and shot.holding and shot.frames==0,'Fresh follow-up B fires one pellet')
  assert(slot<4 and r('MmBulletType',slot)==1 and r('MmBulletAge',slot)==0,'Follow-up pellet exists in a native projectile slot')
  shot.slot=slot;t.followup=shot;t.phase='after-tap'
 else
  originalChargeSpawned(p,slot)
 end
end

local function targetAhead(c)
 for i=0,5 do
  local e=actor(i);local dx=e.x-c.x
  if e.id==6 and e.flag>0 and e.flag<128 and e.state<2 and e.yHigh==1
     and dx>=46 and dx<=108 and math.abs(e.y-c.y-8)<=5 then
   local clear=true
   for x=c.x+23,e.x+8,8 do
    if c.block(x,c.y+18)~=0 then clear=false;break end
   end
   if clear then return e end
  end
 end
end

chargeControl=function(s)
 if s.status==0 or s.growth~=0 or not scope() then return end
 if not checks['0'].grant then return {}end
 assert(s.status==1 and s.lives==2 and s.yHigh==1,'Keep the naturally earned Mushroom power throughout combat')
 local c=context();local tier=charge.tiers[1]
 if not tier then tier={power=1,trials={},start=s};charge.tiers[1]=tier end
 local t=tier.trials[1]
 if not t then
  if mask&64~=0 or r('MmChargeFrames')~=0 then return {}end
  t={power=1,target=87,phase='hold',start=s};tier.trials[1]=t;charge.active=t
  return {right=true,b=true}
 end
 assert(s.motor-t.start.motor<=1600,'Bounded route to the first clear Goomba shot')
 if t.phase=='hold' then
  if r('MmChargeFrames')==87 and c.grounded and r('PlayerFacingDir')==1 then
   local e=targetAhead(c)
   if e then
    assert(t.pellet and enemyHP(e.slot)==0,'The target has no earlier projectile damage')
    combat.target=e;t.phase='released';t.release=s
    return {}
   end
  end
  local b=base(c);b.b=true;return b
 end
 if combat.defeat then
  local hit=combat.defeat
  if s.motor-hit.after.player.motor>=25 and s.state==0 and score()>=hit.score+100 then
   assert(s.star==0,'No invincibility power contributes to the defeat')
   combat.credit={before=hit.score,after=score(),player=s}
   t.done=s;tier.complete=s;charge.active=nil
  end
  return {}
 end
 assert(s.motor-t.release.motor<55,'Release and follow-up must meet the naturally approaching target')
 if combat.full and C.mode_value==0 and t.phase=='released' then
  t.phase='tap'
  return {b=true}
 end
 return {}
end
