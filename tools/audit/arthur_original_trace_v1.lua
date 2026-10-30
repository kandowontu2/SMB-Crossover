-- Original UNROM Arthur source discovery. Controller-only, no memory writes.
local frame=0
local bank=0
local ctrl=0
local nmis=0
local input={}
local pcCounts={}
local writes={}
local mapperCounts={}
local ram=assert(io.open(OUTPUT..'frames.ram.bin','wb'))
local timeline=assert(io.open(OUTPUT..'frames.csv','w'))
timeline:write('frame,nmi,bank,inputA,inputB,left,right,down,input42,input43,state04f0,state04f3,x0554,x0557,y0522,y0525,weapon0642,hurt0647\n')
local function read(a)return emu.read(a,emu.memType.nesDebug)end
local function bytes(address,length,kind)
 local t={};for i=0,length-1 do t[#t+1]=string.char(emu.read(address+i,kind))end;return table.concat(t)
end
local function binary(name,address,length,kind)
 local f=assert(io.open(OUTPUT..name,'wb'));f:write(bytes(address,length,kind));f:close()
end
emu.addMemoryCallback(function(a,v)
 bank=v&7
 if frame>=960 then local key=string.format('%04X,%d',a,bank);mapperCounts[key]=(mapperCounts[key]or 0)+1 end
end,emu.callbackType.write,0x8000,0xffff)
emu.addMemoryCallback(function(a,v)ctrl=v end,emu.callbackType.write,0x2000)
emu.addMemoryCallback(function()nmis=nmis+1 end,emu.callbackType.exec,0xc0f0)
emu.addMemoryCallback(function(a)
 if frame<960 then return end
 local b=a>=0xc000 and 7 or bank
 local key=string.format('%d,%04X',b,a);pcCounts[key]=(pcCounts[key]or 0)+1
end,emu.callbackType.exec,0x8000,0xffff)
local function memoryWrite(a,v)
 if frame<960 then return end
 local s=emu.getState();local pc=s['cpu.pc'];local b=pc>=0xc000 and 7 or bank
 local key=string.format('%d,%04X,%04X',b,pc,a)
 local row=writes[key]
 if row then row.count=row.count+1;row.last=v;row.min=math.min(row.min,v);row.max=math.max(row.max,v)
 else writes[key]={count=1,first=v,last=v,min=v,max=v}end
end
emu.addMemoryCallback(memoryWrite,emu.callbackType.write,0,0x21)
emu.addMemoryCallback(memoryWrite,emu.callbackType.write,0x04f0,0x0660)
emu.addEventCallback(function()
 local b={start=frame==120}
 if frame>=980 then
  b.right=(frame<1060)or(frame>=1120 and frame<1180)or(frame>=1220 and frame<1300)or frame>=1450
  b.left=(frame>=1180 and frame<1220)or(frame>=1360 and frame<1450)
  b.down=(frame>=1060 and frame<1120)or(frame>=1300 and frame<1360)
  b.a=(frame>=1120 and frame<1126)or(frame>=1200 and frame<1206)or(frame>=1400 and frame<1406)or(frame>=1500 and frame<1506)or(frame>=1600 and frame<1606)or(frame>=1700 and frame<1706)
  b.b=frame%18==0
 end
 input=b;emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=960 then
  ram:write(bytes(0,2048,emu.memType.nesDebug))
  timeline:write(table.concat({frame,nmis,bank,input.a and 1 or 0,input.b and 1 or 0,input.left and 1 or 0,input.right and 1 or 0,input.down and 1 or 0,
   read(0x42),read(0x43),read(0x4f0),read(0x4f3),read(0x554),read(0x557),read(0x522),read(0x525),read(0x642),read(0x647)},',')..'\n')
 end
 for _,target in ipairs({1000,1100,1250,1350,1500,1780})do
  if frame==target then
   local name=string.format('f%04d',frame)
   binary(name..'.oam.bin',0,256,emu.memType.nesSpriteRam)
   binary(name..'.chr.bin',0,8192,emu.memType.nesPpuDebug)
   binary(name..'.palette.bin',0x3f00,32,emu.memType.nesPpuDebug)
   local f=assert(io.open(OUTPUT..name..'.png','wb'));f:write(emu.takeScreenshot());f:close()
   f=assert(io.open(OUTPUT..name..'.json','w'));f:write('{"frame":'..frame..',"PPUCTRL":'..ctrl..',"sprite_height":'..(((ctrl&32)>0)and 16 or 8)..',"sprite_pattern_table":'..(((ctrl&8)>0)and 4096 or 0)..',"OAM_source":"hardware direct","controller_only":true,"memory_writes":false}\n');f:close()
  end
 end
 if frame==1800 then
  ram:close();timeline:close()
  local f=assert(io.open(OUTPUT..'executed-pc.csv','w'));f:write('bank,pc,count\n');for k,v in pairs(pcCounts)do f:write(k..','..v..'\n')end;f:close()
  f=assert(io.open(OUTPUT..'ram-writers.csv','w'));f:write('bank,pc,address,count,first,last,min,max\n');for k,v in pairs(writes)do f:write(table.concat({k,v.count,v.first,v.last,v.min,v.max},',')..'\n')end;f:close()
  f=assert(io.open(OUTPUT..'mapper-writes.csv','w'));f:write('address,bank,count\n');for k,v in pairs(mapperCounts)do f:write(k..','..v..'\n')end;f:close()
  print('PASS bounded original-ROM source observation1800; NMI='..nmis..'; no component/gameplay qualification');emu.stop(0)
 end
end,emu.eventType.endFrame)
