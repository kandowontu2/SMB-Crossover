-- Controller-only successor: wait for the game's A release, then its jump.
-- Physical input polls can outnumber completed movement updates.
local root = ROSTER_CONFIG.root
local base = dofile(root..'/tools/playthroughs/full_roster_policy_og.lua')
local pending
return function(c)
  local b = base(c)
  if ROSTER_CONFIG.name ~= 'roll' or c.world ~= 0 or c.level ~= 0 then return b end
  if not c.grounded then
    pending = nil
    return b
  end
  if not pending and b.a then pending = 'release' end
  if pending == 'release' then
    b.a = false
    if c.r('A_B_Buttons') & 128 == 0 and c.r('PreviousA_B_Buttons') & 128 == 0 then
      pending = 'press'
      b.a = true
    end
  elseif pending == 'press' then
    b.a = true
  end
  return b
end
