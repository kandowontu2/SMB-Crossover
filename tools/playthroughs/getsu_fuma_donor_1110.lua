-- Original cartridge navigation and fixed checkpoints. No state writes.
local frame=0
local dmaPage,dmaPC,dmaOffset,ppuControl
local snapshots={}
local turns={
 {'down',2}, {'left',2}, {'up',4}, {'right',2}, {'up',4},
 {'right',2}, {'up',2}, {'left',1}, {'up',5}, {'left',2},
}
local pathStart=3052
for _,turn in ipairs(turns) do
 local untilFrame=pathStart+32*turn[2]
 turn[3],turn[4]=pathStart,untilFrame
 pathStart=untilFrame+8
end
local stageStart=pathStart+80
local phases={
 {0,12,'idle',{}}, {12,33,'walk',{left=true}}, {33,51,'brake',{}},
 {51,76,'jump',{a=true}}, {76,117,'land',{}}, {117,127,'sword',{b=true}},
 {127,150,'recover',{}}, {150,166,'crouch',{down=true}},
 {166,176,'crouch-sword',{down=true,b=true}}, {176,200,'finish',{}},
}
local marks={
 [0]={'zone-entry',true}, [12]={'idle'}, [32]={'walk',true}, [50]={'brake'},
 [56]={'jump-rise'}, [72]={'jump',true}, [94]={'jump-fall'}, [116]={'land'},
 [120]={'sword-start'}, [124]={'sword',true}, [149]={'recover'},
 [165]={'crouch'}, [170]={'crouch-sword'}, [199]={'finish'},
}
local writers={}
local phase='route'

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
 for _,turn in ipairs(turns) do
  if frame>=turn[3] and frame<turn[4] then pad[turn[1]]=true;break end
 end
 if frame>=stageStart then
  local tick=frame-stageStart
  for _,input in ipairs(phases) do
   if tick>=input[1] and tick<input[2] then phase,pad=input[3],input[4];break end
  end
 end
 emu.setInput(pad,0)
end,emu.eventType.inputPolled)

emu.addMemoryCallback(function(_,page)
 dmaPage=page
 dmaPC=emu.getState()['cpu.pc']
 local mapped=emu.convertAddress(dmaPC)
 dmaOffset=mapped and mapped.address or -1
end,emu.callbackType.write,0x4014)
emu.addMemoryCallback(function(_,value) ppuControl=value end,emu.callbackType.write,0x2000)

local function observeWriter(address,value)
 if phase=='route' then return end
 local pc=emu.getState()['cpu.pc']
 if pc<0x8000 then return end
 local mapped=emu.convertAddress(pc)
 if not mapped or mapped.memType~=emu.memType.nesPrgRom then return end
 local key=string.format('%s,%04x,%05x,%04x',phase,pc,mapped.address,address)
 local row=writers[key]
 if row then
  row[1]=row[1]+1;row[3]=value;row[4]=math.min(row[4],value);row[5]=math.max(row[5],value)
 else writers[key]={1,value,value,value,value} end
end
emu.addMemoryCallback(observeWriter,emu.callbackType.write,0,0xff)
emu.addMemoryCallback(observeWriter,emu.callbackType.write,0x300,0x7ff)

local function capture(name,draw)
 assert(dmaPage==2 and dmaPC==0xc23d and dmaOffset==115261,'Expected original OAM DMA')
 local sprites={}
 local patterns={}
 local seen={}
 for i=0,63 do
  local function byte(offset) return emu.read(4*i+offset,emu.memType.nesSpriteRam) end
  if byte(0)<240 then
   local tile=byte(1)
   sprites[#sprites+1]=string.format('[%d,%d,%d,%d,%d]',i,byte(0),tile,byte(2),byte(3))
   if not seen[tile] then
    seen[tile]=true
    local tall=(ppuControl&32)~=0
    local first=tall and ((tile&1)*4096+(tile&254)*16) or ((ppuControl&8)*512+tile*16)
    local pattern={}
    for j=0,(tall and 31 or 15) do
     pattern[#pattern+1]=string.format('%02x',emu.read(first+j,emu.memType.nesPpuDebug))
    end
    patterns[#patterns+1]=string.format('[%d,%d,"%s"]',tile,first,table.concat(pattern))
   end
  end
 end
 local palette={}
 for i=0,15 do palette[#palette+1]=string.format('%02x',emu.read(0x3f10+i,emu.memType.nesPpuDebug)) end
 if draw then
  local file=assert(io.open(OUTPUT..name..'.png','wb'))
  file:write(emu.takeScreenshot());file:close()
 end
 snapshots[#snapshots+1]=string.format('{"frame":%d,"name":"%s","dma_page":%d,"dma_pc":%d,"dma_prg":%d,"ppu_control":%d,"oam":[%s],"visible_patterns":[%s],"sprite_palette":"%s"}',
  frame,name,dmaPage,dmaPC,dmaOffset,ppuControl,table.concat(sprites,','),table.concat(patterns,','),table.concat(palette))
end

emu.addEventCallback(function()
 frame=frame+1
 local mark=marks[frame-stageStart]
 if mark then capture(mark[1],mark[2]) end
 if frame==stageStart+200 then
  local file=assert(io.open(OUTPUT..'observations.json','w'))
  file:write('{"controller_only":true,"checkpoints":[',table.concat(snapshots,','),']}\n');file:close()
  local keys={}
  for key in pairs(writers) do keys[#keys+1]=key end
  table.sort(keys)
  local csv=assert(io.open(OUTPUT..'writers.csv','w'))
  csv:write('phase,after_pc,prg_offset,ram,count,first,last,min,max\n')
  for _,key in ipairs(keys) do csv:write(key,',',table.concat(writers[key],','),'\n') end
  csv:close()
  emu.stop(0)
 end
end,emu.eventType.endFrame)
