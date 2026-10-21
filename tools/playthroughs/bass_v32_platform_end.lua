-- Ordinary-controller discovery: give the second jump a real release window.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/bass_v32_lift_tail.lua'))
local age=-1
return function(c)
 local b=prior(c)
 if c.char==9 and c.world==0 and c.level==2 and c.x>=1568 then
  if c.grounded then
   age=-1
   if b.a and not c.lastA then age=0 end
  elseif age>=0 then age=age+1 end
  if age>=0 then
   b.a=age<20 or(age>=25 and age<56)
   b.down=false
  end
 end
 return b
end
