-- Ordinary Right enters the final horizontal pipe from its real upper step.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/bass_v32_late_overworld.lua'))
return function(c)
 if c.char==9 and c.world==1 and c.level==1 and c.areaType==0 and c.x>=2980 then
  return{right=true}
 end
 return prior(c)
end
