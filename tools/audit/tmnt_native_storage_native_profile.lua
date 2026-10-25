-- Read-only identical-work replay: disjoint audio costs and DMC instruction clocks.
local P=assert(TMNT_STORAGE_PROFILE);local C=assert(TMNT_STORAGE_NATIVE)
local function r(n,i)return emu.read(assert(P.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local function tick()return emu.getState()['cpu.cycleCount']end
local function stamp()local s=emu.getState();return{s['ppu.frameCount'],s['ppu.scanline'],s['ppu.cycle'],s['cpu.cycleCount']}end
local function st(q)return table.concat(q,',')end
local function active()return C.entered==1 and r('SelectedCharacter')==19 and r('OperMode')==1 and r('GameEngineSubroutine')==8 end
local audio=assert(io.open(OUTPUT..'audio-components.csv','w'))
audio:write('serial,name,phase,update,startFrame,startScan,startDot,startCPU,endFrame,endScan,endDot,endCPU,inclusiveCycles,IRQCycles,CPUcycles,childCPUcycles,exclusiveCPUcycles\n')
local instructions=assert(io.open(OUTPUT..'dmc-instruction-clocks.csv','w'))
instructions:write('phase,update,bank,pc,register,value,startFrame,startScan,startDot,startCPU,endFrame,endScan,endDot,endCPU,IRQCycles,actualCPUcycles,base6502cycles,extraCycles\n')
local apu=assert(io.open(OUTPUT..'source-apu.csv','w'));apu:write('serial,song,sourceTick,register,value,frame,scan,dot,cpu\n')
local state=assert(io.open(OUTPUT..'source-state.csv','w'));state:write('serial,song,sourceTick,ZP14_RAM174_hex\n')
local irqStart,irqDepth,irqCycles=0,0,0
emu.addMemoryCallback(function()if irqDepth==0 then irqStart=tick()-7 end;irqDepth=irqDepth+1 end,emu.callbackType.exec,L.IrqScrollSplit)
emu.addMemoryCallback(function()irqDepth=irqDepth-1;assert(irqDepth>=0,'Profile IRQ balance');if irqDepth==0 then irqCycles=irqCycles+tick()-irqStart+6 end end,emu.callbackType.exec,L.IrqScrollSplit_RTI)
local stack,serial,installed={},0,{}
local sourceSerial,sourceSong,sourceTick=0,0,-1
for _,h in ipairs(P.hooks)do
 emu.addMemoryCallback(function()
  local source=h.name=='TnNativeInit'or h.name=='TnNativePlay'
  if bank(h.pc)~=h.bank or(not active()and not(source and r('SelectedCharacter')==19 and r('OperMode')==1))then return end
  serial=serial+1
  local s=emu.getState();local sp=s['cpu.sp'];local ret=(emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug)+1)%65536
  local q={serial=serial,name=h.name,phase=C.phase,update=C.step,begin=stamp(),irq=irqCycles,child=0,sp=(sp+2)%256,ret=ret,retbank=bank(ret)}
  if h.name=='TnNativeInit'then sourceSerial=sourceSerial+1;sourceSong=r('TnAudioSong');sourceTick=0;q.source=1
  elseif h.name=='TnNativePlay'then sourceSerial=sourceSerial+1;sourceSong=r('TnAudioSong');sourceTick=sourceTick+1;q.source=1 end
  stack[#stack+1]=q;local key=q.retbank..':'..ret
  if not installed[key]then installed[key]=true
   emu.addMemoryCallback(function()
    local q=stack[#stack];if not q or q.ret~=ret or q.retbank~=bank(ret)or q.sp~=emu.getState()['cpu.sp']then return end
    local finish=stamp();local elapsed=finish[4]-q.begin[4];local irq=irqCycles-q.irq;local cpu=elapsed-irq
    assert(cpu>=q.child,'Disjoint component accounting excludes IRQ exactly once')
    audio:write(table.concat({q.serial,q.name,q.phase,q.update,st(q.begin),st(finish),elapsed,irq,cpu,q.child,cpu-q.child},',')..'\n')
    table.remove(stack);if #stack>0 then stack[#stack].child=stack[#stack].child+cpu end
    if q.source then
     local t={};for i=0,13 do t[#t+1]=string.format('%02x',r('TnAudioZp',i))end;for i=0,173 do t[#t+1]=string.format('%02x',r('TnAudioRam',i))end
     state:write(table.concat({sourceSerial,sourceSong,sourceTick,table.concat(t)},',')..'\n')
    end
   end,emu.callbackType.exec,ret)
  end
 end,emu.callbackType.exec,h.pc)
end
for _,site in ipairs(C.sites)do
 emu.addMemoryCallback(function()
  if bank(site.pc)~=63 or sourceSerial==0 or r('SelectedCharacter')~=19 or r('OperMode')~=1 then return end
  local s=emu.getState();local add=site.mode=='abx'and s['cpu.x']or site.mode=='aby'and s['cpu.y']or 0
  apu:write(table.concat({sourceSerial,sourceSong,sourceTick,site.address+add,s['cpu.a'],st(stamp())},',')..'\n')
 end,emu.callbackType.exec,site.pc)
end
local pending,instructionHooks={},{}
for _,h in ipairs(P.stores)do
 emu.addMemoryCallback(function()
  if not active()or bank(h.pc)~=h.bank then return end
  local s=emu.getState();local key=h.bank..':'..(h.pc+3)
  pending[key]={h=h,begin=stamp(),irq=irqCycles,sp=s['cpu.sp'],phase=C.phase,update=C.step,value=s['cpu.a']}
  if not instructionHooks[key]then instructionHooks[key]=true
   emu.addMemoryCallback(function()
    local q=pending[key];if not q or bank(h.pc+3)~=h.bank or emu.getState()['cpu.sp']~=q.sp then return end
    pending[key]=nil;local finish=stamp();local irq=irqCycles-q.irq;local cycles=finish[4]-q.begin[4]-irq
    instructions:write(table.concat({q.phase,q.update,h.bank,h.pc,h.register,q.value,st(q.begin),st(finish),irq,cycles,4,cycles-4},',')..'\n')
   end,emu.callbackType.exec,h.pc+3)
  end
 end,emu.callbackType.exec,h.pc)
end
local stop=emu.stop
function emu.stop(code)
 if code==0 then assert(#stack==0 and irqDepth==0,'Final disjoint profile balance');audio:close();instructions:close();apu:close();state:close()end
 stop(code)
end
