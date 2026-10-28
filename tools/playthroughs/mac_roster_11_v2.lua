-- Revised for the art-aligned terrain successor; inputs only.
-- v1/v2 native negatives used the former tall collision body.
-- Controller discovery for the boxing roster. Approach the first mushroom
-- from the ground; do not land on its block first. Inputs only, no clear claim.
local phase='approach'
local began=0
local lastX,still=0,0
return function(c)
 if c.char~=15 then return{right=true}end
 if c.world~=0 or c.level~=0 then return{right=true}end
 local function solid(wx,y)
  local t=c.block(wx,y)
  return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3
 end
 local enemy=c.enemy()
 local b={right=true}
 if c.x==lastX then still=still+1 else still=0 end;lastX=c.x
 if phase=='approach'then
  if c.x>=312 then phase='settle';began=c.frame;b={}
  elseif enemy and enemy.dx>0 and enemy.dx<40 and math.abs(enemy.y-c.y)<32 then
   b={down=c.grounded,b=c.poll%8<2}
  end
 elseif phase=='settle'then
  b={}
  if c.frame-began>24 and c.grounded then phase='bump';began=c.frame;b.a=true end
 elseif phase=='bump'then
  b={a=c.frame-began<12}
  if c.frame-began>50 then phase='catch';began=c.frame end
 elseif phase=='catch'then
  if c.status>0 then phase='route'
  else
   local item
   for i=0,5 do
    if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
     item={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i)}
    end
   end
   b={}
   if item and item.state>=128 then
    b.right=c.x<item.x-6;b.left=c.x>item.x+14
    if item.y<c.y-20 and c.grounded and not c.lastA then b.a=true end
   elseif c.frame-began>100 then
    -- Retry the actual block, rather than treating a missing pickup as earned.
    phase='bump';began=c.frame;b.a=true
   end
   return b
  end
 end
 if phase~='route'then return b end
 local feet=c.y+32
 local obstacle=solid(c.x+42,feet-8)or solid(c.x+42,c.y+8)
 local support=false
 for y=math.min(feet+8,232),232,16 do
  if solid(c.x+32,y)then support=true;break end
 end
 local danger=enemy and enemy.dx>0 and enemy.dx<24 and math.abs(enemy.y-c.y)<32
 if c.grounded and not c.lastA and(obstacle or not support or danger or still>18)then b.a=true
 elseif not c.grounded then b.a=c.lastA and c.vy>=128 end
 if enemy and enemy.dx>0 and enemy.dx<64 and math.abs(enemy.y-c.y)<32 then
  b.b=c.poll%8<2
  b.down=c.grounded
  if c.r('LmStars')>0 then b.up=true;b.down=false end
 end
 return b
end
