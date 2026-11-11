-- Controller continuation from the standing jump off the first coin brick.
local goombaGap=tonumber(os.getenv('SMB_PRINCE_GOOMBA_GAP') or '0')
local climbForGroup=os.getenv('SMB_PRINCE_GOOMBA_CLIMB')=='1'
local climbBrake=tonumber(os.getenv('SMB_PRINCE_GOOMBA_BRAKE') or '1700')

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
      switch('late-chain-depart',128)
    elseif commits-changedAt>128 then
      error('No supported climb onto the second brick pair')
    end
  elseif progress=='late-chain-depart' and s.action==3 then
    q.depart=s
    switch('late-chain-far-side',1)
  elseif progress=='late-chain-far-side' then
    local actor=lateActor(q.koopa.slot)
    if not q.koopa_passed and actor.flag==1 and actor.id==0 and actor.x+22<x and s.y<145 then
      q.koopa_passed={state=s,actor=actor}
    end
    if x>=(climbForGroup and climbBrake or 1705) and s.y==176 and support(s) then
      assert(q.koopa_passed and s.lives==2 and s.hp>0,'Native far bank with both lives after the Koopa')
      q.far_side=s
      if climbForGroup then
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
  elseif progress=='late-chain-group-park' and s.y==176 and stood then
    q.group.stance=s
    assert(x>=1714 and x<=1740 and tile(1744,144)==0xc0,'Standing reach beside the first question block')
    switch('late-chain-group-climb',8)
  elseif progress=='late-chain-group-climb' then
    if s.mode==2 or s.mode==6 then q.group.ledge=q.group.ledge or s end
    if s.y<=114 and support(s) and x+13>=1744 then
      q.group.cap=s
      q.group.walkers=lateWalkers(s,6)
      assert(#q.group.walkers==2,'Both real Goombas at the question block')
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
