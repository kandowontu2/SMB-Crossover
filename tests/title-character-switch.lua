local frame=0
local smallMario=assert(L.METASPRITE_SMALL_MARIO_STANDING,'Small Mario sprite ID is available from debug symbols')
local function r(name) return emu.read(assert(L[name],name),emu.memType.nesDebug) end
local function screenshot(tag)
  local file=assert(io.open(OUTPUT..ROM_NAME..'-'..tag..'.png','wb'))
  file:write(emu.takeScreenshot());file:close()
end
emu.addEventCallback(function()
  emu.setInput({left=frame==110 or frame==520,right=frame==80 or frame==230 or frame==550 or(frame>=140 and frame<=470 and (frame-140)%30==0 and frame~=230),
    start=frame==600},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
  frame=frame+1
  if frame==70 then
    assert(r('SelectedCharacter')==0 and r('PlayerSize')==1,'Title starts with small Mario')
  end
  local expected=({[100]=1,[160]=1,[190]=2,[220]=3,[250]=4,[280]=5,[310]=6,[340]=7,[370]=12,[400]=9,[430]=10,[460]=11,[490]=0,[540]=11,[570]=0})[frame]
  if expected then assert(r('SelectedCharacter')==expected,'Twelve-character roster at '..frame) end
  if frame==125 or frame==490 or frame==570 then
    assert(r('SelectedCharacter')==0 and r('PlayerStatus')==0,'Title returns to unpowered Mario')
    assert(r('PlayerSize')==1 and r('ObjectMetasprite')==smallMario,'Mario restores his small standing form')
    screenshot('title-mario-restored')
  end
  if frame==1050 then
    assert(r('OperMode')==1 and r('GameEngineSubroutine')==8,'Starting Mario after switching reaches gameplay')
    assert(r('SelectedCharacter')==0 and r('PlayerStatus')==0 and r('PlayerSize')==1,'Mario starts the level small after repeated switches')
    screenshot('mario-start-after-switching')
    print('PASS repeated left/right and Select switches restore small Mario on character selection and at game start')
    emu.stop(0)
  end
end,emu.eventType.endFrame)
