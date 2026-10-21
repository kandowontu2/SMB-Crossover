-- Extend the accepted authored setup with Bass's corresponding movement
-- edge/step state. A read-only phase probe proves the old arena starts Bass
-- with previousRight=0/step0 versus previousRight=1/step6 across these ROMs.
-- Initialize both to the already-held input; no canonical fields are omitted.
local f=assert(io.open(TEST_DIR..'../../../../tools/profiling/plain_walking_aligned.lua','r'))
local source=f:read('*a');f:close()
local anchor=" w('Player_X_MoveForce',0);w('Player_Y_MoveForce',0);w('FrameCounter',0)"
local at=assert(source:find(anchor,1,true),'Frozen aligned setup anchor')
assert(not source:find(anchor,at+#anchor,true),'One setup anchor')
local initialization=" w('MmStepTimer',0);w('MmPreviousDir',scene.mode=='walk'and 1 or 0)\n w('XgBassStep',0);w('RgPreviousButtons',scene.mode=='walk'and 1 or 0);w('XgFresh',0)\n"
source=source:sub(1,at-1)..initialization..source:sub(at)
assert(load(source,'@aligned-v41','t',_ENV))()
