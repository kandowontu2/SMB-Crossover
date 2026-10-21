-- Controller discovery only. Start the cane before jumping so its active
-- frames contact the lowest hanging brick, opening an actual body-height gap.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local normal=assert(dofile(root..'/tools/playthroughs/mario_luigi_scrooge_policy.lua'))
local step,age=0,0
return function(c)
 if c.char~=12 or c.world~=0 or c.level~=1 or c.areaType~=2 or c.x<840 or c.x>=904 then return normal(c)end
 if c.x<860 then return {right=true}end
 age=age+1
 if step==0 then
  if age>=16 and c.grounded then step=1;age=0 end
  return {}
 elseif step==1 then
  if age>=4 then step=2;age=0 end
  return {b=true}
 elseif step==2 then
  if age>=12 then step=3;age=0 end
  return {right=true,a=true,b=true}
 else
  if age>=32 and c.grounded then step=0;age=0 end
  return {right=true}
 end
end
