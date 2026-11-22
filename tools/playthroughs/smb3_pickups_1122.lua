-- Inject the pinned SMB3 route as SMB3_PICKUP_BASE. Same c context; frame/poll
-- are completed Main counts and lastA is the actual M3Previous edge.
local base=assert(SMB3_PICKUP_BASE)
local kind=assert(SMB3_PICKUP_KIND)
assert(kind==2 or kind==3)
local target=kind==3 and 1024 or 1616
local phase,at,lastJump,hold='route',0,-100,-1
local attempts,seen=0,false
local T={kind=kind,target=target,phase=phase,changes={}}
SMB3_PICKUP_STATE=T
local function change(c,p)
 phase=p;at=c.update;T.phase=p
 T.changes[#T.changes+1]={phase=p,update=c.update,x=c.x,y=c.y,vx=c.vx}
 if #T.changes>16 then table.remove(T.changes,1)end
end
local function actor(c)
 for i=0,5 do
  local flag=c.r('Enemy_Flag',i)
  if flag>0 and flag<128 and c.r('Enemy_ID',i)==46 and c.r('PowerUpType',i)==kind then
   return {slot=i,x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),
    y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i)}
  end
 end
end
local function starSteer(c,goal)
 -- Native Player_GroundHControl also handles air movement: neutral air input
 -- retains X velocity, while the opposite direction brakes it. The native
 -- non-running reversal loses roughly one Q4 unit per update. Brake early
 -- enough to keep both the hero and the scrolling camera left of the block.
 local vx=c.vx>=128 and c.vx-256 or c.vx
 local dx=goal-c.x
 local lead=vx*vx/24+6
 if vx>3 and dx<=lead then return {left=true}end
 if vx< -3 and -dx<=lead then return {right=true}end
 if dx>4 then return {right=true}end
 if dx< -4 then return {left=true}end
 if vx>0 then return {left=true}end
 if vx<0 then return {right=true}end
 return {}
end
local function starBeforeBirth(c,ordinary)
 local vx=c.vx>=128 and c.vx-256 or c.vx
 if phase=='route'then
  if c.x<target-160 then return ordinary end
  change(c,'star-brake')
 end
 if phase=='star-brake'then
  if vx>2 then return {left=true}end
  if vx< -2 then return {right=true}end
  change(c,'star-position')
 end
 if phase=='star-position'then
  -- The prior question block at1504 can leave Small Mario atY128. Get off
  -- that row near1536, actively arrest drift in air, and land below the
  -- actual Star row1600..1631 before advancing to its underside.
  if not(c.grounded and c.y>=160)then return starSteer(c,target-80)end
  local aim=target-8
  if math.abs(c.x-aim)<=4 and math.abs(vx)<=3 and not c.lastA and c.update-lastJump>24 then
   attempts=attempts+1;assert(attempts<=8,'Bounded real SMB3 Star head attempts')
   lastJump=c.update;hold=c.update+18;T.attempts=attempts
   change(c,'star-bump');return {a=true}
  end
  return starSteer(c,aim)
 elseif phase=='star-bump'then
  if c.update-at>75 and c.grounded then change(c,'star-position')end
  local b=starSteer(c,target-8);b.a=c.update<hold;return b
 end
 return ordinary
end
return function(c)
 local ordinary=base(c)
 if c.char~=17 or c.world~=0 or c.level~=0 then return ordinary end
 if c.r('M3Growth')~=0 or c.r('M3Poof')~=0 then return {}end
 local a=actor(c)
 if a and math.abs(a.x-target)<=32 and not seen then seen=true;change(c,'collect');T.birth=a end
 if seen then
  if not a then return {}end -- The observer, never disappearance, grants credit.
  if a.state&128==0 then return {}end -- Let the actual actor clear its block before a catch jump.
  local dx=a.x-4-c.x
  local b={right=dx>6,left=dx< -6}
  if c.grounded and not c.lastA and c.update-lastJump>24 and a.y<c.y-12 and math.abs(dx)<40 then
   lastJump=c.update;hold=c.update+18
  end
  b.a=c.update<hold
  return b
 end
 if kind==2 then return starBeforeBirth(c,ordinary)end
 if phase=='route'then
  if c.x<target-72 then return ordinary end
  change(c,'align')
 end
 if phase=='align'then
  if not c.grounded then return {a=c.lastA and c.y>96}end
  if c.y<160 then return {left=c.x>target-80,right=c.x<target-96}end
  local aim=target-8
  local vx=c.vx>=128 and c.vx-256 or c.vx
  local b={}
  if c.x<aim-12 then b.right=true
  elseif c.x>aim+12 then b.left=true
  elseif vx>3 then b.left=true
  elseif vx< -3 then b.right=true
  elseif c.x<aim-4 then b.right=true
  elseif c.x>aim+4 then b.left=true
  elseif not c.lastA and c.update-lastJump>24 then
   attempts=attempts+1;assert(attempts<=8,'Bounded real SMB3 block-head attempts')
   lastJump=c.update;hold=c.update+18;T.attempts=attempts
   change(c,'bump');b.a=true
  end
  return b
 elseif phase=='bump'then
  if c.update-at>75 and c.grounded then change(c,'align')end
  return {a=c.update<hold}
 end
 return ordinary
end
