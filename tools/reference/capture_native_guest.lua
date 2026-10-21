-- Read-only character-art reference capture from the user's original NES ROM.
-- This does not modify ROM, CPU RAM, registers or saved states.
local frame=0
local function binary(path,data)
 local f=assert(io.open(path,'wb'));f:write(data);f:close()
end
local function buffer(address,length,kind)
 local bytes={}
 for i=0,length-1 do bytes[#bytes+1]=string.char(emu.read(address+i,kind)) end
 return table.concat(bytes)
end
for k,v in pairs(emu.memType) do if k:lower():find('sprite') then print('SPRITE_MEMORY '..k..' '..v) end end
emu.addEventCallback(function()
 emu.setInput({start=frame==120 or (NATIVE_NAME=='pit' and frame==240),right=frame>=400 and frame<430,
  a=frame>=500 and frame<520,down=frame>=600 and frame<620,
  b=frame==650 or frame==680 or (frame>=720 and frame<740),up=frame>=720 and frame<740},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=300 and frame<=800 and frame%5==0 then
  local base=NATIVE_OUTPUT..NATIVE_NAME..'-'..frame
  binary(base..'.png',emu.takeScreenshot())
  binary(base..'.chr',buffer(0,8192,emu.memType.nesPpuDebug))
  binary(base..'.pal',buffer(0x3f00,32,emu.memType.nesPpuDebug))
  binary(base..'.oam',buffer(0,256,assert(emu.memType.nesSpriteRam)))
 end
 if frame==300 then
  local state=emu.getState()
  for k,v in pairs(state) do if k:find('ppu') and (k:lower():find('sprite') or k:lower():find('control')) then print('PPU_STATE '..k..' '..tostring(v)) end end
 end
 if frame==801 then print('PASS native '..NATIVE_NAME..' art references captured with controller input and read-only inspection');emu.stop(0) end
end,emu.eventType.endFrame)
