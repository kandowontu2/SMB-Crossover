-- One controller-only top-stair landing before Scrooge's second floor gap.
-- Physics, resources, collisions and every shared route guard remain native.
local root=assert(ROSTER_CONFIG.root)
local base=assert(dofile(root..'/tools/playthroughs/full_roster_policy_og.lua'))
local phase='approach'
local function solid(t)return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 end

return function(c)
 local b=base(c)
 if ROSTER_CONFIG.name~='scrooge' or ROSTER_CONFIG.mode_value~=0
  or c.char~=12 or c.variant~=0 or c.world~=0 or c.level~=0 or c.areaType~=1
  or c.x<2380 or c.x>=2512 then return b end
 if phase=='approach' and c.x>=2408 and c.y<=100 then phase='land' end
 if phase=='approach' then return b end
 -- Stop over the actual last stair, instead of continuing the lower rebound.
 b.right=c.x<2412;b.left=c.x>2418;b.a=false;b.b=false;b.down=false
 local supported=solid(c.block(c.x+8,144))
 if phase=='land' then
  if supported and c.grounded and c.y<=112 then
   if c.r('ScPogo')~=0 then phase='cross'
   else
    -- A missed airborne rearm needs one stationary hop, not a short crossing.
    phase='rearm';b.a=true;b.b=true;b.down=true
   end
  elseif supported and c.y>=104 and c.y<=112 and c.vy<128 then
   -- Arm while descending so the next grounded native update has ScPogo1.
   phase='armed';b.b=true;b.down=true
  end
 elseif phase=='rearm' then
  b.b=true;b.down=true
  b.a=c.grounded and c.r('ScPogo')==0
  if supported and c.grounded and c.r('ScPogo')~=0 then phase='cross'
  elseif not c.grounded and c.vy<128 then phase='armed' end
 elseif phase=='armed' then
  b.b=true;b.down=true
  -- Also recognize an actual rebound if polling did not expose its ground turn.
  if c.r('ScPogo')~=0 and(c.grounded or c.vy>=128)then phase='cross' end
 end
 if phase=='cross' then
  b.right=true;b.left=false;b.a=false;b.b=true;b.down=true
 end
 return b
end
