-- Appended to the common real-menu/native-boundary component prelude.
local redFires=0;local sawWhite=false;local paletteReads=0;local lifeBefore
local nativeTicks=0;local redTrace={}
emu.addMemoryCallback(function()if entered and actual(0xa000)==B.PnNativeFrameReady then nativeTicks=nativeTicks+1 end end,emu.callbackType.exec,L.PnNativeFrameReady)
local paletteBefore;local roulette={}
local restoreExpected,restoredPackets,restoreIndex=nil,0,nil
local ppuAddress,ppuHigh,ppuStep=0,nil,1
-- Compare the actual final restoration packet, not a later palette-animation
-- phase. SMB cycles question-block color $3F0D independently of the flash.
emu.addMemoryCallback(function()
 if entered and actual(0xa000)==B.PnQueueBombPalette and sawWhite and r('PnPhase',27)==0 and(r('PnNativeStageFlags')&2)==0 then
  restoreExpected={};for i=0,31 do restoreExpected[i]=r('PnBombPaletteShadow',i)&63 end
 end
end,emu.callbackType.exec,L.PnQueueBombPalette)
emu.addMemoryCallback(function()ppuHigh=nil end,emu.callbackType.read,0x2002)
emu.addMemoryCallback(function(_,value)ppuStep=value&4~=0 and 32 or 1 end,emu.callbackType.write,0x2000)
emu.addMemoryCallback(function(_,value)
 if ppuHigh then ppuAddress=(ppuHigh*256+value)&0x3fff;ppuHigh=nil
 else ppuHigh=value&63 end
end,emu.callbackType.write,0x2006)
emu.addMemoryCallback(function(_,value)
 if restoreExpected then
  if not restoreIndex and ppuAddress==0x3f10 then restoreIndex=0 end
  if restoreIndex then
   assert(ppuAddress==0x3f10+restoreIndex,'Final restoration streams all32 sprite/background palette bytes')
   local slot=(restoreIndex+16)%32
   assert(value&63==restoreExpected[slot],'Every actual restored color matches the captured pre-flash palette')
   restoreIndex=restoreIndex+1
   if restoreIndex==32 then restoredPackets=restoredPackets+1;restoreIndex=nil;restoreExpected=nil end
  end
 end
 ppuAddress=(ppuAddress+ppuStep)&0x3fff
end,emu.callbackType.write,0x2007)
local bigStart,bigNative
local paletteTrace=assert(io.open(OUTPUT..'palette-trace.csv','w'));paletteTrace:write('tick,phase,active,flags,busy,queue,background\n')
local function colors()
 local s={};for i=0,31 do s[#s+1]=string.char(emu.read(0x3f00+i,emu.memType.nesPpuDebug)&63)end
 return table.concat(s)
end
local function cap(kind)
 w('PnCapActive',kind);w('PnCapX',72);w('PnCapY',128);w('PnCapPage',0)
 w('PnCapAge',0);w('PnCapFraction',0);w('PnCapVX',0);w('PnCapVXF',0)
 w('PnCapHits',4);w('PnCapChange',0)
end
emu.addMemoryCallback(function()
 if entered and actual(0xa000)==B.Pb9a86 then redFires=redFires+1;redTrace[#redTrace+1]=t..':'..nativeTicks end
end,emu.callbackType.exec,L.Pb9a86)
emu.addMemoryCallback(function()
 if not entered or actual(0xc000)~=B.PnPaletteScreenUpdate or r('PnBombCapturePending')==0 then return end
 local scan=emu.getState()['ppu.scanline']
 assert(scan>=241 and scan<261,'Bell palette snapshot must stay inside VBlank')
 paletteReads=paletteReads+1
end,emu.callbackType.read,0x2007)
emu.addEventCallback(function()
 local b={}
 if not entered then
  if wall>=60 and wall%12==0 then
   if r('CrossoverMenuState')~=2 then b.start=true
   elseif r('CrossoverMenuIndex')<12 then b.down=true
   elseif r('CrossoverMenuIndex')~=17 then b.right=true
   elseif r('VvVariant')~=PN_VARIANT then b.select=true else b.a=true end
  end
 else
  b.b=t>=95 and t<99
  b.a=(t>=160 and t<164)or(t>=320 and not bigStart and redFires<3 and (t-320)%23<4)
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1
 if not entered then
  if r('OperMode')==1 and r('GameEngineSubroutine')==8 then entered=true;t=0 end
  assert(wall<1100,'Real menu enters the Parodius Bell arena');return
 end
 t=t+1
 if t>=155 and t<=275 then paletteTrace:write(table.concat({t,r('PnPhase',27),r('PnActive',27),r('PnNativeStageFlags'),r('PnNativeVramBusy'),r('VRAM_Buffer1_Offset'),emu.read(0x3f00,emu.memType.nesPpuDebug)},',')..'\n');paletteTrace:flush()end
 if t==1 then arena();w('VvGun',8)end
 if t==12 then assert(r('PnBombPaletteReady')==1,string.format('NMI captured the actual world palette: ready=%d pending=%d reads=%d init=%02x mode=%d var=%d',r('PnBombPaletteReady'),r('PnBombCapturePending'),paletteReads,emu.read(0x5dd2,emu.memType.nesDebug),r('OperMode'),r('VvVariant')))end
 if t==18 then lifeBefore=r('NumberofLives');cap(10)end
 if t==32 then
  assert(r('NumberofLives')==lifeBefore+1,'Physical White Bell grants1UP')
  assert(r('VvGun')==8,'Gaining1UP preserves native equipment')
 end
 if t==50 then cap(5)end
 if t>=60 and t<90 then roulette[r('VvMeter')]=true end
 if t==92 then local n=0;for _ in pairs(roulette)do n=n+1 end;assert(n>=4,'Roulette cycles native equipment cells')end
 if t==112 then assert((r('PnBellFlags')&16)==0,'Upgrade input stops roulette after a legal purchase')end
 if t==140 then cap(7)end
 if t==154 then assert((r('PnBellFlags')&1)~=0,'Physical Blue Bell arms the special');paletteBefore=colors()end
 if t==158 then
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
  w('Enemy_X_Position',180);w('Enemy_PageLoc',0);w('Enemy_Y_Position',176);w('Enemy_Y_HighPos',1);w('Enemy_X_Speed',0)
 end
 if t>=165 and t<260 and emu.read(0x3f00,emu.memType.nesPpuDebug)==0x20 then sawWhite=true end
 if t==210 then assert(kills>=1,'Super Bomb defeats a real SMB enemy through its native callback');shot('blue-bomb')end
 if t==275 then
  assert((r('PnBellFlags')&1)==0 and r('PnActive',27)==0,'Super Bomb reaches native completion')
  assert(sawWhite,'Super Bomb visibly flashes the world')
  assert(restoredPackets>0,'Super Bomb restores every captured palette color through an actual complete PPU packet')
 end
 if t==300 then cap(9)end
 if t==315 then assert(r('PnRedRemaining')==3 and(r('PnBellFlags')&4)~=0,'Physical Red Bell supplies exactly3charges')end
 if t==375 then shot('red-crest')end
 if t>=400 and not bigStart and redFires==3 and(r('PnBellFlags')&4)==0 then
  assert(r('PnRedRemaining')==0,'Exactly3Red charges were spent')
  bigStart=t+20
 end
 if bigStart and t==bigStart then arena();cap(8);bigNative=nativeTicks end
 if bigStart and t==bigStart+90 then assert((r('PnBellFlags')&2)~=0 and r('PnSkin')==({17,19,20})[PN_VARIANT],'Physical flashing Bell transforms into native Big');shot('big-bell')end
 if bigStart and t==bigStart+120 then
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
  w('Enemy_X_Position',72);w('Enemy_PageLoc',0);w('Enemy_Y_Position',120);w('Enemy_Y_HighPos',1);w('Enemy_X_Speed',0)
 end
 if bigStart and t==bigStart+150 then assert(r('MmDeathFlag')==0,'Big protects the ship from real body contact')end
 if bigNative and nativeTicks>=bigNative+1536 then
  assert((r('PnBellFlags')&2)==0 and r('PnSkin')==PN_VARIANT,'Big expires and restores its original character skin')
  assert(r('PnMissing')==0,'Every Red/Big/body pose is present')
  assert(paletteReads>=64,'Actual NMI palette reads were checked')
  local f=assert(io.open(OUTPUT..'bell-proof.json','w'));f:write(string.format('{"variant":%d,"frames":%d,"redShots":%d,"paletteReads":%d,"missingPoses":%d,"passed":true,"scope":"Real menu plus explicitly seeded physical Bell/roulette actors, native upgrade input, SuperBomb enemy damage and palette restoration, three Red shots, full Big duration. No all-roster/campaign/audio-parity claim."}',PN_VARIANT,t,redFires,paletteReads,r('PnMissing')));f:close()
  print('PASS Parodius physical Bell integration v'..PN_VARIANT);emu.stop(0)
 end
 assert(wall<7000,string.format('Bounded Bell integration: red=%d active=%02x flags=%02x nativeTicks=%d',redFires,r('PnActive',27),r('PnBellFlags'),nativeTicks))
end,emu.eventType.endFrame)
