-- Original Rygar: controller inputs and read-only OAM / screen observations.
local frame=0
local file=assert(io.open(NATIVE_OUTPUT..'motion.csv','w'))
file:write('frame,buttons,bodyLeft,bodyCenter,bodyTop,diskLeft,diskCenter,diskY,chainX,chainCount,diskTile\n')
local buttons=0
emu.addEventCallback(function()
 local b={start=frame==120,b=frame==300 or frame==340 or frame==380 or frame==420,
  down=frame>=330 and frame<358,left=frame>=320 and frame<325,
  a=frame>=370 and frame<390,right=frame>=410 and frame<435}
 buttons=(b.b and 64 or 0)+(b.down and 4 or 0)+(b.left and 2 or 0)+(b.right and 1 or 0)+(b.a and 128 or 0)
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=290 and frame<=450 then
  local o={};for i=0,255 do o[i]=emu.read(i,emu.memType.nesSpriteRam) end
  local left,top=256,256
  for i=4,7 do if o[i*4]<240 then left=math.min(left,o[i*4+3]);top=math.min(top,o[i*4]+1) end end
  local disk,dy,dt=256,-1,-1;local chains={}
  for i=0,63 do
   local y,t,x=o[i*4],o[i*4+1],o[i*4+3]
   if y<240 and (t==0x46 or t==0x48) then disk=math.min(disk,x);dy=y+1;dt=t end
   if y<240 and t==0x4c then chains[#chains+1]=x end
  end
  file:write(table.concat({frame,buttons,left,left<256 and left+8 or -1,top,disk<256 and disk or -1,disk<256 and disk+8 or -1,dy,table.concat(chains,':'),#chains,dt},',')..'\n')
  local f=assert(io.open(NATIVE_OUTPUT..frame..'.png','wb'));f:write(emu.takeScreenshot());f:close()
  local function dump(suffix,address,size,kind)
   local bytes={};for i=0,size-1 do bytes[#bytes+1]=string.char(emu.read(address+i,kind)) end
   local out=assert(io.open(NATIVE_OUTPUT..'rygar-'..frame..suffix,'wb'));out:write(table.concat(bytes));out:close()
  end
  dump('.oam',0,256,emu.memType.nesSpriteRam)
  dump('.chr',0,8192,emu.memType.nesPpuDebug)
  dump('.pal',0x3f00,32,emu.memType.nesPpuDebug)
 end
 if frame==451 then file:close();print('PASS original Rygar controller-only disk motion capture');emu.stop(0) end
end,emu.eventType.endFrame)
