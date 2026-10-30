-- Observe the real validator/compactor and PPU while the cold route runs.
local frame,mask=0,0
local rows={}
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function row()
 local slot=r('CrossoverMenuIndex')
 if not rows[slot]then rows[slot]={validations=0,optimized=0,visibleWrites=0,lateEnables=0}end
 return rows[slot]
end
local function hook(name,field)
 emu.addMemoryCallback(function(pc)
  local a=emu.convertAddress(pc)
  if a and a.address//8192==B[name]and r('CrossoverMenuState')==2 then
   local q=row();q[field]=q[field]+1
  end
 end,emu.callbackType.exec,L[name])
end
hook('MenuQueueValidate','validations');hook('MenuRemoveHint','optimized')
emu.addMemoryCallback(function(_,value)
 local scan=emu.getState()['ppu.scanline']
 if r('CrossoverMenuState')==2 and mask&0x18==0 and value&0x18~=0 and scan>=0 and scan<240 then
  local q=row();q.lateEnables=q.lateEnables+1
 end
 mask=value
end,emu.callbackType.write,0x2001)
emu.addMemoryCallback(function()
 local scan=emu.getState()['ppu.scanline']
 if r('CrossoverMenuState')==2 and mask&0x18~=0 and scan>=0 and scan<240 then
  local q=row();q.visibleWrites=q.visibleWrites+1
 end
end,emu.callbackType.write,0x2007)
emu.addEventCallback(function()
 frame=frame+1
 if frame==322 then
  local f=assert(io.open(OUTPUT..'queue-observations.csv','w'))
  f:write('slot,validations,optimized,visibleWrites,lateEnables\n')
  for slot=0,27 do local q=rows[slot]
   if q then f:write(table.concat({slot,q.validations,q.optimized,q.visibleWrites,q.lateEnables},',')..'\n')end
  end
  f:close()
 end
end,emu.eventType.endFrame)
dofile(TEST_DIR..'menu_fourth_row_capture_v1.lua')
