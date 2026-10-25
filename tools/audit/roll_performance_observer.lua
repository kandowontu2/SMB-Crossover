-- Native CPU cycles and update/draw counts. No emulated state writes.
return function(cfg)
 local frame,updates,draws=0,0,0
 local interruptDepth,interruptStart,interruptCycles=0,0,0
 local calls,returns={},{}
 local folder=cfg.out or OUTPUT
 local frames=assert(io.open(folder..'roll-performance-frames.csv','w'))
 local spans=assert(io.open(folder..'roll-performance-calls.csv','w'))
 frames:write('frame,phase,world,level,engine,enemies,bullets,updates,draws,lagNmis\n')
 spans:write('name,phase,startFrame,endFrame,cycles,isrCycles,cpuCycles,bullets,enemies\n')
 local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
 local function bank(a)return emu.convertAddress(a).address//8192 end
 local function tick()local s=emu.getState();return s['cpu.cycleCount']or s['cpu.cycle']end
 local function active()return r('SelectedCharacter')==9 and r('RlVariant')==1 and r('OperMode')==1 and r('GameEngineSubroutine')==8 end
 local function phase()return cfg.phase and cfg.phase()or'route'end
 local function fleet()
  local b,e=0,0
  for i=0,3 do if r('MmBulletType',i)~=0 then b=b+1 end end
  for i=0,5 do if r('Enemy_Flag',i)~=0 then e=e+1 end end
  return b,e
 end
 local function beginISR()if interruptDepth==0 then interruptStart=tick()end;interruptDepth=interruptDepth+1 end
 local function endISR()
  interruptDepth=interruptDepth-1;assert(interruptDepth>=0,'Balanced profiler interrupt nesting')
  if interruptDepth==0 then interruptCycles=interruptCycles+tick()-interruptStart+6 end
 end
 emu.addMemoryCallback(beginISR,emu.callbackType.exec,L.NonMaskableInterrupt)
 emu.addMemoryCallback(endISR,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
 emu.addMemoryCallback(beginISR,emu.callbackType.exec,L.IrqScrollSplit)
 emu.addMemoryCallback(endISR,emu.callbackType.exec,L.IrqScrollSplit_RTI)
 local names={'GameLoop','RlSourceMovement','RlWeapons','RlDraw','RlPublish','DrawAllMetasprites','MetaspriteRenderLoop','RlDrawRecord','RlFastRenderLoop','RlBlocks','RlEnemies'}
 for _,name in ipairs(names)do
 if L[name]then
  emu.addMemoryCallback(function()
   if not active()or interruptDepth~=0 or bank(L[name])~=B[name]then return end
   local st=emu.getState();local sp=st['cpu.sp']
   local pc=(emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1)%65536
   local b,e=fleet()
   local row={name=name,sp=(sp+2)%256,pc=pc,start=tick(),isr=interruptCycles,frame=frame,phase=phase(),bullets=b,enemies=e}
   calls[#calls+1]=row
   if not returns[pc]then
    returns[pc]=true
    emu.addMemoryCallback(function()
     if interruptDepth~=0 then return end
     local spNow=emu.getState()['cpu.sp']
     for i=#calls,1,-1 do
      local c=calls[i]
      if c.pc==pc and c.sp==spNow then
       local elapsed=tick()-c.start;local isr=interruptCycles-c.isr
       assert(elapsed>=isr,'Nonnegative native CPU span')
       spans:write(table.concat({c.name,c.phase,c.frame,frame,elapsed,isr,elapsed-isr,c.bullets,c.enemies},',')..'\n')
       table.remove(calls,i)
      end
     end
    end,emu.callbackType.exec,pc)
   end
  end,emu.callbackType.exec,L[name])
 end
 end
 emu.addMemoryCallback(function()if active()and bank(0xa000)==B.RlFrameReady then updates=updates+1 end end,emu.callbackType.exec,L.RlFrameReady)
 emu.addMemoryCallback(function()if active()and bank(0xa000)==B.DrawAllMetasprites then draws=draws+1 end end,emu.callbackType.exec,L.DrawAllMetasprites)
 local lastLag
 emu.addEventCallback(function()
  frame=frame+1
  local lag=r('NmiSkipped');local increment=lastLag and(lag-lastLag)%256 or 0;lastLag=lag
  if active()then
   local b,e=fleet();frames:write(table.concat({frame,phase(),r('WorldNumber'),r('LevelNumber'),r('GameEngineSubroutine'),e,b,updates,draws,increment},',')..'\n')
  end
  updates,draws=0,0
 end,emu.eventType.endFrame)
 return{finish=function()frames:close();spans:close();assert(interruptDepth==0,'Profiler finishes outside an ISR')end}
end
