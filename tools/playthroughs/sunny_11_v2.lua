-- Real controller-only Sunny pickup route. v1 cleared1-1 but its navigator
-- jumped onto the block row before the pickup approach began. Preserve v1.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local mario=assert(dofile(root..'/tools/playthroughs/sunny_11_v1.lua'))
local phase='approach'
local age=0
local settled=0
local earned=false
return function(c)
 if c.world~=0 or c.level~=0 or earned then return mario(c)end
 if c.status>0 then earned=true;return mario(c)end
 if c.x<270 and phase=='approach' then return mario(c)end
 local b={}
 local item
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
   item={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),
    y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i)}
  end
 end
 if item then phase='collect' end
 if phase=='approach' then
  b.right=c.x<329;b.left=c.x>332
  if c.grounded and c.y>=160 and c.x>=329 and c.x<=332 then
   settled=settled+1
   if settled>=16 then phase='bump';age=0 end
  else settled=0 end
 elseif phase=='bump' then
  b.a=age<30
  age=age+1
  if age>90 and c.grounded then phase='approach';settled=0 end
 elseif phase=='collect' then
  if not item then phase='approach';settled=0;return b end
  b.right=c.x<item.x-3;b.left=c.x>item.x+3
  -- Let a native mushroom finish emerging and walk off its own block.
  -- No early overlap pickup, item seeding or repeated jumping into its rise.
 end
 return b
end
