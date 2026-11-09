-- Appended to the bound Mini stage and earned-power controller. Pad input
-- is the only game-state stimulus.
do
 local earned_route = route_tick
 local function right_edge()
  return read(0x0720)+256*read(0x071e)
 end
 local function player_x()
  return r('Player_X_Position')+256*r('Player_PageLoc')
 end
 local function actor(slot)
  return {slot=slot,flag=read(0x10+slot),id=read(0x17+slot),
   state=read(0x1f+slot),x=read(0x76+slot)+256*read(0x5d+slot),
   y=read(0xbe+slot),y_high=read(0xa5+slot),box=read(0x646+slot)}
 end
 local function snapshot_native()
  return {frame=frame,source=updates,counter=r('FrameCounter'),right=right_edge(),
   x=player_x(),y=r('Player_Y_Position'),engine=r('GameEngineSubroutine'),
   timer=r('TimerControl'),status=r('PlayerStatus'),seen=ram(0xc30c),
   scroll=read(0x0701),side_hold=read(0x0782),scroll_lock=r('ScrollLock'),
   input=read(0xdc),support=ram(0xc30d)}
 end
 local function actors()
  local rows={}
  for slot=0,5 do rows[#rows+1]=actor(slot) end
  return rows
 end
 local function keep_holding_right()
  route_pad={right=true,b=true}
 end
 local function relevant()
  return phase=='fullstage' and r('SelectedCharacter')==41
   and r('WorldNumber')==0 and r('LevelNumber')==0 and power.completed
 end
 route_tick=function(s)
  if not power.completed then return earned_route(s) end
  local first=mini_lift_runs[560]
  if not injury.hunt and first and first.boarded and first.departed
   and s.nativeX>=injuryConfig.hunt_x then
   injury.hunt=snapshot_native()
   injury.hunt.actors=actors()
  end
  if not injury.hunt then return first_route(s) end
  keep_holding_right()
  if updates%8==0 and #injury.approach<48 then
   local q=snapshot_native()
   q.actors=actors()
   injury.approach[#injury.approach+1]=q
  end
  check(right_edge()<856,'The third offscreen window began before a powered side hit')
  check(frame-injury.hunt.frame<400,'No powered side hit within the bounded approach')
 end
 emu.addMemoryCallback(guard(function()
  if not relevant() or not valid(injuryConfig.force) then return end
  local slot=emu.getState()['cpu.x']
  if r('PlayerStatus')~=1 or slot>5 then return end
  local enemy=actor(slot)
  if enemy.flag~=1 or (enemy.id~=6 and enemy.id~=2) then return end
  local q=snapshot_native()
  q.enemy=enemy
  injury.force=q
  keep_holding_right()
 end),emu.callbackType.exec,injuryConfig.force.pc)
 emu.addMemoryCallback(guard(function()
  if not relevant() or r('GameEngineSubroutine')~=10
   or not valid(injuryConfig.native_control) then return end
  keep_holding_right()
  injury.reset_epoch=true
  if not injury.start then
   check(injury.force~=nil,'Engine10 must follow actual powered contact')
   check(injury.force.right<856,'Powered contact must precede the third admission window')
   injury.start=snapshot_native()
  end
  check(#injury.native_steps<39,'Native injury control stays within 39 logical steps')
  injury.native_steps[#injury.native_steps+1]=snapshot_native()
 end),emu.callbackType.exec,injuryConfig.native_control.pc)
 emu.addMemoryCallback(guard(function()
  if not relevant() or r('GameEngineSubroutine')~=10
   or not valid(injuryConfig.post_control) then return end
  keep_holding_right()
  injury.reset_epoch=true
  local q=snapshot_native()
  check(#injury.post_control<57,'Bounded active injury snapshots')
  injury.post_control[#injury.post_control+1]=q
  local before=injury.native_steps[#injury.native_steps]
  if not before or before.counter~=q.counter then return end
  check(q.right>=before.right and q.right-before.right<=3,'Native injury camera advances by at most three pixels')
  if q.right<856 then return end
  local birth=camera_lift_spawns[864]
  check(birth~=nil,'No actual constructor at the first eligible injury scroll')
  check(birth.engine==10 and birth.right>=856 and birth.right<=863 and birth.top==192,
   'Third native constructor must be in mode10 while the lift is offscreen')
  local lift=actor(birth.slot)
  check(lift.flag==1 and lift.id==0x25 and lift.state==0x40 and lift.x==864
   and lift.y_high==1 and lift.box==5 and q.seen&4~=0,
   'Actual native lift is published before the enemy loop')
  if q.right>=864 then
   check(q.status==0 and #injury.native_steps>0,'Lost the actual earned power during camera motion')
   injury.visible=q
   injury.visible.actor=lift
  end
 end),emu.callbackType.exec,injuryConfig.post_control.pc)
 emu.addEventCallback(guard(function()
  if not relevant() then return end
  local engine=r('GameEngineSubroutine')
  if engine==10 then
   keep_holding_right()
   injury.reset_epoch=true
  elseif injury.start and not injury.visible then
   check(false,'Injury ended before the complete offscreen interval was crossed')
  end
  if injury.visible then
   check(r('NumberofLives')==startLives,'Powered injury retains the life')
   injury.visible.sprite_chr4=emu.getState()['mapper.chrBanks4']
   injury.completed=true
   transition('finish')
  end
 end),emu.eventType.endFrame)
end
