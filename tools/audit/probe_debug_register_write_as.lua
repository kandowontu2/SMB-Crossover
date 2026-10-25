-- Isolated diagnostic: determine what the debugger API does at a ROM address.
-- Restore the byte immediately and stop; no route or production-state claim.
local frame=0
emu.addEventCallback(function()
 frame=frame+1
 if frame==10 then
  local old=emu.read(0x8000,emu.memType.nesDebug)
  emu.write(0x8000,0x40,emu.memType.nesDebug)
  local after=emu.read(0x8000,emu.memType.nesDebug)
  emu.write(0x8000,old,emu.memType.nesDebug)
  print('DEBUG_REGISTER_PROBE original='..old..' after='..after..' restored='..emu.read(0x8000,emu.memType.nesDebug))
  emu.stop(0)
 end
end,emu.eventType.endFrame)
