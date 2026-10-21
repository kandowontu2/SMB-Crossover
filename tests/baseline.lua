local frame=0
local startX=nil
local function r(name) return emu.read(assert(L[name],name),emu.memType.nesDebug) end
emu.addEventCallback(function()
  emu.setInput({start=frame==120,right=frame>=500 and frame<530},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
  frame=frame+1
  if frame==480 then
    assert(r('OperMode')==1,'Reached gameplay from the title screen')
    assert(r('GameEngineSubroutine')==8,'Player control is active')
    startX=r('Player_X_Position')
    local file=assert(io.open(OUTPUT..ROM_NAME..'-gameplay.png','wb'))
    file:write(emu.takeScreenshot());file:close()
  end
  if frame==535 then
    assert(r('Player_X_Position')>startX,'Controller input moves the player')
    assert(r('Player_State')==0,'Player remains on the ground')
    print('PASS boot, title, level load, player control, floor collision')
    emu.stop(0)
  end
end,emu.eventType.endFrame)
