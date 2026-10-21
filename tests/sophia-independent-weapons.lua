-- Explicit empty-room fixtures with actual B/Select input. Cannon and missile
-- pools must remain independent; Select+B cannot create legacy free missiles.
local frame=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function phase()return math.floor((frame-550)/100),(frame-550)%100 end
local peaks={}
local function fixture(n)
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('Player_Y_Speed',0);w('PlayerFacingDir',1);w('PlayerStatus',1)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('InvOwnedLo',n==0 and 0x81 or n==1 and 0x83 or 0x85,11);w('InvSelected',n==2 and 2 or 1,11)
 w('InvAmmo',20,177);w('InvAmmo',20,178);w('InvPrevious',0);w('RgPreviousButtons',0);w('RgCooldown',0)
 w('GameEngineSubroutine',8);w('TimerControl',0);peaks[n+1]={cannon=0,missile=0}
 if n==2 then
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_X_Position',220);w('Enemy_PageLoc',0)
  w('Enemy_Y_Position',96);w('Enemy_Y_HighPos',1);w('Enemy_BoundBoxCtrl',9);w('EnemyOffscrBitsMasked',0)
  w('MmEnemyHealthLo',255);w('MmEnemyHealthHi',127);w('AvStopwatch',200)
 end
end
emu.addEventCallback(function()
 local n,t=phase()
 local press=(t>=12 and t<15)or(t>=24 and t<27)or(t>=36 and t<39)or(t>=48 and t<51)
 emu.setInput({start=frame==240,down=frame==80,right=frame>=100 and frame<200 and(frame-100)%20==0,
  b=n>=0 and n<3 and press,select=n>=0 and n<3 and((t>=12 and t<15)or(n==2 and press))},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<550 then return end
 local n,t=phase()
 if n==3 then print('PASS Sophia independent three-cannon/missile pools and no legacy free Select+B missiles');emu.stop(0);return end
 if t==0 then assert(r('SelectedCharacter')==11,'Menu selects Sophia');fixture(n)end
 local cannon,missile=0,0
 for i=0,9 do
  local kind=r('RgShotType',i)
  assert(kind~=7,'Select+B cannot create obsolete unmetered missile')
  if kind==6 then cannon=cannon+1 elseif kind==44 or kind==45 then missile=missile+1 end
 end
 peaks[n+1].cannon=math.max(peaks[n+1].cannon,cannon);peaks[n+1].missile=math.max(peaks[n+1].missile,missile)
 if t==85 then
  assert(peaks[n+1].cannon==3,'Three cannons remain available with missiles: '..n..' / '..peaks[n+1].cannon)
  assert(peaks[n+1].missile==(n==0 and 0 or n==1 and 3 or 4),'Independent missile limit: '..n)
  assert(r('InvAmmo',177)==(n==1 and 17 or 20),'Standard volley spends exactly three')
  assert(r('InvAmmo',178)==(n==2 and 16 or 20),'Homing shots spend one each')
 end
end,emu.eventType.endFrame)
