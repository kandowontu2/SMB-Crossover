-- Walk to the real short-pipe edge before jumping; its earlier part is
-- beneath the overhead brick bank. No game memory/register writes.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_samus_contact_receipts.lua'))
local launched,hold=false,0
return function(c)
 c.lastA=(c.r('PreviousA_B_Buttons')&128)~=0
 if c.world==1 and c.level==0 and c.x>=2000 and c.x<2120 then
  if not launched and c.x>=2040 and c.grounded and c.y<=144 and not c.lastA then launched=true;hold=32 end
  if not launched and c.grounded and c.y<=144 then return {right=true,b=c.poll%8<3}end
  if launched then local a=hold>0;if a then hold=hold-1 end;return {right=true,a=a,b=c.poll%8<3}end
 end
 return base(c)
end
