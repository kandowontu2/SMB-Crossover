-- Original cartridge navigation and fixed checkpoints. No state writes.
local frame=0
local dmaPage,dmaPC,dmaOffset
local snapshots={}
local checkpoints={[2695]='gate-approach',[2769]='lower-road',[2890]='west-road',[3045]='north-road'}

emu.addEventCallback(function()
 local pad={}
 if (frame>=950 and frame<955) or (frame>=1110 and frame<1115) then pad.start=true end
 if frame>=2120 and frame<2250 then pad.down=true end
 if frame>=2255 and frame<2310 then pad.left=true end
 if frame>=2315 and frame<2435 then pad.down=true end
 if frame>=2442 and frame<2513 then pad.left=true end
 if frame>=2520 and frame<2585 then pad.down=true end
 if frame>=2592 and frame<2690 then pad.left=true end
 if frame>=2702 and frame<2765 then pad.down=true end
 if frame>=2772 and frame<2885 then pad.left=true end
 if frame>=2896 and frame<3040 then pad.up=true end
 emu.setInput(pad,0)
end,emu.eventType.inputPolled)

emu.addMemoryCallback(function(_,page)
 dmaPage=page
 dmaPC=emu.getState()['cpu.pc']
 local mapped=emu.convertAddress(dmaPC)
 dmaOffset=mapped and mapped.address or -1
end,emu.callbackType.write,0x4014)

local function capture(name)
 assert(dmaPage and dmaPC,'Expected original OAM DMA')
 local sprites={}
 for i=0,63 do
  local base=dmaPage*256+4*i
  local function byte(offset) return emu.read(base+offset,emu.memType.nesDebug) end
  if byte(0)<240 then
   sprites[#sprites+1]=string.format('[%d,%d,%d,%d,%d]',i,byte(0),byte(1),byte(2),byte(3))
  end
 end
 local file=assert(io.open(OUTPUT..name..'.png','wb'))
 file:write(emu.takeScreenshot());file:close()
 snapshots[#snapshots+1]=string.format('{"frame":%d,"name":"%s","dma_page":%d,"dma_pc":%d,"dma_prg":%d,"oam":[%s]}',
  frame,name,dmaPage,dmaPC,dmaOffset,table.concat(sprites,','))
end

emu.addEventCallback(function()
 frame=frame+1
 if checkpoints[frame] then capture(checkpoints[frame]) end
 if frame==3045 then
  local file=assert(io.open(OUTPUT..'observations.json','w'))
  file:write('{"controller_only":true,"checkpoints":[',table.concat(snapshots,','),']}\n');file:close()
  emu.stop(0)
 end
end,emu.eventType.endFrame)
