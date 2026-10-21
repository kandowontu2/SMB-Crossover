-- Controller-only dash jump for the wide final1-3 gap. Back onto the cap,
-- start the dash, jump near its edge, then save the second jump for the fall.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/bass_v34_vertical_caps.lua'))
local phase,age,offAge='position',0,0
return function(c)
 if c.lastA then offAge=0 else offAge=offAge+1 end
 if c.char==9 and c.world==0 and c.level==2 and c.x>=1860 and c.x<2130 and phase~='done'then
  if phase=='position'then
   if c.x>1891 then return{left=true}end
   if c.x<1888 then return{right=true}end
   if not c.grounded or offAge<6 then return{}end
   if c.r('PlayerFacingDir')~=1 then return{right=true}end
   phase='dash';return{right=true,down=true,a=true}
  elseif phase=='dash'then
   if c.r('XgDash')>0 and offAge>=6 and c.x>=1909 then
    phase='first';age=0;return{right=true,a=true}
   end
   return{right=true}
  elseif phase=='first'then
   age=age+1
   if age>12 and c.vy<128 then phase='fall';return{right=true,b=true}end
   return{right=true,a=true,b=true}
  elseif phase=='fall'then
   if offAge>=6 and c.yHigh==1 and c.y>=128 then
    phase='second';age=0;return{right=true,a=true,b=true}
   end
   return{right=true,b=true}
  elseif phase=='second'then
   age=age+1
   if c.grounded and c.x>=2070 then phase='done';return{right=true}end
   return{right=true,a=age<36,b=true}
  end
 end
 return prior(c)
end
