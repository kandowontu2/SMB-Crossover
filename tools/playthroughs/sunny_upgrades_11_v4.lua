-- Controller-only Sunny mushroom + genuine later flower route discovery.
-- No memory writes/cheats; reject missing upgrades instead of crediting a clear.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local travel=assert(dofile(root..'/tools/playthroughs/sunny_11_v3.lua'))
local phase,age='mushroom',0
local target,earned=nil,false
local attempts=0
local function change(c,p)
 phase=p;age=0
 print('SUNNY_UPGRADE_PHASE '..p..' x='..c.x..' y='..c.y)
end
local function steer(c,x) return {right=c.x<x-2,left=c.x>x+2}end
local function pickup(c)
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
   return {x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),
           y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i)}
  end
 end
end
return function(c)
 assert(c.char==23,'Sunny genuine identity')
 if c.status==2 and not earned then earned=true;change(c,'flower-collected')end
 if earned then
  local b=travel(c);b.b=c.poll%24~=0
  return b
 end
 assert(c.world==0 and c.level==0,'Both upgrades required before exit')
 if phase=='mushroom' then
  if c.status==0 then return travel(c)end
  change(c,'search')
 end
 assert(c.status>0,'Mushroom lost before collecting flower')
 age=age+1;assert(age<1000,'Bounded Sunny upgrade phase '..phase)
 local item=pickup(c)
 if phase=='search' then
  for wx=math.floor(math.max(c.x-16,c.camera,900)/16)*16,math.min(c.camera+224,c.x+160,1800),16 do
   for y=80,160,16 do
    local t=c.block(wx,y)
    if (t==0xc1 or t==0x55 or t==0x5a)and(not target or wx<target.x)then target={x=wx,y=y}end
   end
  end
  if target and c.x>=target.x-64 then change(c,'drop')else return travel(c)end
 end
 if phase=='drop' then
  if c.grounded and c.y>=target.y+16 then change(c,'align')else return steer(c,target.x+64)end
 end
 if phase=='align' then
  if math.abs(c.x-target.x)<=2 and c.grounded and c.vx==0 and c.r('PreviousA_B_Buttons')&128==0 then change(c,'bump')
  else return steer(c,target.x)end
 end
 if phase=='bump' then
  if item then change(c,'mount')
  else local b=steer(c,target.x);b.a=age<25;if age>65 and c.grounded then change(c,'align')end;return b end
 end
 if phase=='mount' then
  local x=math.max(target.x-32,c.camera+1)
  local b=steer(c,x)
  if math.abs(c.x-x)<=2 and c.grounded and c.vx==0 and item and item.state>=128 and c.r('PreviousA_B_Buttons')&128==0 then
   attempts=attempts+1;assert(attempts<=6,'Bounded flower mounting attempts')
   change(c,'jump');b.a=true
  end
  return b
 end
 if phase=='jump' then
  if c.grounded and age>4 and c.y<=target.y-32 then return steer(c,item and item.x or target.x)end
  if c.grounded and age>4 then change(c,'mount');return{}end
  local b={a=age<40}
  if c.y<=target.y-32 then b=steer(c,item and item.x or target.x);b.a=age<40 end
  return b
 end
 error('Unknown Sunny upgrade phase '..phase)
end
