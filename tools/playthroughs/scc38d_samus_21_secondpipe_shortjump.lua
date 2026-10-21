-- A shorter fresh jump from the actual tall-pipe support clears the floor
-- Koopa and lands before the following pit. Controller inputs only.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_samus_21_tallpipe_edge.lua'))
local launched,hold=false,0
return function(c)
 c.lastA=(c.r('PreviousA_B_Buttons')&128)~=0
 if c.world==1 and c.level==0 and c.x>=2080 and c.x<2190 then
  if not launched and c.grounded and c.y<=96 and not c.lastA then launched=true;hold=16 end
  if launched then local a=hold>0;if a then hold=hold-1 end;return {right=true,a=a,b=c.poll%8<3}end
 end
 return base(c)
end
