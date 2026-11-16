-- One ordinary post-MF floor/gap approach; no B until actual aligned enemy.
local function shot(i)return {slot=i,action=r('RdWAction',i),x=pos('RdWX','RdWHi',i),y=r('RdWY',i),vx=r('RdWVX',i),vy=r('RdWVY',i),age=r('RdWAge',i),frame=r('RdWFrame',i),anim=r('RdWAnim',i),onScreen=r('RdWOnScreen',i),hit=r('RdWHit',i)}end
local function attackCounts()return {entered=snapshot('_entered'),returned=snapshot('_returned')}end
local function event(kind,row)if #attack.events<8 then attack.events[#attack.events+1]={kind=kind,Main=updates,row=row}end end
local function nativeEnemy(i)
 local a=actor(i);a.high=r('Enemy_Y_HighPos',i);a.boxctrl=r('Enemy_BoundBoxCtrl',i);a.HP={r('MmEnemyHealthLo',i),r('MmEnemyHealthHi',i)};a.hurt=r('MmEnemyFlash',i)
 if a.boxctrl<13 then local o=a.boxctrl*4;a.box={a.x+C.impact_bbox[o+1],a.y+C.impact_bbox[o+2],a.x+C.impact_bbox[o+3],a.y+C.impact_bbox[o+4]}end
 return a
end
local function liveEnemies()
 local out={};for i=0,4 do local a=nativeEnemy(i);if a.flag>0 then out[#out+1]=a end end;return out
end
local function solid(c,x,y)
 local t=c.block(x,y)
 if t==0x5f or t==0x60 or t==0xc2 or t==0xc3 or t==0xc5 then return false end
 return(C.impact_attributes[t+1]&3)==1
end
local function alignedTarget(c)
 local a,v,g=r('RdAction'),r('RdVY'),r('RdGravity')
 if not(c.grounded and c.y>=168 and c.yHigh==1 and(a==0 or a==4 or(a==1 and g==0 and v<128))and(r('RdHeld')&128)==0)then return end
 local mx,my=pos('RdX','RdRoomHi')+8,r('RdY')-6
 for i=0,4 do local e=nativeEnemy(i);impact.seen[e.id]=e.flag>0 or impact.seen[e.id]
  if e.flag==1 and e.high==1 and e.state<32 and e.box and C.impact_eligible[e.id]and e.HP[1]>0 and e.hurt==0 then
   local gap=e.box[1]-mx
   if gap>=64 and gap<=144 and my+2>=e.box[2]and my-2<e.box[4]then
    local clear=true;for x=math.floor(mx/16)*16,e.box[1],16 do if solid(c,x,my)then clear=false end end
    if clear then return e end
   end
  end
 end
end
local function weaponReturned(n,p)
 if not attack.started then return end
 if n=='RdWxSpawn'and not attack.birth then
  local s=shot(p.weapon_slot);assert(s.action==11 and s.vx==4 and s.vy==0,'Real original missile11/VX4')
  assert(r('RdMissiles')==4 and r('RdMaxMissiles')==5 and r('RdMissileMode')==1 and attack.request and attack.ammo,'Real missile cost/request')
  attack.slot=p.weapon_slot;attack.birth={shot=s,player=state(),counts=attackCounts()};event('real-spawn',attack.birth)
 elseif n=='RdWxUpdateSlot'and attack.birth and p.weapon_slot==attack.slot then
  local s=shot(attack.slot);attack.slot_updates=attack.slot_updates+1
  if p.weapon_before.x~=s.x then attack.moves=attack.moves+1;assert(s.x==p.weapon_before.x+4,'Actual missile speed4')end
  if p.weapon_before.action~=4 and s.action==4 then impact.projectile_impact={before=p.weapon_before,after=s,player=state()};assert(s.anim==0x91,'Original missile impact animation91')end
  if p.weapon_before.action~=0 and s.action==0 and not attack.expiry then
   attack.expiry={before=p.weapon_before,after=s,counts=attackCounts(),player=state()};event('actual-removal',attack.expiry)
  end
 elseif n=='RdWxActorContact'and attack.birth and p.A==11 then
  local e=nativeEnemy(p.enemy_slot)
  assert(impact.target and p.enemy_slot==impact.target.slot and p.enemy_before.id==impact.target.id,'Actual selected native target fold11')
  if not impact.hit then
   assert(p.enemy_before.hurt==0 and p.enemy_before.HP[1]>0 and p.enemy_before.HP[2]==0,'Actual admitted source damage target')
   assert(e.HP[1]==p.enemy_before.HP[1]-1 and e.HP[2]==0,'Authorized missile damage exactly1')
   impact.hit={before=p.enemy_before,after=e,player=state(),shot=shot(attack.slot),counts=attackCounts(),folded_A=p.A}
   event('native-actor-damage1',impact.hit)
  end
 end
end
local function attackDrive()
 assert(active()and identity()and r('RdSourceAltPalette')==0 and r('NumberofLives')==2 and r('RdHealthLo')+r('RdHealthHi')>0,'Actual legal living missile approach')
 assert(r('RdTanks')==1 and r('RdGear')==0 and r('RdMaxMissiles')==5,'Earned MF inventory preserved')
 local c=context();local age=updates-attack.start;assert(age<1300,'Bounded one ordinary missile approach')
 if not impact.started then
  impact.started=true;impact.MF_baseline=attack.baseline;impact.initial_enemies=liveEnemies();impact.seen={};attack.phase='approach'
 end
 if attack.phase=='approach'then
  assert(c.world==0 and c.level==0 and c.x<2000,'No aligned live target on bounded ordinary approach')
  impact.last_scan={player=state(),enemies=liveEnemies()}
  local e=alignedTarget(c)
  if e then
   for _,i in ipairs({0xd0,0xe0,0xf0})do if r('RdWAction',i)~=0 then buttons={};return end end
   impact.target=e;impact.lock=state();attack.phase='release';impact.release=updates;buttons={};event('live-aligned-target',e);return
  end
  local action,g,v=r('RdAction'),r('RdGravity'),r('RdVY')
  local ready=c.grounded and(action==0 or action==4 or(action==1 and g==0 and v<128))
  buttons={right=true}
  if impact.gap then
   if v>=128 then impact.gap.admitted=true end
   buttons.a=not impact.gap.admitted or c.x<impact.gap.far
   if impact.gap.admitted and ready and c.x>=impact.gap.far then impact.gap=nil;buttons.a=false end
  elseif ready and c.y>=168 and not c.lastA then
   local feet=r('RdY')+r('RdRadiusY')+1
   if not solid(c,c.x+20,feet)then
    local far;for x=math.floor((c.x+20)/16)*16,c.x+144,16 do if solid(c,x,feet)then far=x;break end end
    assert(far,'Actual loaded far side of gap');impact.gap={far=far,requested=state()};buttons.a=true
   end
  end
 elseif attack.phase=='release'then
  buttons={};if updates-impact.release>=2 and(r('RdHeld')&96)==0 then attack.phase='select'end
 elseif attack.phase=='select'then
  buttons={select=true};if r('RdMissileMode')==1 then attack.phase='rearm';attack.rearm=updates end
 elseif attack.phase=='rearm'then
  buttons={};if updates-attack.rearm>=2 and(r('RdHeld')&96)==0 then attack.phase='fire'end
 elseif attack.phase=='fire'then
  buttons={b=true};if attack.birth then attack.phase='observe'end
 else buttons={}end
 if attack.expiry then
  local now=attackCounts();local enough=true;attack.postexpiry_entered={};attack.postexpiry_returned={}
  for n,v in pairs(now.entered)do local en=v-attack.expiry.counts.entered[n];local re=now.returned[n]-attack.expiry.counts.returned[n];attack.postexpiry_entered[n]=en;attack.postexpiry_returned[n]=re;if en<25 or re<25 then enough=false end end
  if enough then
   assert(#pending==0 and impact.hit and impact.projectile_impact and #impact.HP_writes>0,'Actual native enemy damage/impact/writer and completed work')
   assert(shot(attack.slot).action==0 and shot(attack.slot).frame==0xf7 and r('RdMissiles')==4,'Actual impact animation/removal and no extra fire')
   assert(attack.moves>0 and attack.calls.RdWxCell>0 and attack.calls.RdAnimateProjectile>0 and attack.calls.RdWpRender>0,'Real movement/cell/animation/render calls')
   attack.complete=true;finish('earned-missile-native-contact-and25workers')
  end
 end
end
