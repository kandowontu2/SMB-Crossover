-- One controller-only trial for the second 1-1 floor gap under long bricks.
-- Keep the shared policy and every other identity/area unchanged.
local root=assert(ROSTER_CONFIG.root)
local base=assert(dofile(root.."/tools/playthroughs/full_roster_policy_og.lua"))

return function(c)
 local b=base(c)
 if ROSTER_CONFIG.name=='michelangelo'and ROSTER_CONFIG.mode_value==1
    and c.char==19 and c.variant==2 and c.world==0 and c.level==0
    and c.x>=1328 and c.x<1472 then
  -- Release the early generic gap jump; launch near the actual safe lip.
  -- B stays released so the native attack pose cannot block somersault.
  b.b=false
  b.a=c.x>=1368
 end
 return b
end
