-- Let the real short pipe catch the descending leap before its floor enemy;
-- then use a fresh A edge from that genuine raised support.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_samus_21_aftergap_landing.lua'))
local hold=0
return function(c)
 c.lastA=(c.r('PreviousA_B_Buttons')&128)~=0
 if c.world==1 and c.level==0 and c.x>=1840 and c.x<2944 then
  if hold>0 then hold=hold-1;return {right=true,a=true,b=c.poll%8<3}end
  local e=c.enemy()
  if e and e.id~=13 and e.dx>=0 and e.dx<120 and e.y>c.y+24 then
   if c.grounded and c.y<176 and not c.lastA then hold=31;return{right=true,a=true,b=c.poll%8<3}end
   local tile=c.block(c.x+8,216)
   if c.yHigh==1 and not c.grounded and c.vy<128 and tile~=0 and tile~=0x23 then
    if c.r('PlayerFacingDir')~=1 then return {right=true,b=true}end
    return {b=c.poll%8<3}
   end
  end
 end
 return base(c)
end
