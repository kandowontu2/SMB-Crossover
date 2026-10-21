-- Controller-only retiming from the coral support. The earlier32 route
-- takes off near2060; reproduce that position before its column jump.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_v34_pipe_mount.lua'))
local phase,offAge,age='position',0,0
return function(c)
 if c.lastA then offAge=0 else offAge=offAge+1 end
 if c.char==1 and c.world==1 and c.level==1 and c.areaType==0 and c.x>=2050 and c.x<2300 then
  if phase=='position'then
   if c.x>2059 then return{left=true}end
   if c.x<2058 then return{right=true}end
   if not c.grounded or offAge<8 then return{}end
   phase='prepare';age=0;return{right=true}
  elseif phase=='prepare'then
   age=age+1
   if age>=6 then phase='column';return{right=true,a=true}end
   return{right=true}
  elseif phase=='column' or phase=='apex'then
   if c.grounded and c.x>=2090 and c.yHigh==1 and c.y<=32 then phase='roof';return{right=true}end
   if c.yHigh==1 and c.y<=4 then phase='apex'end
   return{right=true,a=phase=='column',b=c.poll%8<4}
  end
  return{right=true,b=c.poll%8<4}
 end
 return prior(c)
end
