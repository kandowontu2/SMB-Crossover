-- Explicit native flat-room fixtures. Actual Select presses must not spend
-- homing ammo without the live on-screen target required by 2.02 Sophia.as.
local frame=0
local cases={'empty','defeated','flattened','live'}
local seen=false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function phase()return math.floor((frame-550)/80),(frame-550)%80 end
local function fixture(kind)
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('Player_Y_Speed',0);w('PlayerFacingDir',1);w('PlayerStatus',1)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('InvOwnedLo',0x85,11);w('InvSelected',2,11);w('InvAmmo',5,11*16+2);w('InvPrevious',0)
 w('RgPreviousButtons',0);w('GameEngineSubroutine',8);w('TimerControl',0);seen=false
 if kind~='empty' then
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',kind=='defeated'and 0x20 or kind=='flattened'and 2 or 0)
  w('Enemy_X_Position',190);w('Enemy_PageLoc',0);w('Enemy_Y_Position',176);w('Enemy_Y_HighPos',1)
  w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('Enemy_BoundBoxCtrl',9);w('EnemyOffscrBitsMasked',0)
  w('EnemyFrameTimer',255);w('MmEnemyHealthLo',100);w('MmEnemyHealthHi',0)
 end
end
emu.addEventCallback(function()
 local n,t=phase()
 emu.setInput({start=frame==60 or frame==240,down=frame==80,
  right=frame>=100 and frame<200 and(frame-100)%20==0,select=n>=0 and n<4 and t==12},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 local n,t=phase()
 if n==4 then print('PASS Sophia homing preserves ammo without a live target and launches at an eligible enemy');emu.stop(0);return end
 if t==0 then assert(r('SelectedCharacter')==11,'Real menu selects Sophia');fixture(cases[n+1])end
 for i=0,9 do if r('RgShotType',i)==45 then seen=true end end
 if t==25 then
  local valid=cases[n+1]=='live'
  assert(seen==valid,'Homing target eligibility: '..cases[n+1])
  assert(r('InvAmmo',11*16+2)==(valid and 4 or 5),'Homing ammunition: '..cases[n+1])
  assert(r('GameEngineSubroutine')==8,'Target handling preserves active gameplay')
 end
 if n==3 and t==30 then
  w('Enemy_Flag',0)
  for _,name in ipairs({'Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_Y_HighPos','Enemy_BoundBoxCtrl','EnemyOffscrBitsMasked','MmEnemyHealthLo','MmEnemyHealthHi'})do
   w(name,r(name),1)
  end
  w('Enemy_Flag',1,1);w('Enemy_State',0,1);w('Enemy_X_Position',210,1);w('Enemy_Y_Position',96,1)
 end
 if n==3 and t==36 then
  local found=false
  for i=0,9 do if r('RgShotType',i)==45 and r('SsMode',i)==1 then found=true end end
  assert(found,'Existing homing missile reacquires another live enemy')
  assert(r('InvAmmo',178)==4,'Retargeting does not spend extra ammo')
  w('Enemy_Flag',0,1)
 end
 if n==3 and t==43 then
  local found=false
  for i=0,9 do if r('RgShotType',i)==45 and r('SsMode',i)==255 then found=true end end
  assert(found,'Missile enters inactive expiry after losing all eligible targets')
 end
end,emu.eventType.endFrame)
