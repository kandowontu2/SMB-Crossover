-- Read-only early-update diagnosis around the frozen aligned arena.
local f=assert(io.open(TEST_DIR..'../../../../tools/profiling/plain_walking_aligned.lua','r'))
local source=f:read('*a');f:close()
local anchor='local finalPc=assert(L.PauseSkip)+2'
local addition=[=[
local phase=assert(io.open(prefix..'-initial-phase.csv','w'))
local names={'FrameCounter','SavedJoypadBits','MmStepTimer','MmPreviousDir','MmVX','MmVX+1','MmVX+2','MmXFraction','MmXFraction+1','Player_X_Position','Player_PageLoc'}
phase:write('scene,completed,hardwareFrame,outline,mode,enemies,'..table.concat(names,',')..'\n')
emu.addMemoryCallback(function()
 if depth~=0 or not scene then return end
 local row={index,completed,frame,scene.outline,scene.mode,scene.count}
 for _,name in ipairs(names)do
  local n,i=name:match('^(.-)%+(%d+)$')
  row[#row+1]=r(n or name,tonumber(i))
 end
 phase:write(table.concat(row,',')..'\n');phase:flush()
end,emu.callbackType.exec,assert(L.NoDecTimers))
]=]
local at=assert(source:find(anchor,1,true))
source=source:sub(1,at-1)..addition..source:sub(at)
assert(load(source,'@step-diag-v40','t',_ENV))()
