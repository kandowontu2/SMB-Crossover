-- Release A while stopped on the narrow coral, then start a fresh full
-- jump before walking off. The generic release guard walks off too soon.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_v34_water_late_wall.lua'))
local phase,age='release',0
return function(c)
 if c.char==1 and c.world==1 and c.level==1 and c.areaType==0 and c.x>=2528 and c.x<2730 and phase~='done' then
  if phase=='release' then
   age=age+1
   if age<=6 or not c.grounded then return{}end
   phase='jump';age=0
  end
  age=age+1
  if c.grounded and c.x>=2670 then phase='done';return{right=true}end
  return{right=true,a=age<64}
 end
 return prior(c)
end
