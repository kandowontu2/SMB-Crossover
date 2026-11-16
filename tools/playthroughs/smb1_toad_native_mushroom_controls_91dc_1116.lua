-- Actual authored first row, then legal ground return below its Mushroom.
local phase,headAge,settled,started='opening',0,0,0
return function(c)
 local item
 for i=0,5 do if c.r('Enemy_Flag',i)==1 and c.r('Enemy_ID',i)==46 and c.r('PowerUpType',i)==0 then
  item={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i)}
 end end
 if item then phase='collect' end
 if phase=='opening'then
  local edge=352
  while edge<448 and c.block(edge,144)~=0 do edge=edge+16 end
  assert(edge<=416,'Real first item row bounded before first pipe')
  if c.x<edge+16 then local b=travel(c);b.b=false;return b end
  phase='return';started=c.poll
 end
 assert(c.poll-started<500,'One bounded ordinary firstM admission/collection')
 if phase=='return'then
  local center=math.max(329,c.camera+1)
  assert(center+8<352,'FirstM head column remains within actual camera')
  if c.grounded and c.y>=160 and c.x>=center and c.x<=center+2 then
   settled=settled+1;if settled>=16 then phase='head';headAge=0 end
  else settled=0 end
  return{right=c.x<center,left=c.x>center+2}
 elseif phase=='head'then
  headAge=headAge+1;assert(headAge<100,'One real native head jump')
  return{a=headAge<=24}
 elseif phase=='collect'then
  if not item then return{}end
  return{right=c.x<item.x-3,left=c.x>item.x+3}
 end
 error('Unknown native firstM phase')
end
