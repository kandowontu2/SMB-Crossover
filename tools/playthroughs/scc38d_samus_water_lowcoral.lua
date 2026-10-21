-- A shorter water jump clears the low coral while keeping below the
-- Blooper; upward beam fire uses the ordinary Samus aim control.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_samus_21_lastwinged.lua'))
local launched,hold=false,0
return function(c)
 if c.world==1 and c.level==1 and c.areaType==0 and c.x>=1370 and c.x<1480 then
  local prev=(c.r('PreviousA_B_Buttons')&128)~=0
  if not launched and c.grounded and c.x>=1395 and not prev then launched=true;hold=20 end
  if launched then local a=hold>0;if a then hold=hold-1 end;return {right=true,a=a,up=true,b=c.poll%8<3}end
 end
 return base(c)
end
