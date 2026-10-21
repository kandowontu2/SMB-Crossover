-- Wait on real lower terrain for the upper-bank Goombas, using prone fire.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_bill_lance.lua'))
local ready,done=false,false
return function(c)
 if c.char==3 and c.world==0 and c.level==2 and c.x>=530 and c.x<800 and not done then
  if not ready then
   if c.grounded and c.x>=574 and c.x<=577 then ready=true end
   return {right=c.x<574,left=c.x>577,b=false}
  end
  local active=false
  for i=0,5 do
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   if c.r('Enemy_Flag',i)>0 and c.r('Enemy_Flag',i)<128 and c.r('Enemy_ID',i)==6 and c.r('Enemy_State',i)<32 and x>=550 and x<800 then active=true end
  end
  if active then
   if c.r('PlayerFacingDir')~=1 then return {right=true}end
   return {down=true,b=c.poll%8<3}
  end
  done=true
 end
 return base(c)
end
