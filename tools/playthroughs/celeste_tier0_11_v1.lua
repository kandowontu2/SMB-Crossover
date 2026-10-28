-- Input-only tier0 discovery. No pickups, physics substitution or emu writes.
-- Source arenas prove the second-pipe coyote window and two local elevators;
-- a complete native route is still an experiment, never inferred from this.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local navigate=assert(dofile(root..'/tools/playthroughs/mario_luigi_scrooge_nav.lua'))
local jumpAt=nil
local opening=false
local openingJumped=false
local third='mount'
local walkAt=nil
local boarded={[0]=false,[1]=false}
local cleared={[0]=false,[1]=false}
local finalStair=false
local function age(c,t)return(c.r('CmClock')-t)&255 end
local function released(c)return(c.r('CmPreviousAB')&128)==0 end
local function jump(c,b)
 if released(c)and c.r('CmJumpInterval')==0 and(c.grounded or c.r('CmCoyote')>0)then
  jumpAt=c.r('CmClock');b.a=true;return true
 end
 return false
end
local function hold(c,b)
 b.b=false
 if jumpAt and not c.grounded and age(c,jumpAt)<32 then b.a=true
 elseif c.grounded then jumpAt=nil end
 return b
end
local function platform(c,index)
 local slot=c.r('HpActorSlot',index)-1
 if slot<0 or slot>5 then return nil end
 if c.r('HpActorOwner',slot)~=129+index or c.r('Enemy_Flag',slot)~=1
  or c.r('Enemy_ID',slot)~=0x25 or c.r('Enemy_State',slot)~=0x40 then return nil end
 return slot
end
local function elevator(c,index,wall,target)
 if cleared[index]then return nil end
 if c.x>=wall+32 then
  assert(boarded[index],'Route must observe real native platform boarding')
  cleared[index]=true;return nil
 end
 jumpAt=nil
 local slot=platform(c,index)
 local supported=slot and c.grounded and c.r('PlatformCollisionFlag',slot)==slot
  and math.abs(c.y-(c.r('Enemy_Y_Position',slot)-32))<=1
 if supported and not boarded[index]then
  boarded[index]=true
  print(string.format('CELESTE tier0 platform%d boarded clock=%d x=%d y=%d actor=%d nativeY=%d',wall,c.r('CmClock'),c.x,c.y,slot,c.r('Enemy_Y_Position',slot)))
 end
 -- No jump before boarding. Wait over the real girder and let its original
 -- collision/carry raise the player; no captured-position/outcome substitute.
 if supported and c.y<=112 then
  return{right=true}
 end
 if boarded[index]and c.x>target+8 and c.y<=112 then return{right=true}end
 return{right=c.x<target,left=c.x>target+3}
end
return function(c)
 assert(c.char==0 and c.r('MarioVariant')==4,'Actual Celeste raw0/variant4')
 assert(c.r('CmTier')==0 and c.status==0,'Natural unpowered route; no acquired Mushroom/form')
 if c.world~=0 or c.level~=0 then
  assert(third=='done'and cleared[0]and cleared[1],'Required tier0 traversal witnesses before1-2')
  return{right=true}
 end
 -- Jump before the first walking Goomba, then descend underneath the real
 -- Mushroom block rather than executing the earned-pickup policy.
 if not opening then
  local b={right=true}
  if c.x>=264 and c.grounded and not openingJumped then openingJumped=jump(c,b)end
  if c.x>=420 then opening=true;jumpAt=nil else return hold(c,b)end
 end
 -- Arrive on the48px second pipe, run from its real top near632/Y128,
 -- release A, walk4..6 source updates, then consume genuine coyote grace.
 if third~='done'and c.x>=600 and c.x<784 then
  local b={right=true}
  if c.x>=736 and c.y<=112 then third='done';jumpAt=nil;return b end
  if third=='mount'then
   if c.grounded and c.y==128 then
    jumpAt=nil
    if c.x>626 then return{left=true}end
    third='runup';return b
   end
   b.right=c.x<632;b.left=c.x>636
   if c.grounded and c.y>128 then b.right=true;b.left=false;jump(c,b)end
   return hold(c,b)
  elseif third=='runup'then
   jumpAt=nil
   if c.x>=632 and c.x<=636 and c.vx==32 and c.y==128 then
    third='walk';walkAt=c.r('CmClock')
   end
   return b
  elseif third=='walk'then
   local elapsed=age(c,walkAt)
   if c.x>=640 and c.x<=644 and c.r('CmCoyote')>0 and jump(c,b)then
    third='flight'
    print(string.format('CELESTE tier0 coyote clock=%d x=%d y=%d grace=%d elapsed=%d',c.r('CmClock'),c.x,c.y,c.r('CmCoyote'),elapsed))
   elseif c.x>644 or elapsed>8 then third='mount';return{left=true}end
   return b
  else return hold(c,b)end
 end
 -- Physical boarding and original native25 carry, not a source-clock toggle.
 if c.x>=824 and c.x<976 and not cleared[0]then
  local b=elevator(c,0,912,880);if b then return b end
 end
 if c.x>=2184 and c.x<2304 and not cleared[1]then
  local b=elevator(c,1,2240,2224);if b then return b end
 end
 -- Land on the final real stair before walking to its lip. The old generic
 -- early jump launches from the lower step and does not model this height.
 if c.x>=2384 and c.x<2464 and not finalStair then
  if c.grounded and c.y<=112 and c.x>=2416 and c.x<=2424 then finalStair=true
  else
   local b={right=c.x<2416,left=c.x>2424}
   if c.grounded and c.y>112 then b.right=true;b.left=false;jump(c,b)end
   return hold(c,b)
  end
 end
 local b=navigate(c);local wanted=b.a;b.a=false;b.b=false
 local feet=c.y+32
 local function solid(x,y)local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3 end
 -- A late source-coyote jump avoids spending the limited51px jump before
 -- the96/80px floor gaps. Actual source readback admits every new A edge.
 local edge=not solid(c.x+12,math.min(feet+8,232))
 if edge and c.x>1200 and c.y>=112 then
  wanted=not c.grounded and c.r('CmCoyote')>0 and c.r('CmCoyote')<=4
 end
 if c.x>=3120 and c.x<3184 then
  b.right=true
  wanted=c.grounded and(solid(c.x+12,c.y+24)or c.x>=3148)
 end
 if wanted then jump(c,b)end
 return hold(c,b)
end
