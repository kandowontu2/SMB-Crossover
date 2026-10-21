-- Explicit expansion arenas compare every old quarter-square result with an
-- independent integer product. Uniform source angles exercise the cache;
-- deliberately nonuniform low bits verify its conservative key invalidation.
local frame,case,checks=0,0,0
local centers={{0,0},{255,57},{511,196},{256,250}}
local radii={25,47,91,127,179,180,255}
local total=#centers*#radii*48*2
local expected={}
local interruptDepth=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function signed(v)return v>=128 and v-256 or v end
local function offset(angle,radius)
 local sine=signed(r('SsSine',angle%256))
 local magnitude=math.floor(math.abs(sine)*radius/128)
 return sine<0 and -magnitude or magnitude
end
emu.addMemoryCallback(function()interruptDepth=interruptDepth+1 end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()interruptDepth=interruptDepth-1 end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addMemoryCallback(function()interruptDepth=interruptDepth+1 end,emu.callbackType.exec,L.IrqScrollSplit)
emu.addMemoryCallback(function()interruptDepth=interruptDepth-1 end,emu.callbackType.exec,L.IrqScrollSplit_RTI)
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140,start=frame==200},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if interruptDepth~=0 or frame<550 or r('CurrentBank')%128~=60 then return end
 case=case+1
 if case>total then
  print('PASS Water expansion exact integer products/positions: '..checks..' balls, both directions, seven radii through255, page/Ywrap and nonuniform cache keys')
  emu.stop(0);return
 end
 local k=case-1;local phase=k%48;k=math.floor(k/48)
 local dir=k%2+1;k=math.floor(k/2)
 local radius=radii[k%#radii+1];k=math.floor(k/#radii)
 local center=centers[k+1];local cx,cy=center[1],center[2]
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 w('Player_X_Position',96);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
 w('PlayerStatus',1);w('InvOwnedLo',129,9);w('InvSelected',7,9)
 w('TimerControl',0);w('GameEngineSubroutine',8);w('MmDeathFlag',0)
 w('InvFresh',0);w('SsWaterExpand',1);w('SsWaterFraction',0);w('SsWaterRadius',radius-3)
 w('SsWaterX',cx);w('SsWaterPage',math.floor(cx/256));w('SsWaterY',cy)
 w('SsBodyStop',0);w('SsFreeze',0)
 for slot=0,7 do
  local a=(phase+slot*(phase<32 and 32 or 31))%256
  local dx,dy=offset(a+64,radius),offset(a,radius)
  local nextAngle=(a*256+250+(dir==1 and 0x2b7 or -0x2b7))%65536
  expected[slot]={x=(cx+dx)%65536,y=(cy+dy)%256,yhi=(1+math.floor((cy+dy)/256))%256,
   a=math.floor(nextAngle/256),lo=nextAngle%256,kind=radius>=180 and 0 or 17}
  w('RgShotType',17,slot);w('RgShotAge',19,slot);w('RgShotImpact',0,slot);w('RgShotDir',dir,slot)
  w('SsAngleLo',250,slot);w('SsAngleHi',a,slot);w('SsHidden',0,slot)
  w('SsHitTimer',0,slot);w('RgShotHits',0,slot)
 end
end,emu.callbackType.exec,L.SpecialWeapons)
emu.addMemoryCallback(function()
 if interruptDepth~=0 or frame<550 or r('CurrentBank')%128~=60 or case==0 then return end
 for slot=0,7 do
  local e=expected[slot]
  assert(r('RgShotType',slot)==e.kind,'Exact expanding lifetime '..case..'/'..slot)
  assert(r('RgShotX',slot)+256*r('RgShotPage',slot)==e.x,'Exact expanding worldX '..case..'/'..slot)
  assert(r('RgShotY',slot)==e.y and r('RgShotYHigh',slot)==e.yhi,'Exact expanding wrappedY '..case..'/'..slot)
  assert(r('SsAngleLo',slot)==e.lo and r('SsAngleHi',slot)==e.a,'Exact expanding angle '..case..'/'..slot)
  checks=checks+1
 end
end,emu.callbackType.exec,L.SpecialWeaponsFinish)
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
