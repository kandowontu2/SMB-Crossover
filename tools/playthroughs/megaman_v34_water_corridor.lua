-- Controller-only ascent over the2-2 coral wall, followed by fresh paddle
-- edges through the low ceiling corridor. No state or register writes.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_v34_pipe_mount.lua'))
local phase,offAge,pulse='release',0,0
return function(c)
 if c.lastA then offAge=0 else offAge=offAge+1 end
 if c.char==1 and c.world==1 and c.level==1 and c.areaType==0 and c.x>=2030 and c.x<2380 then
  if phase=='release'then
   if offAge>=8 then phase='climb';return{a=true}end
   return{}
  elseif phase=='climb'then
   if c.yHigh==1 and c.y<=100 then phase='cross';pulse=0;return{right=true}end
   return{a=true}
  end
  if c.yHigh~=1 then return{}end
  if pulse>0 then pulse=pulse-1
  elseif c.y>=96 and offAge>=8 then pulse=12 end
  return{right=true,a=pulse>0,b=c.poll%8<4}
 end
 return prior(c)
end
