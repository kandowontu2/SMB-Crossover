-- Ordinary buster fire from the safe floor before the approaching Cheep Cheep.
-- The starting muzzle intersects its native projectile hurtbox horizontally.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/bass_v32_water_late.lua'))
local done,age=false,0
return function(c)
 if c.char==9 and c.world==1 and c.level==1 and c.areaType==0
  and c.x>=2790 and c.x<2825 and not done then
  age=age+1
  if age<=120 then return{b=age%8<4}end
  done=true;print('BASS32 final fish burst '..c.poll)
 end
 return prior(c)
end
