-- Explicit original StarTropics source-component arena. The native star/heart
-- drop fields below are the stores at original PRG24:$AE66-$AE81, not port
-- graphics or a campaign route. Native actor update/draw code remains intact.
local f=0;local reg=0;local regs={0,2,4,5,6,7,0,1}
local rows=assert(io.open(TEST_DIR..'drops.csv','w'))
rows:write('frame,flags,action,pose,dirty,x,y,kind,oam,ram,palette\n')
local mapper=assert(io.open(TEST_DIR..'mapper.csv','w'))
mapper:write('frame,scanline,select,regs,palette\n')
local function read(a)return emu.read(a,emu.memType.nesDebug)end
local function write(a,v)emu.write(a,v%256,emu.memType.nesDebug)end
local function hex(a,n,t)
 local out={};for i=0,n-1 do out[#out+1]=string.format('%02x',emu.read(a+i,t))end
 return table.concat(out)
end
emu.addMemoryCallback(function(a,v)reg=v end,emu.callbackType.write,0x8000)
emu.addMemoryCallback(function(a,v)
 regs[reg%8+1]=v
 if f>=600 then mapper:write(f..','..emu.getState()['ppu.scanline']..','..reg..','..table.concat(regs,':')..','..hex(0x3f10,16,emu.memType.nesPpuDebug)..'\n')end
end,emu.callbackType.write,0x8001)
emu.addEventCallback(function()
 emu.setInput({start=f<240,down=(f>=280 and f<285)or(f>=340 and f<345),
  a=(f>=400 and f<405)or(f>=500 and f<520)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 f=f+1
 if f==610 or f==690 then
  local heart=f==690
  for i=0,5 do write(0x300+i,0);write(0x324+i,0)end
  write(0x300,1);write(0x306,1);write(0x324,heart and 0xa2 or 0x92)
  write(0x348,heart and 0x80 or 0x81);write(0x330,0x40);write(0x354,7)
  write(0xbe,read(0x50)+32);write(0xca,read(0x34));write(0xb8,0)
  write(0xc4,read(0x50)+32);write(0x31e,0)
  write(0x32a,0);write(0x34e,0);write(0x33c,0);write(0x438,0);write(0x440,0)
 end
 if f>=600 then
  rows:write(f..','..read(0x324)..','..read(0x300)..','..read(0x348)..','..read(0x354)..','..read(0xbe)..','..read(0xca)..','..(f>=690 and 'heart' or 'star')..','..hex(0,256,emu.memType.nesSpriteRam)..','..hex(0,2048,emu.memType.nesDebug)..','..hex(0x3f10,16,emu.memType.nesPpuDebug)..'\n')
  local p=assert(io.open(TEST_DIR..'frame-'..f..'.png','wb'));p:write(emu.takeScreenshot());p:close()
 end
 if f==770 then rows:close();mapper:close();print('PASS original native drop arena capture; arrangement only, no campaign claim');emu.stop(0)end
end,emu.eventType.endFrame)
