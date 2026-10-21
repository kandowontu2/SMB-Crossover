-- Ordinary controller discovery after the certified final34 World1 prefix.
-- No memory/register writes, builds, recordings or cross-ROM state loading.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/root_samus34_no_castle_stop.lua'))
local springPhase,springJumpAt='approach',nil
return function(c)
 c.lastA=(c.r('PreviousA_B_Buttons')&128)~=0
 if c.world==1 and c.level==0 and c.x>=2944 and c.x<3070 then
  local animation=c.r('JumpspringAnimCtrl')
  if springPhase=='approach' then
   if animation>0 then springPhase='compress';return{}end
   if c.grounded and c.x>=2990 and(not springJumpAt or c.poll-springJumpAt>40)then springJumpAt=c.poll end
   return {right=c.x<3008,left=c.x>3012,b=c.poll%12<5,a=springJumpAt and c.poll-springJumpAt<16}
  elseif springPhase=='compress' then
   if animation==0 and c.vy>=128 then springPhase='cross';return {right=true,a=true,b=c.poll%12<5}end
   return {a=animation>=2 and animation<=4}
  end
  return {right=true,a=true,b=c.poll%12<5}
 end
 return base(c)
end
