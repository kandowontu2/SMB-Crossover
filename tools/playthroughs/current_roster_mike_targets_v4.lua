-- Input-only: avoid repeatedly firing into empty space during a gap approach.
-- Earlier v2/v3 input streams were identical and stopped at x1031 before
-- jumping from the controller's stationary fallback; preserve both negatives.
local root=ROSTER_CONFIG.root
local base=dofile(root..'/tools/playthroughs/current_roster_mike_gap_v3.lua')
return function(c)
 local b=base(c)
 if c.char==16 and c.world==0 and c.level==0 then
  local e=c.enemy()
  local near=e and e.dx>0 and e.dx<88 and math.abs(e.y-c.y)<55
  b.b=not not(b.b and near)
 end
 return b
end
