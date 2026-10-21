-- The genuine branch lands too near two Goombas for the source arm muzzle.
-- Retreat on actual floor, turn, and use crouched fire from real distance.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_samus_21_late_ground_combat.lua'))
local phase='back'
return function(c)
 if c.world==1 and c.level==0 and c.x>=2490 and c.x<2610 and phase~='done' then
  if phase=='back' then
   if c.x>2504 then return{left=true}end
   phase='done';return {right=true}
  end
 end
 return base(c)
end
