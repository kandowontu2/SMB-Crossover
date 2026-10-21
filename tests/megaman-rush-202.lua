-- Arena/inventory fixtures; controller B summons Rush, gravity and native
-- ground find the landing, then a controlled falling actor crosses his back.
local frame=0
local bounced=false
local slot
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
emu.addEventCallback(function()emu.setInput({right=frame==80,start=frame==200,b=frame>=560 and frame<565},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then
  for i=0,5 do w('Enemy_Flag',0,i)end
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for p=0,1 do for c=0,15 do w('Block_Buffer_1',0x54,p*208+176+c)end end
  w('PlayerStatus',1);w('InvOwnedLo',1,1);w('InvOwnedHi',5,1);w('InvSelected',8,1);w('InvAmmo',112,24);w('InvDirty',1)
  w('Player_X_Position',128);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',2)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 end
 if frame==570 then
  for i=0,9 do if r('RgShotType',i)==20 then slot=i end end
  assert(slot and r('RgShotX',slot)==116,'Rush falls twenty NES pixels to the facing side of the player center')
  assert(r('RgShotY',slot)<80 and r('InvAmmo',24)==112,'Summoning is free and begins above the player')
 end
 if frame==625 then
  assert(r('SsMode',slot)==1 and r('RgShotY',slot)==208,'Native ground puts Rush feet on the floor')
  assert(r('InvAmmo',24)==112,'Waiting costs no energy')
  w('Player_X_Position',r('RgShotX',slot)-8);w('Player_Y_Position',160);w('Player_State',2);w('Player_Y_Speed',2)
  w('MmVY',0);w('MmVY',0,1);w('MmVY',2,2);w('MmFrictionYActive',0)
 end
 if frame>625 and frame<650 and r('SsMode',slot)==2 then
  bounced=true
  assert(r('InvAmmo',24)==100,'Rush spends twelve energy once at the spring contact')
  assert(r('MmVY',2)>=128,'Spring launches upward')
 end
 if frame==700 then
  assert(bounced and r('RgShotType',slot)==0,'Rush spring, exit animation and accelerating departure finish without a lingering hitbox')
  assert(r('InvAmmo',24)==100 and r('GameEngineSubroutine')==8,'Rush leaves energy and gameplay state intact')
  print('PASS source Rush facing summon, free fall/wait, floor-aligned feet, twelve-unit spring, upward launch and complete departure');emu.stop(0)
 end
end,emu.eventType.endFrame)
