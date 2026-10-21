-- Ordinary controller policy. No memory/register writes or state loads.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/root_samus32_route.lua'))
local phase='approach'
return function(c)
 if c.char==2 and c.world==0 and c.level==2 and c.x>=1070 and c.x<1220 and phase~='done' then
  if phase=='approach' then
   if c.x>=1091 and c.x<=1094 and c.grounded then phase='rise'
   else return {right=c.x<1091,left=c.x>1094,b=c.poll%12<5} end
  end
  if phase=='rise' then
   if c.y<=112 then phase='cross' else return {a=true,b=c.poll%12<5} end
  end
  if phase=='cross' then
   if c.grounded and c.y<=112 and c.x>=1130 then phase='done'
   else return {right=true,a=true,b=c.poll%12<5} end
  end
 end
 return base(c)
end
