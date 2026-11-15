-- Countersteer before the measured42px-body Goomba contact; real barrels only.
-- The caller embeds the frozen baseline as local base.
local phase
return function(c)
 local target
 for i=0,5 do
  local flag,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
  local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
  local y=c.r('Enemy_Y_Position',i)
  local dx=x-c.x
  if flag>0 and flag<128 and id==6 and st<32 and dx>=0 and dx<=160 and math.abs(y-c.y)<64 then
   if not target or dx<target.dx then target={dx=dx,x=x,y=y,slot=i}end
  end
 end
 if not target then phase=nil;return base(c)end
 if not phase and target.dx<=144 and(c.grounded or(c.y>=128 and c.vy<128))then phase='brake'end
 if not phase then return base(c)end
 local vx=c.vx<128 and c.vx or c.vx-256
 if phase=='brake'then
  if vx>0 then return{left=true}end
  phase='retreat'
 end
 if phase=='retreat'then
  if target.dx<112 then return{left=true}end
  phase='face'
 end
 if phase=='face'then
  if c.r('PlayerFacingDir')~=1 or vx<0 then return{right=true}end
  phase='throw'
 end
 if phase=='throw'then
  if not c.grounded then return base(c)end
  if c.r('PlayerFacingDir')~=1 then phase='face';return{right=true}end
  return{b=c.r('DkAttack')==0 and(c.r('DkPrevious')&64)==0}
 end
 return base(c)
end
