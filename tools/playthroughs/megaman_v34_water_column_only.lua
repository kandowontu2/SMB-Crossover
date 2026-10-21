-- Start at the actual coral-top landing. This is explicitly a ceiling-column
-- route, not proof of traversal under the water ceiling.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_v34_pipe_mount.lua'))
local phase,offAge='release',0
return function(c)
 if c.lastA then offAge=0 else offAge=offAge+1 end
 if c.char==1 and c.world==1 and c.level==1 and c.areaType==0 and c.x>=2050 and c.x<2300 then
  if phase=='release'then
   if c.grounded and offAge>=8 then phase='column';return{right=true,a=true}end
   return{}
  elseif phase=='column' or phase=='apex'then
   if c.grounded and c.x>=2090 and c.yHigh==1 and c.y<=32 then phase='roof';return{right=true}end
   if c.yHigh==1 and c.y<=4 then phase='apex'end
   return{right=true,a=phase=='column',b=c.poll%8<4}
  end
  return{right=true,b=c.poll%8<4}
 end
 return prior(c)
end
