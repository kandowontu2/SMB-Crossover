-- Grow/shrink deliberately alternates PlayerStatus. Only route after the
-- genuine transform has completed; a displayed small frame is not damage.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/sunny_upgrades_11_v4.lua'))
return function(c)
 if c.r('GuestPowerupActive')~=0 then return{}end
 return prior(c)
end
