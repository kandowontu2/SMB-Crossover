-- Explicit upgraded-Sophia arena. The only in-flight write is one emulated
-- controller-latch receipt at the real pre-input boundary. No PC/register/ROM
-- or projectile/enemy patch is used to manufacture the new cannon/hit.
local frame,depth,injected,slot,prepared,hit=0,0,false,nil,0,false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function bank(n)return depth==0 and r('CurrentBank')%128==n end
for _,pc in ipairs({assert(L.NonMaskableInterrupt),assert(L.IrqScrollSplit)})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,pc)end
for _,pc in ipairs({assert(L.NonMaskableInterrupt_RTI),assert(L.IrqScrollSplit_RTI)})do emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Balanced late-receipt interrupts')end,emu.callbackType.exec,pc)end
emu.addMemoryCallback(function()
 if frame<550 or injected or not bank(37)then return end
 assert(r('A_B_Buttons')&0x40==0 and r('SavedJoypadBits')&0x40==0 and r('RgPreviousButtons')&0x40==0,'No B receipt exists at the original parsed-input cache gate')
 for i=0,9 do assert(r('RgShotType',i)==0,'Actual initial projectile pool is empty')end
 w('SavedJoypadBits',0x40);injected=true
 print('LATE RECEIPT: native expanded batch parsedB0; one rawB latch receipt before source fresh-input capture')
end,emu.callbackType.exec,assert(L.SophiaCandidatesReady))
emu.addMemoryCallback(function()
 if injected and bank(8)then prepared=prepared+1 end
end,emu.callbackType.exec,assert(L.GuestPrepareEnemies))
emu.addMemoryCallback(function(address,value)
 if not injected or not bank(37)or value~=6 then return end
 slot=address-L.RgShotType
 print('LATE RECEIPT: actual new cannon slot'..slot..' cachedTier'..r('RgAttackPower')..' preparations'..prepared)
end,emu.callbackType.write,assert(L.RgShotType),L.RgShotType+9)
emu.addMemoryCallback(function(address,value)
 if slot==nil or address-L.SsMode~=slot or not bank(37)then return end
 assert(value==2,'A late source B receipt creates the acquired Hyper cannon tier2, not stale cached tier'..value)
end,emu.callbackType.write,assert(L.SsMode),L.SsMode+9)
emu.addMemoryCallback(function()
 if injected and slot~=nil and bank(37)then
  assert(prepared>0,'Actual newly created cannon has a fresh enemy batch before its collision pass')
 end
end,emu.callbackType.exec,assert(L.ExpandedWeaponsFinish))
emu.addMemoryCallback(function(_,value)
 if injected and slot~=nil and bank(8)and value~=500%256 then
  assert(prepared>0,'Actual late-input cannon damage uses freshly prepared candidates')
  hit=true
 end
end,emu.callbackType.write,assert(L.MmEnemyHealthLo))
emu.addEventCallback(function()emu.setInput({start=frame==60 or frame==240,down=frame==80,right=frame>=100 and frame<200 and frame%20==0},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then
  assert(r('SelectedCharacter')==11 and r('GameEngineSubroutine')==8,'Real menu launches late-receipt source arena')
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
  for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_State',0,i);w('AvFrozen',0,i);w('AvFrozenHi',0,i);w('RgEnemyStun',0,i)end
  for i=0,9 do w('RgShotType',0,i)end
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  for _,n in ipairs({'TimerControl','InjuryTimer','GuestHurtKind','GuestHurtTicks','GuestInvulTicks','GuestPowerupActive','RgAttack','RgAttackPower','RgCooldown','RgCrouch','CrouchingFlag','AvStopwatch','XgWall','XgCeiling','RgPreviousButtons','SavedJoypadBits','A_B_Buttons','PreviousA_B_Buttons','InvFresh'})do w(n,0)end
  w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1);w('PlayerStatus',1);w('Player_CollisionBits',3)
  w('InvOwnedLo',0x91,11);w('InvOwnedHi',0,11);w('InvSelected',0,11)
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_X_Position',96);w('Enemy_PageLoc',0);w('Enemy_Y_Position',184);w('Enemy_Y_HighPos',1);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('Enemy_BoundBoxCtrl',9);w('EnemyOffscrBitsMasked',0);w('Enemy_CollisionBits',0)
  w('MmEnemyHealthLo',500%256);w('MmEnemyHealthHi',1);w('GuestEnemyMask',0);w('RgEnemiesPresent',0)
  w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0);w('HorizontalScroll',0);w('ScrollLock',1);w('EnemyObjectPageLoc',255);w('AreaParserTaskNum',0);w('ScrollThirtyTwo',0)
 end
 if hit then assert(slot~=nil and injected,'A genuine source input created the damaging Hyper cannon');print('PASS late rawB receipt: correct source Hyper tier, fresh native enemy candidates and actual cannon damage');emu.stop(0)end
 assert(frame<800,'Actual late-input cannon reaches its target')
end,emu.eventType.endFrame)
