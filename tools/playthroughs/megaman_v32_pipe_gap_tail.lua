-- Walk to the actual pipe's right lip before the long 2-1 crossing.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_v32_overworld_tail.lua'))
local phase,age='approach',0
return function(c)
 if c.char==1 and c.world==1 and c.level==0 and c.x>=1630 and c.x<1780 and phase~='done' then
  if phase=='approach' then
   if c.grounded and c.x>=1667 and not c.lastA then phase='jump';age=0;return{right=true,a=true}end
   return{right=true,b=c.poll%8<3}
  elseif phase=='jump' then
   age=age+1
   if c.grounded and c.x>=1744 then phase='release';age=0 end
   return{right=true,a=age<64}
  elseif phase=='release' then
   age=age+1
   if age>=8 then phase='done' end
   return{right=true}
  end
 end
 return prior(c)
end
