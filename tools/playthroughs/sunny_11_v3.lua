-- Preserve v2's real negative: stopping before the first Goomba was unsafe.
-- Use the verified opening jump route, then return BELOW the mushroom row
-- from its right edge. Ordinary inputs and read-only live actor telemetry.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local travel=assert(dofile(root..'/tools/playthroughs/sunny_11_v1.lua'))
local phase='opening'
local age,settled=0,0
local earned=false
return function(c)
 if c.world~=0 or c.level~=0 or earned then return travel(c)end
 if c.status>0 then earned=true;return travel(c)end
 if phase=='opening' then
  if c.x<426 then return travel(c)end
  phase='return'
 end
 local item
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
   item={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),
    y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i)}
  end
 end
 if item then phase='collect' end
 if phase=='return' then
  local b={right=c.x<329,left=c.x>332}
  if c.grounded and c.y>=160 and c.x>=329 and c.x<=332 then
   settled=settled+1
   if settled>=16 then phase='bump';age=0 end
  else settled=0 end
  return b
 elseif phase=='bump' then
  age=age+1
  if age>90 and c.grounded then phase='return';settled=0 end
  return {a=age<=24}
 elseif phase=='collect' then
  if not item then phase='return';settled=0;return {}end
  return {right=c.x<item.x-3,left=c.x>item.x+3}
 end
 return {}
end
