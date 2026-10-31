-- Controller-only direction check before the existing route. No game writes.
local base=dofile(ROSTER_CONFIG.root..'/tools/playthroughs/current_roster_chip_pickup_v2.lua')
local phase=0
return function(c)
 if c.world==0 and c.level==0 then
  if phase==0 then
   if c.x>=156 then phase=1 else return {right=true} end
  end
  if phase==1 then
   if c.x<=112 then phase=2 else return {left=true} end
  end
 end
 return base(c)
end
