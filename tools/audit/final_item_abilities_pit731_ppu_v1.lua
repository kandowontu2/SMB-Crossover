-- Read-only full PPU capture, registered BEFORE the original stop callback.
local pitPpu=assert(io.open(OUTPUT..'actual-ppu.argb','wb'))
local pitPpuIndex=assert(io.open(OUTPUT..'actual-ppu-index.csv','w'))
pitPpuIndex:write('ordinal,ppu_frame,scanline,dot,cpu_cycle,phase,updates,mode,tier\n')
local pitPpuFrames,pitPpuClosed=0,false
emu.addEventCallback(function()
 assert(not pitPpuClosed,'Full PPU capture closes only at the original completed-case stop')
 local s=emu.getState();local screen=emu.getScreenBuffer()
 assert(#screen==256*240,'Actual full PPU dimensions')
 local chunks={};for i,v in ipairs(screen)do chunks[i]=string.pack('<I4',v)end
 pitPpu:write(table.concat(chunks));pitPpu:flush();pitPpuFrames=pitPpuFrames+1
 pitPpuIndex:write(table.concat({pitPpuFrames,s['ppu.frameCount'],s['ppu.scanline'],s['ppu.cycle'],s['cpu.cycleCount'],phase,updates,r('CrossoverBehaviorVersion'),r('PlayerStatus')},',')..'\n');pitPpuIndex:flush()
 if done then
  pitPpu:close();pitPpuIndex:close();pitPpuClosed=true
  local f=assert(io.open(OUTPUT..'ppu-capture-native-result.json','w'))
  f:write(json({passed=true,frames=pitPpuFrames,bytes=pitPpuFrames*256*240*4,actual_mode_readback=r('CrossoverBehaviorVersion'),original_done_seen=true,scope='Full actual endFrame PPU buffer; independent raw/index integrity and agent image review remain required. Capture alone is not an ability or visual pass.'}));f:close()
 end
end,emu.eventType.endFrame)
