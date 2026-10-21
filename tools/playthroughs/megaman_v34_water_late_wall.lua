-- The late coral needs the full held jump; the generic 30-poll release
-- peaks a few pixels too low to put the feet over its top.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_v34_water_roof_tail.lua'))
local phase,age,offAge='approach',0,0
return function(c)
 if c.lastA then offAge=0 else offAge=offAge+1 end
 if c.char==1 and c.world==1 and c.level==1 and c.areaType==0 and c.x>=2448 and c.x<2560 and phase~='done' then
  if phase=='approach' then
   if c.grounded and offAge>=5 then phase='jump';age=0 else return{right=c.x<2468}end
  end
  if phase=='jump' then
   age=age+1
   if c.grounded and c.x>=2528 then phase='done';return{right=true}end
   return{right=true,a=age<64}
  end
 end
 return prior(c)
end
