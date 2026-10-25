-- Ordinary controller route: naturally collect both 1-1 upgrades, then travel.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local pickup=assert(dofile(root..'/tools/playthroughs/bill_easy_progression_t.lua'))
local travel=assert(dofile(root..'/tools/playthroughs/scc38d_bill_21_middle_edge.lua'))
local ready=false
return function(c)
 if c.status>=2 then ready=true end
 if ready then return travel(c)end
 return pickup(c)
end
