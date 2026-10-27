-- Controller-only first-pit run-up. Preserve native Jump/air control and the
-- retained cast/edge/stair policy; do not attack or launch early at this gap.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/current_roster_zelda2_11_v3.lua'))
local phase,crossPolls='land',0
return function(c)
 local b=base(c)
 if c.world~=0 or c.level~=0 or c.x<1000 or phase=='done' then return b end
 if phase=='land' then
  if c.grounded and c.y==176 then phase='runup'
  else return{right=c.x<1064,left=c.x>=1064} end
 end
 if phase=='runup' then
  if c.grounded and c.y==176 and c.x>=1086 and c.x<=1092
   and c.vx>0 and c.vx<128 and(c.r('Z2PreviousButtons')&128)==0 then
   phase='cross';crossPolls=1;return{right=true,a=true}
  end
  return{right=c.x<=1092,left=c.x>1092}
 end
 if phase=='cross' then
  if c.grounded and c.x>=1136 then phase='done';return b end
  crossPolls=crossPolls+1;return{right=true,a=crossPolls<=60}
 end
 return b
end
