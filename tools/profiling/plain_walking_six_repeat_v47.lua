-- Additive repeat coverage for the observed six-Goomba timing/visibility
-- counterexamples. Keep the existing four-enemy fixture frozen.
local f=assert(io.open(TEST_DIR..'../../../../tools/profiling/plain_walking_four_repeat_v42.lua','r'))
local source=f:read('*a');f:close()
local anchor='count=4'
local at=assert(source:find(anchor,1,true))
assert(not source:find(anchor,at+#anchor,true),'One population anchor')
source=source:sub(1,at-1)..'count=6'..source:sub(at+#anchor)
assert(load(source,'@six-repeat-v47','t',_ENV))()
