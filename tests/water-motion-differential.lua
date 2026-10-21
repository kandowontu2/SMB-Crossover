-- Explicit motion arenas, never level-clear evidence. Exercise all 256 orbital
-- angle bytes across horizontal page and vertical wrap boundaries. Expectations
-- reproduce the old signed lookup integration, not the optimized center cache.
local frame,case,checks=0,0,0
local centersX={0,1,8,24,112,240,255,256,511,768}
local centersY={0,10,25,37,57,176,210,250}
local total=#centersX*#centersY*32*2
local expected={}
local interruptDepth=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function signed(v)return v>=128 and v-256 or v end
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
  print('PASS Water Shield exact signed motion: '..checks..' balls, both source rotation directions, all256angles, tenX/page and eightY/wrap centers')
  emu.stop(0);return
 end
 local k=case-1
 local base=k%32;k=math.floor(k/32)
 local dir=k%2+1;k=math.floor(k/2)
 local cy=centersY[k%#centersY+1];k=math.floor(k/#centersY)
 local cx=centersX[k+1]
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 w('Player_X_Position',cx-8);w('Player_PageLoc',math.floor((cx-8)/256))
 w('Player_Y_Position',cy-20);w('Player_Y_HighPos',1);w('Player_State',0)
 w('PlayerStatus',1);w('InvOwnedLo',129,9);w('InvSelected',7,9)
 w('TimerControl',0);w('GameEngineSubroutine',8);w('MmDeathFlag',0)
 w('InvFresh',0);w('SsWaterExpand',0);w('SsBodyStop',0);w('SsFreeze',0)
 for slot=0,7 do
  local rawAngle=base+slot*32-(dir==2 and 128 or 0)
  local a=rawAngle%256
  local dx=signed(r('SsCircle',(a+64)%256));local dy=signed(r('SsCircle',a))
  local x=(cx+dx)%65536;local y=cy+dy
  local advance=dir==1 and 0x2b7 or -0x2b7
  local nextAngle=(a*256+250+advance)%65536
  local unwrapped=rawAngle*256+250+advance
  local reveal=dir==1 and unwrapped>=65536 or dir==2 and unwrapped<=-32768
  expected[slot]={x=x,y=y%256,yhi=1+math.floor(y/256),a=math.floor(nextAngle/256),lo=nextAngle%256,
   hidden=reveal and 0 or slot%2}
  w('RgShotType',17,slot);w('RgShotAge',19,slot);w('RgShotImpact',0,slot)
  w('RgShotDir',dir,slot)
  w('SsAngleLo',250,slot);w('SsAngleHi',a,slot);w('SsHidden',slot%2,slot)
  w('SsHitTimer',0,slot);w('RgShotHits',0,slot)
 end
end,emu.callbackType.exec,L.SpecialWeapons)
emu.addMemoryCallback(function()
 if interruptDepth~=0 or frame<550 or r('CurrentBank')%128~=60 or case==0 then return end
 for slot=0,7 do
  local e=expected[slot]
  assert(r('RgShotType',slot)==17,'Orbit preserves ball '..case..'/'..slot)
  assert(r('RgShotX',slot)+256*r('RgShotPage',slot)==e.x,'Exact worldX '..case..'/'..slot)
  assert(r('RgShotY',slot)==e.y and r('RgShotYHigh',slot)==e.yhi%256,'Exact wrappedY '..case..'/'..slot)
  assert(r('SsAngleLo',slot)==e.lo and r('SsAngleHi',slot)==e.a,'Exact fractional angle '..case..'/'..slot)
  assert(r('SsHidden',slot)==e.hidden,'Exact phased appearance '..case..'/'..slot)
  assert(r('RgShotAge',slot)==20,'Every ball receives one age update')
  checks=checks+1
 end
end,emu.callbackType.exec,L.SpecialWeaponsFinish)
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
