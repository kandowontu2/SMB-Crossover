-- Naturally collect the 1-1 mushroom and flower before following the current
-- Mario route. Fireballs are ordinary B edges, retaining running between them.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local pickup=assert(dofile(root..'/tools/playthroughs/bill_easy_progression_t.lua'))
local travel=assert(dofile(root..'/build/verification/retime-movie-dg-0-0/policy.lua'))
local ready=false
return function(c)
 assert(c.char==0,'Mario power-up route')
 if c.status>=2 then ready=true end
 if ready then
  local b=travel(c)
  b.b=c.poll%24~=0
  return b
 end
 assert(not(c.world~=0 or c.level~=0 or c.x>1400),'Required natural 1-1 upgrades were missed')
 return pickup(c)
end
