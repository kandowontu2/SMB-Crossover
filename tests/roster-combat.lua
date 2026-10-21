local frame=0
local character=assert(ROSTER_CHARACTER)
local enemyX=character==3 and 110 or 68
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
local function clearShots() for i=0,9 do w('RgShotType',0,i) end end
local function bullet()
 clearShots();w('RgShotType',1);w('RgShotX',110);w('RgShotPage',0);w('RgShotY',194);w('RgShotYHigh',1)
 w('RgShotVXHi',2);w('RgShotVXLo',213);w('RgShotVYHi',0);w('RgShotVYLo',0);w('RgShotDir',1);w('RgShotImpact',0);w('RgShotAge',0)
end
emu.addEventCallback(function()
 emu.setInput({right=frame>=80 and frame<80+20*character and (frame-80)%20==0,start=frame==200,
 b=frame==560 or frame==610 or frame==660 or frame==710 or (character~=3 and (frame==800 or frame==870 or frame==940))},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then
  for i=0,5 do w('Enemy_Flag',0,i) end
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
  w('Enemy_PageLoc',0);w('Enemy_Y_HighPos',1);w('MmEnemyHealthLo',100);w('MmEnemyHealthHi',0)
 end
 if frame>=550 and frame<750 and r('Enemy_State')<32 then
  w('Enemy_X_Position',enemyX);w('Enemy_Y_Position',168);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
 end
 if frame==595 or frame==640 then
  local count=frame==595 and 1 or 2
  assert((character==5 and count==2 and r('Enemy_State')>=32)or r('MmEnemyHealthLo')==math.max(0,100-count*({[3]=25,[4]=50,[5]=70})[character]),'Source weapon damage, one hit per swing/shot: '..r('MmEnemyHealthLo'))
 end
 if frame==745 then
  assert(r('Enemy_Flag')==0 or r('Enemy_State')>=32,'Repeated attacks defeat a 100-HP enemy')
  print('PASS guest '..character..' multi-hit health, damage values and one hit per melee swing')
 end
 if frame==790 then
  for i=0,5 do w('Enemy_Flag',0,i) end
  clearShots();w('Player_X_Position',88);w('Player_PageLoc',0);w('PlayerFacingDir',1)
  w('BlockBounceTimer',0);w('Block_Buffer_1',0x51,167);w('MmSolidTerrain',0,167)
 end
 if frame==800 and character==3 then bullet() end
 if frame==825 then
  if character==3 then assert(r('Block_Buffer_1',167)==0x51,'Bill normal bullets need two hits on a brick')
  else assert(r('Block_Buffer_1',167)~=0x51,'Sword/whip breaks a 34-HP brick') end
 end
 if frame==830 and character==3 then bullet() end
 if frame==840 then assert(r('Block_Buffer_1',167)~=0x51,'Brick destruction uses source weapon damage') end
 if frame==860 then clearShots();w('BlockBounceTimer',0);w('Block_Buffer_1',0xc0,167) end
 if frame==870 and character==3 then bullet() end
 if frame==905 then
  assert(r('Block_Buffer_1',167)~=0xc0 and r('CoinTallyFor1Ups')>0,'Weapon activates a question block and its reward')
  clearShots();w('BlockBounceTimer',0);w('Block_Buffer_1',0x54,167)
 end
 if frame==940 and character==3 then bullet() end
 if frame==975 then
  assert(r('Block_Buffer_1',167)==0x54,'Attacks cannot break ground')
  print('PASS guest '..character..' brick damage, question blocks/rewards and protected ground')
  clearShots();w('Player_Y_HighPos',2);w('Player_Y_Position',64);w('Player_State',2);w('Player_Y_Speed',4)
 end
 if frame==1400 then
  assert(r('SelectedCharacter')==character and r('NumberofLives')==1 and r('GameEngineSubroutine')==8,'Pit death loses one life and respawns the same character')
  print('PASS guest '..character..' pit death and character persistence');emu.stop(0)
 end
end,emu.eventType.endFrame)
