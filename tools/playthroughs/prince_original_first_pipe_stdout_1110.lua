-- Controller-only cold launch and original Prince first-pipe crossing.
local rom = os.getenv('SMB_STDOUT_ROM_SHA') or ''
local variant = tonumber(os.getenv('SMB_TEST_VARIANT') or '0')
local cookie = 'a726021676a00802119275ac7f48cce7'
local frame, pad, stopped = 0, 0, false
local commits, sourceUpdates, sourceDraws = 0, 0, 0
local previousCommits, gameplayFrames, idleFrames, maximumUpdates = 0, 0, 0, 0
local progress, events, injuries = 'title', {}, {}
local initial, settled, firstEnemy, jump, climb, top, final
local lastCommit, previousHP, changedAt = -1, 5, 0
local firstPipe, laterPipe = nil, 1
local caps = {}
local late, supportPublications = {}, {}
local obstacles = {{left=608,right=640,top=160,brake=577},{left=736,right=768,top=144,brake=690}}

local function read(address)
  return emu.read(address, emu.memType.nesDebug)
end

local function source(offset, bank)
  return emu.read((bank or 2)*8192+offset, emu.memType.nesWorkRam)
end

local function hexHeader(bank)
  local values = {}
  for i = 0x1fe0,0x1fef do values[#values+1] = string.format('%02x',source(i,bank)) end
  return table.concat(values)
end

local function state()
  return {frame=frame,commit=commits,x=read(0x75)+256*read(0x5c),y=read(0xbd),
    y_high=read(0xa4),ground=read(0x1e),action=source(0x616),pose=source(0x617),
    facing=source(0x615),mode=source(0x618),lock=source(0x6c0),phase=source(0xa6),
    foot=source(0x84)+256*source(0x85),hp=source(0x6cf),lives=read(0x75f),engine=read(0x0f),
    area=read(0x754),world=read(0x764),level=read(0x761),
    scroll=read(0x71f)+256*read(0x71d),nativeInput=read(0xdc)}
end

local function encode(value)
  local kind = type(value)
  if kind=='boolean' or kind=='number' then return tostring(value) end
  if kind=='nil' then return 'null' end
  if kind=='string' then
    return '"'..value:gsub('[%z\1-\31\\"]',function(character)
      return string.format('\\u%04x',string.byte(character))
    end)..'"'
  end
  assert(kind=='table')
  local entries = {}
  if #value>0 then
    for _,item in ipairs(value) do entries[#entries+1]=encode(item) end
    return '['..table.concat(entries,',')..']'
  end
  for key,item in pairs(value) do entries[#entries+1]=encode(key)..':'..encode(item) end
  table.sort(entries)
  return '{'..table.concat(entries,',')..'}'
end

local function finish(passed,reason)
  if stopped then return end
  stopped=true
  print('SMB_NATIVE_RECEIPT '..encode({passed=passed,reason=reason,ROM_SHA256=rom,
    controller_only=true,output_files=0,physical_frames=frame,phase=progress,
    commits=commits,source_updates=sourceUpdates,source_draws=sourceDraws,
    gameplay_physical_frames=gameplayFrames,gameplay_no_original_commit_frames=idleFrames,
    maximum_commits_in_frame=maximumUpdates,initial=initial,settled=settled,
    first_enemy=firstEnemy,running_jump=jump,climb=climb,pipe_top=top,
    terminal=final or state(),events=events,injuries=injuries,added_helpers=false,
    header2=hexHeader(2),header3=hexHeader(3),first_pipe=firstPipe,later_caps=caps,
    later_route=late,fourth_support_publications=supportPublications}))
  emu.stop(passed and 0 or 1)
end

local function guarded(callback)
  return function(...)
    if stopped then return end
    local ok,why=pcall(callback,...)
    if not ok then finish(false,tostring(why)) end
  end
end

local function mapped(pc,bank)
  local physical=emu.convertAddress(pc)
  return physical and physical.memType==emu.memType.nesWorkRam
    and physical.address==bank*8192+(pc&8191)
end

local function observe(pc,bank,callback)
  emu.addMemoryCallback(guarded(function()
    if mapped(pc,bank) and read(0x6002)==38 then callback() end
  end),emu.callbackType.exec,pc)
end

observe(0xb36e,3,function()sourceUpdates=sourceUpdates+1 end)
observe(0xb37c,3,function()commits=commits+1 end)
observe(0xbbc1,3,function()sourceDraws=sourceDraws+1 end)
observe(0xd74b,2,function()
  local s=state()
  if s.x>=895 and s.x<944 and #supportPublications<12 then
    assert(read(0xd74b)==0x8d and read(0xd74c)==0x7f and read(0xd74d)==0xc0,'Original support publication site')
    supportPublications[#supportPublications+1]={state=s,surface=emu.getState()['cpu.a']}
  end
end)

local function enemyNear(x)
  local best
  for slot=0,5 do
    local flag,id=read(0x10+slot),read(0x17+slot)
    local y,high=read(0xbe+slot),read(0xa5+slot)
    local position=read(0x76+slot)+256*read(0x5d+slot)
    local distance=position-x
    if flag>0 and flag<128 and id==6 and high==1 and y>=160 and distance>=-16
      and (not best or distance<best.gap) then
      best={slot=slot,x=position,y=y,gap=distance,state=read(0x1f+slot)}
    end
  end
  return best
end

local function switch(nextPhase,buttons,details)
  progress,pad,changedAt=nextPhase,buttons,commits
  assert(#events<52,'Bounded route phase summary')
  events[#events+1]={phase=nextPhase,state=state(),details=details}
end

local function floor(s)
  return s.y_high==1 and math.abs(s.y-176)<=2 and s.foot>=207 and s.foot<=211
end

local function tile(x,y)
  if x<0 or y<32 or y>=240 then return 0 end
  return read(0x300+((x//256)&1)*208+(y&240)-32+((x&255)//16))
end

local function solid(x,y)
  return read(0xef36+tile(x,y))&1~=0
end

local function support(s)
  if s.y_high~=1 or s.ground~=0 then return false end
  return solid(s.x+2,s.y+32) or solid(s.x+13,s.y+32)
end

local function idle(s)
  return s.pose==15 and s.mode==0 and s.lock==0
end

local function running(s)
  return support(s) and s.action==1 and s.mode==1 and s.pose>=6 and s.pose<=13 and s.lock==0
end

local function capFeet(s,left,top)
  local function foot(x)
    local value=tile(x,top)
    return x>=left and x<left+32 and value>=0x10 and value<=0x13 and tile(x,top-1)==0
  end
  local grounded=support(s) and math.abs(s.y+32-top)<=1
  return grounded and foot(s.x+2),grounded and foot(s.x+13)
end

local function thirdWalkers()
  local walkers={}
  for slot=0,5 do
    local x=read(0x76+slot)+256*read(0x5d+slot)
    local flag=read(0x10+slot)
    if flag>0 and flag<128 and read(0x17+slot)==6 and read(0x1f+slot)<2
      and x>=764 and x<940 and read(0xbe+slot)>=160 then
      walkers[#walkers+1]={slot=slot,x=x,direction=read(0x53f+slot)}
    end
  end
  return walkers
end

local function fourthAndGap(s)
  if progress=='third-park' and s.action~=0 and s.action~=1 and s.action~=10 then
    assert(s.action==42,'Original careful step on third pipe')
    switch('third-settle',0)
  elseif progress=='third-settle' and idle(s) then
    local left,right=capFeet(s,736,144)
    assert(left and right,'Both native third-pipe feet supported')
    late.third_full_cap=s
    switch('third-wait-walkers',0)
  elseif progress=='third-wait-walkers' then
    local left,right=capFeet(s,736,144)
    assert(left and right,'Third cap remains stable while waiting')
    local walkers=thirdWalkers()
    if #walkers==2 and walkers[1].direction==2 and walkers[2].direction==2
      and walkers[1].x<=848 and walkers[2].x<=848 then
      switch('third-standing-jump',129,walkers)
    end
  elseif progress=='third-standing-jump' and s.action==3 then
    switch('third-flight',1)
  elseif progress=='third-flight' and s.x>=784 and s.y==176 and support(s) then
    switch('fourth-recovery',1)
  elseif progress=='fourth-recovery' and s.x>=897 then
    switch('fourth-wall-settle',0)
  elseif progress=='fourth-recovery' and idle(s) and support(s) then
    switch('fourth-wall-step',65)
  elseif progress=='fourth-wall-step' and s.action~=0 and s.action~=1 then
    switch('fourth-wall-settle',0)
  elseif progress=='fourth-wall-settle' and idle(s) and support(s) then
    if s.x>=897 then switch('fourth-up',8) else switch('fourth-wall-step',65) end
  elseif progress=='fourth-up' then
    local left,right=capFeet(s,912,144)
    if left or right then
      late.fourth_partial=s
      switch('fourth-anchor-step',65)
    elseif s.x>=944 and s.y>=172 then
      error('No supported fourth-pipe traversal')
    end
  elseif progress=='fourth-anchor-step' and s.action~=0 and s.action~=1 and s.action~=10 then
    switch('fourth-anchor-settle',0)
  elseif progress=='fourth-anchor-settle' and idle(s) then
    local left,right=capFeet(s,912,144)
    assert(left and right,'Both native fourth-pipe feet supported')
    late.fourth_full_cap=s
    switch('fourth-cross',1)
  elseif progress=='fourth-cross' and s.x>=960 and s.y==176 and support(s) then
    switch('first-gap-approach',1)
  elseif progress=='first-gap-approach' and s.x>=1059 and s.x<=1090 and running(s) then
    assert(tile(1088,208)==0x54 and tile(1104,208)==0 and tile(1120,208)==0 and tile(1136,208)==0x54,
      'First gap has both actual banks and two empty columns')
    switch('first-gap-takeoff',129)
  elseif progress=='first-gap-takeoff' and s.action==4 then
    switch('first-gap-flight',1)
  elseif progress=='first-gap-flight' and s.x>=1152 and s.y==176 and support(s) then
    late.first_gap=s
    assert(#supportPublications>0,'Observed actual fourth pipe support publication')
    if variant==2 then
      final=s
      finish(true,'Natural Prince crosses four native pipes and the first gap with original actions')
    else
      switch('second-gap-approach',1)
    end
  elseif progress=='second-gap-approach' and s.x>=1340 and s.x<=1356 and s.phase&3<=1 and running(s) then
    assert(tile(1360,208)==0x54 and tile(1376,208)==0 and tile(1392,208)==0
      and tile(1408,208)==0 and tile(1424,208)==0x54,'Second gap has both native banks and three empty columns')
    switch('second-gap-takeoff',129)
  elseif progress=='second-gap-approach' and s.x>=1361 then
    error('Original second-gap takeoff window missed')
  elseif progress=='second-gap-takeoff' and s.action==4 then
    switch('second-gap-flight',1)
  elseif progress=='second-gap-flight' and s.x>=1440 and s.y==176 and support(s) then
    late.second_gap=s
    final=s
    finish(true,'Natural Prince crosses four native pipes and two gaps with original actions')
  end
end

local function laterTick(s)
  local obstacle=obstacles[laterPipe]
  local onFloor=support(s)
  local age=commits-changedAt
  if progress=='later-approach' and s.x>=obstacle.brake and s.x<obstacle.left then
    switch('later-settle',0)
  elseif progress=='later-settle' and onFloor and s.pose==15 and s.mode==0 and s.lock==0 then
    switch('later-up',8)
  elseif progress=='later-up' or progress=='later-climb' or progress=='later-cap-approach' then
    local atCap=s.x+13>=obstacle.left and s.x<obstacle.right
      and onFloor and math.abs(s.y+32-obstacle.top)<=2
    if atCap then
      caps[#caps+1]={obstacle=obstacle,state=s,leadingTile=tile(s.x+13,obstacle.top)}
      if laterPipe==#obstacles then
        if variant==1 then
          final=s
          finish(true,'Natural first pipe and second/third native pipe caps')
        else
          switch('third-park',65)
        end
      else
        switch('later-cross',1)
      end
    elseif progress=='later-cap-approach' then
      pad=1
    elseif s.action==10 and s.foot<=obstacle.top+3 then
      switch('later-cap-approach',1)
    elseif s.mode==2 or s.mode==6 or s.action==10 then
      if progress~='later-climb' then switch('later-climb',9) end
      pad=9
    elseif progress=='later-up' and laterPipe==1 and s.action==47 and age>80 and not obstacle.realigned then
      obstacle.realigned=true
      switch('later-settle',0)
    elseif progress=='later-up' then
      pad=age<55 and 8 or 201
    end
  elseif progress=='later-cross' and s.x>=obstacle.right+16 and onFloor then
    laterPipe=laterPipe+1
    switch('later-approach',1)
  end
end

local function tick()
  gameplayFrames=gameplayFrames+1
  local delta=commits-previousCommits
  previousCommits=commits
  if delta==0 then idleFrames=idleFrames+1 end
  maximumUpdates=math.max(maximumUpdates,delta)
  if commits==lastCommit then return end
  lastCommit=commits
  local s=state()
  assert(read(0x6002)==38 and read(0x771)==1 and read(0x773)==3 and s.engine==8,'Native active Prince 1-1')
  assert(s.world==0 and s.level==0 and s.area==5,'Native World 1-1 area')
  assert(s.lives==2 and s.hp>0 and s.hp<=5,'Alive with both lives')
  assert(source(0xab)==0xa7 and hexHeader(2)==cookie and hexHeader(3)==cookie,'Complete active Prince headers')
  assert(commits-changedAt<900,'First pipe phase progress bound')
  if s.hp~=previousHP then
    injuries[#injuries+1]={from=previousHP,to=s.hp,state=s}
    previousHP=s.hp
  end
  local enemy=enemyNear(s.x)
  firstEnemy=firstEnemy or enemy
  if firstPipe then
    if #caps==2 then fourthAndGap(s) else laterTick(s) end
    return
  end
  if progress=='settle-start' and commits-changedAt>=4 then
    assert(s.x==initial.x and s.hp==5 and floor(s) and sourceDraws>0,'Original neutral starting state and draw')
    settled=s
    switch('approach',1)
  elseif progress=='approach' then
    if not jump and enemy and enemy.gap>=115 and enemy.gap<=136 and s.action==1 and s.mode==1
      and s.pose>=6 and s.pose<14 and s.lock==0 and s.ground==0 then
      jump={request=s,enemy=enemy,minimumY=s.y}
      switch('run-jump',129,enemy)
    elseif s.x>=400 then
      switch('pipe-settle',0)
    end
  elseif progress=='run-jump' then
    jump.minimumY=math.min(jump.minimumY,s.y)
    if not jump.admission and s.action==4 then jump.admission=s;pad=1 end
    if jump.admission and commits-changedAt>=16 and s.action==1 and s.mode==1 and floor(s) then
      jump.landed=s
      if s.x>=400 then switch('pipe-settle',0) else switch('approach',1) end
    elseif not jump.admission and commits-changedAt>=32 then
      error('Original running jump did not admit action 4')
    end
  elseif progress=='pipe-settle' and s.pose==15 and s.mode==0 and s.lock==0 then
    assert(s.facing==255 and s.x>=390 and s.x<448 and floor(s),'Real idle stance before first pipe')
    switch('pipe-up',8)
  elseif progress=='pipe-up' then
    if s.mode==2 or s.mode==6 then climb=climb or s end
    if s.mode~=2 and s.mode~=6 and s.foot<=179 and s.y<=147 then
      assert(climb,'Source ledge mode before physical pipe top')
      top=s
      switch('pipe-over',1)
    elseif s.mode==2 or s.mode==6 or commits-changedAt<64 then
      pad=8
    else
      pad=201  -- Original Up+Right+A+B pipe-approach fallback.
    end
  elseif progress=='pipe-over' and s.x>=496 and floor(s) then
    assert(jump and jump.admission and jump.minimumY<176 and climb and top,'Original jump, ledge and crossing')
    if variant==0 then
      final=s
      switch('first-pipe-cleared',0)
      finish(true,'Natural Prince first pipe cleared using original jump and climb')
    else
      firstPipe=s
      switch('later-approach',1)
    end
  end
end

local function frames(count)
  for _=1,count do coroutine.yield() end
end

local function press(buttons,rest)
  pad=buttons;frames(6);pad=0;frames(rest)
end

local function waitUntil(predicate,bound,label)
  for _=1,bound do
    if predicate() then return end
    coroutine.yield()
  end
  error(label)
end

local route=coroutine.create(function()
  waitUntil(function()return frame>=120 and read(0x6004)==1 and read(0x775)==0 end,500,'Cold title')
  press(16,54)
  assert(read(0x7307)==2 and read(0x7309)==0,'Natural character selection')
  for _,buttons in ipairs({4,4,4,1,1,1,1,1}) do press(buttons,34) end
  assert(read(0x7309)==29 and read(0x6002)==37,'Excitebike slot')
  press(32,34)
  assert(read(0x7309)==29 and read(0x6002)==38,'Natural Prince alternate')
  press(16,34)
  waitUntil(function()
    return read(0x771)==1 and read(0x773)==3 and read(0x0f)==8 and source(0xab)==0xa7
  end,1400,'Original Prince cold construction')
  assert(read(0x7ffb)==0 and read(0x7ffc)==0,'No invincibility or level cheats')
  initial=state()
  assert(initial.x==40 and initial.lives==2 and initial.hp==5,'Authentic starting position, health and lives')
  previousCommits=commits
  switch('settle-start',0)
  while not stopped do tick();coroutine.yield() end
end)

assert(#rom==64 and not rom:find('[^0-9a-f]'),'Exact ROM SHA required')
assert(variant and variant>=0 and variant<=3 and variant%1==0,'Supported Prince route length')
emu.addEventCallback(guarded(function()
  emu.setInput({right=pad&1~=0,up=pad&8~=0,down=pad&4~=0,start=pad&16~=0,
    select=pad&32~=0,b=pad&64~=0,a=pad&128~=0},0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guarded(function()
  frame=frame+1
  assert(frame<=8000,'Bounded physical first-pipe replay')
  local ok,message=coroutine.resume(route)
  assert(ok,message)
end),emu.eventType.endFrame)
