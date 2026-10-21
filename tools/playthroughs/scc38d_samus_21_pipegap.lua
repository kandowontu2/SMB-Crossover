-- Ordinary fresh A edge from the real pipe support before its following gap.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_samus_21_plants_combat.lua'))
local launched,hold=false,0
return function(c)
 c.lastA=(c.r('PreviousA_B_Buttons')&128)~=0
 if c.world==1 and c.level==0 and c.x>=1650 and c.x<1760 then
  if not launched and c.grounded and c.y<=128 and not c.lastA then launched=true;hold=32 end
  if launched then local a=hold>0;if a then hold=hold-1 end;return {right=true,a=a,b=c.poll%8<3}end
 end
 return base(c)
end
