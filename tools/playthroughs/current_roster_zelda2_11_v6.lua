-- Controller-only final-stair landing/retry. Retain all earlier route fixes.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/current_roster_zelda2_11_v5.lua'))
local phase='approach'
return function(c)
 local b=base(c)
 if c.world~=0 or c.level~=0 or c.x<2390 or c.x>=2544 or phase=='done' then return b end
 if c.block(2416,145)~=0x61 or c.block(2432,145)~=0x61
  or c.block(2448,145)~=0 or c.block(2480,145)~=0x61 then return b end
 if c.r('GuestPowerupActive')~=0 or c.r('TimerControl')~=0 then return b end
 if phase=='approach' then
  if c.grounded and c.y<=112 then phase='runup'
  elseif c.x>=2410 and c.y<=112 then phase='brake'
  else return{right=true,a=c.grounded and(c.r('Z2PreviousButtons')&128)==0 or not c.grounded} end
 end
 if phase=='brake' then
  if c.vx>0 and c.vx<128 then return{left=true} end
  phase='land'
 end
 if phase=='land' then
  if c.grounded then
   if c.y<=112 then phase='runup'
   else phase='approach';return{right=true} end
  else return{right=c.x<2418,left=c.x>2436} end
 end
 if phase=='runup' then
  if c.grounded and c.x>=2432 and c.vx>0 and c.vx<128
   and(c.r('Z2PreviousButtons')&128)==0 then phase='cross';return{right=true,a=true} end
  return{right=true}
 end
 if phase=='cross' then
  if c.grounded and c.x>=2480 then phase='done';return b end
  return{right=true,a=true}
 end
 return b
end
