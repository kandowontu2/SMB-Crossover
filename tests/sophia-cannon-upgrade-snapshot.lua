-- Controlled power transitions while real B-created cannon shots are alive.
-- The SWF fixes shotType at construction; upgrading cannot recolor/re-damage
-- a shot already flying across the screen.
local frame=0
local first,second
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
emu.addEventCallback(function()
 emu.setInput({start=frame==240,down=frame==80,right=frame>=100 and frame<200 and(frame-100)%20==0,
  b=frame>=562 and frame<566 or frame>=582 and frame<586 or frame>=602 and frame<606},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,page*208+176+col)end end
  for i=0,5 do w('Enemy_Flag',0,i)end
  for i=0,9 do w('RgShotType',0,i)end
  w('Player_X_Position',32);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
  w('PlayerFacingDir',1);w('PlayerStatus',0);w('InvOwnedLo',1,11);w('InvSelected',0,11);w('RgCooldown',0);w('RgPreviousButtons',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 end
 if frame==570 then
  for i=0,9 do if r('RgShotType',i)==6 then first=i end end
  assert(first and r('SsMode',first)==0,'Initial cannon freezes normal tier')
  w('PlayerStatus',1);w('InvOwnedLo',0x81,11)
 end
 if frame==590 then
  assert(r('RgShotType',first)==6 and r('SsMode',first)==0,'Hyper upgrade leaves existing normal shot unchanged')
  for i=0,9 do if r('RgShotType',i)==6 and r('SsMode',i)==1 then second=i end end
  assert(second,'Fresh B after mushroom creates Hyper cannon')
  w('InvOwnedLo',0x91,11)
 end
 if frame==610 then
  assert(r('RgShotType',second)==6 and r('SsMode',second)==1,'Crusher upgrade leaves existing Hyper shot unchanged')
  local crusher=false
  for i=0,9 do if r('RgShotType',i)==6 and r('SsMode',i)==2 then crusher=true end end
  assert(crusher,'Fresh B after Crusher upgrade creates Crusher cannon')
  print('PASS Sophia cannon tier is frozen per projectile across Normal/Hyper/Crusher upgrades');emu.stop(0)
 end
end,emu.eventType.endFrame)
