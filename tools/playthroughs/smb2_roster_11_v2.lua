-- Controller-only under-block approach after SMB2's high opening enemy jump.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local route=assert(dofile(root..'/tools/playthroughs/full_roster_policy_og.lua'))
local setup=false
return function(c)
 assert(c.char==25,'Actual SMB2 roster identity')
 if c.world==0 and c.level==0 then
  if not setup and c.x>=270 then
   if c.grounded and c.y>=176 and c.x>=280 and c.x<=287 then
    setup=true
   else
    return {right=c.x<282,left=c.x>285}
   end
  end
  -- Do not start another enemy-triggered high jump during the short walk
  -- from this landing gap to the intended underside of the block strip.
  if setup and c.x<332 then return {right=true} end
 end
 return route(c)
end
