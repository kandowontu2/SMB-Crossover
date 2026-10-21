-- Ordinary admission from the real upper exit step; no emulated writes.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local choose=assert(dofile(root..'/tools/playthroughs/scc34_samus_water_drop.lua'))
local enter=false
return function(c)
 if c.world==1 and c.level==1 and c.areaType==0 and c.x>=2980 then
  if c.grounded and c.y<=112 and c.yHigh==1 then enter=true end
  if enter then return {right=true}end
 end
 return choose(c)
end
