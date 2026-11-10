-- Three bounded hardware snapshots; no RAM/ROM writes or per-frame capture.
local frame,pad,control=0,{},0
local base=DONOR=='steve'and 2400 or 1500
local marks={[base]='idle',[base+36]='walk',[base+50]='jump'}
local records={}
local function bytes(addr,n,kind)local t={};for i=0,n-1 do t[#t+1]=string.char(emu.read(addr+i,kind))end;return table.concat(t)end
local function hex(s)return(s:gsub('.',function(c)return string.format('%02x',string.byte(c))end))end
emu.addMemoryCallback(function(_,v)control=v end,emu.callbackType.write,0x2000)
emu.addEventCallback(function()
 local start=DONOR=='steve'and 1800 or 900
 local confirm=DONOR=='steve'and 1960 or 1180
 pad={start=(frame>=start and frame<start+4)or(DONOR=='jay'and frame>=1080 and frame<1084),
  a=(frame>=confirm and frame<confirm+4)or(frame>=base+36 and frame<base+50),right=frame>=base and frame<base+50}
 emu.setInput(pad,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if marks[frame]then
  local pages={};for i=0,7 do local q=emu.convertAddress(i*1024,emu.memType.nesPpuMemory);pages[#pages+1]=q and q.address or -1 end
  local f=assert(io.open(OUTPUT..marks[frame]..'.chr','wb'));f:write(bytes(0,8192,emu.memType.nesPpuDebug));f:close()
  records[#records+1]=string.format('{"pose":"%s","frame":%d,"control":%d,"oam":"%s","palette":"%s","chr_physical_pages":[%s]}',
   marks[frame],frame,control,hex(bytes(0,256,emu.memType.nesSpriteRam)),hex(bytes(0x3f00,32,emu.memType.nesPpuDebug)),table.concat(pages,','))
 end
 if frame==base+60 then
  local f=assert(io.open(OUTPUT..'result.json','w'));f:write('{"passed":true,"ROM_sha256":"'..ROM_SHA..'","controller_only":true,"script_RAM_writes":false,"scope":"Original donor opening discovery; pose labels are controller phases, visual validation required.","records":['..table.concat(records,',')..']}');f:close()
  f=assert(io.open(OUTPUT..'terminal.png','wb'));f:write(emu.takeScreenshot());f:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
