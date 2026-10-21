-- Native support/A-edge controller after the actual high-cap enemy clear.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/policies/agent49-s2-mm-d.lua'))
local phase,off,age='release',0,0
return function(c)
 local b=prior(c)
 if c.lastA then off=0 else off=off+1 end
 if c.world==0 and c.level==2 and c.x>=1104 and c.x<1248 and phase~='done'then
  if phase=='release'then
   if c.grounded and off>=6 then phase='lip';print('MM-S2 uppercap A released '..c.poll)end
   return{}
  elseif phase=='lip'then
   if c.grounded and c.x>=1151 and off>=6 then phase='jump';age=0;return{right=true,a=true}end
   return{right=true}
  elseif phase=='jump'then
   age=age+1
   if c.grounded and c.x>=1208 and c.y<=80 then phase='cross';print('MM-S2 uppercap landed '..c.poll..' X'..c.x..' Y'..c.y);return{right=true}end
   return{right=true,a=age<64}
  elseif phase=='cross'then
   if c.x>=1244 then phase='done'end
   return{right=true}
  end
 end
 return b
end
