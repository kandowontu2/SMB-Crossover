-- Explicit1-2 geometry fixture. Initial world/player setup only; ordinary
-- A/B/Right thereafter must open both brick columns without a powerup grant.
local frame=0
local debris=false
local reward=false
local escaped=false
local log=assert(io.open(OUTPUT..ROM_NAME..'-scrooge-underhang.csv','w'))
log:write('frame,x,y,state,attack,probe_y,roof6,mid6,low6,roof7,mid7,low7\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
emu.addMemoryCallback(function(_,v)if frame>=640 and v~=0 then debris=true end end,emu.callbackType.write,L.Block_State,L.Block_State+1)
emu.addMemoryCallback(function(_,v)if frame>=1140 and v==0x2e then reward=true end end,emu.callbackType.write,L.Enemy_ID,L.Enemy_ID+5)
emu.addEventCallback(function()
 local age=(frame-640)%80
 if frame>=640 and frame<1120 and(r('Player_PageLoc')>0 or r('Player_X_Position')>=144)then escaped=true end
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or(frame>=640 and frame<1120 and not escaped),start=frame==200,
  a=frame>=640 and frame<1120 and not escaped and age<20,b=(frame>=640 and frame<1120 and not escaped and age>=4 and age<8)or(frame>=1140 and frame<1144)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=640 and frame<=1120 then
  log:write(table.concat({frame,r('Player_X_Position'),r('Player_Y_Position'),r('Player_State'),r('ScAttack'),r('MmBulletY'),r('Block_Buffer_1',118),r('Block_Buffer_1',134),r('Block_Buffer_1',150),r('Block_Buffer_1',119),r('Block_Buffer_1',135),r('Block_Buffer_1',151)},',')..'\n')
 end
 if frame==620 then
  assert(r('SelectedCharacter')==12 and r('GameEngineSubroutine')==8,'Scrooge enters underhang fixture')
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
  for p=0,1 do for c=0,15 do w('Block_Buffer_1',0x54,p*208+176+c);w('MmSolidTerrain',1,p*208+176+c)end end
  for col=4,5 do w('Block_Buffer_1',0x52,112+col)end
  for col=6,7 do for row=112,144,16 do w('Block_Buffer_1',0x52,row+col)end end
  for i=0,5 do w('Enemy_Flag',0,i)end
  for i=0,1 do w('Block_State',0,i);w('Block_RepFlag',0,i);w('BlockMetasprite',0,i)end
  w('Player_X_Position',80);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
  w('Player_State',0);w('Player_Y_Speed',0);w('Player_X_Speed',0);w('PlayerFacingDir',1)
  w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
  w('PlayerStatus',0);w('ScPogo',0);w('ScAttack',0);w('ScPrevious',0);w('RgPreviousButtons',0)
  w('TimerControl',0);w('InjuryTimer',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 end
 if frame==1120 then
  log:flush()
  assert(r('Player_PageLoc')>0 or r('Player_X_Position')>=136,'Unpowered cane jump opens both adjacent underhang columns; x='..r('Player_X_Position'))
  assert(debris and r('PlayerStatus')==0,'Real cane brick fragments occur without granting a mushroom')
  for p=0,1 do for c=0,15 do assert(r('Block_Buffer_1',p*208+176+c)==0x54,'The entire protected foundation survives')end end
  assert(r('GameEngineSubroutine')==8,'Underhang escape remains playable')
  print('PASS Scrooge unpowered two-column underhang escape with controller cane jumps, debris and protected ground')
 end
 if frame==1140 then
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
  for p=0,1 do for c=0,15 do w('Block_Buffer_1',0x54,p*208+176+c);w('MmSolidTerrain',1,p*208+176+c)end end
  for i=0,5 do w('Enemy_Flag',0,i)end
  for i=0,1 do w('Block_State',0,i);w('Block_RepFlag',0,i);w('BlockMetasprite',0,i)end
  w('Block_Buffer_1',0xc1,151);w('Block_Buffer_1',0x52,167)
  w('Player_X_Position',96);w('Player_PageLoc',0);w('Player_Y_Position',170);w('Player_Y_HighPos',1)
  w('Player_State',1);w('Player_Y_Speed',0);w('Player_X_Speed',0);w('PlayerFacingDir',1)
  w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
  w('PlayerStatus',0);w('ScPogo',0);w('ScAttack',0);w('ScPrevious',0);w('RgPreviousButtons',0);w('BlockBounceTimer',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 end
 if frame==1240 then
  assert(r('Block_Buffer_1',167)~=0x52,'Lower cane endpoint breaks the ordinary brick')
  assert(r('Block_Buffer_1',151)==0xc4 and reward,'Upper endpoint activates the adjacent question and preserves its used block and real reward')
  for p=0,1 do for c=0,15 do assert(r('Block_Buffer_1',p*208+176+c)==0x54,'Band attack preserves protected foundation')end end
  print('PASS Scrooge cane vertical band preserves stacked question reward/used block while breaking its adjacent brick');log:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
