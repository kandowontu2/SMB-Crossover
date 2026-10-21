-- Explicit collision arena, not a level clear. A real ordinary jump approaches
-- a64px rise, six pixels beyond Scrooge's measured58px ordinary jump.
-- Terrain/player are initialized once; only ordinary A/Right follow.
local frame=0
local entered=false
local maxX=0
local out=assert(io.open(OUTPUT..ROM_NAME..'-scrooge-ledge-corner.csv','w'))
out:write('frame,x,y,state,vx,vy\n')
local function r(n,i)return emu.read(L[n]+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(L[n]+(i or 0),v%256,emu.memType.nesDebug)end
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or(frame>=640 and frame<740),start=frame==200,a=frame>=640 and frame<680},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==620 then
  assert(r('SelectedCharacter')==12 and r('GameEngineSubroutine')==8,'Scrooge enters ledge-corner fixture')
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for page=0,1 do for row=6,12 do for col=0,15 do
   local off=page*208+row*16+col;w('Block_Buffer_1',0x54,off);w('MmSolidTerrain',1,off)
  end end end
  for row=2,5 do for col=8,11 do w('Block_Buffer_1',0x54,row*16+col);w('MmSolidTerrain',1,row*16+col)end end
  for i=0,5 do w('Enemy_Flag',0,i)end
  w('Player_X_Position',80);w('Player_PageLoc',0);w('Player_Y_Position',96);w('Player_Y_HighPos',1)
  w('Player_State',0);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('PlayerFacingDir',1)
  w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
  w('PlayerStatus',0);w('ScPogo',0);w('ScAttack',0);w('ScPrevious',0);w('RgPreviousButtons',0);w('TimerControl',0);w('InjuryTimer',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 end
 if frame>=640 and frame<=740 then
  local x=r('Player_X_Position')+256*r('Player_PageLoc')
  maxX=math.max(maxX,x)
  if x>=128 and r('Player_Y_Position')>32 and r('Player_Y_Position')<128 then entered=true end
  out:write(table.concat({frame,x,r('Player_Y_Position'),r('Player_State'),r('Player_X_Speed'),r('Player_Y_Speed')},',')..'\n')
 end
 if frame==740 then
  assert(not entered,'Ordinary58px jump must not enter the solid64px ledge; maximumX='..maxX)
  assert(r('GameEngineSubroutine')==8,'Corner contact remains playable')
  print('PASS Scrooge ordinary jump respects64px ledge without phasing through lower-side corner')
 end
 if frame==780 then
  -- Exact relative corner state seen in the genuine1-3 trace at8133:
  -- lower-right foot has entered the ledge, horizontal velocity is zero.
  -- This recovery fixture is initialized explicitly; it is not a clear proof.
  w('Player_X_Position',127);w('Player_Y_Position',42);w('Player_Y_HighPos',1)
  w('Player_State',1);w('Player_X_Speed',0);w('Player_Y_Speed',1)
  w('Player_MovingDir',2);w('PlayerFacingDir',2)
  w('ScPogo',0);w('ScAttack',0);w('ScPrevious',0);w('RgPreviousButtons',0);w('XgRise',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  w('MmVY',1,2)
  for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 end
 if frame>=780 and frame<=820 then
  out:write(table.concat({frame,r('Player_X_Position'),r('Player_Y_Position'),r('Player_State'),r('Player_X_Speed'),r('Player_Y_Speed')},',')..'\n')
 end
 if frame==820 then
  out:close()
  assert(r('Player_X_Position')<=128,'A stationary recorded corner contact must not eject across the entire solid ledge; X='..r('Player_X_Position'))
  print('PASS Scrooge stationary recorded corner contact preserves local separation instead of repeated16px traversal');emu.stop(0)
 end
end,emu.eventType.endFrame)
