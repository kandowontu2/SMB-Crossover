-- Native camera can retain support at the left face; land beside the right face.
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
  local edge=352;local cells={}
  while edge<448 do local tile=c.block(edge,144);cells[#cells+1]={x=edge,tile=tile};if tile==0 then break end;edge=edge+16 end
  assert(edge<=416,'Actual first row ends before first pipe')
  if c.x<edge+16 then return travel(c)end
  phase='off-right';started=c.poll;trace.from_cap=state();trace.from_cap_camera=c.camera;trace.from_cap_relativeX=c.x-c.camera
  local left=336;while left>240 and c.block(left-16,144)~=0 do left=left-16 end
  trace.left_edge=left;trace.right_edge=edge;trace.clear_right=edge+16;trace.row_cells=cells
  assert(trace.clear_right<448 and c.block(trace.clear_right,208)~=0,'Real supported right-side ground before pipe')
 end
 assert(c.poll-(started or c.poll)<750,'One bounded ordinary right-clear firstM route')
 if phase=='off-right'then
  trace.last_off_right={state=state(),camera=c.camera,relativeX=c.x-c.camera,feet={c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32)}}
  if c.grounded and c.y>=160 then
   trace.actual_ground=state();trace.ground_camera=c.camera;trace.ground_relativeX=c.x-c.camera
   trace.support_cells={c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32)};phase='head-column';return{}
  end
  return{right=c.x<trace.clear_right,left=c.x>trace.clear_right+2}
 elseif phase=='head-column'then
  local center=math.max(329,c.camera+1);assert(center+8<352,'Real head column stays visible under authoredM')
  if c.grounded and c.y>=160 and c.x>=center and c.x<=center+2 then
   settled=settled+1;if settled>=16 then phase='head';headAge=0;trace.head_request=state();trace.head_camera=c.camera end
  else settled=0 end
  return{right=c.x<center,left=c.x>center+2}
 elseif phase=='head'then
  headAge=headAge+1;assert(headAge<100,'Fresh native grounded head jump');return{a=headAge<=24}
 elseif phase=='collect'then
  if not item then return{}end
  return{right=c.x<item.x-3,left=c.x>item.x+3}
 end
 error('Unknown GB Pit right-clear phase')
end
