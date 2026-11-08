-- Use the original Goku jump once grounded near the last 1-1 gap.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local previous=assert(dofile(root..'/build/goku-gap-1102-v4/policy.lua'))
local launched=false

return function(c)
 local keys=previous(c)
 if c.world~=0 or c.level~=0 or c.engine~=8 or c.x<2400 or c.x>=2488 then
  return keys
 end
 if launched then return {right=true,a=true} end
 if c.x<2434 then return {right=true} end
 if c.grounded and c.r('DpAction')==1 and not c.lastA then
  launched=true
  return {right=true,a=true}
 end
 return {}
end
