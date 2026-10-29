-- Controller-only successor. The prior run waited below a live Goomba until
-- the flower finished rising and lost its mushroom; keep that negative.
-- Successor: let the real row enemy fall, then jump over/stomp it before mounting.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local travel=assert(dofile(root..'/tools/playthroughs/sunny_11_v3.lua'))
local phase,age='mushroom',0
local target,earned=nil,false
local attempts=0
local guardSlot=nil
local guardJumps=0
local rowJumpHold=0
local function hazard(c)
 for i=0,5 do
  local flag,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
  local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
  if flag>0 and flag<128 and id<0x15 and st<0x20 and target and x>=c.camera-16 and x<=target.x+96 and not(id<=2 and st>=2 and c.r('Enemy_X_Speed',i)==0) then return i end
 end
end
local function guardEnemy(c)
 if guardSlot==nil then return nil end
 local i=guardSlot
 if c.r('Enemy_Flag',i)==0 or c.r('Enemy_State',i)>=0x20 then return nil end
 return{x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i)}
end
local function change(c,p)
 phase=p;age=0
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)<0x15 then
   print('KAMIKAZE_GUARD_ACTOR slot='..i..' id='..c.r('Enemy_ID',i)..' state='..c.r('Enemy_State',i)..' x='..(c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i))..' y='..c.r('Enemy_Y_Position',i))
  end
 end
 print('KAMIKAZE_UPGRADE_PHASE '..p..' x='..c.x..' y='..c.y)
end
local function steer(c,x)return{right=c.x<x-2,left=c.x>x+2}end
local function pickup(c)
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
   return{x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),
          y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i)}
  end
 end
end
local function choose(c)
 if c.status==2 and not earned then earned=true;change(c,'flower-collected')end
 if earned then
  local b=travel(c);b.b=false
  return b
 end
 assert(c.world==0 and c.level==0,'Both upgrades required before exit')
 if phase=='mushroom' then
  if c.status==0 then return travel(c)end
  change(c,'search')
 end
 assert(c.status>0,'Mushroom lost before collecting flower')
 age=age+1;assert(age<1000,'Bounded Celeste upgrade phase '..phase)
 local item=pickup(c)
 if phase=='search' then
  for wx=math.floor(math.max(c.x-16,c.camera,900)/16)*16,math.min(c.camera+224,c.x+160,1800),16 do
   for y=80,160,16 do
    local t=c.block(wx,y)
    if(t==0xc1 or t==0x55 or t==0x5a)and(not target or wx<target.x)then target={x=wx,y=y}end
   end
  end
  if target and c.x>=target.x-64 then change(c,'drop')else return travel(c)end
 end
 if phase=='drop' then
  if c.grounded and c.y>=target.y+16 then change(c,'clear-row')else return steer(c,target.x+64)end
 end
 if phase=='clear-row' then
  -- Let both real row Goombas leave the block before jumping below it.
  -- V1 bumped while the second Goomba was descending directly overhead.
  local hold=math.max(target.x-96,c.camera+4)
  local pending,near=false,nil
  for i=0,5 do
   local flag,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
   local ex=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   if flag>0 and flag<128 and id<0x15 and st<0x20 and ex>=hold-24 and ex<=target.x+128 then
    pending=true
    if math.abs(ex-c.x)<36 and c.r('Enemy_Y_Position',i)>=c.y-24 then near=ex end
   end
  end
  if not pending then change(c,'align')
  else
   local b=steer(c,hold)
   if near and c.grounded and not c.lastA then rowJumpHold=24 end
   if rowJumpHold>0 then b.a=true;rowJumpHold=rowJumpHold-1 end
   return b
  end
 end
 if phase=='align' then
  if math.abs(c.x-target.x)<=2 and c.grounded and c.vx==0 and c.r('PreviousA_B_Buttons')&128==0 then change(c,'bump')
  else return steer(c,target.x)end
 end
 if phase=='bump' then
  if item then guardSlot=hazard(c);change(c,guardSlot and 'guard-back' or 'mount')
  else local b=steer(c,target.x);b.a=age<25;if age>65 and c.grounded then change(c,'align')end;return b end
 end
 if phase=='guard-back' then
  local x=math.max(target.x-72,c.camera+1)
  if math.abs(c.x-x)<=2 and c.grounded and c.vx==0 then guardSlot=hazard(c);change(c,guardSlot and 'guard-wait' or 'mount')else return steer(c,x)end
 end
 if phase=='guard-wait' then
  local e=guardEnemy(c)
  if not e or e.x<c.x-28 then change(c,'mount')
  elseif e.y>=target.y+16 and e.x-c.x<28 and not c.lastA then
   guardJumps=guardJumps+1;assert(guardJumps<=8,'Bounded real enemy guard jumps');change(c,'guard-jump');return{a=true}
  else return{}end
 end
 if phase=='guard-jump' then
  if c.grounded and age>8 then change(c,'guard-back');return{}else return{a=age<30}end
 end
 if phase=='mount' then
  local x=math.max(target.x-32,c.camera+1)
  local b=steer(c,x)
  if math.abs(c.x-x)<=2 and c.grounded and c.vx==0 and item and c.r('PreviousA_B_Buttons')&128==0 then
   attempts=attempts+1;assert(attempts<=6,'Bounded flower mounting attempts')
   change(c,'jump');b.a=true
  end
  return b
 end
 if phase=='jump' then
  if c.grounded and age>4 and c.y<=target.y-32 then return steer(c,item and item.x or target.x)end
  if c.grounded and age>4 then change(c,'mount');return{}end
  local b={a=age<40}
  -- Rise beside the row until the full native body clears its top.
  if c.y<=target.y-32 then b.right=c.x<target.x-12;b.left=c.x>target.x-8 end
  if c.y<=target.y-32 then b=steer(c,item and item.x or target.x);b.a=age<40 end
  return b
 end
 error('Unknown Celeste upgrade phase '..phase)
end
return function(c)
 assert(c.char==0 and c.r('MarioVariant')==3,'Genuine Kamikaze identity')
 assert(c.r('X5ChrMode')==0x84,'Skin publication retained')
 if c.level==1 then assert(earned,'Real flower required before controlled 1-2')end
 local view={};for key,value in pairs(c)do view[key]=value end;view.char=23
 return choose(view)
end
