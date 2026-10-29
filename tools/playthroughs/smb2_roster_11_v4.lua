-- Controller-only: climb the last stair before settling for the valley jump.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local route=assert(dofile(root..'/tools/playthroughs/smb2_roster_11_v2.lua'))
local crossed=false
local climbHold,launchHold=0,0
return function(c)
 local b=route(c)
 if c.world==0 and c.level==0 then
  if c.x>450 then b.b=true end
  if not crossed and c.x>=2160 and c.x<2256 then
   b={right=c.x<2188,left=c.x>2189,b=true}
   if c.grounded and c.y<=112 and not c.lastA then
    crossed=true
    launchHold=35
    b={right=true,a=true,b=true}
   elseif c.grounded and c.y>112 and not c.lastA then
    climbHold=25
    b.a=true
   elseif climbHold>0 then
    climbHold=climbHold-1
    b.a=true
   end
  elseif crossed and launchHold>0 then
   launchHold=launchHold-1
   b={right=true,a=true,b=true}
  end
 end
 return b
end
