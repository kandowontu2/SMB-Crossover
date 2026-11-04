-- This observer is appended to the controller so it can share its phase and
-- physical bank/stack return checks. No additional input or emulated writes.
local stack, hooks, stats, cadence = {}, {}, {}, {}
local skippedAddress = 0x013a
local priorSkipped, priorUpdates = nil, 0
local interrupts, isrCycles = {}, 0
local function interruptHook(pc, bank, returning)
 emu.addMemoryCallback(guard(function()
  local physical = emu.convertAddress(pc)
  if not physical or physical.memType ~= emu.memType.nesPrgRom then return end
  local mapped = physical.address//8192
  if mapped ~= bank and not (bank == 127 and (mapped == 119 or mapped == 120 or mapped == 125)) then return end
  local cycle = emu.getState()['cpu.cycleCount']
  if returning then
   local started = table.remove(interrupts)
   if started and #interrupts == 0 then isrCycles = isrCycles + cycle+6-started end
  else
   interrupts[#interrupts+1] = cycle-7
  end
 end), emu.callbackType.exec, pc)
end
interruptHook(0xe33c, 127, false)
interruptHook(0xe40f, 127, true)
interruptHook(0x8000, 126, false)
interruptHook(0x8043, 126, true)
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
  if name == 'CoCheckCode' then
   context.target = string.format('%04x', read(0x016c)+256*read(0x016d))
  end
  stats[phase] = stats[phase] or {}
  stats[phase][name] = stats[phase][name] or {calls=0,elapsed=0,foreground=0,max=0,same_frame_calls=0,same_frame_cycles=0,callers={},targets={}}
  stack[#stack+1] = context
  if not hooks[context.ret] then
   hooks[context.ret] = true
   emu.addMemoryCallback(guard(closeProfile), emu.callbackType.exec, context.ret)
  end
 end), emu.callbackType.exec, pc)
end
emu.addEventCallback(guard(function()
 local skipped = read(skippedAddress)
 if active() and priorSkipped then
  local row = cadence[phase] or {physical=0,updates=0,lag_nmi=0,zero_update=0}
  local steps = updates-priorUpdates
  row.physical = row.physical+1
  row.updates = row.updates+steps
  row.lag_nmi = row.lag_nmi+((skipped-priorSkipped)&255)
  if steps == 0 then row.zero_update = row.zero_update+1 end
  cadence[phase] = row
 end
 priorSkipped, priorUpdates = skipped, updates
end), emu.eventType.endFrame)
profileFinish = function()
 local file = assert(io.open(OUTPUT..'timing.json', 'w'))
 file:write(json({ROM_sha256=C.ROM_sha256,cadence=cadence,routines=stats,open_calls=#stack})..'\n')
 file:close()
end
