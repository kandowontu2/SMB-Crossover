-- Keep moving past the bouncing enemy while safely above it; the earlier
-- generic air pause descended onto the Paratroopa instead of crossing it.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_samus_21_late_retreat.lua'))
return function(c)
 if c.world==1 and c.level==0 and c.x>=2824 and c.x<2944 and not c.grounded then
  return{right=true,b=c.poll%8<3}
 end
 return base(c)
end
