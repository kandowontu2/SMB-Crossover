-- Input-only opening recovery. The prior generic obstacle policy repeatedly
-- jumped from the lone block onto the unopened powerup row. Land in the gap
-- first, then approach the actual underside without another obstacle jump.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local route=assert(dofile(root..'/tools/playthroughs/rogue_dawn_11_v5.lua'))
local phase='travel'
return function(c)
 if c.world==0 and c.level==0 and c.status==0 then
  if phase=='travel' and c.x>=278 then phase='land' end
  if phase=='land' then
   if c.x>=286 and c.x<=288 and c.y>=176 and c.yHigh==1
    and c.r('RdVY')<128 and c.r('RdGravity')==0 then
    phase='underneath'
   else
    return {right=c.x<286,left=c.x>288,b=c.poll%7<3}
   end
  end
  if phase=='underneath' then
   if c.x>=336 and c.x<=338 and c.y>=176 and c.yHigh==1 then
    phase='source-route'
   else
    return {right=c.x<336,left=c.x>338,b=c.poll%7<3}
   end
  end
 end
 return route(c)
end
