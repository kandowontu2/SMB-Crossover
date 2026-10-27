-- Real input only: Grant stands during a ground attack, so attack a target
-- rather than constantly restarting the knife animation on empty ground.
local root = ROSTER_CONFIG.root
local base = dofile(root..'/tools/playthroughs/full_roster_policy_og.lua')
local jump
return function(c)
  local b = base(c)
  if ROSTER_CONFIG.name ~= 'grant' or c.world ~= 0 or c.level ~= 0 then return b end
  if c.engine ~= 8 then jump = nil; return b end
  local enemy = c.enemy()
  local near = enemy and enemy.dx > -8 and enemy.dx < 28 and math.abs(enemy.y - c.y) < 40
  b.b = not not (near and c.r('Cv3Climb') == 0 and c.r('Cv3AttackAge') == 0
    and c.r('Cv3Previous') & 64 == 0)
  if not c.grounded then jump = nil; return b end
  if not jump and b.a then jump = 'release' end
  if jump == 'release' then
    b.a = false
    if c.r('Cv3Previous') & 128 == 0 then jump = 'press'; b.a = true end
  elseif jump == 'press' then
    b.a = true
  end
  return b
end
