-- Explicit durable-enemy arena. Three ordinary controller swings must each
-- damage the same native enemy; repeated active frames must not multiply hits.
local frame=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120,start=frame==200,
  b=(frame>=640 and frame<644)or(frame>=680 and frame<684)or(frame>=720 and frame<724)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==620 then
  assert(r('SelectedCharacter')==12,'Scrooge is selected')
  for i=0,415 do w('Block_Buffer_1',0,i)end
  for p=0,1 do for c=0,15 do w('Block_Buffer_1',0x54,p*208+176+c)end end
  for i=0,5 do w('Enemy_Flag',0,i);w('MmEnemyFlash',0,i)end
  w('Player_X_Position',96);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
  w('Player_State',0);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('PlayerFacingDir',1)
  w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
  w('ScAttack',0);w('ScPogo',0);w('ScPrevious',0);w('SmBombHits',0);w('SmSlot',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
  w('Enemy_X_Position',128);w('Enemy_PageLoc',0);w('Enemy_Y_Position',192);w('Enemy_Y_HighPos',1)
  w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('MmEnemyHealthLo',44);w('MmEnemyHealthHi',1)
 end
 if frame>=620 and frame<750 and r('Enemy_Flag')>0 and r('Enemy_State')<32 then
  w('Enemy_X_Position',128);w('Enemy_Y_Position',192);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
 end
 if frame==665 then
  assert(r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')==200,'First cane swing does exactly 100 damage once')
  print('PASS Scrooge first swing does one hit despite consecutive active frames')
 end
 if frame==705 then
  assert(r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')==100,'Second cane swing damages an already-hit enemy again')
  print('PASS Scrooge new swing resets the per-attack enemy hit mask')
 end
 if frame==755 then
  assert(r('Enemy_Flag')==0 or r('Enemy_State')>=32,'Third swing defeats the durable native enemy')
  assert(r('GameEngineSubroutine')==8,'Cane enemy arena remains playable')
  print('PASS Scrooge repeated independent cane attacks defeat a multi-hit enemy');emu.stop(0)
 end
end,emu.eventType.endFrame)
