-- Source-bound adaptive route. Uses genuine controller inputs only.
local route_obstacles={
 {kind='pipe',left=448,right=480,top=176},{kind='pipe',left=608,right=640,top=160},
 {kind='pipe',left=736,right=768,top=144},{kind='pipe',left=912,right=944,top=144},
 {kind='pit',left=1104,right=1136},{kind='pit',left=1376,right=1424},{kind='pit',left=2448,right=2480}}
local route_index,route_max,route_stationary,route_previous=1,0,0,nil
local route_jumps,route_walls,route_clears={},0,{}
local function route_solid(x,y)
 if y<32 or y>=240 or x<0 then return false end
 local at=0x300+((x//256)&1)*0xd0+(y&240)-32+((x&255)//16)
 return ram(0xd300+read(at))&3==1
end
local function route_enemy(x,y)
 for i=0,5 do
  if read(L.Enemy_Flag+i)>0 and read(L.Enemy_Flag+i)<128 and read(L.Enemy_State+i)&32==0 then
   local ex=read(L.Enemy_X_Position+i)+256*read(L.Enemy_PageLoc+i)
   local ey=read(L.Enemy_Y_Position+i)
   if ex-x>=-8 and ex-x<=46 and math.abs(ey-(y-8))<=40 then return true end
  end
 end
 return false
end
local function route_tick(s)
 route_steps=route_steps+1;check(route_steps<10000,'Fullstage source-update bound')
 local x,y=s.x/16,s.y/16;route_max=math.max(route_max,x)
 if route_previous and x<=route_previous+0.05 then route_stationary=route_stationary+1 else route_stationary=0 end
 route_previous=x;check(route_stationary<400,'Fullstage stationary source-update bound')
 check(r('WorldNumber')==0 and r('LevelNumber')<=1,'No route shortcuts or unintended world')
 local ob=route_obstacles[route_index]
 phases.fullstage.actual_original_jump_entries=route_jumps
 phases.fullstage.actual_obstacle_clears=route_clears
 phases.fullstage.wall_restarts=route_walls
 if ob and x>=ob.right+8 then
  local prior=#route_clears>0 and route_clears[#route_clears].jumps or 0
  check(#route_jumps>prior,'Authored obstacle has its own actual original jump entry')
  route_clears[#route_clears+1]={kind=ob.kind,left=ob.left,right=ob.right,x16=s.x,y16=s.y,source=updates,jumps=#route_jumps,wall_restarts=route_walls}
  events[#events+1]={kind='authored-obstacle-cleared',index=route_index,source=updates,x16=s.x,y16=s.y}
  route_index=route_index+1
 end
 local floor=s.contacts&1~=0 and s.class==2
 local cling=s.contacts&8~=0 and s.contacts&1==0 and s.vy==0
 local front=route_solid(math.floor(x+24),math.floor(y+1))or route_solid(math.floor(x+24),math.floor(y+7))
 local gap=not route_solid(math.floor(x+22),math.floor(y+8))
 local want=front or gap or route_enemy(x,y)
 route_pad={right=true,b=true}
 if s.queued==12 then
  -- Original GROUND_END retains its prior floor contacts for one epoch;
  -- keep A through the already queued JUMP_INIT, then use actual air state.
  route_pad.a=true
 elseif floor then
  -- Release any prior heldA on genuine support before a fresh source jump.
  if want and s.held&128==0 then route_pad.a=true end
 else
  route_pad.a=true
  -- Exactly the qualified wall25 policy: one source release, then freshA
  -- through MiniHostWallJump queues the unchanged original jump initializer.
  if cling and s.queued~=12 and s.held&128~=0 then route_pad.a=false end
 end
end
local source_step=C.hooks.MiniStep
emu.addMemoryCallback(guard(function()
 if phase~='fullstage'or not active()or not valid(source_step)then return end
 if ram(0xc228)==12 then
  check(#route_jumps<200,'Bounded actual original jump records')
  local q={frame=frame,source=updates,x16=word(0xc250),y16=word(0xc252),contacts=ram(0xc24c),held=ram(0xc248),fresh=ram(0xc24a),native_state=r('Player_State')}
  route_jumps[#route_jumps+1]=q
  if q.contacts&8~=0 and q.contacts&1==0 then route_walls=route_walls+1 end
 end
end),emu.callbackType.exec,source_step.pc)
local function route_endframe()
 check(r('NumberofLives')==startLives,'Fullstage retains actual lives')
 check(r('GameEngineSubroutine')~=11,'Fullstage natural death')
 if r('WorldNumber')==0 and r('LevelNumber')==1 and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 and ram(0xc300)==2 then
  check(#route_clears==7,'Actual active1-2 requires all four pipes and three authored pits')
  check(#route_jumps>0 and boxes>50 and dmas>50,'Actual original movement/native collision/hardware observed')
  check(route_max>3200,'Native castle route reached without shortcut')
  phases.fullstage.actual_original_jump_entries=route_jumps
  phases.fullstage.actual_obstacle_clears=route_clears
  phases.fullstage.wall_restarts=route_walls
  route_complete=true;transition('finish')
 end
end
