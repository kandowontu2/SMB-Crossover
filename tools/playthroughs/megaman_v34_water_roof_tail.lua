-- Continue the independently replayed column landing using ordinary controls.
-- This deliberately preserves the qualified above-ceiling diagnostic route.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_v34_pipe_mount.lua'))
return function(c)
 if c.char==1 and c.world==1 and c.level==1 and c.areaType==0 and c.x>=2090 and c.x<2300 then
  return {right=true,b=c.poll%8<4}
 end
 return prior(c)
end
