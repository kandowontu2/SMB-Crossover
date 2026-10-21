-- Unmodified DuckTales empty-ground B input, selected OAM/screens only.
-- Native golf is object-conditional; this reference does not assert a swing.
local frame=0
local out=assert(io.open(OUTPUT..'native-scrooge-cane.csv','w'))
out:write('frame,y,oam\n')
emu.addEventCallback(function()
 emu.setInput({start=frame>=60 and frame<66,a=frame>=150 and frame<156,
  b=frame>=400 and frame<404},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=390 and frame<=430 then
  local rows={}
  for i=0,63 do
   local q=i*4;local y=emu.read(q,emu.memType.nesSpriteRam);local x=emu.read(q+3,emu.memType.nesSpriteRam)
   if y>=64 and y<208 and x>=80 and x<=176 then rows[#rows+1]=string.format('%d:%d:%d:%d',y,emu.read(q+1,emu.memType.nesSpriteRam),emu.read(q+2,emu.memType.nesSpriteRam),x)end
  end
  out:write(frame..','..emu.read(0x640,emu.memType.nesDebug)..','..table.concat(rows,' ')..'\n')
  if frame%5==0 then local f=assert(io.open(OUTPUT..'native-scrooge-cane-'..frame..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
 end
 if frame==431 then out:close();print('PASS native DuckTales empty-ground B reference; no free swing asserted');emu.stop(0)end
end,emu.eventType.endFrame)
