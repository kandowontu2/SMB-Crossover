-- Preserve the ledge-release jump while firing the ordinary buster forward
-- during the crossing. This policy follows an actual safe combat-wait prefix.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_v34_water_coral_launch.lua'))
return function(c)
 local b=prior(c)
 if c.char==1 and c.world==1 and c.level==1 and c.areaType==0 and c.x>=2528 and c.x<2810 then
  b.b=c.poll%8<4
 end
 return b
end
