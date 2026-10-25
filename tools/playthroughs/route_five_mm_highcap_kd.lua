-- The old high-tail script sets MM32_HIGH_CLEARED for a historical prefix.
-- A new route must actually spawn and clear that encounter before climbing.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/route_five_roof_piranha_v2_kd.lua'))
local phase,age,quiet='spawn',0,0
return function(c)
 if c.char==1 and c.world==0 and c.level==2 and c.x>=544 and c.x<680 and phase~='done' then
  age=age+1;assert(age<1000,'High-cap encounter made no progress')
  local foe=false
  for i=0,5 do
   local flag,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   if flag>0 and flag<128 and id<0x15 and st<32 and not(id==6 and st>=2) and x>=520 and x<820 then foe=true end
  end
  if phase=='spawn' then
   if foe then phase='back' end
   return {right=c.x<614}
  elseif phase=='back' then
   if c.x<=581 then phase='wait' end
   return {left=c.x>581}
  elseif phase=='wait' then
   quiet=foe and 0 or quiet+1
   if quiet>=16 then phase='approach' end
   return {right=c.r('PlayerFacingDir')~=1,b=c.poll%8<3}
  elseif phase=='approach' then
   if c.grounded and c.x>=612 and not c.lastA then phase='climb';age=0;return{right=true,a=true} end
   return {right=true}
  elseif phase=='climb' then
   if c.grounded and c.y<=32 and c.x>=656 then phase='done' end
   return {right=true,a=age<40}
  end
 end
 return prior(c)
end
