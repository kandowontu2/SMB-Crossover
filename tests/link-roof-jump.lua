-- Isolated movement arena, not a stage clear: real Link A input jumps from
-- a Y96 support toward the Y32 castle roof. No CPU/ROM/save-state patches.
local frame,minY,jumped,roofStop=0,255,false,false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local log=assert(io.open(OUTPUT..ROM_NAME..'-link-roof-jump.csv','w'))
log:write('frame,y,state,vy,headY\n')
emu.addEventCallback(function()
 emu.setInput({right=frame==100 or frame==120 or frame==140 or frame==160,start=frame==240,a=frame>=620 and frame<650},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if frame>=620 and frame<660 and r('SelectedCharacter')==4 and r('Player_Y_Position')<32 and r('Player_Y_Speed')==1 then roofStop=true end
end,emu.callbackType.exec,L.DoFootCheck)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=600 then for i=0,5 do w('Enemy_Flag',0,i)end end
 if frame==600 then
  assert(r('SelectedCharacter')==4 and r('GameEngineSubroutine')==8,'Actual menu starts Link')
  for i=0,415 do w('Block_Buffer_1',0,i)end
  for page=0,1 do for col=0,15 do
   w('Block_Buffer_1',0x61,page*208+col)
   w('Block_Buffer_1',0x61,page*208+64+col)
  end end
  w('Player_X_Position',80);w('Player_PageLoc',0);w('Player_Y_Position',64);w('Player_Y_HighPos',1)
  w('Player_State',0);w('Player_Y_Speed',0);w('Player_X_Speed',0)
  w('PlayerStatus',0);w('PlayerSize',0);w('PlayerFacingDir',1)
  w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
  w('RgAttack',0);w('RgThrust',0);w('CrouchingFlag',0);w('DisableCollisionDet',0);w('BlockBounceTimer',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 end
 if frame>=620 and frame<=710 then
  local y=r('Player_Y_Position');minY=math.min(minY,y)
  if r('Player_Y_Speed')>=128 then jumped=true end
  log:write(table.concat({frame,y,r('Player_State'),r('Player_Y_Speed'),y+17},',')..'\n');log:flush()
  assert(r('Player_Y_HighPos')==1 and y+17>=32,'Link cannot cross above the solid castle roof with a controller jump; y='..y)
 end
 if frame==710 then
  assert(jumped and minY<32,'Actual A jump exercises the formerly skipped head window')
  assert(roofStop,'Native collision actually cancels upward motion below canonicalY32')
  assert(r('Player_Y_Position')==64 and r('Player_State')==0,'Link lands back on the original support')
  log:close();print('PASS actual Link controller jump stops beneath castle roof and returns to support, minY='..minY);emu.stop(0)
 end
end,emu.eventType.endFrame)
