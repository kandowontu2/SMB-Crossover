-- Leave the high question block, land on the real pillar's right edge, then
-- jump to the next bank. Running off the high block falls below that bank.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/route_five_mm_kd.lua'))
local phase,age='drop',0
return function(c)
 if c.world==0 and c.level==3 and c.x>=470 and c.x<600 and phase~='done' then
  age=age+1;assert(age<220,'Castle pillar landing did not progress')
  if phase=='drop' then
   if c.grounded and c.y>=120 then phase='jump';age=0 end
   return {right=c.x<502,left=c.x>503}
  elseif phase=='jump' then
   if c.x>=558 and c.grounded then phase='done' end
   return {right=true,a=age<36}
  end
 end
 return prior(c)
end
