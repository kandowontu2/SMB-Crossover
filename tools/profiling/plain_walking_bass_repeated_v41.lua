-- Supplement to the full20-scene comparison, not its replacement. Repeat
-- the one four-Goomba/outlines-on Bass walking counterexample twenty times
-- under live native music to expose phase and endpoint-counter variability.
local f=assert(io.open(TEST_DIR..'../../../../tools/profiling/plain_walking_aligned.lua','r'))
local source=f:read('*a');f:close()
local seed=" w('Player_X_MoveForce',0);w('Player_Y_MoveForce',0);w('FrameCounter',0)"
local at=assert(source:find(seed,1,true))
local initialization=" w('MmStepTimer',0);w('MmPreviousDir',scene.mode=='walk'and 1 or 0)\n w('XgBassStep',0);w('RgPreviousButtons',scene.mode=='walk'and 1 or 0);w('XgFresh',0)\n"
source=source:sub(1,at-1)..initialization..source:sub(at)
local marker="local samples=assert(io.open(prefix..'-updates.csv','w'))"
local pos=assert(source:find(marker,1,true))
source=source:sub(1,pos-1).."scenes={}\nfor i=1,20 do scenes[i]={outline=0,mode='walk',count=4}end\n"..source:sub(pos)
assert(load(source,'@bass-repeated-v41','t',_ENV))()
