-- Explicit flat-floor profiler: completed main-loop work, physical lag and OAM
-- DMA for idle/cane/pogo, both with an empty room and six native actors.
local frame=0
local depth,start,interrupts=0,0,0
local begin,beganInterrupt,kind
local rows={}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function cycles()return emu.getState()['cpu.cycleCount']end
local function phase()
 if frame>=650 and frame<750 then return 'idle-empty'end
 if frame>=800 and frame<900 then return 'cane-empty'end
 if frame>=950 and frame<1050 then return 'cane-six-actors'end
 if frame>=1100 and frame<1200 then return 'pogo-six-actors'end
 if frame>=1250 and frame<1350 then return 'idle-six-actors'end
end
local function row(name)if not rows[name]then rows[name]={samples={},lag=0,dma=0}end;return rows[name]end
local function interrupt()if depth==0 then start=cycles()end;depth=depth+1 end
local function resume()depth=depth-1;if depth==0 then interrupts=interrupts+cycles()-start end end
emu.addMemoryCallback(function()interrupt();local p=phase();if p and r('NmiDisable')>=128 then row(p).lag=row(p).lag+1 end end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(resume,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addMemoryCallback(interrupt,emu.callbackType.exec,L.IrqScrollSplit)
emu.addMemoryCallback(resume,emu.callbackType.exec,L.IrqScrollSplit_RTI)
emu.addMemoryCallback(function()if depth==0 and phase()then begin=cycles();beganInterrupt=interrupts;kind=phase()end end,emu.callbackType.exec,L.GameLoop)
emu.addMemoryCallback(function(_,v)
 if v==0 and begin and depth==0 then
  local a=row(kind).samples;a[#a+1]=cycles()-begin-(interrupts-beganInterrupt);begin=nil
 end
end,emu.callbackType.write,L.NmiDisable)
emu.addMemoryCallback(function()local p=phase();if p then row(p).dma=row(p).dma+1 end end,emu.callbackType.write,0x4014)
emu.addEventCallback(function()
 local attack=(frame>=800 and frame<1050 and frame%16<4)or(frame>=1100 and frame<1200)
 emu.setInput({down=frame==80 or(frame>=1100 and frame<1200),right=frame==100 or frame==120,start=frame==200,b=attack},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if phase()then assert(r('GameEngineSubroutine')==8,'Every profile sample measures active gameplay')end
 if frame==620 then
  assert(r('SelectedCharacter')==12,'Scrooge selected for profiling')
  for i=0,415 do w('Block_Buffer_1',0,i)end
  for p=0,1 do for c=0,15 do w('Block_Buffer_1',0x54,p*208+176+c)end end
  for i=0,5 do w('Enemy_Flag',0,i)end
  w('Player_X_Position',96);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
  w('Player_State',0);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('PlayerFacingDir',1)
  w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 end
 if frame==940 then
  w('InjuryTimer',255)
  for i=0,5 do
   w('Enemy_Flag',1,i);w('Enemy_ID',6,i);w('Enemy_State',0,i);w('Enemy_BoundBoxCtrl',9,i)
   w('Enemy_X_Position',144+16*i,i);w('Enemy_PageLoc',0,i);w('Enemy_Y_Position',192,i);w('Enemy_Y_HighPos',1,i)
   w('Enemy_X_Speed',0,i);w('Enemy_Y_Speed',0,i);w('MmEnemyHealthLo',136,i);w('MmEnemyHealthHi',19,i)
  end
 end
 if frame>=940 and frame<1400 then
  for i=0,5 do
   assert(r('Enemy_Flag',i)>0 and r('Enemy_State',i)<32,'All six native profile actors remain active')
   w('Enemy_X_Position',144+16*i,i);w('Enemy_Y_Position',192,i);w('Enemy_X_Speed',0,i);w('Enemy_Y_Speed',0,i)
  end
 end
 if frame==1100 then
  w('InjuryTimer',255)
  w('Player_Y_Position',112);w('Player_State',2);w('Player_Y_Speed',1);w('MmVY',1,2)
  w('ScAttack',0);w('ScPogo',0);w('ScPrevious',0)
 end
 if frame==1250 then w('InjuryTimer',255)end
 if frame==1400 then
  local f=assert(io.open(OUTPUT..ROM_NAME..'-scrooge-performance.csv','w'));f:write('phase,samples,average,max,physicalLag,completedDma\n')
  for _,p in ipairs({'idle-empty','cane-empty','cane-six-actors','pogo-six-actors','idle-six-actors'})do
   local a=assert(rows[p]);local total,maximum=0,0
   for _,v in ipairs(a.samples)do total=total+v;maximum=math.max(maximum,v)end
   assert(#a.samples>=30,'A substantial sample of completed main-loop work is profiled: '..p)
   local average=math.floor(total/#a.samples)
   f:write(table.concat({p,#a.samples,average,maximum,a.lag,a.dma},',')..'\n')
   print('PASS PROFILE Scrooge '..p..': '..average..'/'..maximum..' main-loop cycles, '..a.lag..'/100 lag, '..a.dma..'/100 completed DMA')
  end
  f:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
