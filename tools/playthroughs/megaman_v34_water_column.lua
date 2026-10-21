-- Explicit controller route over the exposed2-2 water ceiling column.
-- This matches the geometry used by the earlier32 traversal; it is not
-- evidence for a below-ceiling swimming route. MM2.02 has grounded jumps.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_v34_pipe_mount.lua'))
local phase,offAge='release',0
return function(c)
 if c.lastA then offAge=0 else offAge=offAge+1 end
 if c.char==1 and c.world==1 and c.level==1 and c.areaType==0 and c.x>=2030 and c.x<2300 then
  if phase=='release'then
   if offAge>=8 then phase='climb';return{a=true}end
   return{}
  elseif phase=='climb'then
   if c.yHigh==1 and c.y<=100 then phase='land'end
   return{a=true}
  elseif phase=='land'then
   if c.grounded and c.yHigh==1 and c.y<=112 then phase='nextrelease';return{}end
   return{right=c.x<2065,left=c.x>2067,a=true}
  elseif phase=='nextrelease'then
   if offAge>=8 then phase='column';return{right=true,a=true}end
   return{}
  elseif phase=='column' or phase=='apex'then
   if c.grounded and c.x>=2090 and c.yHigh==1 and c.y<=32 then phase='roof';return{right=true}end
   -- The successful32 stream releases just before the exposed column top.
   -- Preserve that source jump-release control, rather than holding past it.
   if c.yHigh==1 and c.y<=5 then phase='apex'end
   return{right=true,a=phase=='column',b=c.poll%8<4}
  end
  return{right=true,b=c.poll%8<4}
 end
 return prior(c)
end
