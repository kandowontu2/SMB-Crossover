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
   if dx>0 and dx<160 and math.abs(y-c.y)<48 and(not selected or dx<selected.dx)then
    selected={slot=slot,id=id,x=x,y=y,state=s,dx=dx}
   end
  end
 end
 local old=oldEnemy()
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
