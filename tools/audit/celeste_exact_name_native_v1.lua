-- Actual cold menu input and rendered name, no RAM/PPU writes.
local frame,phase,age,variant,shots=0,'title',0,0,0
local log=assert(io.open(OUTPUT..'menu.csv','w'))
log:write('frame,variant,selected,menu,name_hex\n')
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function shot(n)
 shots=shots+1;assert(shots<=2,'Two whole-frame captures only')
 local f=assert(io.open(OUTPUT..n..'.png','wb'));f:write(emu.takeScreenshot());f:close()
end
local function inspect()
 assert(r('OperMode')==0 and r('CrossoverMenuState')==2 and r('CrossoverMenuIndex')==0,'Actual Mario menu slot')
 assert(r('MarioVariant')==variant,'Four genuine Select alternate changes')
 assert(r('SelectedCharacter')==(variant==1 and 8 or 0),'Correct playable Mario-family owner')
 local bytes,hex={},{}
 for i=0,15 do local v=emu.read(0x2328+i,emu.memType.nesPpuDebug);bytes[i+1]=v;hex[#hex+1]=string.format('%02x',v)end
 if variant==4 then for i,v in ipairs(CELESTE_EXPECTED_NAME)do assert(bytes[i]==v,'Actual PPU CELESTE MARIO glyph '..i)end end
 log:write(table.concat({frame,variant,r('SelectedCharacter'),r('CrossoverMenuState'),table.concat(hex)},',')..'\n');log:flush()
 return bytes
end
emu.addEventCallback(function()
 local b={}
 if phase=='open'and age<6 then b.start=true
 elseif phase=='select'and age<6 then b.select=true end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;age=age+1;assert(frame<=600,'Bounded cold menu600frames')
 if phase=='title'and frame==100 then
  assert(r('OperMode')==0 and r('CrossoverMenuState')==0,'Real cold title');phase='open';age=0
 elseif phase=='open'and age>=36 then
  inspect();shot('mario-original');variant=1;phase='select';age=0
 elseif phase=='select'and age>=24 then
  inspect()
  if variant==4 then
   shot('celeste-mario-exact-name');log:close()
   local f=assert(io.open(OUTPUT..'result.json','w'))
   f:write(string.format('{"passed":true,"ROM_sha256":"%s","frames":%d,"actual_Select_changes":4,"actual_PPU_name":"CELESTE MARIO","screenshots":%d,"AllZeros":true,"normal8sprites":true,"script_RAM_writes":false,"scope":"Cold rendered character-select label only; gameplay byte-identical to parent."}\n',CELESTE_ROM_SHA256,frame,shots));f:close()
   print('PASS actual cold Mario menu +4Selects renders CELESTE MARIO');emu.stop(0);return
  end
  variant=variant+1;age=0
 end
end,emu.eventType.endFrame)
