-- A real left-facing B press creates the complete shield. Explicit empty-floor
-- and inventory fixtures are separate from controller-only progression runs.
local frame,age,updates,done=0,0,0,false
local before
local interruptDepth=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function signed(v)return v>=128 and v-256 or v end
emu.addMemoryCallback(function()interruptDepth=interruptDepth+1 end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()interruptDepth=interruptDepth-1 end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addMemoryCallback(function()interruptDepth=interruptDepth+1 end,emu.callbackType.exec,L.IrqScrollSplit)
emu.addMemoryCallback(function()interruptDepth=interruptDepth-1 end,emu.callbackType.exec,L.IrqScrollSplit_RTI)
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140,start=frame==200,
  left=frame>=555 and frame<558,b=frame>=562 and frame<568},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if interruptDepth~=0 or frame<550 or r('CurrentBank')%128~=60 then return end
 before={}
 for a=0,255 do before[a]=signed(r('SsCircle',a))end
end,emu.callbackType.exec,L.SpecialWeapons)
emu.addMemoryCallback(function()
 if interruptDepth~=0 or frame<550 or r('CurrentBank')%128~=60 or r('RgShotType',9)~=17 then return end
 updates=updates+1
 local cx=r('Player_X_Position')+256*r('Player_PageLoc')+8
 local cy=(r('Player_Y_Position')+20)%256
 for i=0,7 do
  local slot=9-i;local initial=i*32-128
  local oldAngle=(initial*256-(updates-1)*0x2b7)%65536
  local oldHi=math.floor(oldAngle/256)
  local nextAngle=(initial*256-updates*0x2b7)%65536
  local ex=(cx+before[(oldHi+64)%256])%65536;local ey=cy+before[oldHi]
  assert(r('RgShotDir',slot)==2,'Creation facing is retained by every shield ball')
  assert(r('RgShotX',slot)+256*r('RgShotPage',slot)==ex,'Left source orbit worldX '..updates..'/'..i)
  assert(r('RgShotY',slot)==ey%256,'Left source orbit Y '..updates..'/'..i)
  assert(r('SsAngleHi',slot)*256+r('SsAngleLo',slot)==nextAngle,'Left source signed angle '..updates..'/'..i)
  local hidden=i~=0 and initial*256-updates*0x2b7> -32768
  assert((r('SsHidden',slot)~=0)==hidden,'Left source staged appearance '..updates..'/'..i)
 end
 if updates==100 then
  assert(r('InvAmmo',151)==96,'Left shield keeps one sixteen-unit summoning cost')
  print('PASS real left-facing Water Shield summon, all eight exact signed orbits/reveals and energy through100updates')
  done=true;emu.stop(0)
 end
end,emu.callbackType.exec,L.SpecialWeaponsFinish)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
  for i=0,5 do w('Enemy_Flag',0,i)end
  for i=0,9 do w('RgShotType',0,i)end
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  w('Player_X_Position',96);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
  w('PlayerStatus',1);w('InvOwnedLo',129,9);w('InvSelected',7,9);w('InvAmmo',112,151);w('InvDirty',1)
 end
 if frame==1100 then assert(done,'Left shield controller fixture completed100nativeupdates')end
end,emu.eventType.endFrame)
