-- Original donor discovery; controller input/read-only snapshots only.
local frame=0
local samples=assert(io.open(OUTPUT..'observations.csv','w'))
samples:write('frame,mode,player,playerX,playerY,buttons\n')
local function read(a)return emu.read(a,emu.memType.nesDebug)end
local function dump(name,n,mem)
 local f=assert(io.open(OUTPUT..name,'wb'));local bytes={}
 for i=0,n-1 do bytes[#bytes+1]=string.char(emu.read(i,mem))end
 f:write(table.concat(bytes));f:close()
end
emu.addEventCallback(function()
 frame=frame+1
 local start=(frame>=65 and frame<=68)or(frame>=180 and frame<=183)
 emu.setInput({start=start},0,0)
 if frame%30==0 then
  samples:write(table.concat({frame,read(0x7e2),read(0x726),read(0x90),read(0xa2),start and16 or0},',')..'\n');samples:flush()
 end
 if frame==120 or frame==240 or frame==360 then
  local png=assert(io.open(OUTPUT..'frame'..frame..'.png','wb'));png:write(emu.takeScreenshot());png:close()
  dump('ram'..frame..'.bin',2048,emu.memType.nesDebug)
 end
 if frame==360 then
  samples:close()
  dump('palette.bin',32,emu.memType.nesPaletteRam)
  emu.stop(0)
 end
end,emu.eventType.startFrame)
