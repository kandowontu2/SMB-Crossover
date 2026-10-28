-- Actual small-only successor; no changes to route or source physics.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local route=assert(dofile(root..'/tools/playthroughs/celeste_upgrades_11_v8.lua'))
return function(c)
 assert(c.char==0 and c.r('MarioVariant')==4,'Real Celeste selection')
 if c.r('CmClock')>0 then
  assert(c.r('PlayerSize')==1,'Celeste must remain genuinely small at every tier')
  assert(c.r('CmPose')>=12 and c.r('CmPose')<=23,'Only original native small poses')
 end
 return route(c)
end
