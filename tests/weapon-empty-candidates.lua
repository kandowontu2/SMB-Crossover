-- Explicit six-Goomba arena. Ordinary neutral/Right inputs, empty weapon pools;
-- the source gates may omit cache preparation only when it has no consumer.
local char=assert(EMPTY_CANDIDATE_CHARACTER)
local frame,depth,updates,calls,armed=0,0,0,0,false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
for _,pc in ipairs({assert(L.NonMaskableInterrupt),assert(L.IrqScrollSplit)})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,pc)end
for _,pc in ipairs({assert(L.NonMaskableInterrupt_RTI),assert(L.IrqScrollSplit_RTI)})do emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Balanced empty-candidate interrupts')end,emu.callbackType.exec,pc)end
emu.addMemoryCallback(function()
 if frame>=550 and depth==0 then calls=0;armed=true end
end,emu.callbackType.exec,assert(L.NoDecTimers))
emu.addMemoryCallback(function()
 if armed and depth==0 and r('CurrentBank')%128==8 then calls=calls+1 end
end,emu.callbackType.exec,assert(L.GuestPrepareEnemies))
emu.addMemoryCallback(function(address,value)
 local slot=address-L.Enemy_Flag
 if frame>=550 and value==0 and r('Enemy_Flag',slot)~=0 then
  print('EMPTY ACTOR CLEAR slot'..slot..' pc'..emu.getState()['cpu.pc']..' bank'..r('CurrentBank')..' y'..r('Enemy_Y_Position',slot)..' high'..r('Enemy_Y_HighPos',slot)..' x'..r('Enemy_X_Position',slot)..' page'..r('Enemy_PageLoc',slot)..' left'..r('ScreenLeft_PageLoc')..':'..r('ScreenLeft_X_Pos')..' right'..r('ScreenRight_PageLoc')..':'..r('ScreenRight_X_Pos'))
 end
end,emu.callbackType.write,assert(L.Enemy_Flag),L.Enemy_Flag+5)
emu.addMemoryCallback(function()
 if not armed or depth~=0 then return end
 assert(calls==0,'Empty pools without attack input do not prepare enemy candidates: c'..char..' calls'..calls)
 assert(r('GameEngineSubroutine')==8 and r('TimerControl')==0 and r('InjuryTimer')==0,'Empty-cache control keeps ordinary gameplay live')
 for i=0,5 do assert(r('Enemy_Flag',i)==1 and r('Enemy_ID',i)==6,'Every native enemy remains live and processed: slot'..i..' flag'..r('Enemy_Flag',i)..' id'..r('Enemy_ID',i)..' playerX'..r('Player_X_Position')..' enemyX'..r('Enemy_X_Position',i))end
 for i=0,9 do assert(r('RgShotType',i)==0,'No inventory projectile was silently introduced')end
 for i=0,2 do assert(r('SmShotType',i)==0 and r('SmBombAge',i)==0,'No Samus primary/bomb consumer exists')end
 updates=updates+1;armed=false
 if updates==48 then print('PASS empty primary/inventory pools c'..char..':48 complete native six-enemy updates and neutral/Right input, zero candidate scans, no attack/injury/script pause');emu.stop(0)end
end,emu.callbackType.exec,assert(L.PauseSkip)+2)
emu.addEventCallback(function()
 local choose=char<6 and frame>=80 and frame<80+20*char and frame%20==0 or char>=6 and frame>=100 and frame<100+20*(char-6)and frame%20==0
 emu.setInput({start=frame==60 or frame==240,right=choose or updates>=24,down=char>=6 and frame==80},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then
  assert(r('SelectedCharacter')==char and r('GameEngineSubroutine')==8,'Real menu launches empty-cache character')
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
  for i=0,5 do
   for _,n in ipairs({'Enemy_State','Enemy_X_Speed','Enemy_Y_Speed','Enemy_X_MoveForce','Enemy_Y_MoveForce','Enemy_CollisionBits','EnemyOffscrBitsMasked','AvFrozen','AvFrozenHi','RgEnemyStun'})do w(n,0,i)end
   w('Enemy_Flag',1,i);w('Enemy_ID',6,i);w('Enemy_BoundBoxCtrl',9,i);w('Enemy_MovingDir',1,i);w('Enemy_PageLoc',1,i);w('Enemy_X_Position',88+24*i,i);w('Enemy_Y_Position',184,i);w('Enemy_Y_HighPos',1,i);w('Enemy_X_Speed',8,i)
  end
  for i=0,9 do w('RgShotType',0,i)end
  for i=0,3 do w('MmBulletType',0,i)end
  for i=0,2 do w('SmShotType',0,i);w('SmBombAge',0,i);w('MmVX',0,i);w('MmVY',0,i)end
  for _,n in ipairs({'InjuryTimer','TimerControl','GuestHurtKind','GuestHurtTicks','GuestInvulTicks','GuestPowerupActive','StarInvincibleTimer','RgAttack','RgThrust','RgCrouch','CrouchingFlag','SmBall','SmCrouch','SmFlip','MmSliding','AvSlash','AvStopwatch','XgWall','Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','A_B_Buttons','PreviousA_B_Buttons','SavedJoypadBits','RgPreviousButtons','InvFresh'})do w(n,0)end
  w('Player_X_Position',8);w('Player_PageLoc',1);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('Player_CollisionBits',3);w('PlayerFacingDir',1)
  w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',1);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',1);w('ScrollLock',1);w('HorizontalScroll',0);w('AreaParserTaskNum',0);w('ScrollThirtyTwo',0);w('EnemyObjectPageLoc',255);w('EnemyFrenzyBuffer',0);w('EnemyFrenzyQueue',0);w('PlayerOutlinesOff',1);w('FrameCounter',0)
 end
 assert(frame<900,'Bounded empty-candidate control completes')
end,emu.eventType.endFrame)
