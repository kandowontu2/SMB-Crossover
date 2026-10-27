-- Controller discovery only. Keep the existing route and native movement.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/full_roster_policy_og.lua'))
local gap='approach'
return function(c)
 local b=base(c)
 if ROSTER_CONFIG.name~='alucard' or c.char~=5 or c.variant~=3
    or c.world~=0 or c.level~=0 or c.x<2380 or c.x>=2512 then return b end
 -- Reuse the existing Roll controller's landing maneuver: jumping from
 -- the lower step spends the height before the far side of this gap.
 if gap=='approach' and c.x>=2410 and c.y<=100 then gap='land' end
 if gap=='land' then
  b={right=c.x<2412,left=c.x>2420,a=false,b=false}
  if c.grounded and c.y<=112 then
   gap='jump';b={right=true,a=true,b=false}
  end
 elseif gap=='jump' then b={right=true,a=true,b=false} end
 return b
end
