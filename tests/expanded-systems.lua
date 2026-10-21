-- Explicit setup in the real 2-2 room: water physics, actual controller
-- attacks against native enemies/blocks, protected terrain and death/respawn.
local c=assert(EXPANDED_CHARACTER)
-- Rygar's original standing hand is higher than the other guests' weapons.
local targetBlock=c==7 and 151 or 167
local frame,audioChecks,writes=0,0,0
local before
local fields={'Player_X_Position','Player_Y_Position','Player_State','SelectedCharacter','GameEngineSubroutine','R0','R1','R2','R3','R4','R5','R6','R7'}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
local function velocity(n)local v=r(n)+256*r(n,1)+65536*r(n,2);if v>=0x800000 then v=v-0x1000000 end;return v/65536 end
local function shots()for i=0,9 do w('RgShotType',0,i) end end
local function player(y,state)
 w('Player_X_Position',40);w('Player_PageLoc',0);w('Player_Y_Position',y);w('Player_Y_HighPos',1);w('Player_State',state);w('Player_Y_Speed',0);w('PlayerFacingDir',1)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i) end
 w('MmXFraction',0);w('MmXFraction',0,1);w('MmYFraction',0);w('MmYFraction',0,1)
 w('XgJumpUsed',0);w('XgDash',0);w('XgRise',0);w('XgWallContact',0);w('XgWall',0);w('XgCeiling',0);w('XgHoverActive',0)
end
local function block(tile,terrain)
 for i=0,5 do w('Enemy_Flag',0,i) end
 for i=0,415 do w('Block_Buffer_1',0,i);w('RgMeleeBlocks',0,i) end
 for col=0,15 do w('Block_Buffer_1',0x54,176+col) end
 for i=0,1 do w('Block_State',0,i);w('Block_RepFlag',0,i);w('BlockMetasprite',0,i) end
 w('Block_Buffer_1',tile,targetBlock);w('MmSolidTerrain',terrain or 0,targetBlock);w('MmBrickHealth',0,targetBlock);w('BlockBounceTimer',0)
 w('RgAttack',0);w('RgCooldown',0);shots();player(176,0);w('Player_X_Position',88)
end
emu.addMemoryCallback(function()writes=writes+1 end,emu.callbackType.write,0x4000,0x400f)
emu.addMemoryCallback(function()
 if frame<550 then return end
 before={};for _,n in ipairs(fields) do before[n]=r(n) end
end,emu.callbackType.exec,L.AudioUpdate)
emu.addMemoryCallback(function()
 if not before then return end
 for _,n in ipairs(fields) do assert(r(n)==before[n],'Added-character audio must preserve interrupted '..n) end
 audioChecks=audioChecks+1;before=nil
end,emu.callbackType.exec,L.ExitNMI)
emu.addEventCallback(function()
 emu.setInput({select=c==8 and frame==180,down=c~=8 and frame==80,right=(c~=8 and frame>=100 and frame<100+20*(c-6) and (frame-100)%20==0) or (frame>=560 and frame<600),start=frame==200,
 a=frame==620 or (frame>=660 and frame<680),b=(frame>=750 and frame<954 and (frame-750)%40<4)
 or(frame>=1010 and frame<1014)or(frame>=1040 and frame<1044)
 or(frame>=1090 and frame<1094)or(frame>=1120 and frame<1124)
 or(frame>=1190 and frame<1194)or(frame>=1220 and frame<1224)
 or(frame>=1270 and frame<1274)or(frame>=1300 and frame<1304)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==199 then w('WorldNumber',1);w('LevelNumber',1);w('AreaNumber',2) end
 if frame>=540 and frame<730 then for i=0,5 do w('Enemy_Flag',0,i);w('Whirlpool_PageLoc',0,i) end end
 if frame==550 then
  assert(r('SelectedCharacter')==c and r('AreaType')==0 and r('SwimmingFlag')==1,'Actual 2-2 room starts with selected added character')
  player(176,0)
 end
 if frame==599 then assert(math.abs(velocity('MmVX')-.75)<.002,'Water walking caps at .75 NES px/frame') end
 if frame==620 then player(100,1) end
 if frame==621 then
  if c==8 or c==9 then assert(velocity('MmVY')< -1,'Luigi paddles; Bass can use his second jump underwater')
  elseif c==11 then assert(math.abs(velocity('MmVY'))<.002,'Sophia drifts in water without a free mid-water jump')
  else assert(velocity('MmVY')>0,'Guest cannot jump freely in mid-water') end
 end
 if frame==660 then player(176,0) end
 if frame==661 then
  local jump=({[6]=500,[7]=660,[8]=200,[9]=500,[10]=400,[11]=400})[c]/120
  local gravity=({[6]=400,[7]=500,[8]=350,[9]=500,[10]=500,[11]=400})[c]/7200
  if c==11 then gravity=0 end -- setJumpRise(true) defies gravity.
  assert(math.abs(velocity('MmVY')-(-jump+gravity))<.003,'Character-specific underwater jump and gravity: '..velocity('MmVY')..' / '..(-jump+gravity))
  print('PASS added character '..c..' real water room, ground speed, paddle/double-jump rules and water trajectory')
 end
 if frame==730 then
  player(176,0);shots();w('PlayerStatus',2)
  for i=0,5 do w('Enemy_Flag',0,i) end
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9);w('Enemy_PageLoc',0);w('Enemy_Y_HighPos',1)
  w('MmEnemyHealthLo',0);w('MmEnemyHealthHi',0)
 end
 if frame>=730 and frame<970 and r('Enemy_Flag')>0 and r('Enemy_State')<32 then
  w('Enemy_X_Position',c==10 and 72 or 110);w('Enemy_Y_Position',c==8 and 184 or 176);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
 end
 if frame==970 then
  assert(r('Enemy_Flag')==0 or r('Enemy_State')>=32,'Actual controller attacks defeat a native Goomba with shared enemy health: '..r('MmEnemyHealthLo'))
  print('PASS added character '..c..' actual primary attacks and native enemy defeat')
 end
 if frame==1000 then block(0x51) end
 if frame==1080 then
  assert((r('Block_Buffer_1',targetBlock)==0x51)==(c==8),'Only Luigi fireballs leave bricks intact')
  block(0xc0)
 end
 if frame==1180 then
  assert((r('Block_Buffer_1',targetBlock)==0xc0)==(c==8),'Question block activation follows character weapon rules')
  block(0x54)
 end
 if frame==1260 then assert(r('Block_Buffer_1',targetBlock)==0x54,'Weapons preserve ground');block(0x52,1) end
 if frame==1340 then
  assert(r('Block_Buffer_1',targetBlock)==0x52,'Weapons preserve underground terrain sharing a brick metatile')
  assert(audioChecks>700 and writes>500,'Native APU audio and interrupt preservation exercised: checks='..audioChecks..' writes='..writes..' character='..r('SelectedCharacter')..' song='..r('XgAudioSong')..' event='..r('XgAudioEvent')..' engine='..r('GameEngineSubroutine'))
  if c~=8 then assert(r('XgAudioSong')>0,'Character-specific native stage music is active') end
  print('PASS added character '..c..' brick/question/terrain rules, native APU writes and NMI state preservation')
  shots();w('Player_Y_HighPos',2);w('Player_Y_Position',64);w('Player_State',2);w('Player_Y_Speed',4)
 end
 -- Native Mario-style pit death falls to YHigh6 before its life/lives-screen
 -- transition. Independent Mario/Luigi 2-2 controls take643/647 frames.
 if frame==(c==8 and 2100 or 1800) then
  assert(r('SelectedCharacter')==c and r('NumberofLives')==1 and r('GameEngineSubroutine')==8,'Death respawns the same added character')
  print('PASS added character '..c..' death, life deduction, native music restart and respawn');emu.stop(0)
 end
end,emu.eventType.endFrame)
