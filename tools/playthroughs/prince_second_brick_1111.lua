-- Controller continuation from the standing jump off the first coin brick.
local goombaGap=tonumber(os.getenv('SMB_PRINCE_GOOMBA_GAP') or '0')
local climbForGroup=os.getenv('SMB_PRINCE_GOOMBA_CLIMB')=='1'
local climbBrake=tonumber(os.getenv('SMB_PRINCE_GOOMBA_BRAKE') or '1700')
local climbNudge=tonumber(os.getenv('SMB_PRINCE_GOOMBA_NUDGE') or '0')
local climbStep=os.getenv('SMB_PRINCE_GOOMBA_STEP')=='1'
local holdOnCap=os.getenv('SMB_PRINCE_SECOND_BRICK_HOLD')=='1'
local backtrackGroup=os.getenv('SMB_PRINCE_BACKTRACK_GROUP')=='1'
local backtrackBrake=tonumber(os.getenv('SMB_PRINCE_BACKTRACK_BRAKE') or '1652')
local backtrackStart=tonumber(os.getenv('SMB_PRINCE_BACKTRACK_START') or '1670')

observe(0xd6d1,2,function()
  if progress~='late-chain-hold-cap' then return end
  local q=late.chain
  q.support_entries=q.support_entries or {}
  if #q.support_entries>=12 then return end
  local cpu=emu.getState()
  q.support_entries[#q.support_entries+1]={state=state(),a=cpu['cpu.a'],x=cpu['cpu.x'],y=cpu['cpu.y'],
    sp=cpu['cpu.sp'],source_y=source(0x611),delta=source(0x88),
    base_column=source(0x7a),index=source(0x4b1),raw=source(0x78)+256*source(0x79),
    baseline=source(0x9b)+256*source(0x9c),old_foot=source(0x86)+256*source(0x87)}
end)

for _,at in ipairs({0xc60f,0xc078,0xc07f,0xc09f,0xc616}) do
  emu.addMemoryCallback(guarded(function(_,value)
    if progress~='late-chain-hold-cap' then return end
    local q=late.chain
    if #q.support_writes>=48 then return end
    local cpu=emu.getState()
    local pc=cpu['cpu.pc']
    local map=emu.convertAddress(pc)
    q.support_writes[#q.support_writes+1]={target=at,value=value,pc=pc,physical=map and map.address,
      commit=commits,action=source(0x616),mode=source(0x618),pose=source(0x617),
      x=read(0x75)+256*read(0x5c),y=read(0xbd),ground=read(0x1e),
      raw=source(0x78)+256*source(0x79),foot=source(0x84)+256*source(0x85),
      previous=source(0x86)+256*source(0x87),cell=source(0x7d)+256*source(0x7e)}
  end),emu.callbackType.write,at)
end

local function throughSecondBrick(s)
  local x=s.x
  local q=late.chain
  local stood=support(s) and idle(s)
  if progress=='late-chain-recovery' then
    if x>=1580 then
      q.brake=s
      switch('late-chain-park',0)
    elseif s.y==176 and stood then
      switch('late-chain-step',65)
    end
  elseif progress=='late-chain-park' and s.y==176 and stood then
    q.stance=s
    if x>=1577 then
      assert(x<=1600,'Standing reach is beside the second brick')
      switch('late-chain-climb',8)
    else
      switch('late-chain-step',65)
    end
  elseif progress=='late-chain-step' and s.action==42 then
    switch('late-chain-park',0)
  elseif progress=='late-chain-climb' then
    if s.mode==2 or s.mode==6 then q.ledge=q.ledge or s end
    if s.y<=114 and support(s) and x+13>=1600 then
      assert(tile(1600,144)==0x51 and tile(1616,144)==0x57,'Actual second brick pair')
      q.cap=s
      q.koopa=lateWalkers(s,0)[1]
      assert(q.koopa and q.koopa.direction==2,'Actual approaching green Koopa beneath the brick')
      if holdOnCap then
        q.support_writes={}
        switch('late-chain-hold-cap',0)
      else
        switch('late-chain-depart',128)
      end
    elseif commits-changedAt>128 then
      error('No supported climb onto the second brick pair')
    end
  elseif progress=='late-chain-hold-cap' then
    if s.action==7 or s.y>114 or x<q.cap.x then error('Neutral lost support after the second climb') end
    if commits-changedAt>=20 then
      local footTile=tile(x+13,144)
      assert(support(s) and (footTile==0x51 or footTile==0x57) and s.lives==2,
        'Neutral settles with both lives and a foot on the authored bricks')
      final=s
      finish(true,'Neutral retains the exposed brick pair support')
    end
  elseif progress=='late-chain-depart' and s.action==3 then
    q.depart=s
    switch('late-chain-far-side',1)
  elseif progress=='late-chain-far-side' then
    local actor=lateActor(q.koopa.slot)
    if not q.koopa_passed and actor.flag==1 and actor.id==0 and actor.x+22<x and s.y<145 then
      q.koopa_passed={state=s,actor=actor}
    end
    -- The running pose briefly publishes Player_State 2 while its foot is
    -- still over flat terrain. Begin braking there to hit the narrow stance.
    local canBrake=support(s) and s.y==176
    if (climbForGroup or backtrackGroup) and s.action==1 and s.mode==1 and s.y>=174 and s.y<=178 then
      canBrake=canBrake or tile(x+13,208)==0x54
    end
    local target=backtrackGroup and backtrackStart or (climbForGroup and climbBrake or 1705)
    if x>=target and canBrake then
      assert(q.koopa_passed and s.lives==2 and s.hp>0,'Native far bank with both lives after the Koopa')
      q.far_side=s
      if backtrackGroup then
        q.group={retreat=s}
        switch('late-chain-group-backtrack',2)
      elseif climbForGroup then
        q.group={brake=s}
        switch('late-chain-group-park',0)
      elseif goombaGap==0 then
        final=s
        finish(true,'Original two climbs and standing jumps pass the live Koopa')
      else
        q.group={samples={}}
        switch('late-chain-group-run',1)
      end
    end
  elseif progress=='late-chain-group-backtrack' then
    if not q.group.walkers then
      local walkers=lateWalkers(s,6)
      if #walkers==2 then q.group.walkers=walkers end
    end
    if x<=backtrackBrake and s.facing==0 then
      q.group.brake=s
      switch('late-chain-group-backtrack-park',0)
    end
  elseif progress=='late-chain-group-backtrack-park' and s.y==176 and stood then
    q.group.stance=s
    assert(x>=1600 and x<=1652 and s.facing==0 and q.group.walkers,
      'Left-facing stance beside the original brick pair')
    switch('late-chain-group-backtrack-climb',8)
  elseif progress=='late-chain-group-backtrack-climb' then
    if s.mode==2 or s.mode==6 then q.group.ledge=q.group.ledge or s end
    if s.y<=114 and support(s) and (solid(x+2,144) or solid(x+13,144)) then
      q.group.cap=s
      switch('late-chain-group-backtrack-wait',0)
    elseif commits-changedAt>140 then
      error('No supported climb on the far side of the brick pair')
    end
  elseif progress=='late-chain-group-backtrack-wait' then
    assert(s.y<=114 and support(s),'Original stance stays on the brick pair while the walkers pass')
    local trailing=lateActor(q.group.walkers[2].slot)
    if trailing.flag==0 or (trailing.id==6 and trailing.x+20<x) then
      q.group.below={state=s,actor=trailing}
      switch('late-chain-group-backtrack-depart',1)
    end
  elseif progress=='late-chain-group-backtrack-depart' and x>=1850 and s.y==176 and support(s) then
    q.group.landing=s
    final=s
    finish(true,'Original rear climb lets both Goombas pass below before Prince crosses')
  elseif progress=='late-chain-group-park' and s.y==176 and stood then
    q.group.stance=s
    q.group.stance_walkers=lateWalkers(s,6)
    if x<1724 and climbStep and not q.group.step then
      q.group.step=s
      switch('late-chain-group-step',65)
    elseif x<1724 and climbNudge>0 and not q.group.nudge then
      q.group.nudge=s
      switch('late-chain-group-nudge',1)
    else
      assert(x>=1714 and x<=1748 and tile(1744,144)==0xc0,'Standing reach beside the first question block')
      switch('late-chain-group-climb',8)
    end
  elseif progress=='late-chain-group-nudge' and commits-changedAt>=climbNudge then
    q.group.nudge_end=s
    switch('late-chain-group-park',0)
  elseif progress=='late-chain-group-step' and s.action==42 then
    q.group.step_end=s
    switch('late-chain-group-park',0)
  elseif progress=='late-chain-group-climb' then
    if s.mode==2 or s.mode==6 then q.group.ledge=q.group.ledge or s end
    local surface=s.y<=114 and (solid(x+2,144) or solid(x+13,144))
    if s.y<=174 then
      local trace=q.group.reach_trace or {}
      q.group.reach_trace=trace
      local previous=trace[#trace]
      if #trace<18 and (not previous or previous.action~=s.action or previous.pose~=s.pose) then
        trace[#trace+1]={action=s.action,pose=s.pose,mode=s.mode,x=x,y=s.y,
          ground=s.ground,commit=commits,surface=surface}
      end
    end
    if s.y<=114 and (support(s) or (surface and s.action==10)) and x+13>=1744 then
      q.group.cap=s
      q.group.walkers=q.group.stance_walkers
      assert(#q.group.walkers==2,'Both real Goombas on the approach to the question block')
      switch('late-chain-group-depart',128)
    elseif commits-changedAt>130 then
      error('No supported climb onto the first question block')
    end
  elseif progress=='late-chain-group-depart' and s.action==3 then
    q.group.depart=s
    switch('late-chain-group-over',1)
  elseif progress=='late-chain-group-over' then
    if not q.group.above and s.y<=144 then
      local nearest=lateActor(q.group.walkers[2].slot)
      if nearest.id==6 and nearest.flag==1 and x>nearest.x+16 then
        q.group.above={state=s,actor=nearest}
      end
    end
    if x>=1850 and s.y==176 and support(s) then
      assert(q.group.above and s.lives==2 and s.hp>0,'Passed the second live Goomba while above it')
      q.group.landing=s
      final=s
      finish(true,'Original question-block climb and standing jump pass the Goomba pair')
    end
  elseif progress=='late-chain-group-run' then
    local actors=lateWalkers(s,6)
    local first=actors[1]
    if first and #q.group.samples<20 then
      local last=q.group.samples[#q.group.samples]
      if not last or commits-last.state.commit>=4 then
        q.group.samples[#q.group.samples+1]={state=s,actors=actors}
      end
    end
    if first and first.x-x<=goombaGap and first.x-x>=40 and running(s) then
      q.group.request={state=s,actors=actors}
      q.group.tiles={}
      for col=x&~15,math.min((x&~15)+128,s.scroll+240),16 do
        local cells={}
        for y=112,208,16 do cells[#cells+1]=tile(col,y) end
        q.group.tiles[#q.group.tiles+1]={x=col,rows_112_to_208=cells}
      end
      switch('late-chain-group-jump',129)
    end
  elseif progress=='late-chain-group-jump' and s.action==4 then
    q.group.admitted=s
    switch('late-chain-group-flight',1)
  elseif progress=='late-chain-group-flight' then
    local heights=q.group.heights or {}
    q.group.heights=heights
    if #heights<16 and (not heights[#heights] or heights[#heights].pose~=s.pose) then heights[#heights+1]=s end
    if x>=1920 and s.y==176 and support(s) then
      q.group.landing=s
      final=s
      finish(true,'Original running jump passes the Goomba group after the Koopa')
    end
  end
end
