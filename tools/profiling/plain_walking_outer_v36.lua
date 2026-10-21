-- Read-only extension of the frozen aligned crowd observer. The authored
-- arenas are unchanged. Measures previously excluded work before NoDecTimers.
local base=assert(io.open(TEST_DIR..'../../../../tools/profiling/plain_walking_aligned.lua','r'))
local source=base:read('*a');base:close()
local anchor=" {'ProcFireball_Bubble',0},{'EnemiesAndLoopsCore',0},{'EnemyMovementSubs',0},"
assert(source:find(anchor,1,true),'Frozen observer capture list')
source=source:gsub(" %{'ProcFireball_Bubble',0%},%{'EnemiesAndLoopsCore',0%},%{'EnemyMovementSubs',0%},",
 " {'InventoryUiTick',59},{'UpdateTopScore',3},\n"..anchor,1)
local before=" if not scene then return end\n local pc=L.NoDecTimers"
local after=" if not scene then return end\n if observed()and outerStart then outerSamples:write(table.concat({index,char,scene.outline,scene.mode,scene.count,completed-7,cycles()-outerStart-(irqCycles-outerIrq)},',')..'\\n');outerSamples:flush()end\n local pc=L.NoDecTimers"
assert(source:find(before,1,true),'Original NoDecTimers observer')
local p=assert(source:find(before,1,true))
source=source:sub(1,p-1)..after..source:sub(p+#before)
local declaration="local function captureRoutine(name,bank)"
-- GameLoop is in the fixed $8000 CODE window. CurrentBank tracks $A000,
-- which is unrelated here and can differ between mappers after reset.
local insertion="local outerStart,outerIrq\nlocal outerSamples=assert(io.open(prefix..'-outer.csv','w'))\nouterSamples:write('scene,character,outlinesOff,mode,enemies,update,preCoreForegroundCycles\\n')\nemu.addMemoryCallback(function()if depth==0 then outerStart=cycles();outerIrq=irqCycles end end,emu.callbackType.exec,assert(L.GameLoop))\n"
local d=assert(source:find(declaration,1,true))
source=source:sub(1,d-1)..insertion..source:sub(d)
assert(load(source,'@aligned-outer-v36','t',_ENV))()
