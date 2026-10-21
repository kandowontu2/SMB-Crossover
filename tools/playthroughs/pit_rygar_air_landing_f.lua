-- Stop before descending into a live floor enemy. This only changes input.
local log
local rows=0
return function(c)
 local b=base(c)
 local hazard
 local floor
 if not c.grounded and c.yHigh==1 and c.vy<128 and c.y<176
 and not(c.world==0 and c.level==0 and c.x>=700 and c.x<840)then
  for y=math.min(c.y+32,232),232 do
   local t=c.block(c.x+8,y)
   if t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3 then floor=y;break end
  end
  if floor then
   for slot=0,5 do
    local f,id,s=c.r('Enemy_Flag',slot),c.r('Enemy_ID',slot),c.r('Enemy_State',slot)
    local x=c.r('Enemy_X_Position',slot)+256*c.r('Enemy_PageLoc',slot)
    local y=c.r('Enemy_Y_Position',slot)
    local dx=x-c.x
    if f>0 and f<128 and id<0x15 and s<0x20 and not(id==6 and s>=2)
    and dx>12 and dx<96 and math.abs(y+24-floor)<=16 and(not hazard or dx<hazard.dx)then
     hazard={slot=slot,id=id,x=x,y=y,dx=dx}
    end
   end
  end
 end
 if hazard then
  b.right=false
  if not log then
   log=assert(io.open(ROSTER_CONFIG.out..'air-landing-f-controller.csv','w'))
   log:write('frame,poll,world,level,x,y,state,vy,floor,slot,id,enemyX,enemyY,enemyDx,health,facing,mask\n')
  end
  rows=rows+1
  local m=0;for k,n in pairs({a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1})do if b[k]then m=m+n end end
  log:write(table.concat({c.frame,c.poll,c.world,c.level,c.x,c.y,c.state,c.vy,floor,hazard.slot,hazard.id,hazard.x,
   hazard.y,hazard.dx,c.r('MmEnemyHealthLo',hazard.slot)+256*c.r('MmEnemyHealthHi',hazard.slot),c.r('PlayerFacingDir'),m},',')..'\n');log:flush()
  assert(rows<38000,'Air landing controller bounded log')
 end
 return b
end
