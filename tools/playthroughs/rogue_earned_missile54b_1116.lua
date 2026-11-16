-- Additive ordinary-input attack phase AFTER all frozen MF credit/+25 gates.
local function shot(i)return {slot=i,action=r('RdWAction',i),x=pos('RdWX','RdWHi',i),y=r('RdWY',i),
 vx=r('RdWVX',i),vy=r('RdWVY',i),age=r('RdWAge',i),frame=r('RdWFrame',i),onScreen=r('RdWOnScreen',i)}end
local function attackCounts()return {entered=snapshot('_entered'),returned=snapshot('_returned')}end
local function event(kind,row)if #attack.events<8 then attack.events[#attack.events+1]={kind=kind,Main=updates,row=row}end end
local function weaponReturned(n,p)
 if not attack.started then return end
 if n=='RdWxSpawn'and not attack.birth then
  local s=shot(p.weapon_slot);assert(s.action==11 and s.vx==4 and s.vy==0,'Original actual missile11/VX4')
  assert(r('RdMissiles')==4 and r('RdMaxMissiles')==5 and r('RdMissileMode')==1,'Actual one missile cost')
  assert(attack.request and attack.ammo,'Actual original request20 and ammo writer')
  attack.slot=p.weapon_slot;attack.birth={shot=s,player=state(),counts=attackCounts()};event('real-spawn',attack.birth)
 elseif n=='RdWxUpdateSlot'and attack.birth and p.weapon_slot==attack.slot then
  local after=shot(attack.slot);attack.slot_updates=attack.slot_updates+1
  if p.weapon_before.x~=after.x then attack.moves=attack.moves+1;assert(after.x==p.weapon_before.x+4,'Actual source horizontal missile speed4')end
  if p.weapon_before.action==11 and after.action==0 then
   assert(after.onScreen==0 and not attack.expiry,'Actual offscreen source expiry')
   attack.expiry={before=p.weapon_before,after=after,counts=attackCounts(),player=state()};event('offscreen-expiry',attack.expiry)
  end
 end
end
local function attackDrive()
 assert(active()and identity()and r('RdSourceAltPalette')==0 and r('NumberofLives')==2,'Actual admitted source attack')
 assert(r('RdTanks')==1 and r('RdGear')==0 and r('RdMaxMissiles')==5,'Earned inventory preserved')
 assert(r('RdHealthLo')==attack.baseline.health_raw[1]and r('RdHealthHi')==attack.baseline.health_raw[2],'Captured actual HP preserved during stationary attack')
 local age=updates-attack.start;assert(age<180,'Bounded real missile lifetime')
 if attack.phase=='release'then
  buttons={};if age>=2 and(r('RdHeld')&96)==0 then attack.phase='select'end
 elseif attack.phase=='select'then
  buttons={select=true};if r('RdMissileMode')==1 then attack.phase='rearm';attack.rearm=updates end
 elseif attack.phase=='rearm'then
  buttons={};if updates-attack.rearm>=2 and(r('RdHeld')&96)==0 then attack.phase='fire'end
 elseif attack.phase=='fire'then
  buttons={b=true};if attack.birth then attack.phase='observe'end
 else buttons={}end
 if attack.expiry then
  local now=attackCounts();local enough=true
  attack.postexpiry_entered={};attack.postexpiry_returned={};attack.postbirth_returned={}
  for name,value in pairs(now.entered)do
   local e=value-attack.expiry.counts.entered[name];local ret=now.returned[name]-attack.expiry.counts.returned[name]
   attack.postexpiry_entered[name]=e;attack.postexpiry_returned[name]=ret
   attack.postbirth_returned[name]=now.returned[name]-attack.birth.counts.returned[name]
   if e<25 or ret<25 then enough=false end
  end
  if enough then
   assert(#pending==0 and attack.moves>0 and attack.calls.RdWxCell>0 and attack.calls.RdAnimateProjectile>0 and attack.calls.RdWpRender>0,'Actual movement/cell/animation/render and completed returns')
   assert(r('RdMissiles')==4 and shot(attack.slot).action==0,'No extra firing or stale projectile')
   attack.complete=true;finish('earned-missile-motion-expiry-and25workers')
  end
 end
end
