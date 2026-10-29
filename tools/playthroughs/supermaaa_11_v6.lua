-- Input-only recovery if the first Goomba jump lands atop the unopened row.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local route=assert(dofile(root..'/tools/playthroughs/supermaaa_11_v5.lua'))
local drop=false
return function(c)
 local b=route(c)
 if c.world==0 and c.level==0 and c.status==0 and c.block(344,152)==0xc1 then
  if c.grounded and c.y<=128 and c.x>=300 and c.x<392 then drop=true end
  if drop then
   b={left=c.x>282,right=c.x<280}
   if c.grounded and c.y>=160 then drop=false end
  end
 end
 return b
end
