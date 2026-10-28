-- Real Alex/Ryan input route. Preserve generic-v2's final-gap negative.
-- Land on the existing final stair before crossing; no map/physics writes.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local travel=assert(dofile(root..'/tools/playthroughs/full_roster_policy_og.lua'))
local mounted=false
return function(c)
 assert(c.char==21,'Genuine RCR identity')
 local b=travel(c)
 if c.world~=0 or c.level~=0 then return b end
 if not mounted and c.x>=2390 and c.x<2440 then
  if c.grounded and c.y<=112 and c.x>=2416 then
   mounted=true
   return {right=true,b=true}
  end
  return {right=c.x<2418,left=c.x>2422,
   a=c.grounded and c.y>112 and not c.lastA}
 end
 return b
end
