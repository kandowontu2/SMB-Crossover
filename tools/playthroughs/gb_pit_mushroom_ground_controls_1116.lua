-- Walk off the actual first row before a fresh grounded authored-M head jump.
local phase,started,settled,headAge='opening',nil,0,0
return function(c)
 local item
 for i=0,5 do if c.r('Enemy_Flag',i)==1 and c.r('Enemy_ID',i)==46 and c.r('PowerUpType',i)==0 then
  item={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i)}
 end end
 food.ground_route=food.ground_route or{}
 local trace=food.ground_route
 if item then phase='collect'end
 if phase=='opening'then
  local edge=352;while edge<448 and c.block(edge,144)~=0 do edge=edge+16 end
  assert(edge<=416,'Authored first row ends before first pipe')
  if c.x<edge+16 then return travel(c)end
  phase='off-left';started=c.poll;trace.from_cap=state()
  local left=336;while left>240 and c.block(left-16,144)~=0 do left=left-16 end
  assert(left>=304 and left<=336 and c.block(left,144)~=0 and c.block(left-16,144)==0,'Actual left edge of first row')
  trace.left_edge=left;trace.clear_left=left-24
 end
 assert(c.poll-(started or c.poll)<750,'One bounded grounded firstM route')
 if phase=='off-left'then
  trace.last_off_left={x=c.x,y=c.y,camera=c.camera,relativeX=c.x-c.camera,grounded=c.grounded}
  if c.grounded and c.y>=160 then
   trace.actual_ground=state();trace.ground_camera=c.camera;trace.ground_relativeX=c.x-c.camera
   trace.support_cells={c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32)};phase='head-column';return{}
  end
  return{left=c.x>math.max(trace.clear_left,c.camera+1)}
 elseif phase=='head-column'then
  local center=math.max(329,c.camera+1);assert(center+8<352,'Authored firstM stays within actual camera')
  if c.grounded and c.y>=160 and c.x>=center and c.x<=center+2 then
   settled=settled+1;if settled>=16 then phase='head';headAge=0;trace.head_request=state()end
  else settled=0 end
  return{right=c.x<center,left=c.x>center+2}
 elseif phase=='head'then
  headAge=headAge+1;assert(headAge<100,'Fresh original grounded head jump');return{a=headAge<=24}
 elseif phase=='collect'then
  if not item then return{}end
  return{right=c.x<item.x-3,left=c.x>item.x+3}
 end
 error('Unknown GB Pit firstM phase')
end
