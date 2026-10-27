-- Controller-only near-stair landing before the final1-1 stair gap.
-- The original running jump passed the near top while still airborne and
-- reached the far wall below its top. Native Mario physics stay unchanged.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/mario_luigi_scrooge_policy.lua'))
local phase,held='brake',0
return function(c)
 local b=base(c)
 if c.char~=0 or c.world~=0 or c.level~=0 or c.x<2360 or c.x>=2580 or phase=='done' then return b end
 if phase=='brake' then
  if c.vx<=16 or c.vx>=128 then phase='land'
  else b.right=false;b.left=true;b.b=false;return b end
 end
 if phase=='land' then
  if c.grounded and c.y<=112 then phase='runup';return{right=true,b=true} end
  b.right=c.x<2420;b.left=c.x>2428;b.b=false
  return b
 end
 if phase=='runup' then
  if c.grounded and c.y<=112 and c.x>=2428 and c.x<=2440
   and c.vx>0 and c.vx<128 and(c.r('PreviousA_B_Buttons')&128)==0 then
   phase='cross';held=1;return{right=true,b=true,a=true}
  end
  return{right=c.x<=2440,left=c.x>2440,b=true}
 end
 if phase=='cross' then
  if c.grounded and c.x>=2480 then phase='done';return b end
  held=held+1;return{right=true,b=true,a=held<=40}
 end
 return b
end
