-- The user's unmodified DuckTales ROM. Controller input and read-only captures.
local frame=0
local function dump(path,address,length,kind)
 local f=assert(io.open(path,'wb'));for i=0,length-1 do f:write(string.char(emu.read(address+i,kind)))end;f:close()
end
local audio=SCROOGE_AUDIO and assert(io.open(SCROOGE_OUTPUT..'amazon.csv','w'))or nil
local last={}
if audio then
 audio:write('frame,register,value\n')
 emu.addMemoryCallback(function(a,v)
  last[a]=v
  if frame>=300 then audio:write((frame-300)..','..(a-0x4000)..','..v..'\n')end
 end,emu.callbackType.write,0x4000,0x4015)
end
local motion=not audio and assert(io.open(SCROOGE_OUTPUT..'motion.csv','w'))or nil
if motion then motion:write('frame,y,oam\n')end
emu.addEventCallback(function()
 emu.setInput({start=frame>=60 and frame<66,a=(frame>=150 and frame<156)or(not audio and frame>=400 and frame<410),
  down=not audio and frame>=415 and frame<600,b=not audio and((frame>=415 and frame<600)or(frame>=705 and frame<711)),
  right=not audio and frame>=650 and frame<690},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if audio and frame==300 then
  for a=0x4000,0x400f do audio:write('0,'..(a-0x4000)..','..(last[a]or 0)..'\n')end
  audio:write('0,21,'..(last[0x4015]or 15)..'\n')
 end
 if not audio and frame>=300 and frame<=760 then
  local base=SCROOGE_OUTPUT..'scrooge-'..frame
  dump(base..'.chr',0,8192,emu.memType.nesPpuDebug)
  dump(base..'.pal',0,32,emu.memType.nesPaletteRam)
  dump(base..'.oam',0,256,emu.memType.nesSpriteRam)
  local f=assert(io.open(base..'.png','wb'));f:write(emu.takeScreenshot());f:close()
  local tiles={};for s=0,63 do local y=emu.read(s*4,emu.memType.nesSpriteRam);local a=emu.read(s*4+2,emu.memType.nesSpriteRam)
   if y>60 and y<205 and(a&3)==0 then tiles[#tiles+1]=tostring(emu.read(s*4+1,emu.memType.nesSpriteRam))end
  end
  motion:write(frame..','..emu.read(0x640,emu.memType.nesDebug)..','..table.concat(tiles,' ')..'\n')
 end
 if frame==(audio and 10300 or 761)then
  if audio then audio:close()else motion:close()end
  print('PASS native DuckTales controller reference '..(audio and 'Amazon APU music' or 'walk, jump, cane/pogo OAM and motion'));emu.stop(0)
 end
end,emu.eventType.endFrame)
