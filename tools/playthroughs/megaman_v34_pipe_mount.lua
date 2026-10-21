-- The gap crossing hook expects the pipe top. Mount it first when this new
-- controller history approaches on the floor; release A before the next jump.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_v34_ground_group.lua'))
local phase,age,offAge='approach',0,0
return function(c)
 if c.lastA then offAge=0 else offAge=offAge+1 end
 if c.char==1 and c.world==1 and c.level==0 and c.x>=1620 and c.x<1680 and phase~='done'then
  if phase=='approach'and c.grounded and c.y>128 and offAge>=5 then phase='climb';age=0 end
  if phase=='climb'then
   age=age+1
   if c.grounded and c.y<=128 then phase='release';age=0;return{}end
   if age>80 and c.grounded then phase='approach';return{}end
   return{right=true,a=age<36}
  elseif phase=='release'then
   age=age+1
   if age<6 then return{}end
   phase='done'
  end
 end
 return prior(c)
end
