-- Ordinary controller timing from native Piranha state and a fresh retraction timer.
-- Fight a closer floor enemy before walking to the pipe waiting point.
-- Retain at least48 native frames before starting the crossing. Retract fully,
-- then approach inside its33px emergence exclusion while making the jump.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_samus_21_below.lua'))
local active,phase,settle,hold=nil,'wait',0,0
return function(c)
 c.lastA=(c.r('PreviousA_B_Buttons')&128)~=0
 if c.world==1 and c.level==0 then
  if active and phase=='cross' then
   if c.x>active+48 then active=nil;phase='wait';settle=0
   else local a=hold>0;if a then hold=hold-1 end;return {right=true,a=a,b=c.poll%8<3}end
  end
  local plant
  for i=0,5 do
   if c.r('Enemy_Flag',i)>0 and c.r('Enemy_Flag',i)<128 and c.r('Enemy_ID',i)==13 and c.r('Enemy_State',i)<32 then
    local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
    local dx=x-c.x
    if dx> -16 and dx<140 and(not plant or dx<plant.dx)then plant={slot=i,x=x,dx=dx}end
   end
  end
  if plant then
   local near=c.enemy()
   if c.grounded and near and near.id~=13 and near.dx>0 and near.dx<100 and math.abs(near.y-c.y)<32 then return base(c)end
   if active~=plant.x then active=plant.x;phase='wait';settle=0 end
   local target=math.max(c.camera+1,plant.x-56)
   if c.grounded and c.x>=target and c.x<=target+2 and not c.lastA and c.r('Enemy_Y_Position',plant.slot)>=c.r('PiranhaPlantDownYPos',plant.slot) and c.r('PiranhaPlant_MoveFlag',plant.slot)==0 and c.r('EnemyFrameTimer',plant.slot)>=48 then
    settle=settle+1
    if settle>=4 then phase='cross';hold=31;return {right=true,a=true,b=c.poll%8<3}end
   else settle=0 end
   return {right=c.x<target,left=c.x>target+2,b=c.poll%8<3}
  end
  active=nil;phase='wait';settle=0
 end
 return base(c)
end
