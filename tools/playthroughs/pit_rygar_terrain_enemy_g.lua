-- Read-only controller line of sight; a solid wall separates floor threats.
local function clearPath(c,x,y)
 for wx=math.floor((c.x+16)/16)*16,math.floor((x-1)/16)*16,16 do
  local t=c.block(wx,y)
  if t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3 then return false end
 end
 return true
end
local base=(function()
-- Read-only controller selection: a passed enemy must not hide one ahead.
local file
local rows=0
return function(c)
 local oldEnemy=c.enemy
 local selected
 for slot=0,5 do
  local f,id,s=c.r('Enemy_Flag',slot),c.r('Enemy_ID',slot),c.r('Enemy_State',slot)
  if f>0 and f<128 and(id<0x15 or id==0x2d or id==0x33)and s<0x20 and not(id==6 and s>=2)then
   local x=c.r('Enemy_X_Position',slot)+256*c.r('Enemy_PageLoc',slot)
   local y=c.r('Enemy_Y_Position',slot)
   local dx=x-c.x
   if dx>0 and dx<160 and math.abs(y-c.y)<48 and clearPath(c,x,c.y+24)and(not selected or dx<selected.dx)then
    selected={slot=slot,id=id,x=x,y=y,state=s,dx=dx}
   end
  end
 end
 local old=oldEnemy()
 if old and not clearPath(c,old.x,c.y+24)then old=nil end
 -- Inherit the ordinary selector when no forward threat shares our height.
 c.enemy=function()return selected or old end
 local b=base(c)
 c.enemy=oldEnemy
 if selected or(old and old.dx<0)then
  if not file then
   file=assert(io.open(ROSTER_CONFIG.out..'forward-enemy-e-controller.csv','w'))
   file:write('frame,poll,world,level,x,y,state,vy,priorSlot,priorId,priorDx,selectedSlot,selectedId,selectedDx,selectedY,mask,actors\n')
  end
  local actors={}
  for s=0,5 do actors[#actors+1]=table.concat({s,c.r('Enemy_Flag',s),c.r('Enemy_ID',s),c.r('Enemy_State',s),
   c.r('Enemy_X_Position',s)+256*c.r('Enemy_PageLoc',s),c.r('Enemy_Y_Position',s),
   c.r('Enemy_MovingDir',s),c.r('MmEnemyHealthLo',s)+256*c.r('MmEnemyHealthHi',s)},':')end
  local m=0;for k,n in pairs({a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1})do if b[k]then m=m+n end end
  rows=rows+1
  file:write(table.concat({c.frame,c.poll,c.world,c.level,c.x,c.y,c.state,c.vy,old and old.slot or -1,
   old and old.id or -1,old and old.dx or 999,selected and selected.slot or -1,selected and selected.id or -1,
   selected and selected.dx or 999,selected and selected.y or -1,m,table.concat(actors,';')},',')..'\n');file:flush()
  assert(rows<38000,'Forward enemy controller audit bound')
 end
 return b
end

end)()
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
    and dx>12 and dx<96 and math.abs(y+24-floor)<=16 and clearPath(c,x,floor-16)and(not hazard or dx<hazard.dx)then
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
