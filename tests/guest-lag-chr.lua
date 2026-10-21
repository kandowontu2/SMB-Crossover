-- Natural Bass movement/shot load exercises late NMIs while poses cross CHR
-- banks. An explicit empty arena prevents unrelated enemy contacts. A lag NMI
-- retains hardware OAM, so it must also retain its physical CHR mapping.
local frame,lagCount,changes,draws=0,0,0,0
local lag=false
local inNmi=false
local selector=0
local physical={}
local mmc5=ROM_NAME:find('mmc5')~=nil
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
local function bank(index,value)
 if frame>=550 and lag then
  assert(physical[index]==value,'Lag NMI changed CHR bank '..index..' while retaining old hardware OAM')
 end
 if frame>=550 and physical[index]~=value then changes=changes+1 end
 physical[index]=value
end
if mmc5 then
 emu.addMemoryCallback(function(a,v)bank(a-0x5120,v)end,emu.callbackType.write,0x5120,0x512b)
else
 emu.addMemoryCallback(function(a,v)selector=v&7 end,emu.callbackType.write,0x8000)
 emu.addMemoryCallback(function(a,v)
  if selector<6 then bank(selector,v)end
  if frame>=550 and not inNmi and selector==7 then
   assert(r('CurrentBank')==v,'Main-thread PRG bank must be published before the hardware switch, so an intervening NMI restores it')
  end
 end,emu.callbackType.write,0x8001)
end
emu.addMemoryCallback(function()
 inNmi=true
 lag=r('NmiDisable')>=128
 if frame>=550 and lag then lagCount=lagCount+1 end
end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()lag=false;inNmi=false end,emu.callbackType.exec,assert(L.NonMaskableInterrupt_RTI))
emu.addMemoryCallback(function()if frame>=550 then draws=draws+1 end end,emu.callbackType.write,0x4014)
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140 or frame>=560 and frame%80<40,
  left=frame>=560 and frame%80>=40,start=frame==240,
  b=frame>=560 and frame%8==0,a=frame>=560 and frame%100<35,up=frame>=560 and frame%64<16},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=540 then for i=0,5 do w('Enemy_Flag',0,i)end end
 if frame==550 then
  for i=0,415 do w('Block_Buffer_1',0,i)end
  for col=0,15 do w('Block_Buffer_1',0x54,176+col);w('Block_Buffer_1',0x54,384+col)end
  w('Player_X_Position',80);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 end
 if frame==1800 then
  assert(r('SelectedCharacter')==9 and r('MmDeathFlag')==0,'Bass stayed alive in the graphics stress arena')
  assert(lagCount>5 and changes>20 and draws>100,'Both lag/regular NMIs and changing CHR were exercised')
  print('PASS lag NMIs retain physical CHR with old hardware OAM across '..lagCount..' lag frames and '..changes..' bank changes')
  emu.stop(0)
 end
end,emu.eventType.endFrame)
