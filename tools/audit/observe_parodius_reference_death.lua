-- Ordinary controller exploration of the authenticated original cartridge.
-- No emulated memory/register writes; a source trace, not candidate evidence.
local f=0
local function r(a)return emu.read(a,emu.memType.nesDebug)end
local function hex(a,n,kind)local s={}for i=0,n-1 do s[#s+1]=string.format('%02x',emu.read(a+i,kind))end;return table.concat(s)end
local dma,ctrl=nil,0
local scenes=assert(io.open(OUTPUT..'original-burst.csv','w'))
scenes:write('frame,pose,skin,active,drawFlags,paletteOverride,x,y,ctrl,oam,palette\n')
local seen={}
local previousPose,poseAge=nil,0
local render=assert(io.open(OUTPUT..'render-burst.csv','w'))
render:write('frame,pose,skin,active,drawFlags,paletteOverride,x,y,ctrl,oam,palette\n')
local function patterns()
 local data={}
 for i=0,7 do
  local mapped=emu.convertAddress(i*1024,emu.memType.nesPpuMemory)
  assert(mapped.address>=0 and mapped.memType==emu.memType.nesChrRom,'Original CHR mapping')
  for a=0,1023 do data[#data+1]=string.char(emu.read(mapped.address+a,mapped.memType))end
 end
 return table.concat(data)
end
local startSeen={}
emu.addEventCallback(function()
 local pose=r(0x6410)
 if pose==previousPose then poseAge=poseAge+1 else poseAge=0 end
 previousPose=pose
 if f<2000 or(r(0x6500)&16)==0 or pose==0 or poseAge<2 or startSeen[pose]then return end
 startSeen[pose]=true
 local st=emu.getState();local keys={};for k in pairs(st)do if k:find('mapper')or k:find('ppu')then keys[#keys+1]=k end end;table.sort(keys)
 local state=assert(io.open(OUTPUT..'start-state-'..pose..'.txt','w'))
 for _,k in ipairs(keys)do state:write(k..'='..tostring(st[k])..'\n')end
 for i=0,7 do local a=emu.convertAddress(i*1024,emu.memType.nesPpuMemory);state:write('converted'..i..'='..tostring(a.address)..':'..tostring(a.memType)..'\n')end
 state:close()
 local chr=assert(io.open(OUTPUT..'start-ppu-'..pose..'.bin','wb'));chr:write(patterns());chr:close()
 render:write(table.concat({f,pose,r(0x87),r(0x6500),r(0x63e0),r(0x6440),r(0x6260),r(0x62c0),ctrl,hex(0,256,emu.memType.nesSpriteRam),hex(0x3f00,32,emu.memType.nesPpuDebug)},',')..'\n')
end,emu.eventType.startFrame)
emu.addMemoryCallback(function(_,page)dma=hex(page*256,256,emu.memType.nesDebug)end,emu.callbackType.write,0x4014)
emu.addMemoryCallback(function(_,value)ctrl=value end,emu.callbackType.write,0x2000)
local out=assert(io.open(OUTPUT..'reference.csv','w'))
out:write('frame,mode,character,active,pose,animation,cursor,delay,x,y\n')
local pulses={[120]=true,[250]=true,[400]=true,[600]=true,[800]=true,[1500]=true}
emu.addEventCallback(function()
 emu.setInput({start=pulses[f]or pulses[f-1],a=f==1100 or f==1101 or f==1400 or f==1401 or f==1700 or f==1701,
 right=(f>=280 and f<340)or((REFERENCE_VARIANT or 1)>=2 and(f==350 or f==351))or((REFERENCE_VARIANT or 1)>=3 and(f==380 or f==381))or f>=1600,b=f>=1600},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 f=f+1
 out:write(table.concat({f,r(0x8b),r(0x8f),r(0x6500),r(0x6410),r(0x6770),r(0x6740),r(0x6710),r(0x6260),r(0x62c0)},',')..'\n')
 if f>2000 and(r(0x6500)&16)~=0 and r(0x6410)~=0 and poseAge>=3 and not seen[r(0x6410)]and dma then
  -- Completed image only. Physical CHR is captured at startFrame above:
  -- the original remaps every page to blank51 during vertical blank.
  scenes:write(table.concat({f,r(0x6410),r(0x87),r(0x6500),r(0x63e0),r(0x6440),r(0x6260),r(0x62c0),ctrl,dma,hex(0x3f00,32,emu.memType.nesPpuDebug)},',')..'\n')
  local shot=assert(io.open(OUTPUT..'original-burst-'..r(0x6410)..'.png','wb'));shot:write(emu.takeScreenshot());shot:close();seen[r(0x6410)]=true
 end
 if f%200==0 then local p=assert(io.open(OUTPUT..'reference-'..f..'.png','wb'));p:write(emu.takeScreenshot());p:close()end
 if f==4000 then out:close();scenes:close();render:close();print('PASS bounded original reference controller exploration');emu.stop(0)end
end,emu.eventType.endFrame)
