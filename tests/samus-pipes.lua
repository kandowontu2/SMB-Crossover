local frame=0
local stopped
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
local function x() return r('Player_PageLoc')*256+r('Player_X_Position') end
emu.addEventCallback(function()
  emu.setInput({right=frame==80 or frame==100 or (frame>=500 and frame<1100) or
      (frame>=1150 and frame<1200)or(frame>=1205 and frame<1360),left=(frame>=1100 and frame<1120) or (frame>=1400 and frame<1600),
    start=frame==140,down=frame==1200 or frame==1203},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
  frame=frame+1
  if frame>=490 then for i=0,5 do w('Enemy_Flag',0,i) end end
  if frame==1000 then
    stopped=x()
    assert(stopped==433,'Standing Samus stops at the first pipe edge: '..stopped)
  end
  if frame>1000 and frame<=1100 then
    assert(x()==stopped,'Holding Right cannot drift through the pipe at '..frame)
    assert(r('MmXFraction')==0 and r('MmXFraction',1)==0,'Wall contact clears fractional drift')
  end
  if frame==1120 then w('InvOwnedLo',2,2);w('PlayerStatus',1); assert(x()==stopped-25,'Samus can immediately move away from the wall') end
  if frame==1350 then
    assert(r('SmBall')==1 and x()==433,'Morph Ball also stops at the pipe')
    print('PASS pipe collision holds indefinitely for standing and Morph Ball; moving away remains immediate')
  end
  if frame==1400 then
    w('Player_PageLoc',1);w('Player_X_Position',244)
    w('MmXFraction',0);w('MmXFraction',0,1)
  end
  if frame==1550 then stopped=x();assert(stopped==479,'Leftward collision stops at the far edge: '..stopped) end
  if frame>1550 and frame<=1600 then assert(x()==stopped,'Holding Left cannot creep through the pipe') end
  if frame==1600 then
    print('PASS leftward pipe collision remains solid with fractional Samus movement')
    emu.stop(0)
  end
end,emu.eventType.endFrame)
