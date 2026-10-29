-- Controller-only setup: land in the gap before approaching the mushroom.
-- SMB2's high enemy jump otherwise lands on top of the target block strip.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local route=assert(dofile(root..'/tools/playthroughs/full_roster_policy_og.lua'))
local setup=false
return function(c)
 assert(c.char==25,'Actual SMB2 roster identity')
 if c.world==0 and c.level==0 and not setup and c.x>=270 then
  if c.grounded and c.y>=176 and c.x>=280 and c.x<=287 then
   setup=true
  else
   return {right=c.x<282,left=c.x>285}
  end
 end
 return route(c)
end
