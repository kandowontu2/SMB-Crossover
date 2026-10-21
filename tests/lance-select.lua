-- Actual title/menu inputs: Select toggles Bill/Lance in the same roster slot.
local frame=0
local startX
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function shot(tag)local f=assert(io.open(OUTPUT..ROM_NAME..'-lance-'..tag..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
local function name(expected)
 for i,v in ipairs(expected)do assert(emu.read(0x2308+i-1,emu.memType.nesPpuDebug)==v,'Highlighted character name is updated at '..i..': '..emu.read(0x2308+i-1,emu.memType.nesPpuDebug)..' / '..v)end
end
emu.addEventCallback(function()
 emu.setInput({right=frame==80 or frame==100 or frame==120 or frame==220 or(frame>=700 and frame<720),left=frame==240,
  select=(frame>=140 and frame<155)or frame==180 or frame==200 or frame==260 or frame==280,a=frame==320},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==170 or frame==215 or frame==255 or frame==295 then
  assert(r('SelectedCharacter')==3 and r('BillVariant')==1 and r('CrossoverMenuState')==2,'Lance occupies Bill\'s roster slot')
  name({0x24,0x24,0x24,0x15,0x0a,0x17,0x0c,0x0e,0x24,0x0b,0x0e,0x0a,0x17,0x24,0x24,0x24})
  assert(emu.read(0x3f11,emu.memType.nesPpuDebug)==0x1c,'Lance uses source turquoise hair')
  assert(emu.read(0x3f12,emu.memType.nesPpuDebug)==0x36 and emu.read(0x3f13,emu.memType.nesPpuDebug)==0x0f,'Lance retains skin and black outlines')
  local pointer=r('SmPosePtr')+256*r('SmPosePtr',1)
  assert(pointer==L.RgLANCE_STANDRight,'Colored preview uses Lance\'s own source graphics')
  assert(emu.read(0x2326,emu.memType.nesPpuDebug)==0x1c,'Bill/Lance toggle hint appears above the outlines option')
  if frame==170 then shot('select')end
 end
 if frame==195 or frame==275 then
  assert(r('SelectedCharacter')==3 and r('BillVariant')==0,'Another Select press restores Bill')
  assert(emu.read(0x3f11,emu.memType.nesPpuDebug)==0x12,'Bill retains his original blue suit')
 end
 if frame==235 then
  assert(r('SelectedCharacter')==4,'Right still navigates away from Bill/Lance')
  for i=0,19 do assert(emu.read(0x2326+i,emu.memType.nesPpuDebug)==0x24,'Bill/Lance hint clears on another character')end
 end
 if frame==700 then
  assert(r('SelectedCharacter')==3 and r('BillVariant')==1 and r('GameEngineSubroutine')==8,'Confirm launches a game as Lance')
  for i,v in ipairs({0x15,0x0a,0x17,0x0c,0x0e})do assert(emu.read(0x2043+i-1,emu.memType.nesPpuDebug)==v,'Gameplay HUD says LANCE')end
  startX=r('Player_X_Position')+256*r('Player_PageLoc');shot('gameplay')
 end
 if frame==725 then
  assert(r('Player_X_Position')+256*r('Player_PageLoc')>startX,'Lance responds to gameplay movement')
  print('PASS Bill/Lance Select toggle, held-button edge, source preview/colors/name, navigation away/back, confirmation, HUD and movement')
  emu.stop(0)
 end
end,emu.eventType.endFrame)
