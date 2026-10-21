-- Ordinary-controller spring approach; no emulated state/position writes.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/bass_v32_overworld_tail.lua'))
local phase,jumpAt,crossAge='approach',nil,0
return function(c)
 if c.char==9 and c.world==1 and c.level==0 and c.x>=2944 and c.x<3090 then
  local animation=c.r('JumpspringAnimCtrl')
  if phase=='approach' then
   if animation>0 then phase='compress';return{}end
   if c.grounded and c.x>=2990 and(not jumpAt or c.poll-jumpAt>60)then jumpAt=c.poll end
   return{right=c.x<3008,left=c.x>3012,a=jumpAt and c.poll-jumpAt<24}
  elseif phase=='compress' then
   if animation==0 and c.vy>=128 then phase='cross';crossAge=0;return{right=true,a=true}end
   return{a=animation>=2 and animation<=4}
  end
  crossAge=crossAge+1
  return{right=true,a=crossAge<64}
 end
 return prior(c)
end
