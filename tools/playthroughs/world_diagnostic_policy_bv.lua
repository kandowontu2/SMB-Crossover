-- Explicit-cheat diagnostic driver. Real foot-height support, no RAM writes.
-- Stop outside the first parsed cannon's close-range suppression radius.
local age,hold=-1,nil
local log=assert(io.open(ROSTER_CONFIG.out..'cannon-state.csv','w'))
log:write('poll,frame,x,y,camera,hold,slot,cannonX,cannonY,timer\n')
local footlog=assert(io.open(ROSTER_CONFIG.out..'foot-decisions.csv','w'))
footlog:write('poll,x,y,grounded,current,ahead,obstacle,jump\n')
local function solid(t)return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 end
return function(c)
 local cannon
 for i=0,5 do
  local page=c.r('Cannon_PageLoc',i)
  local x=page*256+c.r('Cannon_X_Position',i)
  if page>0 and x>=c.x-160 and x<=c.camera+320 then
   if not cannon or x<cannon then cannon=x end
   log:write(table.concat({c.poll,c.frame,c.x,c.y,c.camera,hold or 0,i,x,c.r('Cannon_Y_Position',i),c.r('Cannon_Timer',i)},',')..'\n')
  end
 end
 if cannon and not hold and c.x>=cannon-100 then hold=cannon end
 if hold then log:flush();return{b=c.poll%12<4}end
 local b={right=true,b=c.char==0 or c.poll%8<3}
 local feet=c.y+32
 local support=c.block(c.x+24,math.min(feet+3,239))
 local current=c.block(c.x+8,math.min(feet+3,239))
 local obstacle=solid(c.block(c.x+20,feet-7))or solid(c.block(c.x+20,c.y+7))
 local previous=(c.r('PreviousA_B_Buttons')&128)~=0
 if c.grounded then
  age=-1
  if not previous and(obstacle or not solid(support))then b.a=true;age=0 end
 elseif age>=0 then age=age+1;b.a=age<30 end
 if c.grounded then footlog:write(table.concat({c.poll,c.x,c.y,c.grounded and 1 or 0,current,support,obstacle and 1 or 0,b.a and 1 or 0},',')..'\n');footlog:flush()end
 return b
end
