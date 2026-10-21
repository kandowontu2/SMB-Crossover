-- Ordinary controller discovery; the old used-block stop was specific to a
-- different route and stranded this route over the first castle gap.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/root_samus32_low_cap.lua'))
return function(c)
 c.lastA=(c.r('PreviousA_B_Buttons')&128)~=0
 return base(c)
end
