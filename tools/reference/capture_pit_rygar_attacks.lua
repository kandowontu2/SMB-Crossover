-- Read-only controller capture of native crouch/ground/air attacks.
local frame=0
local function save(path,data)
 local f=assert(io.open(path,'wb'));f:write(data);f:close()
end
local function bytes(address,length,kind)
 local out={};for i=0,length-1 do out[#out+1]=string.char(emu.read(address+i,kind)) end
 return table.concat(out)
end
emu.addEventCallback(function()
 emu.setInput({start=frame==120 or (NATIVE_NAME=='pit' and frame==240),
  down=frame>=320 and frame<375,b=frame==340 or frame==400 or frame==455 or frame==510,
  a=frame>=450 and frame<470,up=frame>=500 and frame<530},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=300 and frame<=550 then
  local base=NATIVE_OUTPUT..NATIVE_NAME..'-'..frame
  save(base..'.png',emu.takeScreenshot())
  save(base..'.chr',bytes(0,8192,emu.memType.nesPpuDebug))
  save(base..'.pal',bytes(0x3f00,32,emu.memType.nesPpuDebug))
  save(base..'.oam',bytes(0,256,emu.memType.nesSpriteRam))
 end
 if frame==551 then print('PASS native '..NATIVE_NAME..' attack references');emu.stop(0) end
end,emu.eventType.endFrame)
