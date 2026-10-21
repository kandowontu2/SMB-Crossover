-- Actual native enemy contact starts death; only the arena/enemy are fixtures.
local c=assert(DEATH_CHARACTER)
local frame,start,landed,xstart,ystart=0,nil,nil,nil,nil
local moved,rose=false,false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
emu.addEventCallback(function()
 emu.setInput({right=frame>=80 and frame<80+20*c and (frame-80)%20==0,start=frame==240},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then
  assert(r('SelectedCharacter')==c,'Death fixture character')
  for i=0,415 do w('Block_Buffer_1',0,i) end
  for col=0,15 do w('Block_Buffer_1',0x54,176+col) end
  for i=0,5 do w('Enemy_Flag',0,i) end
  w('Player_X_Position',120);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
  w('Player_State',0);w('PlayerStatus',0);w('InjuryTimer',0);w('StarInvincibleTimer',0);w('PlayerFacingDir',1)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i) end
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_PageLoc',0);w('Enemy_X_Position',120)
  w('Enemy_Y_Position',184);w('Enemy_Y_HighPos',1);w('Enemy_BoundBoxCtrl',9);w('Enemy_X_Speed',0)
 end
 if frame>550 and not start and r('GameEngineSubroutine')==11 then
  start=frame;xstart=r('Player_X_Position');ystart=r('Player_Y_Position')
 end
 if start then
  for i=0,5 do w('Enemy_Flag',0,i) end
  if c~=4 then
   moved=moved or r('Player_X_Position')<xstart-5
   rose=rose or r('Player_Y_Position')<ystart-5
   if not landed and r('RgDeathLanded')~=0 then
    landed=frame
    assert(moved and rose,'Corpse moves backward and rises before landing')
    assert(r('Player_Y_Position')==176,'Corpse lands on the actual logical floor')
   end
  end
  if r('GameEngineSubroutine')==6 then
   assert(r('ObjectMetasprite')==0,'The live body cannot reappear on the life-loss transition')
   if c==4 then assert(frame-start==219,'Link completes flash, wait, spin, gray, cross and 650ms delay')
   else assert(landed and frame-landed==(c==3 and 90 or 130),'Death delay begins on landing') end
   print('PASS character '..c..' normal death from native enemy contact, source animation phases and landing-dependent delay');emu.stop(0)
  end
 end
 if frame==1100 then assert(false,'Normal death failed to finish') end
end,emu.eventType.endFrame)
