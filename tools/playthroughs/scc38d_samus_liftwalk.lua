-- Controller-only feedback from the real upper ascending lift. Walking across
-- its right edge leaves Samus below the ceiling and above the ordinary bank.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_samus_feedback.lua'))
return function(c)
 if c.world==0 and c.level==1 and c.areaType==2 and c.x>=2460 and c.x<2656 then
  return {right=true,b=c.poll%12<5}
 end
 return base(c)
end
