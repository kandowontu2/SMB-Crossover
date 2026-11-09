-- This observer is appended to the controller so it can share its phase and
-- physical bank/stack return checks. No additional input or emulated writes.
local stack, hooks, stats, cadence = {}, {}, {}, {}
local sample = MiniSample or {}
local instructionSample, instructionCounts = nil, {}
local instructionCalls = {}
local lastInstruction
local function sampleInstruction()
 if not instructionSample then return end
 local state = emu.getState()
 local cycle = state['cpu.cycleCount']
 if lastInstruction then
  instructionCounts[lastInstruction.key] = (instructionCounts[lastInstruction.key] or 0)+cycle-lastInstruction.cycle
 end
 local pc=state['cpu.pc']
 local phys=emu.convertAddress(pc)
 local bank = 'RAM'
 if phys and phys.memType==emu.memType.nesPrgRom then bank=tostring(phys.address//8192)
 elseif phys and phys.memType==emu.memType.nesWorkRam then bank='WRAM'..(phys.address//8192) end
 local key=string.format('%s:%04x',bank,pc)
 instructionCalls[key]=(instructionCalls[key] or 0)+1
 lastInstruction={key=key,cycle=cycle}
end
local skippedAddress = 0x013a
local priorSkipped, priorUpdates = nil, 0
local priorMesenLag, mesenLagKey
local polled = false
local function controllerRead() polled = true end
emu.addMemoryCallback(controllerRead, emu.callbackType.read, 0x4016)
emu.addMemoryCallback(controllerRead, emu.callbackType.read, 0x4017)
local interrupts, isrCycles = {}, 0
local isrCompleted, unmatchedReturns = {}, 0
local function interruptHook(pc, bank, kind, returning)
 emu.addMemoryCallback(guard(function()
  local physical = emu.convertAddress(pc)
  if not physical or physical.memType ~= emu.memType.nesPrgRom then return end
  local mapped = physical.address//8192
  if mapped ~= bank and not (bank == 127 and (mapped == 119 or mapped == 120 or mapped == 125)) then return end
  local state = emu.getState()
  local cycle, sp = state['cpu.cycleCount'], state['cpu.sp']
  if returning then
   local entry = interrupts[#interrupts]
   if not entry or entry.kind ~= kind or entry.sp ~= sp then
    unmatchedReturns = unmatchedReturns+1
    return
   end
   table.remove(interrupts)
   local duration = cycle+6-entry.cycle
   local row = isrCompleted[entry.path] or {calls=0,cycles=0,max=0}
   row.calls = row.calls+1
   row.cycles = row.cycles+duration
   row.max = math.max(row.max,duration)
   isrCompleted[entry.path] = row
   if #interrupts == 0 then isrCycles = isrCycles+duration end
  else
   local path = kind
   if kind == 'nmi' then path = read(0x0139) >= 128 and 'lag_nmi' or 'normal_nmi' end
   interrupts[#interrupts+1] = {kind=kind,path=path,sp=sp,cycle=cycle-7}
  end
 end), emu.callbackType.exec, pc)
end
interruptHook(0xe33c, 127, 'nmi', false)
interruptHook(0xe40f, 127, 'nmi', true)
interruptHook(0x8000, 126, 'irq', false)
interruptHook(0x8043, 126, 'irq', true)
local function closeProfile()
 local state = emu.getState()
 while #stack > 0 and matches(stack[#stack]) do
  local call = table.remove(stack)
  local elapsed = state['cpu.cycleCount'] - call.cycle
  local row = stats[call.phase][call.name]
  local cpu = elapsed - (isrCycles-call.isrCycles)
  row.calls = row.calls + 1
  row.elapsed = row.elapsed + elapsed
  row.foreground = row.foreground + cpu
  row.max = math.max(row.max, elapsed)
  if call.name == 'GameLoop' then
   row.slowest = row.slowest or {}
   local sample = call.scene
   sample.cycles = cpu
   sample.gross = elapsed
   row.slowest[#row.slowest+1] = sample
   table.sort(row.slowest, function(a,b) return a.cycles>b.cycles end)
   if #row.slowest>8 then table.remove(row.slowest) end
   if instructionSample == call then
    sampleInstruction()
    instructionSample=nil
    local sorted={}
    for key,cycles in pairs(instructionCounts) do sorted[#sorted+1]={key=key,cycles=cycles,visits=instructionCalls[key]} end
    table.sort(sorted,function(a,b)return a.cycles>b.cycles end)
    local file=assert(io.open(OUTPUT..'instruction-sample.json','w'))
    file:write(json({scene=call.scene,opcodes=sorted,scope='One actual controller-reached GameLoop; elapsed cycles include interrupted work.'})..'\n')
    file:close()
    result(true,'Bounded one-update diagnostic completed')
    csv:close()
    done=true
    emu.stop(0)
   end
  end
  if call.name == 'BackgroundGuard' or call.name == 'ProbeFloor' or call.name == 'ProbeSides' then
   row.last_return = {a=state['cpu.a'],p=state['cpu.ps'] or state['cpu.p'],y=state['cpu.y']}
  end
  local caller = string.format('%04x', call.ret)
  row.callers[caller] = (row.callers[caller] or 0)+1
  if call.target then row.targets[call.target] = (row.targets[call.target] or 0)+1 end
  if call.frame == frame then
   row.same_frame_calls = row.same_frame_calls + 1
   row.same_frame_cycles = row.same_frame_cycles + elapsed
  end
 end
end
for name, hook in pairs(MiniProfileHooks) do
 local pc, bank = hook[1], hook[2]
 emu.addMemoryCallback(guard(function()
  if not active() then return end
  local phys = emu.convertAddress(pc)
  if not phys then return end
  if bank >= 0 then
   if phys.memType ~= emu.memType.nesPrgRom or phys.address ~= bank*8192+(pc&8191) then return end
  elseif phys.memType ~= emu.memType.nesWorkRam or phys.address ~= 2*8192+pc-0x8000 then return end
  local context = return_context()
  context.name, context.phase = name, phase
  context.cycle, context.frame = emu.getState()['cpu.cycleCount'], frame
  context.isrCycles = isrCycles
  if name == 'GameLoop' then
   context.scene={frame=frame,x=read(0x75)+256*read(0x5c),y=read(0xbd),
                  state=read(0x1e),keys=read(0xdc),engine=read(0x0f),
                  block0=read(0x27),block1=read(0x28),enemies={}}
   for i=0,5 do context.scene.enemies[i+1]=read(0x10+i) end
  end
  if name == 'CoCheckCode' then
   context.target = string.format('%04x', read(0x016c)+256*read(0x016d))
  end
  stats[phase] = stats[phase] or {}
  stats[phase][name] = stats[phase][name] or {calls=0,elapsed=0,foreground=0,max=0,same_frame_calls=0,same_frame_cycles=0,callers={},targets={}}
  if name == 'MiniBackground' then
   local guard = {}
   for _,at in ipairs({0x0f,0x719,0x706,0xdc,0x701,0x46,0x8e,0x711,0x1e,0xa4,0xbd,0x7da1}) do
    guard[string.format('%04x',at)] = read(at)
   end
   stats[phase][name].last_entry = guard
  end
  stack[#stack+1] = context
  if name=='GameLoop' and not instructionSample and
     ((sample.frame and frame==sample.frame) or
      (sample.x and context.scene.x>=sample.x and context.scene.y<145)) then
   instructionSample=context
   emu.addMemoryCallback(sampleInstruction,emu.callbackType.exec,0x0000,0xffff)
  end
  if not hooks[context.ret] then
   hooks[context.ret] = true
   emu.addMemoryCallback(guard(closeProfile), emu.callbackType.exec, context.ret)
  end
 end), emu.callbackType.exec, pc)
end
emu.addEventCallback(guard(function()
 local skipped = read(skippedAddress)
 local state = emu.getState()
 if not mesenLagKey then
  for key, value in pairs(state) do
   if type(key) == 'string' and type(value) == 'number' and key:lower():match('lagcounter$') then
    mesenLagKey = key
    break
   end
  end
 end
 local mesenLag = mesenLagKey and state[mesenLagKey]
 if active() and priorSkipped then
  local row = cadence[phase] or {physical=0,updates=0,lag_nmi=0,zero_update=0}
  local steps = updates-priorUpdates
  row.physical = row.physical+1
  row.updates = row.updates+steps
  row.lag_nmi = row.lag_nmi+((skipped-priorSkipped)&255)
  if mesenLag and priorMesenLag then row.mesen_lag = (row.mesen_lag or 0)+mesenLag-priorMesenLag end
  if not polled then row.no_controller_read = (row.no_controller_read or 0)+1 end
  if steps == 0 then row.zero_update = row.zero_update+1 end
  cadence[phase] = row
 end
 priorSkipped, priorUpdates = skipped, updates
 priorMesenLag = mesenLag
 polled = false
end), emu.eventType.endFrame)
profileFinish = function()
 local file = assert(io.open(OUTPUT..'timing.json', 'w'))
 file:write(json({ROM_sha256=C.ROM_sha256,cadence=cadence,routines=stats,open_calls=#stack,
                  mesen_lag_key=mesenLagKey,interrupts=isrCompleted,
                  unmatched_interrupt_returns=unmatchedReturns,open_interrupts=#interrupts})..'\n')
 file:close()
end
