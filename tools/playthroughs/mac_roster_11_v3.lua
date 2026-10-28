-- v2's Hard route launched from the lower stair and fell short. Land on the
-- existing final stair before crossing the gap. Inputs only, no map changes.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/mac_roster_11_v2.lua'))
local mounted=false
return function(c)
 local b=base(c)
 if c.world~=0 or c.level~=0 then return b end
 if not mounted and c.x>=2390 and c.x<2440 then
  if c.grounded and c.y<=112 and c.x>=2416 then
   mounted=true
   return {right=true,b=true}
  end
  return {right=c.x<2418,left=c.x>2422,
   a=c.grounded and c.y>112 and not c.lastA}
 end
 if mounted and c.x<2540 then b.b=true end
 return b
end
