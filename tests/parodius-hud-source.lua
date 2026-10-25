-- Ordinary controls on the authenticated original cartridge, for HUD research.
-- No inventory, health, position, mapper, or original-ROM memory writes.
local variant=assert(PN_SOURCE_VARIANT)
assert(variant>=1 and variant<=3)
local frame=0
local capturedHud=false
local function pulse(first)return frame>=first and frame<first+8 end
emu.addEventCallback(function()
 local down=pulse(280)or(variant>=2 and pulse(304))or(variant>=3 and pulse(328))
 emu.setInput({start=pulse(120)or pulse(240),down=down,right=pulse(420),
               a=pulse(360)or pulse(480)or pulse(600),b=frame>=700},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==1798 then
  emu.addMemoryCallback(function()
   if capturedHud then return end
   local s=emu.getState()
   if s['ppu.scanline']~=216 then return end
   capturedHud=true
   local h=assert(io.open(OUTPUT..'hud-ppu.bin','wb'))
   for a=0,0x3fff do h:write(string.char(emu.read(a,emu.memType.nesPpuDebug)))end
   h:close()
   h=assert(io.open(OUTPUT..'hud-capture-time.txt','w'))
   h:write('frame='..s['ppu.frameCount']..'\nscanline='..s['ppu.scanline']..'\n')
   h:close()
  end,emu.callbackType.read,0,0x1fff,emu.cpuType.nes,emu.memType.nesPpuMemory)
 end
 if frame~=1800 then return end
 assert(capturedHud,'Original bar font was captured during its actual raster display')
 local f=assert(io.open(OUTPUT..'ppu.bin','wb'))
 for a=0,0x3fff do f:write(string.char(emu.read(a,emu.memType.nesPpuDebug)))end
 f:close()
 f=assert(io.open(OUTPUT..'screen.argb','wb'))
 for _,pixel in ipairs(emu.getScreenBuffer())do f:write(string.pack('<I4',pixel))end
 f:close()
 local s=emu.getState()
 f=assert(io.open(OUTPUT..'source-state.txt','w'))
 f:write('requested_variant='..variant..'\nframe='..s['ppu.frameCount']
         ..'\nvariant_008f='..emu.read(0x8f,emu.memType.nesDebug)
         ..'\nskin_0087='..emu.read(0x87,emu.memType.nesDebug)..'\n')
 f:close()
 print('Original Parodius HUD source captured; selection/pixels require validation')
 emu.stop(0)
end,emu.eventType.endFrame)
