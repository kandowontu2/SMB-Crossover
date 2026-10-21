local frame=0
local explosions=0
local shortApex=255
local longApex=255
local bulletY
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
emu.addEventCallback(function()
  emu.setInput({right=(frame>=80 and frame<100) or frame==130 or (frame>=500 and frame<570),left=frame==120 or (frame>=605 and frame<608),
    start=frame==150,b=frame==580 or frame==620,
    a=(frame>=660 and frame<663) or (frame>=720 and frame<748)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
  frame=frame+1
  if frame==110 then assert(r('SelectedCharacter')==1,'Holding Right moves once') end
  if frame==125 then assert(r('SelectedCharacter')==0,'Left selects Mario') end
  if frame==140 then assert(r('SelectedCharacter')==1,'A fresh Right press returns to Mega Man') end
  if frame==490 then
    -- Solid three-tile wall immediately ahead, inside the streamed block map.
    for row=8,10 do w('Block_Buffer_1',0x51,row*16+8) end
  end
  if frame==575 then
    assert(r('Player_X_Position')<=115 and r('Player_X_Position')>=100,'Solid wall blocks Mega Man: x='..r('Player_X_Position'))
  end
  if frame==600 then assert(r('MmBulletType',3)==0,'Buster is consumed by a wall hit') end
  if frame==624 then
    assert(r('MmBulletDir',3)==2 and r('MmBulletType',3)==1,'Buster fires left after turning')
    bulletY=r('MmBulletY',3)
  end
  if frame==628 then assert(r('MmBulletY',3)==bulletY,'Leftward buster also stays horizontal') end
  if frame==650 then
    for row=8,10 do w('Block_Buffer_1',0,row*16+8) end
    w('Player_X_Position',48); w('Player_PageLoc',0)
  end
  if frame>=660 and frame<710 then shortApex=math.min(shortApex,r('Player_Y_Position')) end
  if frame>=720 and frame<780 then longApex=math.min(longApex,r('Player_Y_Position')) end
  if frame==790 then
    assert(longApex<shortApex-8,'Holding A jumps higher than tapping A')
    assert(r('Player_State')==0,'Both jump lengths return to the floor')
    print('PASS selection edges, left selection, wall collision, wall impact, leftward shots, variable jump')
    emu.stop(0)
  end
end,emu.eventType.endFrame)
