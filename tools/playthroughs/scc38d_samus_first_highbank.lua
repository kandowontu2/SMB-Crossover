-- The first high1-3 bank needs an earlier forward launch from the real lower
-- bank. Waiting until the wall is24px ahead puts the head under its ledge.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_samus_liftwalk.lua'))
local launched,hold=false,0
return function(c)
 c.lastA=(c.r('PreviousA_B_Buttons')&128)~=0
 if c.world==0 and c.level==2 and c.x>=575 and c.x<650 then
  if not launched and c.grounded and c.x>=590 and not c.lastA then launched=true;hold=32 end
  local a=hold>0
  if a then hold=hold-1 end
  return {right=true,a=a,b=c.poll%12<5}
 end
 return base(c)
end
