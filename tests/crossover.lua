local frame=0
local initialX,initialY,bulletY
local function r(name,offset) return emu.read(assert(L[name],name)+(offset or 0),emu.memType.nesDebug) end
local function shot(tag)
  local f=assert(io.open(OUTPUT..ROM_NAME..'-'..tag..'.png','wb'));f:write(emu.takeScreenshot());f:close()
end
emu.addEventCallback(function()
  emu.setInput({right=frame==80 or (frame>=500 and frame<520),start=frame==120,
    a=frame>=540 and frame<570,b=frame==620 or frame==630},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
  frame=frame+1
  if frame==100 then
    assert(r('SelectedCharacter')==1,'Right selects Mega Man')
    assert(r('CrossoverMenuState')==2,'Start opened the separate character selection')
    assert(emu.read(0x2363,emu.memType.nesPpuDebug)==0x0d,'Selection explains D-pad controls')
    assert(emu.read(0x230c,emu.memType.nesPpuDebug)==0x16,'Only the highlighted full name appears beneath the preview')
    shot('title')
  end
  if frame==480 then
    assert(r('OperMode')==1 and r('GameEngineSubroutine')==8,'Mega Man reaches gameplay')
    assert(r('SelectedCharacter')==1,'Selection persists through level loading')
    assert(r('Player_State')==0,'Mega Man lands on the floor')
    initialX=r('Player_X_Position'); initialY=r('Player_Y_Position')
    shot('megaman')
  end
  if frame==250 then shot('intermediate') end
  if frame==510 then
    assert(r('MmVX')==0 and r('MmVX',1)==0x60 and r('MmVX',2)==1,'2.02 movePlayer applies immediate 165 Flash px/s after startup')
    shot('running')
  end
  if frame==525 then
    assert(r('Player_X_Position')>initialX,'Mega Man moves right')
    assert(r('Player_X_Speed')==0 and r('MmVX')==0 and r('MmVX',1)==0 and r('MmVX',2)==0,'2.02 movePlayer stops immediately on direction release')
  end
  if frame==535 then assert(r('Player_X_Speed')==0,'Released direction stays stopped') end
  if frame==550 then
    assert(r('Player_State')==1 and r('Player_Y_Position')<initialY,'A starts a jump')
    shot('jumping')
  end
  if frame==615 then
    assert(r('Player_State')==0,'Jump lands on the floor')
  end
  if frame==624 then
    assert(r('MmBulletType',3)==1,'B shoots without a fire flower')
    bulletY=r('MmBulletY',3)
    shot('shooting')
  end
  if frame==628 then
    assert(r('MmBulletY',3)==bulletY,'Buster shot flies horizontally')
    assert(r('MmBulletType',3)==1,'Buster shot remains active')
  end
  if frame==635 then
    assert(r('MmBulletType',2)==1,'A second B press fires another buster slot')
    print('PASS selection, persistence, run/stop, jump/land, flower-free shooting, horizontal flight, independent shots')
    emu.stop(0)
  end
end,emu.eventType.endFrame)
