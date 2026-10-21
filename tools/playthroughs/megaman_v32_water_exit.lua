-- Controller-only final water pipe approach from the real Y112 support.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_v32_water_tail.lua'))
return function(c)
 if c.char==1 and c.world==1 and c.level==1 and c.areaType==0 and c.x>=2980 then
  return{right=true}
 end
 return prior(c)
end
