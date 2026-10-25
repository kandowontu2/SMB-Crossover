-- Original-cartridge observation with explicitly granted contact protection.
-- This is source research, not a controller-only clear.
local frame=0
local function r(a)return emu.read(a,emu.memType.nesDebug)end
local function file(n,d)local f=assert(io.open(OUTPUT..n,'wb'));f:write(d);f:close()end
local changes=assert(io.open(OUTPUT..'pickup-types.csv','w'))
changes:write('frame,pc,bank,slot,type,active,x,y,frameId,group,phase,aux\n')
local seen={}
emu.addMemoryCallback(function(a,v)
 if v<4 or v>10 then return end
 local i=a-0x6200;local s=emu.getState();local p=emu.convertAddress(s['cpu.pc'])
 changes:write(table.concat({frame,string.format('%04x',s['cpu.pc']),p and p.address//8192 or -1,i,v,r(0x6500+i),r(0x6260+i),r(0x62c0+i),r(0x6410+i),r(0x66e0+i),r(0x64a0+i),r(0x64d0+i)},',')..'\n')
 if not seen[v]then seen[v]=frame end
end,emu.callbackType.write,0x621c,0x622f)
emu.addMemoryCallback(function()
 local p=emu.convertAddress(0x8000)
 if p and p.address//8192==10 and frame>700 then emu.write(0x5b,60,emu.memType.nesDebug)end
end,emu.callbackType.exec,0x806a)
emu.addEventCallback(function()
 local b={start=frame==120 or frame==240,down=frame==280,right=frame==420,
          a=frame==360 or frame==480 or frame==600,
          b=frame>=700 and frame%8<3}
 -- Stay in the upper-middle lane and shoot through the scripted enemy waves.
 if frame>=700 then b.up=r(0x62c0)>80;b.down=r(0x62c0)<76 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 for i=28,47 do
  local kind=r(0x6200+i)
  if kind>=4 and kind<=10 and r(0x6500+i)~=0 and seen['capture'..kind]==nil then
   seen['capture'..kind]=frame
   file('pickup-'..kind..'.png',emu.takeScreenshot())
   local ram={};for a=0x6200,0x67ff do ram[#ram+1]=string.char(r(a))end
   file('pickup-'..kind..'-actors.bin',table.concat(ram))
  end
 end
 if frame==6000 then
  file('endpoint.png',emu.takeScreenshot());changes:close()
  print('PASS original Parodius pickup observation');emu.stop(0)
 end
end,emu.eventType.endFrame)
