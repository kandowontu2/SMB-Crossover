-- Recover the same naturally earned Goomba power, then use it on the route.
local recovery = {}
charge.recovery = recovery

local function drop()
 return {kind=r('KbDropKind'), age=r('KbDropAge'),
  x=256*r('KbDropPage')+r('KbDropX'), y=r('KbDropY'), vy=r('KbDropVY')}
end

local function recoveryPad()
 if not charge.swallowed or recovery.restored then return nil end
 if recovery.recovered then return {down=true} end
 if recovery.bounced then return {b=true} end
 if recovery.spawned then return {} end
 if r('KbAction')~=0 or r('Player_State')~=0 then return {} end
 return {select=true}
end

hook('dropCopy',function()
 if recovery.pressed or not charge.swallowed then return end
 assert(r('KbFresh')&32~=0 and r('SavedJoypadBits')&32~=0 and r('KbCopy')==1
  and r('KbDropKind')==0 and r('KbMouth')==0 and r('Player_State')==0,
  'Actual fresh Select discards the natural ground charge from the floor')
 recovery.pressed=player()
end)

hook('weaponDone',function()
 if not recovery.pressed or recovery.restored then return end
 local s=drop()
 if not recovery.spawned then
  assert(s.kind==1 and s.age==1 and s.vy==254 and s.x==x() and r('KbCopy')==0
   and s.y==r('Player_Y_Position')+20,'The discarded charge is a separate live copy star')
  recovery.spawned=s
 elseif not recovery.bounced then
  assert(s.kind==1 and s.y<=200 and r('KbCopy')==0 and s.age<64,
   'Copy star stays above native ground during its first bounce')
  if s.age>8 and s.vy==254 then
   assert(recovery.approach and recovery.approach.vy<128 and s.y==200
    and s.x>recovery.spawned.x,'The descending copy star genuinely bounces off the ground')
   recovery.bounced=s
  end
  recovery.approach=s
 elseif not recovery.recovered and s.kind==0 then
  assert(r('SavedJoypadBits')&64~=0 and r('KbCopy')==0 and r('KbMouth')==255
   and r('KbMouthCopy')==1,'Inhaling the copy star recovers the same Goomba in Kirby’s mouth')
  recovery.recovered=player()
 elseif recovery.recovered and r('KbCopy')==1 then
  assert(r('SavedJoypadBits')&4~=0 and r('KbMouth')==0 and r('KbAction')==3
   and r('KbHealth')==6,'Swallowing restores the earned ability without changing health')
  recovery.restored=player()
 end
end)
