-- Controller-only retained stair-top crossing from the tracked
-- current_roster_recheck_routes.py::stair_controller. No state writes.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/full_roster_policy_og.lua'))
local phase,held='approach',0
return function(c)
 local b=base(c)
 if c.world~=0 or c.level~=0 or c.x<2390 or c.x>=2512 then return b end
 if phase=='approach'and c.grounded then phase='hop';held=0 end
 if phase=='hop'then
  held=held+1
  b={right=c.x<2406,left=c.x>2420,a=held<=10}
  if held>10 and c.grounded and c.y<=112 then phase='runup';held=0 end
  return b
 elseif phase=='runup'then
  if c.grounded and c.x>=2424 and c.vx>0 and c.vx<128 then phase='cross';held=1;return{right=true,a=true}end
  return{right=true}
 elseif phase=='cross'then
  held=held+1;return{right=true,a=held<=40}
 end
 return b
end
