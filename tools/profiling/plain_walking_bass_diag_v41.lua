-- Read-only initial phase receipt. Keep the entire v40 authored arena and
-- all204 canonical fields; sample Bass startup input and step state too.
local f=assert(io.open(TEST_DIR..'../../../../tools/profiling/plain_walking_aligned_v40.lua','r'))
local wrapper=f:read('*a');f:close()
local base=assert(io.open(TEST_DIR..'../../../../tools/profiling/plain_walking_aligned.lua','r'))
local source=base:read('*a');base:close()
-- Apply the exact already accepted v40 setup before adding read-only hooks.
local seed=" w('Player_X_MoveForce',0);w('Player_Y_MoveForce',0);w('FrameCounter',0)"
local pos=assert(source:find(seed,1,true))
source=source:sub(1,pos-1).." w('MmStepTimer',0);w('MmPreviousDir',scene.mode=='walk'and 1 or 0)\n"..source:sub(pos)
assert(wrapper:find("w('MmStepTimer',0);w('MmPreviousDir',scene.mode=='walk'and 1 or 0)",1,true),'Exact frozen setup')
local addition=[=[
local phase=assert(io.open(prefix..'-initial-phase.csv','w'))
local names={'FrameCounter','SavedJoypadBits','RgPreviousButtons','XgFresh','XgBassStep','RgShootPose','MmSlideStop','SsBodyStop','MmVX','MmVX+1','MmVX+2','MmXFraction','MmXFraction+1','Player_X_Position','Player_PageLoc'}
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
local anchor='local finalPc=assert(L.PauseSkip)+2'
local at=assert(source:find(anchor,1,true))
source=source:sub(1,at-1)..addition..source:sub(at)
assert(load(source,'@bass-initial-phase-v41','t',_ENV))()
