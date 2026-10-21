local frame=0
local poses={}
local checked=0
local blink=0
local diedAt
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
local function rom(bank,address) return emu.read(bank*0x2000+address%0x2000,emu.memType.nesPrgRom) end
emu.addEventCallback(function()
  emu.setInput({right=frame==80 or frame==100 or (frame>=500 and frame<550),start=frame==140,
    a=(frame>=510 and frame<540) or frame==700,down=frame==650 or frame==654,
    up=frame>=560 and frame<570,b=frame==530 or frame==565 or frame==680},0)
end,emu.eventType.inputPolled)
-- Validate completed CPU OAM, before publication; a physical frame can interrupt a draw.
emu.addMemoryCallback(function()
  if frame>=490 and frame<790 and r('CurrentBank')%128==4 then
    local used=0
    if r('ObjectMetasprite')~=0 then
      used=rom(13,r('SmPosePtr')+256*r('SmPosePtr',1))
      poses[r('SmPose')]=true
    else blink=blink+1 end
    assert(used<=56 and used%4==0,'Samus pose fits her fourteen-entry OAM reservation')
    for offset=used,55,4 do
      assert(r('Sprite_Y_Position',offset)==0xf8,'No stale Samus OAM at frame '..frame..', byte '..offset)
    end
    checked=checked+1
  end
end,emu.callbackType.exec,L.DoneDrawingPlayer)
emu.addEventCallback(function()
  frame=frame+1
  if frame>=490 and frame<800 then for i=0,5 do w('Enemy_Flag',0,i) end end
  if frame==640 then w('InvOwnedLo',2,2);w('PlayerStatus',1)end
  if frame==740 then w('InjuryTimer',20) end
  if frame==790 then
    local n=0;for _ in pairs(poses) do n=n+1 end
    assert(n>=10 and checked>=180 and blink>=10,'Replay covers body, aim, spin, Morph Ball and injury blink')
    print('PASS Samus OAM across variable-size poses and injury blinking')
    -- The earlier Morph fixture intentionally grants an upgrade. Restore
    -- an unpowered character before testing lethal contact and its burst.
    w('PlayerStatus',0);w('InvOwnedLo',1,2);w('SmBall',0);w('SmCrouch',0)
  end
  if frame==800 then
    w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0)
    w('Enemy_X_Position',r('Player_X_Position'));w('Enemy_PageLoc',r('Player_PageLoc'))
    w('Enemy_Y_Position',r('Player_Y_Position'));w('Enemy_Y_HighPos',1)
    w('Enemy_BoundBoxCtrl',9);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
    w('InjuryTimer',0)
  end
  if frame>800 and not diedAt and r('MmDeathFlag')~=0 then diedAt=frame end
  if diedAt and frame==diedAt+10 then
    assert(r('ObjectMetasprite')==0 and r('MmDeathPit')==0,'Contact death replaces the Samus body')
    local visible=0
    for offset=0,95,4 do if r('Sprite_Y_Position',offset)<240 then visible=visible+1 end end
    assert(visible==6,'All six original Samus death pieces render: '..visible)
    assert(r('PlayerChrBank')>=L.SAMUS_CHR_DEATH and r('PlayerChrBank')<L.SAMUS_CHR_END,'Death uses the original guts animation banks')
    print('PASS six-piece Samus death burst and separate CHR animation')
  end
  if diedAt and frame==diedAt+179 then assert(r('NumberofLives')==2,'Normal Samus death waits 3000ms') end
  if diedAt and frame==diedAt+183 then
    assert(r('NumberofLives')==1,'Normal death subtracts one life after 180 frames')
    print('PASS source Samus death duration and life loss')
  end
  if frame==1250 then
    assert(diedAt and r('GameEngineSubroutine')==8 and r('SelectedCharacter')==2,'Samus respawns with selection intact')
    assert(r('MmDeathFlag')==0 and r('SmBall')==0,'Respawn resets death and Morph Ball state')
    print('PASS Samus respawn and state cleanup')
    emu.stop(0)
  end
end,emu.eventType.endFrame)
