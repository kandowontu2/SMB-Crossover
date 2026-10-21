-- Explicit collision arena, not a manufactured stage clear. Link2.02
-- hitEnemy1040..1058 does not allow an unprotected ordinary foot stomp.
local frame,depth=0,0
local contact,checked=false,false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
for _,pc in ipairs({assert(L.NonMaskableInterrupt),assert(L.IrqScrollSplit)})do
 emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,pc)
end
for _,pc in ipairs({assert(L.NonMaskableInterrupt_RTI),assert(L.IrqScrollSplit_RTI)})do
 emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Balanced Link body fixture interrupt scope')end,emu.callbackType.exec,pc)
end
emu.addEventCallback(function()
 emu.setInput({right=frame>=80 and frame<160 and(frame-80)%20==0,start=frame==200},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if frame>=560 and depth==0 and r('CurrentBank')%128==0 and r('ObjectOffset')==0 then contact=true end
end,emu.callbackType.exec,L.HandlePECollisions)
emu.addMemoryCallback(function()
 if not contact or checked or depth~=0 then return end
 assert(emu.read(L.NoDecTimers,emu.memType.nesDebug)==0xe6 and emu.read(L.NoDecTimers+1,emu.memType.nesDebug)==L.FrameCounter,'Actual completed foreground contact boundary')
 checked=true
 assert(r('GameEngineSubroutine')==8 and r('TimerControl')==0 and r('GuestHurtKind')==4 and r('GuestHurtTicks')>0 and r('PlayerStatus')==0,'Unprotected Link foot contact must damage Link, not perform a native stomp: engine'..r('GameEngineSubroutine')..' enemyState'..r('Enemy_State'))
 assert(r('Enemy_Flag')==1 and r('Enemy_State')<2 and r('MmEnemyHealthLo')==100 and r('MmEnemyHealthHi')==0,'Unprotected contact cannot defeat/damage the enemy or bypass source HP')
 print('PASS actual unprotected Link2.02 foot collision damages the player and preserves the enemy; star/shell/thrust exceptions need their separate fixtures');emu.stop(0)
end,emu.callbackType.exec,L.NoDecTimers)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then assert(r('SelectedCharacter')==4 and r('GameEngineSubroutine')==8,'Real menu launches Link before the isolated body-contact arena')end
 if frame==560 then
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,page*208+176+col)end end
  for i=0,5 do w('Enemy_Flag',0,i)end
  for i=0,9 do w('RgShotType',0,i)end
  w('AreaType',1);w('SwimmingFlag',0);w('TimerControl',0);w('GameEngineSubroutine',8)
  w('Player_X_Position',128);w('Player_PageLoc',0);w('Player_Y_Position',146);w('Player_Y_HighPos',1)
  w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0);w('HorizontalScroll',0)
  w('Player_State',2);w('Player_X_Speed',0);w('Player_Y_Speed',2);w('PlayerStatus',1);w('PlayerSize',0)
  w('StarInvincibleTimer',0);w('InjuryTimer',0);w('StompTimer',0);w('GuestPowerupActive',0)
  w('RgAttack',0);w('RgThrust',0);w('RgThrustReset',0);w('RgCrouch',0);w('CrouchingFlag',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  w('MmVY',2,2);w('MmFrictionYActive',0)
  for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9);w('Enemy_CollisionBits',0)
  w('Enemy_X_Position',128);w('Enemy_PageLoc',0);w('Enemy_Y_Position',176);w('Enemy_Y_HighPos',1)
  w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('EnemyOffscrBitsMasked',0)
  w('MmEnemyHealthLo',100);w('MmEnemyHealthHi',0)
 end
 if frame>700 then assert(false,'A real ordinary foot collision must occur before body-fixture watchdog')end
end,emu.eventType.endFrame)
