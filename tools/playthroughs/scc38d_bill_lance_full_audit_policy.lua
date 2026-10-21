-- Extra read-only actual selection guard for independent Bill/Lance replay.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_bill_13_secondbank_combat.lua'))
local frame=0
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local log=assert(io.open(ROSTER_CONFIG.out..'actual-character.csv','w'));log:write('frame,character,billVariant\n')
local last=nil
emu.addEventCallback(function()
 frame=frame+1
 if frame>540 and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
  assert(r('SelectedCharacter')==3,'Actual selected character is Bill/Lance')
  assert(r('BillVariant')==ROSTER_CONFIG.variant,'Actual Bill/Lance menu variant')
  local now=r('WorldNumber')..'-'..r('LevelNumber')
  if now~=last then log:write(frame..',3,'..r('BillVariant')..'\n');log:flush();last=now end
 end
end,emu.eventType.endFrame)
return base
