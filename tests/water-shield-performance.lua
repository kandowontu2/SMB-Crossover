-- Empty native floor isolates shield CPU cost; every projectile still updates.
local c=WATER_CHARACTER or 9
local frame=0
local irqDepth,irqStart,interruptCycles=0,0,0
local begin,drawBegin,interruptAt,drawInterruptAt
local stats={physics={},draw={},lag=0,lagFrames={},updates=0,game={draw={},skip={}},dma=0,expFrames=0,expLag=0,expDma=0}
local gameBegin,gameInterrupt,gameDrew
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function cycles()return emu.getState()['cpu.cycleCount']end
local function expansion()
 if frame<900 or r('SsWaterExpand')==0 then return false end
 local count=0
 for i=0,9 do if r('RgShotType',i)==17 and r('SsHidden',i)==0 then count=count+1 end end
 return count==8
end
local function interrupt()
 if irqDepth==0 then irqStart=cycles()end
 irqDepth=irqDepth+1
end
local function resume()
 irqDepth=irqDepth-1
 if irqDepth==0 then interruptCycles=interruptCycles+cycles()-irqStart end
end
emu.addMemoryCallback(function()
 interrupt()
 if frame>=800 and frame<900 and r('NmiDisable')>=128 then stats.lag=stats.lag+1;stats.lagFrames[#stats.lagFrames+1]=frame end
 if expansion()then
  stats.expFrames=stats.expFrames+1
  if r('NmiDisable')>=128 then stats.expLag=stats.expLag+1 end
 end
end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(resume,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addMemoryCallback(interrupt,emu.callbackType.exec,L.IrqScrollSplit)
emu.addMemoryCallback(resume,emu.callbackType.exec,L.IrqScrollSplit_RTI)
emu.addMemoryCallback(function()
 if frame>=550 and irqDepth==0 then gameBegin=cycles();gameInterrupt=interruptCycles;gameDrew=false end
end,emu.callbackType.exec,L.GameLoop)
emu.addMemoryCallback(function()
 if gameBegin and irqDepth==0 and r('CurrentBank')%128==4 then gameDrew=true end
end,emu.callbackType.exec,L.DrawAllMetasprites)
emu.addMemoryCallback(function(_,v)
 if v==0 and gameBegin and irqDepth==0 then
  if frame>=800 and frame<900 then
   local t=stats.game[gameDrew and 'draw' or 'skip'];t[#t+1]=cycles()-gameBegin-(interruptCycles-gameInterrupt)
  end
  gameBegin=nil
 end
end,emu.callbackType.write,L.NmiDisable)
emu.addMemoryCallback(function()
 if frame>=800 and frame<900 then stats.dma=stats.dma+1 end
 if expansion()then stats.expDma=stats.expDma+1 end
end,emu.callbackType.write,0x4014)
local function phase()
 local n=0
 for i=0,9 do if r('RgShotType',i)==17 and r('SsHidden',i)==0 then n=n+1 end end
 if n==8 then return r('SsWaterExpand')==0 and 'orbit' or 'expand'end
end
emu.addMemoryCallback(function()
 if frame>=550 and irqDepth==0 and r('CurrentBank')%128==60 then begin=cycles();interruptAt=interruptCycles end
end,emu.callbackType.exec,L.SpecialWeapons)
emu.addMemoryCallback(function()
 if begin and irqDepth==0 and r('CurrentBank')%128==60 then
  stats.updates=stats.updates+1
  local p=phase()
  if p then local t=stats.physics[p]or{};t[#t+1]=cycles()-begin-(interruptCycles-interruptAt);stats.physics[p]=t end
  begin=nil
 end
end,emu.callbackType.exec,L.SpecialWeaponsFinish)
emu.addMemoryCallback(function()
 if frame>=550 and irqDepth==0 and r('CurrentBank')%128==60 then drawBegin=cycles();drawInterruptAt=interruptCycles end
end,emu.callbackType.exec,L.SpecialDrawShots)
emu.addMemoryCallback(function()
 if drawBegin and irqDepth==0 and r('CurrentBank')%128==60 then
  local p=phase()
  if p then local t=stats.draw[p]or{};t[#t+1]=cycles()-drawBegin-(interruptCycles-drawInterruptAt);stats.draw[p]=t end
  drawBegin=nil
 end
end,emu.callbackType.exec,L.SpecialDrawFinish)
emu.addEventCallback(function()
 local choose=c==1 and frame==80 or c==9 and(frame==100 or frame==120 or frame==140)
 emu.setInput({right=choose,down=c==9 and frame==80,start=frame==200,b=frame>=560 and frame<565 or frame>=900 and frame<905},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=540 then for i=0,5 do w('Enemy_Flag',0,i)end end
 if frame==550 then
  assert(r('SelectedCharacter')==c,'Selected shield user')
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
  w('Player_X_Position',96);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
  w('PlayerStatus',1);w('InvOwnedLo',129,c);w('InvSelected',7,c);w('InvAmmo',112,c*16+7);w('InvDirty',1)
 end
 if frame==1200 then
  local f=assert(io.open(OUTPUT..ROM_NAME..'-water-performance-'..c..'.csv','w'));f:write('routine,phase,samples,average,maximum\n')
  for _,kind in ipairs({'physics','draw'})do for _,p in ipairs({'orbit','expand'})do
   local t=assert(stats[kind][p],kind..'/'..p);local total,maximum=0,0
   for _,v in ipairs(t)do total=total+v;maximum=math.max(maximum,v)end
   assert(#t>=15,'Full shield phase sampled')
   local avg=math.floor(total/#t);f:write(table.concat({kind,p,#t,avg,maximum},',')..'\n')
   if p=='orbit' then
    assert(avg<=(kind=='physics'and 4200 or 3400),'Water Shield retains its measured CPU improvement: '..kind..' '..avg)
   elseif kind=='physics' then
    assert(avg<=5600 and maximum<=6100,'Water expansion retains exact-vector CPU improvement: '..avg..'/'..maximum)
   end
   print('PASS PROFILE character '..c..' '..kind..' '..p..': '..avg..' average / '..maximum..' max exclusive CPU cycles, '..#t..' samples')
  end end
  f:write('lag,full-orbit-hardware-frames,100,'..stats.lag..','..stats.updates..'\n')
  for _,kind in ipairs({'draw','skip'})do
   local t=stats.game[kind];local total,maximum=0,0;for _,v in ipairs(t)do total=total+v;maximum=math.max(maximum,v)end
   f:write(table.concat({'GameLoop',kind,#t,#t>0 and math.floor(total/#t)or 0,maximum},',')..'\n')
   print('PASS PROFILE GameLoop '..kind..': '..(#t>0 and math.floor(total/#t)or 0)..' average / '..maximum..' max exclusive CPU cycles, '..#t..' samples')
  end
  f:write('OAM-DMA,full-orbit-hardware-frames,100,'..stats.dma..','..stats.dma..'\n')
  f:write('OAM-DMA,full-expansion-hardware-frames,'..stats.expFrames..','..stats.expDma..','..stats.expLag..'\n');f:close()
  local mmc5=ROM_NAME:find('mmc5')~=nil
  local maxLag=c==1 and 0 or(mmc5 and 5 or 15)
  local minDma=c==1 and 100 or(mmc5 and 95 or 85)
  print('PROFILE orbit skipped hardware frames: '..table.concat(stats.lagFrames,','))
  assert(stats.expFrames>=50,'A substantial full eight-ball expansion was measured')
  assert(stats.expDma>=(mmc5 and math.ceil(stats.expFrames*0.80)or math.floor(stats.expFrames*0.50)),'Expansion completes actual OAM DMA on the improved hardware-frame bound: '..stats.expDma..'/'..stats.expFrames)
  assert(stats.lag<=maxLag,'Water Shield hardware-frame stalls stay within measured bound: '..stats.lag)
  assert(stats.dma>=minDma,'Water Shield completes actual sprite DMA on enough hardware frames: '..stats.dma)
  print('PASS PROFILE Water Shield completed OAM DMA '..stats.dma..'/100 hardware frames')
  print('PASS PROFILE Water Shield full-expansion completed OAM DMA '..stats.expDma..'/'..stats.expFrames..' hardware frames, lag '..stats.expLag)
  print('PASS PROFILE Water Shield full-orbit lag '..stats.lag..'/100 hardware frames');emu.stop(0)
 end
end,emu.eventType.endFrame)
