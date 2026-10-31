-- Passive timing only. Original route/render deadline assertions stay intact.
local P=assert(FF_NMI_PROFILE)
local f=assert(io.open(ROSTER_CONFIG.prefix..'NMI-budget.csv','w'))
f:write('record,event,ppuFrame,cycle,elapsed,scanline,dot,pc,bank,mode,task,engine,x,disabled,softDisabled,ctrl,offset,palettePending,paletteFamily,PPUDATAwrites,value,queue84hex\n')
local q,count=nil,0
local function r(n)return emu.read(assert(P.ram[n],n),emu.memType.nesDebug)end
local function bank(pc)local a=emu.convertAddress(pc);return a and a.address//8192 or -1 end
local function log(name,value)
 if not q then return end
 count=count+1;assert(count<=30000,'Bounded passive NMI budget events')
 local s=emu.getState();local queue={}
 for i=0,83 do queue[#queue+1]=string.format('%02x',emu.read(P.ram.VRAM_Buffer1+i,emu.memType.nesDebug))end
 f:write(table.concat({count,name,s['ppu.frameCount'],s['cpu.cycleCount'],s['cpu.cycleCount']-q.start,s['ppu.scanline'],s['ppu.cycle'],s['cpu.pc'],bank(s['cpu.pc']),r('OperMode'),r('OperMode_Task'),r('GameEngineSubroutine'),r('Player_X_Position')+256*r('Player_PageLoc'),r('DisableScreenFlag'),r('NmiDisable'),r('VRAM_Buffer_AddrCtrl'),r('VRAM_Buffer1_Offset'),r('SmFreezePalettePending'),r('SmFreezeLastBlue'),q.writes,value or -1,table.concat(queue)},',')..'\n');f:flush()
end
local function valid(h)
 local b=bank(h.pc)
 if b~=h.bank and not(h.bank==127 and b==125)then return false end
 for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Actual timing hook '..h.name)end
 return true
end
for _,h in ipairs(P.hooks)do
 emu.addMemoryCallback(function()
  if not valid(h)then return end
  if h.name=='NonMaskableInterrupt'then
   if r('SelectedCharacter')~=22 then return end
   assert(q==nil,'Prior NMI completed before next entry')
   q={start=emu.getState()['cpu.cycleCount'],writes=0};log('NMI-entry')
  elseif h.name=='NMI-return'then log('NMI-return');q=nil
  else log(h.name)end
 end,emu.callbackType.exec,h.pc)
end
emu.addMemoryCallback(function()if q then q.writes=q.writes+1 end end,emu.callbackType.write,0x2007)
emu.addMemoryCallback(function(_,value)log('PPUMASK',value)end,emu.callbackType.write,0x2001)
emu.addMemoryCallback(function(_,value)log('DMA-request',value)end,emu.callbackType.write,0x4014)
