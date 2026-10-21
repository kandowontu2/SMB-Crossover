-- Candidate controller timing for the three underground plants. The native
-- small body needs a running launch for the tall pipe during retraction.
local passed={}
local lastPassed
local plant,phase,hold,alignJump=nil,'align',0,0
local log=assert(io.open(ROSTER_CONFIG.out..'luigi-pipe-enemies.csv','w'))
log:write('frame,x,y,phase,slot,id,state,enemyX,enemyY,vx,flag\n')
return function(c)
 if c.world~=0 or c.level~=1 or c.x<1450 or c.x>2020 then return end
 for slot=0,5 do if c.r('Enemy_Flag',slot)>0 then
  log:write(table.concat({c.frame,c.x,c.y,phase,slot,c.r('Enemy_ID',slot),c.r('Enemy_State',slot),c.r('Enemy_X_Position',slot)+256*c.r('Enemy_PageLoc',slot),c.r('Enemy_Y_Position',slot),c.r('Enemy_X_Speed',slot),c.r('Enemy_Flag',slot)},',')..'\n')
 end end
 log:flush()
 if plant and phase=='jump' then
  local b={right=true,b=true,a=hold>0}
  hold=math.max(0,hold-1)
  if hold==0 and c.x>plant.x+24 then passed[plant.x]=true;lastPassed=plant.x;plant=nil;phase='align' end
  return b
 end
 if not plant then
  for slot=0,5 do
   if c.r('Enemy_Flag',slot)>0 and c.r('Enemy_Flag',slot)<128 and c.r('Enemy_ID',slot)==13 then
    local px=c.r('Enemy_X_Position',slot)+256*c.r('Enemy_PageLoc',slot)
    if not passed[px] and px>=c.x-12 and px-c.x<200 and(not plant or px<plant.x)then plant={x=px,slot=slot}end
   end
  end
 end
 if not plant then return end
 -- The middle pipe is only96px beyond the previous plant. A136px run-up
 -- would ask the controller to walk back through that already-cleared pipe.
 local target=math.max(plant.x-136,lastPassed and lastPassed+24 or 0,c.camera+1)
 if phase=='align' then
  local vx=c.vx<128 and c.vx or c.vx-256
  local b={right=c.x<target-2,left=c.x>target+2}
  local e=c.enemy()
  if e and e.id~=13 and math.abs(e.dx)<36 and c.grounded and not c.lastA and alignJump==0 then alignJump=28 end
  if alignJump>0 then b.a=true;alignJump=alignJump-1 end
  if math.abs(c.x-target)<=3 then
   b.left=vx>7;b.right=vx< -7
   if c.grounded and c.y>=160 and math.abs(vx)<8 then phase='wait';return{}end
  end
  return b
 elseif phase=='wait' then
  local down=c.r('PiranhaPlantDownYPos',plant.slot)
  if c.r('PiranhaPlant_Y_Speed',plant.slot)==1 and c.r('PiranhaPlant_MoveFlag',plant.slot)~=0 and c.r('Enemy_Y_Position',plant.slot)<down then phase='run' end
  return{}
 elseif phase=='run' then
  local b={right=true,b=true}
  if c.x>=plant.x-82 and c.grounded and not c.lastA then phase='jump';hold=32;b.a=true end
  return b
 end
end
