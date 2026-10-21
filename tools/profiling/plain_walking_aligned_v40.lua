-- Authored-arena setup correction, independently identified by the read-only
-- step-phase observer. Staging real held Right can run an extra foreground
-- update before setup. Reset its source movement edge/timer along with vx
-- and position, so both ROMs begin in the same held-input phase.
-- Retain all20 scenes, sixty measured updates and every204 canonical fields.
local f=assert(io.open(TEST_DIR..'../../../../tools/profiling/plain_walking_aligned.lua','r'))
local source=f:read('*a');f:close()
local anchor=" w('Player_X_MoveForce',0);w('Player_Y_MoveForce',0);w('FrameCounter',0)"
local at=assert(source:find(anchor,1,true),'Frozen aligned setup anchor')
assert(not source:find(anchor,at+#anchor,true),'One setup anchor')
local initialization=" w('MmStepTimer',0);w('MmPreviousDir',scene.mode=='walk'and 1 or 0)\n"
source=source:sub(1,at-1)..initialization..source:sub(at)
assert(load(source,'@aligned-v40','t',_ENV))()
