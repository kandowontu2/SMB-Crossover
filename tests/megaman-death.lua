local frame=0
local diedAt
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
emu.addEventCallback(function()
  emu.setInput({right=frame==80,start=frame==120},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
  frame=frame+1
  if frame==490 then for i=0,5 do w('Enemy_Flag',0,i) end end
  if frame==500 then
    w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0)
    w('Enemy_X_Position',r('Player_X_Position'));w('Enemy_PageLoc',r('Player_PageLoc'))
    w('Enemy_Y_Position',184);w('Enemy_Y_HighPos',1)
    w('Enemy_BoundBoxCtrl',9);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
  end
  if frame>500 and not diedAt and r('MmDeathFlag')~=0 then diedAt=frame end
  if diedAt and frame==diedAt+32 then
    assert(r('MmDeathPit')==0,'Enemy contact starts the normal death burst')
    assert(r('ObjectMetasprite')==0,'Death burst replaces the character sprite')
    assert(r('PlayerChrBank')==0x90,'Particles use the hosted particle CHR bank')
    local f=assert(io.open(OUTPUT..ROM_NAME..'-megaman-death.png','wb'));f:write(emu.takeScreenshot());f:close()
  end
  if diedAt and frame==diedAt+167 then
    assert(r('NumberofLives')==2,'Lives are retained until the 300 ms separation plus 2500 ms delay ends')
  end
  if diedAt and frame==diedAt+171 then
    assert(r('NumberofLives')==1,'Death subtracts one life after the delay')
    print('PASS normal death burst, original particle art and source death timers')
  end
  if frame==1100 then
    assert(diedAt,'Contact killed helmetless Mega Man')
    assert(r('GameEngineSubroutine')==8 and r('Player_Y_HighPos')==1,'Death restarts the level')
    assert(r('SelectedCharacter')==1 and r('MmDeathFlag')==0,'Restart keeps selection and clears death state')
    print('PASS death state resets on respawn')
    emu.stop(0)
  end
end,emu.eventType.endFrame)
