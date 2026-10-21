-- Explicit isolated pickup/combat fixtures, not a controller-only level clear.
-- Native collision handlers collect the mushroom/flower; all shots use B.
local frame=0
local sfx,pickupSfx=0,0
local livesBefore
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
local function player()
 w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('PlayerFacingDir',1)
end
local function pickup(kind)
 w('Enemy_Flag',1,5);w('Enemy_ID',0x2e,5);w('Enemy_State',0x80,5)
 w('PowerUpType',kind,5);w('Enemy_BoundBoxCtrl',3,5)
 w('Enemy_X_Position',r('Player_X_Position'),5);w('Enemy_PageLoc',0,5)
 w('Enemy_Y_Position',184,5);w('Enemy_Y_HighPos',1,5);w('Enemy_X_Speed',0,5);w('Enemy_Y_Speed',0,5)
end
local function count()local n=0;for i=0,1 do if r('Fireball_State',i)~=0 then n=n+1 end end;return n end
emu.addMemoryCallback(function(_,v)if frame>=1000 and(v&0x20)~=0 then sfx=sfx+1 end end,
 emu.callbackType.write,L.Square1SoundQueue)
emu.addMemoryCallback(function(_,v)if(v&0x20)~=0 then pickupSfx=pickupSfx+1 end end,
 emu.callbackType.write,L.Square2SoundQueue)
emu.addEventCallback(function()
 emu.setInput({start=frame==200,b=frame==1060 or frame==1062 or(frame>=1064 and frame<1069)
  or(frame>=1150 and frame<1250 and(frame-1150)%24<4)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=540 and frame<550 then for i=0,5 do w('Enemy_Flag',0,i)end end
 if frame==550 then
  assert(r('SelectedCharacter')==0 and r('GameEngineSubroutine')==8,'Native Mario starts normally')
  player()
 end
 if frame==560 then pickup(0)end
 if frame==730 then assert(r('PlayerStatus')==1 and r('PlayerSize')==0 and r('GameEngineSubroutine')==8,'Real mushroom collision finishes native growth')end
 if frame==740 then pickup(1)end
 if frame==1000 then assert(r('PlayerStatus')==2 and r('PlayerSize')==0 and r('GameEngineSubroutine')==8,'Real flower collision finishes native fire transition');player()end
 if frame==1061 then assert(count()==1,'First fresh B creates a native fireball')end
 if frame==1063 then assert(count()==2,'Second fresh B creates the second fireball')end
 if frame==1065 or frame==1068 then assert(count()==2,'Third fresh B and held B respect the native two-fireball pool')end
 if frame==1140 then
  assert(sfx>=2,'Native fireball sound is queued for actual shots')
  for i=0,1 do w('Fireball_State',0,i)end
  for i=0,5 do w('Enemy_Flag',0,i)end
  player();w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
  w('Enemy_PageLoc',0);w('Enemy_Y_HighPos',1)
 end
 if frame>=1140 and frame<1250 and r('Enemy_Flag')~=0 and r('Enemy_State')<32 then
  w('Enemy_X_Position',110);w('Enemy_Y_Position',184);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
 end
 if frame==1250 then
  assert(r('Enemy_Flag')==0 or r('Enemy_State')>=32,'Controller-fired native Mario fireballs defeat the Goomba')
  assert(r('GameEngineSubroutine')==8,'Mario remains active after native upgrades and combat')
  for i=0,5 do w('Enemy_Flag',0,i)end
  player();pickup(2)
 end
 if frame==1270 then assert(r('StarInvincibleTimer')>0,'Real star collision enables native invincibility')end
 if frame==1280 then livesBefore=r('NumberofLives');pickup(3)end
 if frame==1430 then
  assert(r('NumberofLives')==livesBefore+1,'Real green mushroom awards one life through native floating-score processing')
  assert(pickupSfx>=4,'All four real pickup kinds queue their native pickup sound')
  print('PASS Mario real mushroom/flower/star/1-up effects, fresh-B native fireball pool, fire/pickup SFX and Goomba defeat')
  emu.stop(0)
 end
end,emu.eventType.endFrame)
