-- Ordinary Bill/Lance 38d discovery. Only controller inputs and reads.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local choose=assert(dofile(root..'/tools/playthroughs/scc34_samus21_spring_hold.lua'))
return function(c)
 c.lastA=(c.r('PreviousA_B_Buttons')&128)~=0
 return choose(c)
end
