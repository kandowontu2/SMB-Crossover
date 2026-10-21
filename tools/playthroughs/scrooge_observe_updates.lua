-- Read-only cold-boot reference for retiming an existing ordinary input stream.
-- Counts real writes to the native update counter; no emulated writes/state loads.
local cfg=assert(ROSTER_CONFIG)
local updates=0
local frame,poll=0,0
local out=assert(io.open(cfg.out..'game-update-inputs.csv','w'))
out:write('poll,frame,updates,mask\n')
local masks={}
local reference=cfg.replay or cfg.prefix
assert(reference)
for line in io.lines(reference)do
 local p,_,m=line:match('^(%d+),(%d+),(%d+)$')
 if p then masks[tonumber(p)]=tonumber(m)end
end
local tick=assert(L.NoDecTimers)
assert(tick>=L.GameLoop and tick<L.GameLoop+256,'Foreground GameLoop INC label')
local inNmi=false
emu.addMemoryCallback(function()inNmi=true end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()inNmi=false end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
local ticks=assert(io.open(cfg.out..'game-tick-actions.csv','w'))
ticks:write('tick,frame,poll,mask\n')
emu.addMemoryCallback(function()
 assert(not inNmi,'Native update counter executes in foreground')
 assert(emu.read(tick,emu.memType.nesDebug)==0xe6 and emu.read(tick+1,emu.memType.nesDebug)==L.FrameCounter,'Confirmed INC FrameCounter opcode')
 updates=updates+1
 ticks:write(updates..','..frame..','..poll..','..emu.read(L.SavedJoypad1Bits,emu.memType.nesDebug)..'\n');ticks:flush()
end,emu.callbackType.exec,tick)
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
emu.addEventCallback(function()
 poll=poll+1
 out:write(poll..','..frame..','..updates..','..assert(masks[poll])..'\n')
 out:flush()
end,emu.eventType.inputPolled)
return function()return {}end
