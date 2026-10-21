-- Source pressAtkBtn has a projectile limit, not an eight-update fire delay.
-- An empty arena is a fixture; every shot comes from actual controller input.
local frame=0
local c=assert(EXPANDED_CHARACTER)
local limit=c==11 and 3 or 2
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
local function count()
 local n=0
 for i=0,9 do if r('RgShotType',i)~=0 then n=n+1 end end
 return n
end
emu.addEventCallback(function()
 emu.setInput({start=frame==60 or frame==200,select=c==8 and frame==180,down=c~=8 and frame==80,
  right=c~=8 and frame>=100 and frame<100+20*(c-6) and (frame-100)%20==0,
  b=frame==560 or frame==562 or (frame>=564 and frame<569)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=540 and frame<550 then for i=0,5 do w('Enemy_Flag',0,i) end end
 if frame==550 then
  assert(r('SelectedCharacter')==c and r('GameEngineSubroutine')==8,'Character entered active level')
  w('PlayerStatus',c==8 and 2 or 0);w('Player_X_Position',64);w('Player_PageLoc',0)
  w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1)
 end
 if frame==561 then assert(count()==1,'First fresh press fires immediately') end
 if frame==563 then assert(count()==2,'Second fresh press fires after only two updates') end
 if frame==565 then assert(count()==limit,'Third fresh press obeys the source projectile limit') end
 if frame==568 then
  assert(count()==limit,'Holding B does not create automatic shots')
  print('PASS fresh attack presses, source projectile pool and no invented fire delay for character '..c)
  emu.stop(0)
 end
end,emu.eventType.endFrame)
