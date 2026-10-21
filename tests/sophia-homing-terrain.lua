-- Source homing missiles ignore all terrain. The actual Select-created shot
-- must never enter the shared terrain probe, even when it occupies slot9.
local frame,blocked=0,0
local seen,passed=false,false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
emu.addMemoryCallback(function()
 if frame>=550 and r('CurrentBank')%128==8 and r('MmBulletType')==72 then blocked=blocked+1 end
end,emu.callbackType.exec,L.Blocks)
emu.addEventCallback(function()
 emu.setInput({start=frame==240,down=frame==80,right=frame>=100 and frame<200 and(frame-100)%20==0,select=frame>=562 and frame<566},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
  for row=0,10 do w('Block_Buffer_1',0x54,row*16+8)end
  for i=0,5 do w('Enemy_Flag',0,i)end
  for i=0,9 do w('RgShotType',0,i)end
  w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1)
  w('PlayerStatus',1);w('InvOwnedLo',0x85,11);w('InvSelected',2,11);w('InvAmmo',20,178);w('InvPrevious',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_X_Position',220);w('Enemy_PageLoc',0);w('Enemy_Y_Position',176);w('Enemy_Y_HighPos',1)
  w('Enemy_BoundBoxCtrl',9);w('EnemyOffscrBitsMasked',0);w('MmEnemyHealthLo',255);w('MmEnemyHealthHi',127);w('AvStopwatch',200)
 end
 if frame>550 then
  for i=0,9 do if r('RgShotType',i)==45 then
   seen=true
   if r('RgShotX',i)+256*r('RgShotPage',i)>145 then passed=true end
  end end
 end
 if frame==660 then
  assert(seen,'Actual Select creates homing missile')
  assert(blocked==0,'Homing missiles must bypass terrain probes in every pool slot: '..blocked)
  assert(passed,'Homing missile crosses the solid wall toward its live target')
  print('PASS source homing ignores terrain; real slot9 missile crosses a protected solid wall without terrain probes');emu.stop(0)
 end
end,emu.eventType.endFrame)
