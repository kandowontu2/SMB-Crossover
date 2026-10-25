-- Land on the real upper bank, release Jump, then take off near its lip.
-- This is a controller route adaptation, not a terrain or physics change.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..(ROSTER_CONFIG.character==3 and '/tools/playthroughs/route_five_bill_kd.lua' or '/tools/playthroughs/route_five_mm_notch_kd.lua')))
local phase,age='approach',0
return function(c)
 if c.world==0 and c.level==1 and c.x>=1220 and c.x<1340 and phase~='done' then
  if phase=='approach' and c.y<=112 then phase='land' end
  if phase=='land' then
   if c.grounded and c.y<=112 then phase='walk';age=0 end
   return {right=c.x<1250,left=c.x>1254}
  elseif phase=='walk' then
   age=age+1
   if c.x>=1272 and c.grounded and age>5 then phase='jump';age=0 end
   return {right=true}
  elseif phase=='jump' then
   age=age+1
   if c.x>=1334 then phase='done' end
   return {right=true,a=age<33}
  end
 end
 return prior(c)
end
