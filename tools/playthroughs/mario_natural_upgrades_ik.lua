-- Mario-only controller route: return beneath the first mushroom, let it
-- emerge and walk off the blocks, then mount the later flower normally.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local travel=assert(dofile(root..'/build/verification/retime-movie-dg-0-0/policy.lua'))
local phase,age='first-pass',0
local target,ready=nil,false
local mountAttempts=0
local log=assert(io.open(ROSTER_CONFIG.out..'natural-upgrades.csv','w'))
log:write('poll,phase,x,y,power,targetX,targetY\n')
local function change(c,p)
 if p=='flower-jump' then mountAttempts=mountAttempts+1;assert(mountAttempts<=6,'Bounded flower mounting attempts')end
 phase=p;age=0
 log:write(table.concat({c.poll,p,c.x,c.y,c.status,target and target.x or 0,target and target.y or 0},',')..'\n');log:flush()
end
local function steer(c,x)
 return {right=c.x<x-2,left=c.x>x+2}
end
local function pickup(c)
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
   return {x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),
           y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i)}
  end
 end
end
return function(c)
 assert(c.char==0,'Native Mario input route')
 if c.status==2 and not ready then ready=true;change(c,'flower-collected')end
 if ready or c.world~=0 or c.level~=0 then
  assert(ready,'Both 1-1 upgrades required before leaving')
  local b=travel(c);b.b=c.poll%24~=0
  -- The borrowed pose guide reads the roster A latch. Native Mario consumes
  -- PreviousA_B_Buttons, so release a held A before another grounded jump.
  if c.grounded and b.a and c.r('PreviousA_B_Buttons')&128~=0 then b.a=false end
  return b
 end
 if c.status==1 and phase:sub(1,5)=='first' then change(c,'flower-search')end
 assert(not(phase:sub(1,6)=='flower' and c.status==0),'Mushroom lost before collecting the flower')
 age=age+1;assert(age<1000,'Bounded natural pickup phase: '..phase)
 local item=pickup(c)
 if phase=='first-pass' then
  if c.x<384 then return travel(c)end
  change(c,'first-drop')
 end
 if phase=='first-drop' then
  if c.grounded and c.y>=160 then change(c,'first-align')else return steer(c,400)end
 end
 if phase=='first-align' then
  if c.x>=330 and c.x<=334 and c.grounded and c.vx==0 and c.r('PreviousA_B_Buttons')&128==0 then change(c,'first-bump')
  else return steer(c,332)end
 end
 if phase=='first-bump' then
  if item then change(c,'first-collect')
  else local b=steer(c,332);b.a=age<25;if age>65 and c.grounded then change(c,'first-align')end;return b end
 end
 if phase=='first-collect' then
  if item and item.y>=144 then return steer(c,item.x)end
  return steer(c,400)
 end
 if phase=='flower-search' then
  for wx=math.floor(math.max(c.x-16,c.camera)/16)*16,math.min(c.camera+224,c.x+160),16 do
   for y=80,160,16 do
    local t=c.block(wx,y)
    if (t==0xc1 or t==0x55 or t==0x5a)and(not target or wx<target.x)then target={x=wx,y=y}end
   end
  end
  if target and c.x>=target.x-64 then change(c,'flower-drop')else return travel(c)end
 end
 if phase=='flower-drop' then
  if c.grounded and c.y>=target.y+16 then change(c,'flower-align')else return steer(c,target.x+64)end
 end
 if phase=='flower-align' then
  if math.abs(c.x-target.x)<=2 and c.grounded and c.vx==0 and c.r('PreviousA_B_Buttons')&128==0 then change(c,'flower-bump')
  else return steer(c,target.x)end
 end
 if phase=='flower-bump' then
  if item then change(c,'flower-mount')
  else local b=steer(c,target.x);b.a=age<25;if age>65 and c.grounded then change(c,'flower-align')end;return b end
 end
 if phase=='flower-mount' then
  local b=steer(c,math.max(target.x-32,c.camera+1))
  if math.abs(c.x-math.max(target.x-32,c.camera+1))<=2 and c.grounded and c.vx==0 and item and item.state>=128 and c.r('PreviousA_B_Buttons')&128==0 then change(c,'flower-jump');b.a=true end
  return b
 end
 if phase=='flower-jump' then
  if c.grounded and age>4 and c.y<=target.y-32 then return steer(c,item and item.x or target.x)end
  if c.grounded and age>4 then change(c,'flower-mount');return{}end
  local b={a=age<40}
  if c.y<=target.y-32 then b=steer(c,item and item.x or target.x);b.a=age<40 end
  return b
 end
 error('Unknown natural pickup phase '..phase)
end
