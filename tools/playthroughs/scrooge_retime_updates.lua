-- Discovery only: retime real controller buttons by native update-counter writes.
-- Host counters/files only. No emulated writes or savestate loads.
local cfg=assert(ROSTER_CONFIG)
cfg.policyAllModes=true -- Ordinary postmenu inputs also span injury/auto modes.
local root=assert(cfg.out:match('^(.*)/build/'))
local tail=ROSTER_TICK_TAIL_POLICY and assert(dofile(ROSTER_TICK_TAIL_POLICY))
local source=ROSTER_TICK_REFERENCE or(root..'/build/roster-through-2-2/mls-v12-scrooge-observe-c-12-v0-mmc3/game-tick-actions.csv')
local masks,oldFrames={},{}
local maxUpdate,lastPoll=0,0
for line in io.lines(source)do
 local u,f,p,m=line:match('^(%d+),(%d+),(%d+),(%d+)$')
 if u then
  p,f,u,m=tonumber(p),tonumber(f),tonumber(u),tonumber(m)
  masks[u],oldFrames[u]=m,f
  maxUpdate=math.max(maxUpdate,u);lastPoll=p
 end
end
assert(lastPoll>=(ROSTER_TICK_MIN_POLL or 20717),'Reference observer is not complete')
local prior,priorFrame=0,0
for u=0,maxUpdate do
 if masks[u]~=nil then prior,priorFrame=masks[u],oldFrames[u]
 else masks[u],oldFrames[u]=prior,priorFrame end
end
local updates,completed=0,0
local completeClock=ROSTER_TICK_COMPLETE_CLOCK or false
local polls,lastPollUpdates=0,0
local tick=assert(L.NoDecTimers)
assert(tick>=L.GameLoop and tick<L.GameLoop+256,'Foreground GameLoop INC label')
local inNmi=false
emu.addMemoryCallback(function()inNmi=true end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()inNmi=false end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
if completeClock then
 -- Observe the exact foreground STA NmiDisable after all game work. Exec
 -- avoids startup memory clears, NMI/IRQ borrowed state and INC dummy writes.
 local finish=assert(L.PauseSkip)+2
 assert(finish>tick and finish<L.GameLoop+256,'Foreground GameLoop completion label')
 emu.addMemoryCallback(function()
  assert(not inNmi,'GameLoop finishes in foreground')
  assert(emu.read(finish,emu.memType.nesDebug)==0x8d and
   emu.read(finish+1,emu.memType.nesDebug)+256*emu.read(finish+2,emu.memType.nesDebug)==L.NmiDisable,
   'Confirmed final absolute STA NmiDisable opcode')
  completed=updates
 end,emu.callbackType.exec,finish)
end
local mismatches=assert(io.open(cfg.out..'missed-tick-inputs.csv','w'))
mismatches:write('tick,expectedMask,actualMask,mode,task,engine\n')
local gaps=assert(io.open(cfg.out..'multi-tick-gaps.csv','w'))
gaps:write('poll,firstTick,lastTick,expectedMaskChanges\n')
emu.addEventCallback(function()
 polls=polls+1
 if updates-lastPollUpdates>1 then
  local changes=0
  for u=lastPollUpdates+2,math.min(updates,maxUpdate)do
   if masks[u]~=masks[u-1]then changes=changes+1 end
  end
  gaps:write(polls..','..(lastPollUpdates+1)..','..updates..','..changes..'\n');gaps:flush()
 end
 lastPollUpdates=updates
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 assert(not inNmi,'Native update counter executes in foreground')
 assert(emu.read(tick,emu.memType.nesDebug)==0xe6 and emu.read(tick+1,emu.memType.nesDebug)==L.FrameCounter,'Confirmed INC FrameCounter opcode')
 updates=updates+1
 local actual=emu.read(L.SavedJoypad1Bits,emu.memType.nesDebug)
 if updates<=maxUpdate and actual~=masks[updates]then
  local function r(n)return emu.read(L[n],emu.memType.nesDebug)end
  mismatches:write(table.concat({updates,masks[updates],actual,r('OperMode'),r('OperMode_Task'),r('GameEngineSubroutine')},',')..'\n');mismatches:flush()
 end
end,emu.callbackType.exec,tick)
local out=assert(io.open(cfg.out..'retime.csv','w'))
out:write('poll,frame,updates,completedUpdates,sourceFrame,mask\n')
local bits={a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1}
return function(c)
 local clock=completeClock and completed or updates
 if clock>maxUpdate and tail then return tail(c)end
 local u=math.min(clock+1,maxUpdate)
 local mask=masks[u]
 out:write(c.poll..','..c.frame..','..updates..','..completed..','..oldFrames[u]..','..mask..'\n');out:flush()
 local b={}
 for n,v in pairs(bits)do b[n]=(mask&v)>0 end
 return b
end
