-- Ordinary native controller input; all memory/OAM/CHR access is read-only.
local frame=0
local out=assert(io.open(NATIVE_OUTPUT..'walk.csv','w'))
out:write('frame,left,top,tiles,attrs\n')
emu.addEventCallback(function()
 emu.setInput({start=frame==120,right=frame>=300 and frame<400,left=frame>=430 and frame<490},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=290 and frame<=500 then
  local left,top=256,256;local tiles,attrs={},{}
  for i=4,7 do
   local y=emu.read(i*4,emu.memType.nesSpriteRam)
   if y<240 then left=math.min(left,emu.read(i*4+3,emu.memType.nesSpriteRam));top=math.min(top,y+1) end
   tiles[#tiles+1]=emu.read(i*4+1,emu.memType.nesSpriteRam);attrs[#attrs+1]=emu.read(i*4+2,emu.memType.nesSpriteRam)
  end
  out:write(table.concat({frame,left,top,table.concat(tiles,':'),table.concat(attrs,':')},',')..'\n')
  for _,s in ipairs({{'.ram',0,2048,emu.memType.nesDebug},{'.oam',0,256,emu.memType.nesSpriteRam},{'.chr',0,8192,emu.memType.nesPpuDebug},{'.pal',0x3f00,32,emu.memType.nesPpuDebug}}) do
   local bytes={};for i=0,s[3]-1 do bytes[#bytes+1]=string.char(emu.read(s[2]+i,s[4])) end
   local f=assert(io.open(NATIVE_OUTPUT..'rygar-'..frame..s[1],'wb'));f:write(table.concat(bytes));f:close()
  end
 end
 if frame==501 then out:close();print('PASS original Rygar walking capture, controller-only');emu.stop(0) end
end,emu.eventType.endFrame)
