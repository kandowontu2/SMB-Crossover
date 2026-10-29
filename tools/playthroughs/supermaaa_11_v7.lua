-- Remember the earned mushroom after damage; never return to its empty block.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local opening=assert(dofile(root..'/tools/playthroughs/supermaaa_11_v6.lua'))
local travel=assert(dofile(root..'/tools/playthroughs/supermaaa_11_v2.lua'))
local earned=false
return function(c)
 earned=earned or c.status>0
 local b=travel(c)
 if not earned then b=opening(c)end
 if c.world==0 and c.level==0 and c.yHigh==1 and c.x>420 then
  local floor=c.block(c.x+8,208)
  local ahead=c.block(c.x+32,208)
  if floor~=0 and ahead==0 then
   if not c.grounded and c.vy>0 and c.vy<128 and c.y>120 then
    local vx=c.vx>=128 and c.vx-256 or c.vx
    b={left=vx>0,right=vx<0,b=true,a=false}
   elseif c.grounded then
    b={right=not c.lastA,b=true,a=not c.lastA}
   end
  end
 end
 return b
end
