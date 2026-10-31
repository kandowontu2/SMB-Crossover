-- Additive passive diagnostic. The original visible-lives assertion stays exact.
local diagnostic=assert(io.open(OUTPUT..'palette-write-order.csv','w'))
diagnostic:write('seq,event,frame,phase,age,ppuFrame,cpuCycle,scanline,dot,pc,physicalBank,rawA,rawC,address,value,ctrl,latch,ppuAddress,VRAMoffset,published,screen,disabled,NmiDisable,ack,class,R0,R1,R2,NmiR0,NmiR1,P0,P2,BG,queue84hex\n')
local diagCount,diagAddr,diagLatch,diagCtrl=0,0,0,0
local function diagHex(at,count)
 local out={};for i=0,count-1 do out[#out+1]=string.format('%02x',emu.read(at+i,emu.memType.nesDebug))end;return table.concat(out)
end
local function diagEmit(event,address,value)
 if r('SelectedCharacter')~=25 or done then return end
 diagCount=diagCount+1;assert(diagCount<=30000,'Bounded passive palette diagnostics')
 local state=emu.getState();local pc=state['cpu.pc']
 local function pa(a)return string.format('%02x%02x%02x',ppu(a),ppu(a+1),ppu(a+2))end
 diagnostic:write(table.concat({diagCount,event,frame,phase,age,state['ppu.frameCount'],state['cpu.cycleCount'],state['ppu.scanline'],state['ppu.cycle'],pc,bank(pc),r('CurrentBank'),r('CurrentBankC'),address or -1,value or -1,diagCtrl,diagLatch,diagAddr,
  r('VRAM_Buffer1_Offset'),r('VRAM_Buffer_AddrCtrl'),r('ScreenRoutineTask'),r('DisableScreenFlag'),r('NmiDisable'),r('S2PaletteAck'),r('S2NativeCharacter'),r('R0'),r('R1'),r('R2'),r('NmiR0'),r('NmiR1'),pa(0x3f11),pa(0x3f19),ppu(0x3f00),diagHex(L.VRAM_Buffer1,84)},',')..'\n');diagnostic:flush()
end
emu.addMemoryCallback(function(_,value)diagCtrl=value end,emu.callbackType.write,0x2000)
emu.addMemoryCallback(function()diagLatch=0 end,emu.callbackType.read,0x2002)
emu.addMemoryCallback(function(_,value)
 if diagLatch==0 then diagAddr=((value&63)<<8)|(diagAddr&255)else diagAddr=(diagAddr&0x3f00)|value end
 diagLatch=1-diagLatch
end,emu.callbackType.write,0x2006)
emu.addMemoryCallback(function(_,value)
 local address=diagAddr&0x3fff
 if address>=0x3f00 then diagEmit('PPUDATA-palette-before',address,value)end
 diagAddr=(diagAddr+((diagCtrl&4)~=0 and32 or1))&0x3fff
end,emu.callbackType.write,0x2007)
-- Registered BEFORE the original UI DMA callback so a failure retains tuple.
emu.addMemoryCallback(function(_,page)
 if phase=='launch'and r('OperMode')==1 and r('ScreenRoutineTask')==7 then diagEmit('lives-DMA-BEFORE-original-assert',0x4014,page)end
end,emu.callbackType.write,0x4014)
for _,entry in ipairs(S2_DIAGNOSTIC_HOOKS)do
 emu.addMemoryCallback(function()
  if bank(entry.pc)==entry.bank then
   for i,value in ipairs(entry.bytes)do assert(emu.read(entry.pc+i-1,emu.memType.nesDebug)==value,'Bound exact diagnostic hook '..entry.name)end
   diagEmit(entry.name,entry.pc,-1)
  end
 end,emu.callbackType.exec,entry.pc)
end
