-- Passive hardware/state observer. All writes are from the game CPU.
local mode,nametables,split
local writes,passes=0,0
local frame=0
local touched={}
emu.addMemoryCallback(function(a,v)mode=v&3 end,emu.callbackType.write,0x5104)
emu.addMemoryCallback(function(a,v)nametables=v end,emu.callbackType.write,0x5105)
emu.addMemoryCallback(function(a,v)split=v end,emu.callbackType.write,0x5200)
emu.addMemoryCallback(function(a,v)
 assert(mode==2,'Profile RAM writes use CPU R/W ExRAM mode')
 assert(v==0,'This foundation build only initializes profile RAM')
 touched[a]=true;writes=writes+1
end,emu.callbackType.write,0x5c00,0x5fff)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=30 then
  assert(mode==2 and nametables==0x44 and split==0,'CIRAM nametables/manual IRQ remain independent of CPU ExRAM')
 end
 if frame==50 or frame==500 or frame==900 then
  local count=0
  for a=0x5c00,0x5fff do
   assert(touched[a],'CPU initialized every ExRAM address')
   assert(emu.read(a,emu.memType.nesMemory)==0,'Actual CPU-mapped profile byte is zero')
   count=count+1
  end
  passes=passes+count
 end
 if frame==950 then
  local f=assert(io.open(OUTPUT..ROM_NAME..'-exram.json','w'))
  f:write(string.format('{"passed":true,"cpuInitWrites":%d,"actualCpuReadChecks":%d,"exramMode":%d,"nametableMap":%d,"hardwareSplit":%d,"observerWrites":false}\n',writes,passes,mode,nametables,split));f:close()
 end
end,emu.eventType.endFrame)
dofile('C:/Users/kando/Documents/ChatGPT/SMB Crossover/build/verification/protoman-candidate-agent/native_proto.lua')
