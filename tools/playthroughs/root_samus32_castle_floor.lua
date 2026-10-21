-- Ordinary controller route: leave the raised used block before crossing
-- the first castle pit. No emulated memory/register writes or state loads.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/root_samus32_low_cap.lua'))
local floorReady=false
return function(c)
 if c.char==2 and c.world==0 and c.level==3 and c.x>=430 and c.x<512 and not floorReady then
  if c.grounded and c.y>=128 then floorReady=true
  else return {left=c.x>438,right=c.x<435,b=c.poll%12<5} end
 end
 return base(c)
end
