-- Read-only original-game movement evidence; controller input is the only
-- mutation. RAM snapshots help distinguish pose offsets from world motion.
local frame=0
local csv=assert(io.open(NATIVE_OUTPUT..'motion.csv','w'))
csv:write('frame,bodyLeft,bodyTop,bodyBottom,visible\n')
local ram=assert(io.open(NATIVE_OUTPUT..'ram.bin','wb'))
emu.addEventCallback(function()
 emu.setInput({start=frame==120,right=frame>=210 and frame<230,left=frame>=230 and frame<250,
  b=frame==250,a=(frame>=260 and frame<290) or (frame>=350 and frame<355)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=180 and frame<=440 then
  local left,top,bottom,visible=256,256,-1,0
  for i=4,7 do
   local y=emu.read(i*4,emu.memType.nesSpriteRam)
   if y<240 then left=math.min(left,emu.read(i*4+3,emu.memType.nesSpriteRam));top=math.min(top,y+1);bottom=math.max(bottom,y+16);visible=visible+1 end
  end
  csv:write(table.concat({frame,left,top,bottom,visible},',')..'\n')
  local bytes={};for i=0,2047 do bytes[#bytes+1]=string.char(emu.read(i,emu.memType.nesDebug)) end;ram:write(table.concat(bytes))
  if frame%10==0 then local f=assert(io.open(NATIVE_OUTPUT..frame..'.png','wb'));f:write(emu.takeScreenshot());f:close() end
 end
 if frame==441 then csv:close();ram:close();print('PASS original Rygar movement observation captured, no memory writes');emu.stop(0) end
end,emu.eventType.endFrame)
