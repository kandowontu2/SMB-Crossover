-- Two ordinary jumps: land on the1-2 pipe, then cross the pit from its edge.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local follow=assert(dofile(root..'/tools/playthroughs/rygar_gap_dL.lua'))
local phase=nil
local log=assert(io.open(ROSTER_CONFIG.out..'pipe-gap.csv','w'))
log:write('frame,poll,phase,x,y,state,vx,vy\n')
return function(c)
 if c.world~=0 or c.level~=1 then phase=nil;return follow(c)end
 if not phase and c.x>=1818 and c.x<=1828 and c.grounded and c.y==176 then phase='onto-pipe'end
 if phase then
  if phase=='onto-pipe'and c.x>=1858 then phase='land'end
  if phase=='land'and c.grounded and c.y<176 then phase='cross'end
  log:write(table.concat({c.frame,c.poll,phase,c.x,c.y,c.state,c.vx,c.vy},',')..'\n');log:flush()
  if c.x>=1970 then phase=nil;return follow(c)end
  if phase=='land'then return{b=c.frame%12<5}end
  return{right=true,a=not c.grounded or c.r('RgPreviousButtons')&128==0,b=c.frame%12<5}
 end
 return follow(c)
end
