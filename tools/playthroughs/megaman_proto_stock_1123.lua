local targetByKind={[0]=336,1248,1616,1024}
local T={kind=0,phase='travel',events={}}
ROBOT_STOCK_STATE=T
local heldUntil=0

local function change(c,phase)
 T.phase=phase;T.since=c.update
 if #T.events==20 then table.remove(T.events,1)end
 T.events[#T.events+1]={phase=phase,kind=T.kind,x=c.x,y=c.y,update=c.update}
end

local function speed(c)return c.vx<128 and c.vx or c.vx-256 end
local function steer(c,goal,band)
 local distance=goal-c.x-speed(c)/5
 return {right=distance>band,left=distance< -band}
end

local function item(c,kind)
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==46 and c.r('PowerUpType',i)==kind then
   return {x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),
           y=c.r('Enemy_Y_Position',i),mature=c.r('Enemy_State',i)&128~=0}
  end
 end
end

local function defend(c,buttons)
 local e=c.enemy()
 if e and math.abs(e.dx)<104 and math.abs(e.y-c.y)<24 then
  local facing=e.dx>0 and 1 or 2
  if c.r('PlayerFacingDir')~=facing then
   return {left=facing==2,right=facing==1}
  end
  -- Face the Goomba and fire from a stop before walking into its row.
  -- The original run reversed from the Flower while firing and lost its
  -- Mushroom at X1210 before the Goomba's second hit.
  if T.kind~=0 then return {b=c.update%8<3}end
  buttons.b=c.update%8<3
 end
 return buttons
end

return function(c)
 if c.growth~=0 then return {}end
 if c.status>0 and T.kind==0 then
  T.kind=C.expected[2];T.actor=nil;T.missing=nil;T.attempts=0;change(c,'travel')
 end
 local kind=T.kind;local target=targetByKind[kind]
 local a=item(c,kind)
 if a and not T.actor then T.actor=a;T.trace={};change(c,'emerge')end
 if T.actor and not a then
  T.missing=T.missing or {update=c.update,x=c.x,y=c.y};return {}
 end
 if a and c.update%8==0 then
  if #T.trace==16 then table.remove(T.trace,1)end
  T.trace[#T.trace+1]={update=c.update,x=c.x,y=c.y,item=a}
 end
 if T.phase=='travel'then
  if c.x<target-72 then return base(c)end
  change(c,'align')
 end
 if T.phase=='align'then
  local aim=target-5
  if not c.grounded or c.y<160 then
   local b=steer(c,target-53,3)
   if c.grounded and c.x<=target-53 then b.right=false;b.left=true end
   return defend(c,b)
  end
  if math.abs(c.x-aim)<=2 and math.abs(speed(c))<=4 and not c.lastA then
   T.attempts=(T.attempts or 0)+1
   assert(T.attempts<=8,'Bounded authored head-bump attempts')
   heldUntil=c.update+30;change(c,'bump');return {a=true}
  end
  return defend(c,steer(c,aim,2))
 end
 if T.phase=='bump'then
  if c.grounded and c.update-T.since>52 then change(c,'align')end
  return {a=c.update<heldUntil}
 end
 if T.phase=='emerge'then
  local waitX=kind==0 and target+56 or kind==1 and target-49 or target+38
  if not a.mature then return defend(c,steer(c,waitX,4))end
  change(c,'collect')
 end
 if T.phase=='collect'then
  if kind==0 then
   local aim=a.y>=148 and a.x-4 or target+66
   return defend(c,steer(c,aim,3))
  end
  if kind==1 and c.grounded and c.y>=160 then
   if math.abs(c.x-(target-47))<4 and not c.lastA then
    heldUntil=c.update+31;change(c,'collect-jump');return {a=true,right=true}
   end
   return defend(c,steer(c,target-47,2))
  end
  if kind>=2 then
   if c.grounded and c.y-a.y>14 and a.x>=target+9 and math.abs(c.x-a.x)<24 and not c.lastA then
    heldUntil=c.update+30;change(c,'collect-jump');return {a=true}
   end
   local aim=math.max(target+34,a.x-4)
   if kind==3 then aim=math.min(aim,1091)end
   return defend(c,steer(c,aim,3))
  end
  return defend(c,steer(c,a.x-4,3))
 end
 if T.phase=='collect-jump'then
  if c.grounded and c.update-T.since>4 then change(c,'collect')end
  local b=steer(c,a.x-4,3);b.a=c.update<heldUntil;return b
 end
 return {}
end
