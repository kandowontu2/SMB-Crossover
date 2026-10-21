-- Read-only controller discovery: test the release actually consumed by the
-- game rather than the previous physical-poll command, which lag can skip.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/root_samus32_castle_floor.lua'))
return function(c)
 c.lastA=(c.r('PreviousA_B_Buttons')&128)~=0
 return base(c)
end
