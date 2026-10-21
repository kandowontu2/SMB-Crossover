-- Ordinary S2 controller: wait below the tall1-3 cap for its real Goombas.
-- The historical helper set MM32_HIGH_CLEARED for an old fixed prefix; the
-- fresh S2 prefix has not killed them, so derive readiness from native actors.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/policies/agent49-s2-mm-c.lua'))
local phase,quiet,age='position',0,0
return function(c)
 local b=prior(c)
 if c.world==0 and c.level==2 and c.x>=544 and c.x<680 and phase~='done'then
  local foe=false
  for i=0,5 do
   local flag,id,state=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   if flag>0 and flag<128 and id<21 and state<32 and not(id==6 and state>=2)and x>=520 and x<820 then foe=true end
  end
  if phase=='position'then
   if c.grounded and c.x>=580 and c.x<=584 then phase='wait';print('MM-S2 highcap wait '..c.poll)end
   return{right=c.x<580,left=c.x>584}
  elseif phase=='wait'then
   quiet=foe and 0 or quiet+1
   if quiet>=20 then phase='approach';print('MM-S2 actual highcap foes clear '..c.poll)end
   return{right=c.r('PlayerFacingDir')~=1,b=c.poll%8<4}
  elseif phase=='approach'then
   if c.grounded and c.x>=612 and not c.lastA then phase='jump';age=0;return{right=true,a=true}end
   return{right=true}
  elseif phase=='jump'then
   age=age+1
   if c.grounded and c.y<=32 and c.x>=656 then phase='done';print('MM-S2 highcap landed '..c.poll)end
   return{right=true,a=age<64}
  end
 end
 return b
end
