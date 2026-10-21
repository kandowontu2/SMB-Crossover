-- Controller-only front-end flow, including idle time beyond the old demo.
local frame=0
local titleCore,demos=0,0
local startX
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function shot(tag)
 local f=assert(io.open(OUTPUT..ROM_NAME..'-select-'..tag..'.png','wb'))
 f:write(emu.takeScreenshot());f:close()
end
emu.addMemoryCallback(function() if r('OperMode')==0 then titleCore=titleCore+1 end end,emu.callbackType.exec,L.GameCoreRoutine)
emu.addMemoryCallback(function() demos=demos+1 end,emu.callbackType.exec,L.DemoEngine)
emu.addEventCallback(function()
 emu.setInput({start=(frame>=900 and frame<930) or (frame>=1420 and frame<1440),
  right=frame==80 or (frame>=945 and frame<=1165 and (frame-945)%20==0) or frame==1320 or frame==1460 or frame==1480 or frame==1500 or (frame>=1900 and frame<1920),
  left=frame==1220 or frame==1300,down=frame==1240,up=frame==1260,select=frame==1280,
  b=frame==1340,a=frame==1540},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=60 and frame<=890 then
  assert(r('OperMode')==0 and r('CrossoverMenuState')==0,'Title remains static before Start')
  assert(r('SelectedCharacter')==0,'Directions cannot choose a character on the title')
  assert(r('Sprite0HitDetectFlag')==0,'Static front end has no gameplay HUD IRQ')
  for offset=0,255,4 do assert(r('Sprite_Y_Position',offset)>=240,'Title has no Mario or demo sprites') end
 end
 if frame==800 then
  assert(r('CrossoverBehaviorVersion')==0 and r('PlayerOutlinesOff')==1,'Real power-on defaults are behavior1.0 and shadows OFF')
  shot('title')
 end
 if frame==931 then assert(r('OperMode')==0 and r('CrossoverMenuState')==2,'Holding opening Start cannot launch the game') end
 if frame>=955 and frame<=1175 and (frame-955)%20==0 then
  local character=math.floor((frame-955)/20+1)%12
  assert(r('SelectedCharacter')==({[8]=12})[character] or (character~=8 and r('SelectedCharacter')==character),'All twelve choices wrap left/right')
  assert(r('AreaChrBank')==0x3c,'Dedicated background CHR is active')
  local cursor=0x2000+(character<6 and 11 or 17)*32+2+(character%6)*5
  assert(emu.read(cursor,emu.memType.nesPpuDebug)==0x3f,'Arrow highlights the selected portrait in either row')
  for i=0,11 do
   local visibleTiles=0
   for y=0,4 do for x=0,3 do
    if emu.read(0x2000+(6+math.floor(i/6)*6+y)*32+1+(i%6)*5+x,emu.memType.nesPpuDebug)~=0x24 then visibleTiles=visibleTiles+1 end
   end end
   assert(visibleTiles>0,'All twelve background portraits are present')
  end
  local visible=0
  for offset=0,255,4 do if r('Sprite_Y_Position',offset)<240 then visible=visible+1 end end
  assert(visible>0 and visible<=16,'Selected character has a complete private preview')
  assert(r('PlayerStatus')==0 and r('PlayerSize')==1,'Browsing does not grant Mario a mushroom')
  shot(tostring(character))
 end
 local expected=({[1230]=11,[1250]=5,[1270]=11,[1290]=0,[1310]=11,[1330]=0})[frame]
 if expected then assert(r('SelectedCharacter')==expected,'Directional/Select navigation wraps predictably') end
 if frame==1250 then assert(r('CrossoverOptionsFocus')==0 and r('CrossoverMenuState')==2,'Down changes roster rows; the character grid has no Options focus')end
 if frame==1270 then
  assert(r('CrossoverOptionsFocus')==0 and r('CrossoverMenuState')==2,'Up returns to the other roster row')
  for x=0,31 do assert(emu.read(0x2340+x,emu.memType.nesPpuDebug)==0x24,'Old outline option row is absent from character select')end
 end
 if frame==1410 then
  assert(r('OperMode')==0 and r('CrossoverMenuState')==0,'B returns to the static title')
  shot('back')
 end
 if frame==1520 then assert(r('SelectedCharacter')==3 and r('CrossoverMenuState')==2,'Reopened menu selects Bill');shot('bill') end
 if frame==1900 then
  assert(r('SelectedCharacter')==3 and r('OperMode')==1 and r('GameEngineSubroutine')==8,'A confirms the selected character and loads World 1-1')
  assert(r('AreaChrBank')~=0x3c,'Gameplay restores the area background bank')
  assert(r('GamePauseStatus')%2==0,'Confirmation never pauses the new game')
  startX=r('Player_X_Position')
 end
 if frame==1925 then
  assert(r('Player_X_Position')>startX,'Controller moves the chosen character after loading')
  assert(titleCore==0 and demos==0,'Neither gameplay nor attract demo runs on the title/select screen')
  shot('gameplay')
  print('PASS static title, separate twelve-character select, preview banks, held-Start gate, navigation, B-back, confirmation and real gameplay')
  emu.stop(0)
 end
end,emu.eventType.endFrame)
