local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/route_five_mm_kd.lua'))
local phase,age='approach',0
return function(c)
 if c.world==0 and c.level==1 and c.x>=1138 and c.x<1188 and phase~='done' then
  if phase=='approach' then
   if c.x>=1150 and c.y==112 and c.grounded then phase='back' end
  end
  if phase=='back' then
   if c.x<=1146 then phase='fire';age=0 end
   return {left=c.x>1146}
  elseif phase=='fire' then
   age=age+1
   if age>60 then phase='done' end
   return {right=c.r('PlayerFacingDir')~=1,b=c.poll%10<4}
  end
 end
 return prior(c)
end
