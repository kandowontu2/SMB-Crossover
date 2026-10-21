-- Explicit RAM arenas. Real controller B/Select shots exercise private source
-- death actors, both independent drop checks, saturation, and native Bowser.
local cases={
 {name='normal-immediate-only',power=0,early=0,late=1},
 {name='hyper-delayed-only',power=1,early=1,late=0},
 {name='crusher-both-rolls',power=2,early=0,late=0},
 {name='missile-neither-roll',weapon=1,early=1,late=1},
 {name='homing-both-rolls',weapon=2,early=0,late=0},
 {name='piranha-source-pivot',enemyID=13,early=0,late=0},
 {name='six-simultaneous',power=2,enemies=6,early=1,late=1},
 {name='all-ten-projectiles-occupied',power=2,fullpool=true,early=1,late=1},
 {name='genuine-saturation',saturated=true,early=1,late=1},
 {name='fake-bowser-native',bowser=true,world=0,early=0,late=0},
 {name='final-bowser-native',bowser=true,world=7,early=0,late=0},
}
local frame=0
local kills,points,bowser,early,late,created,maxActive,updates
local pending,returns=nil,{}
local defeatPending,defeatReturns=nil,{}
local life={}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function phase()return math.floor((frame-550)/200),(frame-550)%200 end
local depth=0
for _,pc in ipairs({L.NonMaskableInterrupt,L.IrqScrollSplit})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,pc)end
for _,pc in ipairs({L.NonMaskableInterrupt_RTI,L.IrqScrollSplit_RTI})do emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Balanced interrupt guards')end,emu.callbackType.exec,pc)end
local function valid(bank)
 local n,t=phase();return n>=0 and n<#cases and t>=0 and depth==0 and r('CurrentBank')%128==bank
end
local function fixture(c)
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('SophiaEffectAge',0,i);w('Enemy_State',0,i);w('MmEnemyHealthLo',0,i);w('MmEnemyHealthHi',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('InvDropKind',0,i)end
 w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('WorldNumber',c.world or 0)
 w('PlayerStatus',1);w('InvOwnedLo',c.power==2 and 0x97 or c.power==0 and 7 or 0x87,11);w('InvOwnedHi',0,11)
 w('InvSelected',c.weapon or 1,11);w('InvAmmo',60,177);w('InvAmmo',20,178);w('InvPrevious',0);w('RgPreviousButtons',0);w('RgCooldown',0)
 w('TimerControl',0);w('GameEngineSubroutine',8);w('AvStopwatch',255);w('SophiaDropBlocked',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,(c.enemies or 1)-1 do
  w('Enemy_Flag',1,i);w('Enemy_ID',c.bowser and 0x2d or c.enemyID or 6,i);w('Enemy_State',0,i)
  w('Enemy_X_Position',112,i);w('Enemy_PageLoc',0,i);w('Enemy_Y_Position',176,i);w('Enemy_Y_HighPos',1,i)
  if c.enemyID==13 then w('PiranhaPlantUpYPos',176,i);w('PiranhaPlantDownYPos',200,i)end
  w('Enemy_BoundBoxCtrl',9,i);w('EnemyOffscrBitsMasked',0,i);w('MmEnemyHealthLo',1,i);w('MmEnemyHealthHi',0,i)
 end
 -- Concurrent stress uses six live weapon actors within the independent caps:
 -- three cannons plus three standard missiles. Individual family cases above
 -- are created by real controller B/Select; no weapon gains piercing here.
 if c.enemies==6 then for i=0,5 do
  w('RgShotType',i<3 and 6 or 44,i);w('RgShotX',112,i);w('RgShotPage',0,i);w('RgShotY',195,i);w('RgShotYHigh',1,i);w('RgShotDir',1,i)
  w('RgShotAge',0,i);w('RgShotImpact',0,i);w('RgShotHits',0,i);w('SsMode',i<3 and 2 or 1,i);w('SsHitTimer',0,i)
  for _,name in ipairs({'RgShotVXLo','RgShotVXHi','RgShotVYLo','RgShotVYHi','RgShotFracX','RgShotFracY'})do w(name,0,i)end
 end end
 if c.bowser then w('BowserHitPoints',1);w('BowserFront_Offset',0)end
 kills=0;points=0;bowser=0;early=0;late=0;created=0;maxActive=0;updates=0;pending=nil;life={}
end
-- These outdoor collision arenas have no initialized native Bowser AI state.
-- Pin the isolated target at the weapon boundary until the real B shot lands;
-- its native defeat/victory handler itself remains untouched and executes fully.
emu.addMemoryCallback(function()
 local n=phase();local c=cases[n+1]
 if not valid(37)or not c.bowser or bowser~=0 then return end
 w('Enemy_Flag',1);w('Enemy_ID',0x2d);w('Enemy_State',0);w('EnemyOffscrBitsMasked',0)
 w('Enemy_X_Position',112);w('Enemy_PageLoc',0);w('Enemy_Y_Position',176);w('Enemy_Y_HighPos',1)
 w('MmEnemyHealthLo',1);w('MmEnemyHealthHi',0)
end,emu.callbackType.exec,assert(L.ExpandedWeapons))
emu.addMemoryCallback(function()
 if not valid(59)then return end
 local n=phase();kills=kills+1
 if cases[n+1].saturated and kills==1 then for i=0,5 do w('SophiaEffectAge',i+1,i);w('SophiaEffectX',180+i*8,i);w('SophiaEffectPage',0,i);w('SophiaEffectY',96,i);w('SophiaEffectYHigh',1,i)end end
 local x=emu.getState()['cpu.x'];assert(r('Enemy_Flag',x)~=0,'Source explosion starts from a live target')
 local st=emu.getState();local sp=st['cpu.sp'];local original,shots={},{}
 for i=0,9 do original[i]=r('RgShotType',i)end
 if cases[n+1].fullpool then
  local free={};for i=0,9 do if original[i]==0 then free[#free+1]=i end end
  for j,i in ipairs(free)do w('RgShotType',j<=2 and 6 or j<=5 and 44 or 45,i)end
 end
 for i=0,9 do shots[i]=r('RgShotType',i)end
 local pc=emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1
 defeatPending={sp=sp,x=x,shots=shots,original=original,full=cases[n+1].fullpool}
 if defeatReturns[pc]then return end
 defeatReturns[pc]=true
 emu.addMemoryCallback(function()
  if not defeatPending or not valid(59)or emu.getState()['cpu.sp']~=defeatPending.sp+2 then return end
  local p=defeatPending;defeatPending=nil
  assert(r('Enemy_Flag',p.x)==0 and r('EnemyMetasprite',p.x)==0,'Source removes the enemy and its queued native metasprite immediately')
  for i=0,9 do assert(r('RgShotType',i)==p.shots[i],'Private explosion allocation preserves every occupied projectile slot')end
  if p.full then for i=0,9 do w('RgShotType',p.original[i],i)end end
 end,emu.callbackType.exec,pc)
end,emu.callbackType.exec,assert(L.SophiaDefeatEnemy))
emu.addMemoryCallback(function()
 if valid(59)then bowser=bowser+1 end
end,emu.callbackType.exec,assert(L.SophiaDefeatBowser))
local dropPending,dropReturns=nil,{}
local function dropOrigin(point)
 local st=emu.getState();local sp=st['cpu.sp'];local x=st['cpu.x'];local expected={}
 if point then
  expected.x=r('SophiaEffectX',x)+256*r('SophiaEffectPage',x)
  expected.y=(r('SophiaEffectY',x)+8)%256
 else
  expected.x=r('Enemy_X_Position',x)+256*r('Enemy_PageLoc',x)+8
  expected.y=(r('Enemy_ID',x)==13 and r('PiranhaPlantUpYPos',x)+16 or r('Enemy_Y_Position',x)+24)%256
 end
 local before={};for i=0,3 do before[i]=r('InvDropKind',i)end
 local pc=emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1
 dropPending={sp=sp,before=before,expected=expected}
 if dropReturns[pc]then return end
 dropReturns[pc]=true
 emu.addMemoryCallback(function()
  if not dropPending or not valid(59)or emu.getState()['cpu.sp']~=dropPending.sp+2 then return end
  local p=dropPending;dropPending=nil
  for i=0,3 do if p.before[i]==0 and r('InvDropKind',i)~=0 then
   assert(r('InvDropX',i)+256*r('InvDropPage',i)==p.expected.x,'Source pickup centers on saved enemy/effect world X')
   assert(r('InvDropY',i)==p.expected.y,'Source pickup bottom pivot equals center plus half-height (Piranha uses raised bottom minus half-height)')
  end end
 end,emu.callbackType.exec,pc)
end
emu.addMemoryCallback(function()
 local n=phase();if not valid(59)then return end
 dropOrigin(false)
 early=early+1;w('PseudoRandomBitReg',cases[n+1].early,1);w('PseudoRandomBitReg',0,2)
end,emu.callbackType.exec,assert(L.InventoryEnemyDrop))
emu.addMemoryCallback(function()
 local n=phase();if not valid(59)then return end
 dropOrigin(true)
 late=late+1;w('PseudoRandomBitReg',cases[n+1].late,1);w('PseudoRandomBitReg',0,2)
end,emu.callbackType.exec,assert(L.InventoryDropPoint))
for i=0,3 do emu.addMemoryCallback(function(_,v)
 if valid(59)and v>0 and r('InvDropKind',i)==0 then created=created+1 end
end,emu.callbackType.write,assert(L.InvDropKind)+i)end
emu.addMemoryCallback(function()
 if not valid(59)then return end
 updates=updates+1
 local st=emu.getState();local sp=st['cpu.sp'];local before={}
 for i=0,5 do before[i]=r('SophiaEffectAge',i)end
 local pc=emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1
 pending={sp=sp,before=before}
 if returns[pc]then return end
 returns[pc]=true
 emu.addMemoryCallback(function()
  if not pending or not valid(59)or emu.getState()['cpu.sp']~=pending.sp+2 then return end
  local p=pending;pending=nil
  for i=0,5 do
   local expected=p.before[i]==0 and 0 or p.before[i]==128 and 1 or p.before[i]==12 and 0 or p.before[i]+1
   assert(r('SophiaEffectAge',i)==expected,'Exactly two native updates per source frame, slot '..i)
   if p.before[i]~=0 then life[i]=(life[i]or 0)+1 end
  end
 end,emu.callbackType.exec,pc)
end,emu.callbackType.exec,assert(L.SophiaUpdateEffects))
emu.addEventCallback(function()
 local n,t=phase();local c=cases[n+1]
 emu.setInput({start=frame==240,down=frame==80,right=frame>=100 and frame<200 and(frame-100)%20==0,
  b=c and not c.weapon and t>=12 and t<16,select=c and c.weapon and t>=12 and t<16},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<550 then return end
 local n,t=phase();local c=cases[n+1]
 if not c then print('PASS Sophia source enemy explosions: real five weapon families, six concurrent actors, both independent drop rolls, bounded saturation and native fake/final Bowser');emu.stop(0);return end
 if t==0 then assert(r('SelectedCharacter')==11,'Real menu selected Sophia');fixture(c)end
 w('AvStopwatch',255)
 local active=0;for i=0,5 do if r('SophiaEffectAge',i)~=0 then active=active+1 end end
 maxActive=math.max(maxActive,active)
 if t==170 then
  if c.bowser then
   assert(bowser==1 and kills==0 and maxActive==0,'Native Bowser defeat bypasses source effect in '..c.name)
   assert(early==0 and late==0 and created==0,'Bowser dropsItems=false in '..c.name)
   assert(r('SophiaDropBlocked')==0,'Bowser drop suppression clears after native sequence')
  else
   assert(kills==(c.enemies or 1),'Real controller weapon defeats targets in '..c.name..', got '..kills)
   assert(maxActive==(c.saturated and 6 or c.enemies or 1),'Private effect count in '..c.name..', got '..maxActive)
   assert(early==kills,'Immediate source drop check once per target in '..c.name)
   assert(late==(c.saturated and 7 or kills),'Independent expiry/saturation source drop checks in '..c.name..', got '..late)
   if not c.saturated then
    for _,count in pairs(life)do assert(count==13,'Newborn plus twelve visible updates in '..c.name..', got '..count)end
    local expected=(c.early==0 and 1 or 0)+(c.late==0 and 1 or 0)
    assert(created==expected,'Independent immediate/expiry drop outcomes in '..c.name..', got '..created)
   end
   for i=0,5 do assert(r('SophiaEffectAge',i)==0,'Effect pool expires cleanly')end
  end
 end
end,emu.eventType.endFrame)
