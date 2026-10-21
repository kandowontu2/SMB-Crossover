-- Ordinary final34 Samus controller discovery; no state or memory writes.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local dry=assert(dofile(root..'/tools/playthroughs/scc34_samus21_spring_hold.lua'))
local water=assert(dofile(root..'/tools/playthroughs/root_samus_water.lua'))
return function(c)
 c.lastA=(c.r('PreviousA_B_Buttons')&128)~=0
 if c.areaType==0 then return water(c)end
 return dry(c)
end
