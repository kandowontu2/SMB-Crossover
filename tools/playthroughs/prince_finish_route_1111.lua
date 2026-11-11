-- Continue on authored terrain after the verified question-block crossing.
local finishStop=tonumber(os.getenv('SMB_PRINCE_FINISH_STOP') or '0')
local finishCombat=os.getenv('SMB_PRINCE_FINISH_COMBAT')=='1'
local finishCombatGap=tonumber(os.getenv('SMB_PRINCE_FINISH_COMBAT_GAP') or '86')
local waitOnBrick=os.getenv('SMB_PRINCE_FINISH_BRICK_WAIT')=='1'
local lureWalkers=os.getenv('SMB_PRINCE_FINISH_LURE')=='1'
local ending

local function finishGeometry(s)
  local cells={}
  for col=math.max(s.scroll&~15,(s.x&~15)-16),math.min((s.x&~15)+96,s.scroll+239),16 do
    local rows={}
    for y=96,208,16 do rows[#rows+1]=tile(col,y) end
    cells[#cells+1]={x=col,rows=rows}
  end
  return cells
end

local function startEnding(s)
  final=nil
  ending={start=s,front=s.x,advanced=commits,marks={},
    climbs={{wall=s,kind='walker-brick',tiles=finishGeometry(s)}},jumps={}}
  late.finish=ending
  switch('late-finish-brake',0)
end

local function endingFrame()
  if not ending then return false end
  local s=state()
  if s.world==0 and s.level==1 and s.engine==8 and read(0x773)==3 then
    assert(ending.flag and ending.castle and ending.gap and s.lives==2,
      'Native flagpole, castle, third gap and active underground 1-2')
    final=s
    finish(true,'Prince cleared authored 1-1 and entered underground 1-2')
    return true
  end
  if s.engine~=8 or s.level~=0 then
    assert(s.lives==2 and s.engine~=11,'Prince survived the native exit sequence')
    if s.engine==4 and s.x>=3100 then ending.flag=ending.flag or s end
    if s.engine==5 and s.x>=3140 then ending.castle=ending.castle or s end
    pad=0
    return true
  end
  return false
end

local function endingTick(s)
  local p=ending
  local x=s.x
  if x>p.front then p.front=x;p.advanced=commits end
  if #p.marks==0 or x>=p.marks[#p.marks].state.x+96 then
    p.marks[#p.marks+1]={state=s,tiles=finishGeometry(s),actors=lateWalkers(s)}
  end
  if finishStop>0 and x>=finishStop and support(s) then
    final=s
    p.stop={state=s,tiles=finishGeometry(s)}
    finish(true,'Prince reached the late route checkpoint on authored terrain')
    return
  end
  if x>=2480 and s.y<=176 and support(s) and p.gap_jump then p.gap=p.gap or s end
  if commits-p.advanced>260 then
    p.obstruction={state=s,tiles=finishGeometry(s),actors=lateWalkers(s)}
    error('Original late route stopped advancing')
  end
  local age=commits-changedAt
  if progress=='late-finish-brake' then
    if support(s) and idle(s) then
      local attempt=p.climbs[#p.climbs]
      attempt.stance=s
      if attempt.kind=='retreat-brick' and s.facing==0 then
        attempt.retreat_stance=s
        switch('late-finish-step-left',66)
      elseif attempt.pipe_left and x+15<attempt.pipe_left and (attempt.steps or 0)<2 then
        attempt.steps=(attempt.steps or 0)+1
        switch('late-finish-pipe-step',65)
      else
        switch('late-finish-climb',8)
      end
    elseif age>110 then
      error('Original brake never settled beside the late wall')
    end
  elseif progress=='late-finish-step-left' and s.action==42 then
    switch('late-finish-step-settle',0)
  elseif progress=='late-finish-pipe-step' then
    if s.action==42 or s.action==30 then switch('late-finish-brake',0)
    elseif age>75 then error('Original careful pipe step did not start') end
  elseif progress=='late-finish-step-settle' and support(s) and idle(s) then
    p.climbs[#p.climbs].left_stance=s
    switch('late-finish-turn-right',1)
  elseif progress=='late-finish-turn-right' and s.facing==255 then
    p.climbs[#p.climbs].kind='retreat-right'
    p.advanced=commits
    switch('late-finish-brake',0)
  elseif progress=='late-finish-climb' then
    local attempt=p.climbs[#p.climbs]
    if s.mode==2 or s.mode==6 or s.action==10 then attempt.hang=attempt.hang or s end
    local takeoffY=attempt.pipe_left and 147
      or (attempt.kind=='stair' or attempt.kind=='third-stair') and 104
    if takeoffY and attempt.hang and s.action==10 and idle(s) and s.y<=takeoffY then
      attempt.cap=s
      local kind=attempt.pipe_left and 'pipe-top'
        or attempt.kind=='third-stair' and 'third-cap' or 'stair-top'
      p.jumps[#p.jumps+1]={kind=kind,request=s}
      switch('late-finish-jump',128)
    elseif attempt.hang and support(s) and idle(s) and s.y<=attempt.stance.y-8 then
      attempt.cap=s
      if attempt.kind=='walker-brick' then
        if waitOnBrick then
          p.brick_walkers=lateWalkers(s,6)
          assert(#p.brick_walkers==2,'Both natural Goombas walk toward the late brick')
          switch('late-finish-brick-wait',0)
        else
          p.jumps[#p.jumps+1]={kind='brick-walkers',request=s,actors=lateWalkers(s)}
          switch('late-finish-jump',128)
        end
      elseif attempt.kind=='retreat-right' then
        p.advanced=commits
        switch('late-finish-second-wait',0)
      else
        switch('late-finish-run',1)
      end
    elseif age>165 then
      error('Original Up did not reach support over the late wall')
    elseif attempt.pipe_left and age>=64 and not attempt.hang then
      pad=201
    end
  elseif progress=='late-finish-brick-wait' then
    assert(s.y<=114 and support(s),'Ordinary brick supports neutral while the walkers pass')
    local trailing=lateActor(p.brick_walkers[2].slot)
    if trailing.flag==0 or (trailing.id==6 and trailing.x+24<x) then
      p.walkers_below={state=s,actor=trailing}
      p.advanced=commits
      switch('late-finish-run',1)
    end
  elseif progress=='late-finish-retreat' then
    if s.facing==0 and x<=1948 and s.y==176 then
      p.climbs[#p.climbs+1]={kind='retreat-brick',wall=s,tiles=finishGeometry(s)}
      switch('late-finish-brake',0)
    end
  elseif progress=='late-finish-second-wait' then
    assert(s.y<=114 and support(s),'The same authored brick holds the left-facing climb')
    local trailing=lateActor(p.second_group.actors[2].slot)
    if trailing.flag==0 or (trailing.id==6 and trailing.x+24<x) then
      p.second_group.below={state=s,actor=trailing}
      p.advanced=commits
      switch('late-finish-run',1)
    end
  elseif progress=='late-finish-jump' then
    if s.action==4 or s.action==3 then
      local jump=p.jumps[#p.jumps]
      jump.admission=s
      jump.minimum_y=s.y
      jump.poses={}
      if jump.kind=='gap' then p.gap_jump=jump end
      switch('late-finish-air',1)
    elseif age>42 then
      error('Original late jump did not admit a jump action')
    end
  elseif progress=='late-finish-air' then
    local jump=p.jumps[#p.jumps]
    jump.minimum_y=math.min(jump.minimum_y,s.y)
    if #jump.poses<20 and (#jump.poses==0 or jump.poses[#jump.poses].state.pose~=s.pose) then
      jump.poses[#jump.poses+1]={state=s,actors=lateWalkers(s)}
    end
    if jump.kind=='third-cap' and (x>=2448 or p.gap_hang) then
      if s.action==9 or s.mode==2 then p.gap_hang=p.gap_hang or s end
      if p.gap_hang and s.action==10 then
        pad=8
        if idle(s) and s.y<=112 then
          jump.landing=s
          p.jumps[#p.jumps+1]={kind='gap',request=s,tiles=finishGeometry(s)}
          switch('late-finish-jump',128)
        end
      else
        pad=p.gap_hang and 136 or 128
      end
      if age>170 then error('Original gap catch did not produce a second takeoff') end
      return
    end
    if jump.kind=='third-cap' then return end
    if age>=12 and support(s) and s.action~=4 and s.action~=3 then
      jump.landing=s
      switch('late-finish-run',1)
    elseif age>140 then
      error('Original late jump did not find authored footing')
    end
  elseif progress=='late-finish-run' then
    if lureWalkers and not p.second_group and p.walkers_below and x>=1905 and x<=1940 then
      local walkers=lateWalkers(s,6)
      if #walkers==2 and walkers[1].x>=1995 then
        p.second_group={turn=s,actors=walkers}
        p.advanced=commits
        switch('late-finish-retreat',2)
        return
      end
    end
    if not p.gap and x>=2400 and x+13<2448 and running(s) and s.phase&3<=1 then
      p.jumps[#p.jumps+1]={kind='gap',request=s,tiles=finishGeometry(s)}
      switch('late-finish-jump',129)
      return
    end
    if finishCombat and running(s) then
      local target=lateWalkers(s)[1]
      if target and target.x-x>=34 and target.x-x<=finishCombatGap and math.abs(target.y-s.y)<=32
          and (x<2320 or p.gap) then
        p.jumps[#p.jumps+1]={kind='walker',request=s,enemy=target}
        switch('late-finish-jump',129)
        return
      end
    end
    if support(s) and commits-p.advanced>=28 and solid(x+17,s.y+24) then
      local kind=x>=2110 and x<=2143 and 'stair'
        or x>=2330 and x<=2367 and 'third-stair' or 'wall'
      local pipe=x>=2575 and x<2608 and 2608 or x>=2830 and x<2864 and 2864 or nil
      p.climbs[#p.climbs+1]={wall=s,kind=kind,pipe_left=pipe,tiles=finishGeometry(s)}
      switch('late-finish-brake',0)
    end
  end
end
