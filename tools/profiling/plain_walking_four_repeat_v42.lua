-- Supplement to the full matched arenas: repeat default-outlines-off
-- four-Goomba walking twenty times under live music on each binary.
-- Retain all204 observation fields and sixty completed updates per repeat.
local f=assert(io.open(TEST_DIR..'../../../../tools/profiling/plain_walking_aligned.lua','r'))
local source=f:read('*a');f:close()
local seed=" w('Player_X_MoveForce',0);w('Player_Y_MoveForce',0);w('FrameCounter',0)"
local at=assert(source:find(seed,1,true))
assert(not source:find(seed,at+#seed,true),'Exactly one shared arena seed')
local initialization=" w('MmStepTimer',0);w('MmPreviousDir',scene.mode=='walk'and 1 or 0)\n w('XgBassStep',0);w('RgPreviousButtons',scene.mode=='walk'and 1 or 0);w('XgFresh',0)\n"
source=source:sub(1,at-1)..initialization..source:sub(at)
local marker="local samples=assert(io.open(prefix..'-updates.csv','w'))"
local pos=assert(source:find(marker,1,true))
assert(not source:find(marker,pos+#marker,true),'Exactly one output anchor')
source=source:sub(1,pos-1).."scenes={}\nfor i=1,20 do scenes[i]={outline=1,mode='walk',count=4}end\n"..source:sub(pos)
assert(load(source,'@four-repeat-v42','t',_ENV))()
