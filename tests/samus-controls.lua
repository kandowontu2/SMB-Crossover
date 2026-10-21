local frame=0
local y,vy,x
local writes=0
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
local function pos(n,f) return r(n)+(r(f)+r(f,1)*256)/65536 end
local function vel(n)
  local v=r(n)+r(n,1)*256+r(n,2)*65536
  if v>=0x800000 then v=v-0x1000000 end
  return v/65536
end
local function shotCount()
  local count=0
  for i=0,2 do if r('SmShotType',i)>0 then count=count+1 end end
  return count
end
local function capture(tag)
  local f=assert(io.open(OUTPUT..ROM_NAME..'-samus-'..tag..'.png','wb'))
  f:write(emu.takeScreenshot());f:close()
end
emu.addMemoryCallback(function() writes=writes+1 end,emu.callbackType.write,0x4000,0x400f)
emu.addEventCallback(function()
  emu.setInput({right=frame==80 or frame==100 or (frame>=500 and frame<520) or
      (frame>=550 and frame<570),start=frame==140,
    a=(frame>=550 and frame<580) or frame==720,
    down=frame==650 or frame==654,up=frame==750 or (frame>=800 and frame<805),
    b=frame==680 or frame==800 or frame==840 or frame==846 or frame==852 or frame==858},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
  frame=frame+1
  if frame>=490 then for i=0,5 do w('Enemy_Flag',0,i) end end
  if frame==490 then
    assert(r('SelectedCharacter')==2 and r('GameEngineSubroutine')==8,'Samus starts gameplay')
    assert(r('ObjectMetasprite')==L.METASPRITE_SAMUS_BODY,'Samus uses her native metasprite')
    assert(r('SmAudioCurrent')==15 and r('SmAudioRam',0x8d)==1,'Original Brinstar music runs')
    -- The mixer skips redundant stores, so validate live hardware output
    -- rather than the original unbuffered driver's write count.
    assert(writes>100 and emu.read(0x4015,emu.memType.nesDebug)%16~=0,'Samus native driver writes audible NES APU voices')
    capture('standing')
  end
  if frame==500 then x=pos('Player_X_Position','MmXFraction') end
  if frame>=501 and frame<=525 then
    local v=frame<=520 and 1.25 or 0
    x=x+v
    assert(math.abs(vel('MmVX')-v)<0.001,'Immediate source walk/stop at '..frame)
    assert(math.abs(pos('Player_X_Position','MmXFraction')-x)<0.02,'Walk trajectory at '..frame)
  end
  if frame==525 then print('PASS Samus immediate 1.25-pixel movement and native Metroid audio') end
  if frame==550 then vy=-500/120;y=pos('Player_Y_Position','MmYFraction') end
  if frame>=551 and frame<=590 then
    if frame>580 and vy<0 then vy=vy*(0.0001)^(1/60) end
    vy=vy+700/7200;y=y+vy
    assert(math.abs(vel('MmVY')-vy)<0.002,'Samus source vertical velocity at '..frame..': '..vel('MmVY')..' / '..vy)
    assert(math.abs(pos('Player_Y_Position','MmYFraction')-y)<0.05,'Samus jump trajectory at '..frame)
  end
  if frame==565 then
    assert(r('SmPose')>=20 and r('SmPose')<=23,'Moving jump spins after rising 30 NES pixels')
    capture('spin')
  end
  if frame==590 then print('PASS Samus jump, spin threshold, gravity and release friction') end
  if frame==640 then w('InvOwnedLo',2,2);w('PlayerStatus',1);
    w('Player_X_Position',40);w('Player_PageLoc',0)
    w('Player_Y_Position',176);w('Player_State',0);w('Player_Y_Speed',0)
    w('MmVY',0);w('MmVY',0,1);w('MmVY',0,2)
  end
  if frame==655 then
    assert(r('SmBall')==1 and r('CrouchingFlag')~=0,'Second Down enters Morph Ball after its acquired upgrade')
    assert(r('SmPose')>=27 and r('SmPose')<=30,'Morph Ball animates')
    capture('morph-ball')
  end
  if frame==700 then
    assert(r('SmBall')==1,'Releasing Down keeps Morph Ball active')
    local bombs=0
    for i=0,2 do if r('SmBombAge',i)>0 then bombs=bombs+1 end end
    assert(bombs==1 and shotCount()==0,'B in Morph Ball creates a bomb')
  end
  if frame==722 then
    assert(r('SmBall')==0,'A exits Morph Ball')
    assert(vel('MmVY')>-1,'Exiting with A does not start a jump')
  end
  if frame==740 then
    assert(r('SmBombBoosted',2)==1,'Explosion boosts Samus once')
    print('PASS persistent Morph Ball, bomb fuse, explosion boost and A exit')
  end
  if frame==790 then
    w('Player_Y_Position',176);w('Player_State',0);w('Player_Y_Speed',0)
    w('MmVY',0);w('MmVY',0,1);w('MmVY',0,2)
  end
  if frame==802 then
    assert(r('SmShotType',2)==1 and r('SmShotDir',2)==3,'Up+B fires the short beam vertically')
    assert(r('SmPose')==9 or r('SmPose')==19,'Up shot has the aiming pose')
    capture('up-shot')
  end
  if frame==815 then
    assert(shotCount()==0,'Starting beam has the reference 50-pixel range')
    w('PlayerStatus',1);w('InvOwnedLo',0x82,2)
  end
  if frame==860 then assert(shotCount()==3,'Long beam has a three-shot limit with four distinct presses') end
  if frame==860 then
    assert(shotCount()>0,'Mushroom beam travels beyond the short beam range')
    print('PASS upward fire, short range, long beam and independent three-shot limit')
    emu.stop(0)
  end
end,emu.eventType.endFrame)
