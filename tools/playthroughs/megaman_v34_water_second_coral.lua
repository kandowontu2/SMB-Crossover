-- The next coral is another actual grounded launch point. Preserve a
-- stopped A release here rather than walking into the following water gap.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_v34_water_coral_fire.lua'))
local phase,age='release',0
return function(c)
 if c.char==1 and c.world==1 and c.level==1 and c.areaType==0 and c.x>=2600 and c.x<2730 and phase~='done' then
  if phase=='release' then
   age=age+1
   if age<=6 or not c.grounded then return{b=c.poll%8<4}end
   phase='jump';age=0
  end
  age=age+1
  return{right=true,a=age<64,b=c.poll%8<4}
 end
 return prior(c)
end
