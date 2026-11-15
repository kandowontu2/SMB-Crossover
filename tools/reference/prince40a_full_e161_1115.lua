-- Controller-only cold launch and original Prince first-pipe crossing.
local rom = os.getenv('SMB_STDOUT_ROM_SHA') or ''
local variant = tonumber(os.getenv('SMB_TEST_VARIANT') or '0')
assert(variant==3,'Full Prince route requires native variant3')
local cookie = 'a7260209e6eb04c8dbe70c3197b0cb4b'
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

local verifiedMainEntries,verifiedMainReturns,verifiedGrounded=0,0,0
local verifiedPendingMain,verifiedAnyStar=nil,false
local newPacketVerified=nil
local function finish(passed,reason)
  if passed then assert(newPacketVerified,'Actual tier2 packet consumer readback required');assert(read(0x75b)==2 and source(0x6ee)==1,'Earned sword persists into actual1-2')end
  if stopped then return end
  stopped=true
  print('SMB_NATIVE_RECEIPT '..encode({passed=passed,reason=reason,ROM_SHA256=rom,
    controller_only=true,output_files=0,physical_frames=frame,phase=progress,
    commits=commits,source_updates=sourceUpdates,source_draws=sourceDraws,new_candidate_readback=newPacketVerified,persistent_sword={native_PlayerStatus=read(0x75b),Sword=source(0x6ee)},Main_entries=verifiedMainEntries,Main_returns=verifiedMainReturns,Main_pending=verifiedPendingMain~=nil,grounded_1_2_completed_returns=verifiedGrounded,observed_natural_Star=verifiedAnyStar,
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
observe(0xd746,2,function()
  local s=state()
  if s.x>=895 and s.x<944 and #supportPublications<12 then
    assert(read(0xd746)==0x8d and read(0xd747)==0x7f and read(0xd748)==0xc0,'Original support publication site')
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
  assert(#events<180,'Bounded route phase summary')
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

-- Continuation of the cold four-pipe replay. Uses the same read-only state and input helpers.
local koopaBrake=tonumber(os.getenv('SMB_PRINCE_KOOPA_BRAKE') or '1540')
local koopaMode=os.getenv('SMB_PRINCE_KOOPA_MODE') or 'standing'
local koopaJumpX=tonumber(os.getenv('SMB_PRINCE_KOOPA_JUMP_X') or '1501')

for _,address in ipairs({0xc078,0xc07a,0xc07f,0xc4b1}) do
  emu.addMemoryCallback(guarded(function(_,value)
    local k=late.koopa
    if not k or not k.top or progress~='late-ledge-run' or commits>k.top.commit+6 then return end
    local q=k.query_writes or {}
    k.query_writes=q
    if #q>=80 then return end
    local cpu=emu.getState()
    local pc=cpu['cpu.pc']
    local memory=emu.convertAddress(pc)
    q[#q+1]={address=address,value=value,pc=pc,physical=memory and memory.address,
      commit=commits,frame=frame,x=read(0x75)+256*read(0x5c),action=source(0x616)}
  end),emu.callbackType.write,address)
end

for _,address in ipairs({0x75,0x5c,0xc60f,0xc610}) do
  emu.addMemoryCallback(guarded(function(_,value)
    if not late.koopa or (progress~='late-ledge-run' and progress~='late-ledge-step'
      and progress~='late-ledge-settle') then return end
    local writes=late.koopa.writes or {}
    late.koopa.writes=writes
    if #writes>=18 then return end
    local cpu=emu.getState()
    local pc=cpu['cpu.pc']
    local mapping=emu.convertAddress(pc)
    local write={target=address,value=value,pc=pc,mapping=mapping and mapping.address,
      memory=mapping and mapping.memType,source_x=source(0x60f)+256*source(0x610),state=state()}
    if pc==0xc42a then
      local sp=cpu['cpu.sp']
      write.caller=(1+read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255)))&65535
      write.raw_x=source(0x78)+256*source(0x79)
      write.cell_x=source(0x7d)+256*source(0x7e)
      write.surface=source(0x7f)+256*source(0x80)
      write.align_x=source(0xa1)
      write.index=source(0x4b1)
      write.material=source(0x9f)
    end
    writes[#writes+1]=write
  end),emu.callbackType.write,address)
end

local function lateActor(slot)
  return {slot=slot,flag=read(0x10+slot),id=read(0x17+slot),state=read(0x1f+slot),
    x=read(0x76+slot)+256*read(0x5d+slot),y=read(0xbe+slot),direction=read(0x53f+slot)}
end

local function lateWalkers(s,kind)
  local result={}
  for slot=0,5 do
    local a=lateActor(slot)
    if a.flag==1 and a.id<=6 and a.state&32==0 and a.y>=160 and a.x>=s.x-16
        and (kind==nil or a.id==kind) then
      result[#result+1]=a
    end
  end
  table.sort(result,function(a,b)return a.x<b.x end)
  return result
end

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

-- Continue on authored terrain after the verified question-block crossing.
local finishStop=tonumber(os.getenv('SMB_PRINCE_FINISH_STOP') or '0')
local finishCombat=os.getenv('SMB_PRINCE_FINISH_COMBAT')=='1'
local finishCombatGap=tonumber(os.getenv('SMB_PRINCE_FINISH_COMBAT_GAP') or '86')
local waitOnBrick=os.getenv('SMB_PRINCE_FINISH_BRICK_WAIT')=='1'
local lureWalkers=os.getenv('SMB_PRINCE_FINISH_LURE')=='1'
local ending

local verifiedHooks={["entry"]={["bytes"]={169,255,141,57,1,32,86,131},["offset"]=1032921,["pc"]=33497},["ram"]={["AreaType"]=1875,["CheatInvincible"]=32763,["CheatStartLevel"]=32764,["OperMode"]=1905,["OperMode_Task"]=1907,["StarInvincibleTimer"]=1948},["returns"]={{["bytes"]={104,205,58,1,240,238,32,196},["offset"]=1032894,["pc"]=33470},{["bytes"]={104,169,0,141,59,1,76,178},["offset"]=1032912,["pc"]=33488}}}
local function verifiedHook(h,fn)
  emu.addMemoryCallback(guarded(function()
    local a=emu.convertAddress(h.pc)
    if not a or a.memType~=emu.memType.nesPrgRom or a.address~=h.offset then return end
    for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Exact compiled Main witness')end
    fn()
  end),emu.callbackType.exec,h.pc)
end
verifiedHook(verifiedHooks.entry,function()
  assert(not verifiedPendingMain,'Previous complete Main returned')
  local sp=emu.getState()['cpu.sp']
  local pc=read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1
  assert(pc==verifiedHooks.returns[1].pc or pc==verifiedHooks.returns[2].pc,'Authenticated native Main caller')
  verifiedMainEntries=verifiedMainEntries+1;verifiedPendingMain={pc=pc,sp=(sp+2)&255}
end)
for _,h in ipairs(verifiedHooks.returns)do verifiedHook(h,function()
  assert(verifiedPendingMain and verifiedPendingMain.pc==h.pc and verifiedPendingMain.sp==emu.getState()['cpu.sp'],'Same Main caller/SP return')
  verifiedPendingMain=nil;verifiedMainReturns=verifiedMainReturns+1
  local s=state()
  if read(0x6002)==38 and s.engine==8 then
    assert(read(verifiedHooks.ram.CheatInvincible)==0 and read(verifiedHooks.ram.CheatStartLevel)==0,'Ordinary current no-cheat gameplay')
    verifiedAnyStar=verifiedAnyStar or read(verifiedHooks.ram.StarInvincibleTimer)>0
  end

  late.body_transition=late.body_transition or {samples={}}
  local transition=late.body_transition
  local now={active=source(0x6e0),uid=source(0x61c),sword=source(0x6ee),marker=source(0x6de),facing=source(0x615),guard_facing=source(0x623),x=s.x,y=s.y,Main=verifiedMainReturns,commit=commits}
  local previous=transition.previous
  if not transition.loss and previous and previous.active==1 and previous.sword==2 and previous.facing~=previous.guard_facing and now.active==0 and now.marker==1 then
    transition.loss={before=previous,after=now}
  end
  if transition.loss and not transition.sheath and now.sword==1 then transition.sheath=now end
  if transition.sheath and not transition.movement and math.abs(now.x-transition.sheath.x)>=8 then transition.movement=now end
  if not transition.readmitted and transition.movement and now.active==1 and now.sword==2 and now.marker==0 and s.x>=1800 and s.y==176 and s.hp>0 then
    assert(late.fourth_practical_cap and s.lives==2,'Four actual caps and living opposed-loss re-admission')
    transition.readmitted=now
  end
  transition.previous=now
  if ending and s.world==0 and s.level==1 and s.engine==8 and read(verifiedHooks.ram.OperMode)==1 and read(verifiedHooks.ram.OperMode_Task)==3 then
    pad=0
    assert(ending.flag and ending.castle and ending.gap and s.lives==2,'Full authored native exit chain')
    if read(verifiedHooks.ram.AreaType)==2 and s.y_high==1 and math.abs(s.y-176)<=1 and s.ground==0 and s.hp>0 and source(0xab)==0xa7 and hexHeader(2)==cookie and hexHeader(3)==cookie then
      verifiedGrounded=verifiedGrounded+1
    else verifiedGrounded=0 end
    ending.completed_grounded_1_2=verifiedGrounded
    if verifiedGrounded>=25 then
      final=s;finish(true,'Prince earned-sword full1-1 and25 living grounded completed Main returns in1-2')
    end
  end
end)end

-- A low flag catch can reach engine state 5 before the next original update.
emu.addMemoryCallback(guarded(function(_,value)
  if not ending or value~=4 or read(0x761)~=0 then return end
  local s=state()
  local contact=read(0x07)
  if s.x>=3158 and s.x<=3171 and contact>=6 and contact<=9 then
    s.native_flag_write=value
    s.flag_contact=contact
    ending.flag=ending.flag or s
  end
end),emu.callbackType.write,0x0f)


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
  if s.world==0 and s.level==1 and s.engine==8 and read(0x773)==3 and read(0x753)==2 and floor(s) and idle(s) then
    assert(ending.flag and ending.castle and ending.gap and s.lives==2,
      'Native flagpole, castle, third gap and active underground 1-2')
    pad=0
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


local function latePipeControlSample(s)
 if s.x<2570 or s.x>2660 then return end
 if not late.late_pipe_geometry then
  local cells={}
  for x=2544,2672,16 do for y=128,208,16 do
   local at=0x300+((x//256)&1)*208+(y&240)-32+((x&255)//16)
   local value=tile(x,y);assert(value==read(at),'Actual native BlockBuffer tile')
   cells[#cells+1]={x=x,y=y,address=at,value=value,attribute=read(0xef36+value)}
  end end
  late.late_pipe_geometry={at=s,source='Actual native BlockBuffer and MTileAttribute, read only',cells=cells}
 end
 local rows=late.late_pipe_control or {};late.late_pipe_control=rows
 local key=progress..':'..s.x..':'..s.y..':'..s.action..':'..s.pose..':'..s.mode
 if late.late_pipe_key==key then return end
 late.late_pipe_key=key
 local box={read(0x658)+s.scroll,read(0x659),read(0x65a)+s.scroll,read(0x65b)}
 rows[#rows+1]={phase=progress,state=s,source_x=source(0x60f)+256*source(0x610),
  source_pad=source(0x40a),requested_pad=pad,body_world_at_control_sample=box,
  fresh_outcomes=#(late.fresh_step_outcomes or {})}
 if #rows>64 then table.remove(rows,17)end
end

local function endingTick(s)
  latePipeControlSample(s)
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
        attempt.step_outcome_start=#(late.fresh_step_outcomes or {})
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
    local attempt=p.climbs[#p.climbs]
    if #(late.fresh_step_outcomes or {})>(attempt.step_outcome_start or 0) then switch('late-finish-brake',0)
    elseif age>75 then error('Original careful pipe step did not start') end
  elseif progress=='late-finish-step-settle' and support(s) and idle(s) then
    local originalCap=p.climbs[1].cap
    if originalCap and x>originalCap.x-9 then
      switch('late-finish-step-left',66)
      return
    end
    p.climbs[#p.climbs].left_stance=s
    switch('late-finish-turn-right',1)
  elseif progress=='late-finish-turn-right' and s.facing==255 then
    p.climbs[#p.climbs].kind='retreat-right'
    p.advanced=commits
    switch('late-finish-brake',0)
  elseif progress=='late-finish-climb' then
    local attempt=p.climbs[#p.climbs]
    if s.mode==2 or s.mode==6 or s.action==10 then
      if not attempt.hang then attempt.hang=s;p.advanced=commits end
    end
    local takeoffY=attempt.pipe_left and 147
      or (attempt.kind=='stair' or attempt.kind=='third-stair') and 104
      or attempt.kind=='final-stair' and attempt.stance.y-20
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
          switch('late-finish-brick-runup',1)
        end
      elseif attempt.kind=='retreat-right' then
        p.advanced=commits
        switch('late-finish-second-wait',0)
      else
        switch('late-finish-run',1)
      end
    elseif age>165 and(not attempt.hang or commits-attempt.hang.commit>165)then
      p.obstruction={state=s,tiles=finishGeometry(s),actors=lateWalkers(s),attempt=attempt}
      error('Original Up did not reach support over the late wall')
    elseif attempt.pipe_left and age>=64 and not attempt.hang then
      pad=8
    end
  elseif progress=='late-finish-brick-runup' then
    if running(s) and support(s) then
      p.jumps[#p.jumps+1]={kind='brick-running',request=s,actors=lateWalkers(s),tiles=finishGeometry(s)}
      switch('late-finish-jump',129)
    elseif age>64 then
      p.obstruction={state=s,tiles=finishGeometry(s),actors=lateWalkers(s)}
      error('Original brick running approach did not admit running')
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
  elseif progress=='late-finish-flag-brake' then
    if s.y_high==1 and s.y>=174 and s.y<=178 and idle(s) and s.action==0 then
      p.jumps[#p.jumps+1]={kind='flag',request=s}
      switch('late-finish-jump',128)
    elseif age>115 then
      error('Original flag approach did not settle before a fresh standing jump')
    end
  elseif progress=='late-finish-run' then
    if not p.flag_brake and x>=3115 and s.y>=174 and s.y<=178 and s.action==1 then
      p.flag_brake=s
      switch('late-finish-flag-brake',0)
      return
    end
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
        or x>=2330 and x<=2367 and 'third-stair'
        or x>=2928 and x<3008 and 'final-stair' or 'wall'
      local pipe=x>=2575 and x<2608 and 2608 or x>=2830 and x<2864 and 2864 or nil
      p.climbs[#p.climbs+1]={wall=s,kind=kind,pipe_left=pipe,tiles=finishGeometry(s)}
      switch('late-finish-brake',0)
    end
  end
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
    if s.action==10 then pad=0 end
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
    if s.y==112 and support(s) and s.mode==0 and s.pose==15 and tile(x+13,144)==0xc0 then
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
      startEnding(s)
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

local function afterSecondGap(s)
  if progress:sub(1,11)=='late-chain-' then throughSecondBrick(s);return end
  local onFloor=support(s)
  local stood=onFloor and idle(s)
  local x=s.x
  if progress=='late-second-approach' and x>=1320 then
    switch('late-second-brake',0)
  elseif progress=='late-second-brake' and stood then
    switch('late-second-left',2)
  elseif progress=='late-second-left' and x<=1312 and s.facing==0 then
    switch('late-second-park',0)
  elseif progress=='late-second-park' and stood then
    switch('late-second-run',1)
  elseif progress=='late-second-run' then
    assert(x<1361,'Original second-gap running jump has a supported takeoff')
    if x>=1328 and x<=1356 and s.phase&3<=1 and running(s) then
      assert(tile(1360,208)==0x54 and tile(1376,208)==0 and tile(1392,208)==0
        and tile(1408,208)==0 and tile(1424,208)==0x54,'Actual three-column second gap')
      late.second_request=s
      switch('late-second-jump',129)
    end
  elseif progress=='late-second-jump' and s.action==4 then
    late.second_admission=s
    switch('late-second-flight',1)
  elseif progress=='late-second-flight' and x>=1440 and s.y==176 and onFloor then
    late.second_gap=s
    local pair=lateWalkers(s,6)
    assert(#pair==2 and pair[1].direction==2 and pair[2].direction==2,'Actual leftward Goomba pair')
    late.reverse={pair=pair,falls={}}
    switch('late-brake',0)
  elseif progress=='late-brake' and stood then
    switch('late-face-left',2)
  elseif progress=='late-face-left' and s.facing==0 then
    switch('late-settle-left',0)
  elseif progress=='late-settle-left' and stood then
    assert(s.facing==0 and x+2>=1424,'Supported original left-facing standing jump')
    late.reverse.request=s
    switch('late-reverse-jump',128)
  elseif progress=='late-reverse-jump' and s.action==3 then
    late.reverse.admission=s
    switch('late-reverse-flight',2)
  elseif progress=='late-reverse-flight' and x+2<1376 and s.y==176 and onFloor then
    late.reverse.landing=s
    switch('late-wait-walkers',0)
  elseif progress=='late-wait-walkers' then
    local cleared=0
    for _,a in ipairs(late.reverse.pair) do
      local now=lateActor(a.slot)
      local key=tostring(a.slot)
      if now.flag==1 and now.id==6 and now.x>=1376 and now.x<1424 and now.y>=204 then
        late.reverse.falls[key]=late.reverse.falls[key] or now
      elseif now.flag==0 and late.reverse.falls[key] then
        cleared=cleared+1
      end
    end
    if cleared==2 and stood then switch('late-return-backup',2) end
  elseif progress=='late-return-backup' and x<=s.scroll+4 then
    switch('late-return-settle',0)
  elseif progress=='late-return-settle' and stood then
    assert(s.facing==0 and x+13<1376,'Backed away from the actual lip')
    switch('late-return-face',1)
  elseif progress=='late-return-face' and s.facing==255 then
    switch('late-return-park',0)
  elseif progress=='late-return-park' and stood then
    assert(x+13<1376 and tile(x+13,208)==0x54,'Original return takeoff stays on the near bank')
    late.reverse.return_request=s
    switch('late-forward-jump',128)
  elseif progress=='late-forward-jump' and (s.action==3 or s.action==4) then
    late.reverse.return_admission=s
    switch('late-forward-flight',1)
  elseif progress=='late-forward-flight' and x>=1440 and s.y==176 and onFloor then
    late.reverse.return_landing=s
    switch('late-koopa-approach',1)
  elseif progress=='late-koopa-approach' and x>=koopaBrake then
    assert(x<=1559,'Brake before the first green Koopa')
    late.koopa={brake=s,minimum_y=s.y}
    switch('late-koopa-settle',0)
  elseif progress=='late-koopa-settle' and stood then
    local koopa=lateWalkers(s,0)[1]
    assert(x<1600 and s.facing==255,'Supported standing A before the Koopa')
    late.koopa.request={state=s,actor=koopa}
    if koopaMode~='standing' then
      late.koopa.tiles={}
      for col=1488,1648,16 do
        local cells={}
        for y=112,176,16 do cells[#cells+1]=tile(col,y) end
        late.koopa.tiles[#late.koopa.tiles+1]={x=col,rows_112_to_176=cells}
      end
      switch('late-koopa-climb',8)
    else
      switch('late-koopa-jump',128)
    end
  elseif progress=='late-koopa-climb' then
    if s.mode==2 or s.mode==6 then late.koopa.ledge=late.koopa.ledge or s end
    if s.y<=114 and onFloor and solid(x+13,144) then
      late.koopa.top=s
      if koopaMode=='climb' then
        final=s
        finish(true,'Original climb reaches the authored brick above the Koopa route')
      elseif koopaMode=='step' then
        switch('late-ledge-step',65)
      elseif koopaMode=='air' or koopaMode=='air-right' then
        late.koopa.ledge_request=s
        switch('late-ledge-jump',koopaMode=='air' and 128 or 129)
      else
        switch('late-ledge-run',1)
      end
    elseif commits-changedAt>=120 then
      error('Original Up does not reach the authored brick from this stance')
    end
  elseif progress=='late-ledge-step' and s.action==42 then
    late.koopa.step=s
    switch('late-ledge-settle',0)
  elseif progress=='late-ledge-settle' then
    if s.y>116 then error('Original careful step did not retain the single brick')end
    if stood and solid(x+2,144) then
      late.koopa.ledge_stance=s
      switch('late-ledge-run',1)
    end
  elseif progress=='late-ledge-run' then
    local samples=late.koopa.run or {}
    late.koopa.run=samples
    if #samples<12 and (not samples[#samples] or x~=samples[#samples].x) then
      samples[#samples+1]=s
    end
    if x>=koopaJumpX and s.y<=114 and running(s) then
      late.koopa.ledge_request=s
      switch('late-ledge-jump',129)
    elseif x>=1521 or s.y>116 then
      error('Lost native brick support before original jump admission')
    end
  elseif progress=='late-ledge-jump' then
    if s.action==4 or s.action==3 then
      late.koopa.ledge_admission=s
      if koopaMode=='runway' then
        assert(s.action==4 and s.x==1513 and s.y==112 and s.hp==4 and s.lives==2
          and support(s),'Real running jump admission from the coin brick')
        final=s
        finish(true,'Original walk and running jump admission on the supported coin brick')
      else
        switch('late-ledge-flight',1)
      end
    elseif s.y>119 or commits-changedAt>24 then
      error('Lost the authored brick before original A admission')
    end
  elseif progress=='late-ledge-flight' then
    local airborne=late.koopa.airborne or {}
    late.koopa.airborne=airborne
    if #airborne<18 and (not airborne[#airborne] or s.pose~=airborne[#airborne].pose) then
      airborne[#airborne+1]=s
    end
    if x+13>=1600 and s.y<=114 and onFloor then
      late.koopa.ledge_landing=s
      final=s
      finish(true,'Original running jump lands on the next authored brick above the Koopa')
    elseif s.y>144 or x>1648 then
      late.chain={entry=s}
      switch('late-chain-recovery',1)
    end
  elseif progress=='late-koopa-jump' and s.action==3 then
    late.koopa.admission=s
    switch('late-koopa-flight',1)
  elseif progress=='late-koopa-flight' then
    late.koopa.minimum_y=math.min(late.koopa.minimum_y,s.y)
    late.koopa.actor=late.koopa.actor or lateWalkers(s,0)[1]
    if x>=1705 and onFloor and s.action~=3 then
      local seen=late.koopa.request.actor or late.koopa.actor
      assert(seen,'Observed the authored green Koopa')
      local actor=lateActor(seen.slot)
      assert((actor.flag==0 or actor.id~=0 or actor.state&32~=0 or actor.x+12<x+2)
        and late.koopa.minimum_y<176,'Native support beyond the Koopa and actual airborne interval')
      late.koopa.clear=s
      switch('late-enemy-probe',1)
    end
  elseif progress=='late-enemy-probe' then
    local samples=late.enemies or {}
    late.enemies=samples
    local walkers=lateWalkers(s)
    if #walkers>0 and #samples<20 and (not samples[#samples] or commits-samples[#samples].state.commit>=4) then
      samples[#samples+1]={state=s,actors=walkers}
    end
    if x>=1760 and #walkers>0 then
      final=s
      finish(true,'Natural supported ground after the first Koopa; captured the next native group')
    end
  end
end

local function fourthAndGap(s)
  if progress=='third-partial-wait' then
    local left,right=capFeet(s,736,144)
    assert((left or right) and idle(s),'Real third-cap support throughout safe phase wait')
    local walkers=thirdWalkers()
    if #walkers==2 and walkers[1].direction==2 and walkers[2].direction==2 and walkers[1].x<=848 and walkers[2].x<=848 then
      switch('third-running-approach',1,walkers)
    end
  elseif progress=='third-running-approach' then
    if s.x>=744 and s.action==1 and s.mode==1 and s.pose>=6 and s.pose<=13 and s.lock==0 then
      late.third_running_request=s;switch('third-running-takeoff',129)
    end
  elseif progress=='third-running-takeoff' and s.action==4 then
    late.third_running_admission=s;switch('third-running-flight',1)
  elseif progress=='third-running-flight' then
    if s.x>=897 and s.pose==15 and s.mode==0 and s.lock==0 then
      late.fourth_practical_stand=s;switch('fourth-practical-up',8)
    elseif s.mode==2 or s.mode==6 then
      switch('fourth-practical-up',8)
    end
  elseif progress=='fourth-practical-up' then
    local left,right=capFeet(s,912,144)
    if left or right then
      late.fourth_practical_cap=s;late.fourth_partial=s
      switch('fourth-anchor-step',65)
    end
  elseif progress=='third-park' and s.action~=0 and s.action~=1 and s.action~=10 then
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
      switch('flower-approach',1)
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
          switch('third-partial-wait',0)
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
      pad=8
    end
  elseif progress=='later-cross' and s.x>=obstacle.right+16 and onFloor then
    laterPipe=laterPipe+1
    switch('later-approach',1)
  end
end

local function routeTick()
  if endingFrame() then return end
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
  if ending then endingTick(s);return end
  local enemy=enemyNear(s.x)
  firstEnemy=firstEnemy or enemy
  if firstPipe then
    if progress:sub(1,5)=='late-' then
      afterSecondGap(s)
    elseif #caps==2 then fourthAndGap(s) else laterTick(s) end
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
      pad=8  -- Ordinary original Up throughout the pipe approach.
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



local collected=false
local flowerSeen=false
local flowerTrace={}
local itemSeen=false
late.hpWrites={}
emu.addMemoryCallback(guarded(function(address,value)
  if read(0x6002)==38 and read(0x0f)==8 and value<source(0x6cf) and #late.hpWrites<12 then
    local cpu=emu.getState()
    local sp=cpu['cpu.sp']
    local stack={}
    for i=1,12 do stack[i]=read(0x100+((sp+i)&255)) end
    late.hpWrites[#late.hpWrites+1]={pc=cpu['cpu.pc'],value=value,old=source(0x6cf),state=state(),stack=stack,fall=source(0x6c6)}
  end
end),emu.callbackType.write,0xc6cf)

local itemTrace={}
local matureSeen=false
local minimumY=255
local jumpTrace={}
local yWrites={}
local supportTrace={}
local headTrace={}
local headCalls=0
local headReturns={}
local headHits={}
local returnedHeads=0
local headLayouts={}
local pendingHead=nil
emu.addMemoryCallback(guarded(function()
  if read(0x6002)==38 and progress:sub(1,7)=='pickup-' then
    local s=state()
    if s.x>=230 and s.x<=400 then
      headCalls=headCalls+1
      local cpu=emu.getState()
      local sp=cpu['cpu.sp']
      local index=read(0x106)
      local layout=string.format('%d/%d/%d',read(0x759),index,read(0xe194+index))
      headLayouts[layout]=(headLayouts[layout] or 0)+1
      local ret=read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1
      pendingHead={x=s.x,y=s.y,dy=read(0x8e),action=s.action,pose=s.pose,phase=progress}
      if not headReturns[ret] then
        headReturns[ret]=true
        emu.addMemoryCallback(guarded(function()
          if pendingHead and read(0x6002)==38 then
            local row=pendingHead
            pendingHead=nil
            returnedHeads=returnedHeads+1
            row.tile=emu.getState()['cpu.a']
            row.lowY=read(7)
            if row.tile~=0 and #headHits<30 then headHits[#headHits+1]=row end
          end
        end),emu.callbackType.exec,ret)
      end
      local last=headTrace[#headTrace]
      local dy=read(0x8e)
      if #headTrace<100 and (not last or last.y~=s.y or last.dy~=dy or last.action~=s.action) then
        headTrace[#headTrace+1]={x=s.x,y=s.y,dy=dy,action=s.action,pose=s.pose,phase=progress}
      end
    end
  end
end),emu.callbackType.exec,0xf113)
for _,pc in ipairs({0xd6d1,0xd6da,0xd6fb,0xd6fe,0xd720,0xd739,0xd752}) do
  observe(pc,2,function()
    local age=commits-changedAt
    if progress=='pickup-jump' and age>=120 and age<=140 and #supportTrace<80 then
      local cpu=emu.getState()
      supportTrace[#supportTrace+1]={pc=pc,a=cpu['cpu.a'],p=cpu['cpu.ps'],
        age=age,state=state(),oldFoot=source(0x86),delta=source(0x88),
        queryX=source(0x1369,3)+256*source(0x136a,3),queryY=source(0x136b,3)}
    end
  end)
end
emu.addMemoryCallback(guarded(function(address,value)
  if progress=='pickup-jump' and mapped(0xc611,2) and #yWrites<160 then
    local cpu=emu.getState()
    yWrites[#yWrites+1]={pc=cpu['cpu.pc'],value=value,old=source(0x611),
      phase=source(0xa6),pose=source(0x617),action=source(0x616)}
  end
end),emu.callbackType.write,0xc611)

local startEarnedStage,earnedStageTick,earnedStage
local combat,combatLast,combatPhase,combatJump,combatParried=nil,-1,'settle',false,false
local function combatState()
  local s=state()
  s.sword=source(0x6ee);s.star=read(1948)
  s.source_x=source(0x60f)+256*source(0x610)
  s.cached_x=source(0x4db)+256*source(0x4dc)
  s.guard_uid=source(0x61c);s.guard_hp=source(0x6d0);s.guard_dead=source(0x6de)
  return s
end
local function combatEvent(name)
  local cpu=emu.getState()
  local e={name=name,commit=commits,state=combatState(),x=cpu['cpu.x'],y=cpu['cpu.y'],pc=cpu['cpu.pc'],sp=cpu['cpu.sp']}
  e.stack={};for i=1,12 do e.stack[i]=read(0x100+((e.sp+i)&255)) end
  combat.events[#combat.events+1]=e
  assert(#combat.events<40,'Bounded causal combat trace')
  return e
end
observe(41794,3,function()
  if not combat then return end
  local cpu=emu.getState()
  if cpu['cpu.x']==1 and cpu['cpu.a']==0 and source(0x6d0)==1 then
    local e=combatEvent('original-8725-guard-loss')
    assert(e.state.action==58 and e.state.star==0,'Original attack guard damage')
    combat.loss=e
  end
end)
observe(56985,2,function()
  if not combat or source(0x6d0)~=0 or source(0x6de)~=85 then return end
  combat.proxy=combatEvent('source-proxy-export')
end)
observe(55835,2,function()
  if not combat or source(0x6d0)~=0 or emu.getState()['cpu.y']~=1 then return end
  combat.call=combatEvent('source-native-kind1')
end)
emu.addMemoryCallback(guarded(function()
  if not combat then return end
  local mapped=emu.convertAddress(0x9af8)
  if not mapped or mapped.memType~=emu.memType.nesPrgRom or mapped.address~=126*8192+0x1af8 then return end
  local e=combatEvent('native-9AF8')
  local slot=e.x
  assert(combat.loss and combat.proxy and combat.call,'Original guard/export/call causal chain')
  assert(combat.proxy.commit==commits and combat.call.commit==commits,'Same Main deferred delivery')
  assert(e.state.action==58 and e.state.guard_hp==0 and e.state.guard_dead==85 and e.state.star==0,'Source-earned guard death')
  assert(e.state.guard_uid==(128|slot) and combat.loss.state.guard_uid==e.state.guard_uid,'Retained native guard UID')
  assert(read(0x10+slot)==1 and read(0x17+slot)<7 and read(0x1f+slot)&32==0,'Live native sword target')
  combat.kill=e
end),emu.callbackType.exec,0x9af8)
local function combatTick()
  if combatLast==commits then return end
  combatLast=commits
  local s=combatState()
  assert(s.lives==2 and s.hp==combat.initial.hp and s.star==0,'Earned sword combat health/lives, no Star')
  assert(hexHeader(2)==cookie and hexHeader(3)==cookie,'Private cache runtime authentication')
  assert(commits-combat.start<700,'Bounded earned sword combat')
  combat.actions[tostring(s.action)]=true
  if combat.kill then
    local slot=combat.kill.x
    if not combat.post then
      combat.post={state=s,flag=read(0x10+slot),enemy_state=read(0x1f+slot),score=read(269+slot)}
      assert(combat.post.flag==0 or combat.post.enemy_state&32~=0,'Actual native defeat state after Main')
      assert(combat.post.score==1,'Native Goomba defeat score')
    end
    pad=0
    if commits>=combat.kill.commit+12 then
      assert(combatParried and combat.actions['62'] and combat.actions['58'],'Parry then attack')
      combat.parried=true;combat.terminal=s;late.swordCombat=combat
      startEarnedStage(s);combat=nil
    end
    return
  end
  local target
  for slot=0,5 do
    local flag,id,enemyState=read(0x10+slot),read(0x17+slot),read(0x1f+slot)
    local x,y=read(0x76+slot)+256*read(0x5d+slot),read(0xbe+slot)
    if flag>0 and flag<128 and id<21 and enemyState&32==0 and math.abs(y-s.y)<48
      and (not target or math.abs(x-s.x)<math.abs(target.x-s.x))then target={slot=slot,x=x,y=y}end
  end
  pad=0
  if s.sword==2 then
    combatPhase='combat'
    if s.pose==171 and not combatParried then pad=64
    elseif s.action==62 then combatParried=true
    elseif combatParried and target then
      local direction=target.x>=s.x and 1 or 2
      local gap=math.abs(target.x-s.x)
      pad=gap>=(direction==1 and 38 or 32) and direction or 128
    end
  elseif s.action~=91 and s.mode==0 then combatPhase='approach';pad=1
  elseif combatPhase=='approach'then pad=1 end
  if combatPhase=='approach' and s.x>=1352 and s.x<1376 and not combatJump then pad=129;combatJump=true end
  if combatJump and s.x<1440 and combatPhase=='approach'then pad=s.action~=4 and 129 or 1 end
end
local function startSwordCombat()
  assert(source(1217,3)==76,'Cache runtime A4C1')
  assert(source(1218,3)==205,'Cache runtime A4C2')
  assert(source(1219,3)==164,'Cache runtime A4C3')
  assert(source(1220,3)==173,'Cache runtime A4C4')
  assert(source(1221,3)==15,'Cache runtime A4C5')
  assert(source(1222,3)==198,'Cache runtime A4C6')
  assert(source(1223,3)==141,'Cache runtime A4C7')
  assert(source(1224,3)==219,'Cache runtime A4C8')
  assert(source(1225,3)==196,'Cache runtime A4C9')
  assert(source(1226,3)==76,'Cache runtime A4CA')
  assert(source(1227,3)==112,'Cache runtime A4CB')
  assert(source(1228,3)==169,'Cache runtime A4CC')
  assert(source(2416,3)==173,'Cache runtime A970')
  assert(source(2417,3)==16,'Cache runtime A971')
  assert(source(2418,3)==198,'Cache runtime A972')
  assert(source(2419,3)==141,'Cache runtime A973')
  assert(source(2420,3)==220,'Cache runtime A974')
  assert(source(2421,3)==196,'Cache runtime A975')
  assert(source(2422,3)==76,'Cache runtime A976')
  assert(source(2423,3)==63,'Cache runtime A977')
  assert(source(2424,3)==172,'Cache runtime A978')
  assert(source(5014,3)==32,'Cache runtime B396')
  assert(source(5015,3)==196,'Cache runtime B397')
  assert(source(5016,3)==164,'Cache runtime B398')
  combat={start=commits,initial=combatState(),events={},actions={}}
  assert(combat.initial.sword==1,'Actual authored flower inventory before combat')
  progress='earned-sword-combat';pad=0
  combatTick()
end


startEarnedStage=function(s)
  final=nil
  earnedStage={start=s,marks={},kills={},last=commits,front=s.x,advanced=commits}
  late.earnedStage=earnedStage
  switch('earned-stage-approach',0)
end
emu.addMemoryCallback(guarded(function()
  if not earnedStage then return end
  local map=emu.convertAddress(0x9af8)
  if not map or map.memType~=emu.memType.nesPrgRom or map.address~=126*8192+0x1af8 then return end
  local cpu=emu.getState();local slot=cpu['cpu.x']
  assert(source(0x6d0)==0 and source(0x6de)==85 and source(0x61c)==(128|slot),'Retained source guard earned native defeat')
  assert(read(0x10+slot)==1 and read(0x17+slot)<7 and read(0x1f+slot)&32==0,'Real live native target')
  earnedStage.kills[#earnedStage.kills+1]={state=combatState(),slot=slot,id=read(0x17+slot)}
  assert(#earnedStage.kills<24,'Bounded full-stage combat summary')
end),emu.callbackType.exec,0x9af8)
earnedStageTick=function()
  if ending and endingFrame()then return end
  if earnedStage.last==commits then return end
  earnedStage.last=commits
  local s=combatState()
  assert(s.lives==2 and s.hp>0,'Actual earned-sword stage survival')
  assert(hexHeader(2)==cookie and hexHeader(3)==cookie,'Full-stage Prince auth')
  if s.x>earnedStage.front then earnedStage.front=s.x;earnedStage.advanced=commits end
  if #earnedStage.marks==0 or s.x>=earnedStage.marks[#earnedStage.marks].state.x+96 then
    earnedStage.marks[#earnedStage.marks+1]={state=s,actors=lateWalkers(s)}
  end
  if 0>0 and s.x>=0 and floor(s) then
    final=s;finish(true,'Earned full-stage source checkpoint');return
  end
  if earnedStage.sword_pause and source(0x6ee)==1 and source(0x6de)==85 and s.action==58 then
    -- The real original attack just defeated the imported guard. Keep the
    -- ordinary attack button through a possible nearby replacement actor;
    -- do not insert the old neutral release before its automatic draw.
    pad=128;changedAt=commits
    return
  end
  if source(0x6ee)==2 then
    if not earnedStage.sword_pause then earnedStage.sword_pause={start=commits,pad=pad,state=s} end
    local episode=earnedStage.sword_pause
    if episode.uid~=s.guard_uid then episode.uid=s.guard_uid;episode.start=commits;episode.parried=false end
    assert(commits-episode.start<700,'Bounded actual original parry/approach/attack encounter')
    local target
    for slot=0,5 do
      local flag,id,enemyState=read(0x10+slot),read(0x17+slot),read(0x1f+slot)
      local x,y=read(0x76+slot)+256*read(0x5d+slot),read(0xbe+slot)
      if flag>0 and flag<128 and id<21 and enemyState&32==0 and math.abs(y-s.y)<48
        and(s.x<1800 or slot==(s.guard_uid&127))
        and(not target or math.abs(x-s.x)<math.abs(target.x-s.x))then target={slot=slot,x=x,y=y}end
    end
    pad=0
    if s.x>=1800 and not episode.parried then
      if s.action==62 then episode.parried=true else pad=64 end
    elseif s.pose==171 and not episode.parried then pad=64
    elseif s.action==62 then episode.parried=true
    elseif episode.parried and target then
      local direction=target.x>=s.x and 1 or 2
      local gap=math.abs(target.x-s.x)
      pad=gap>=(direction==1 and 38 or 32)and direction or 128
    end
    changedAt=commits
    if ending then ending.advanced=commits end
    return
  end
  if earnedStage.sword_pause then
    if not earnedStage.sword_pause.released then earnedStage.sword_pause.released=commits+8 end
    if commits<earnedStage.sword_pause.released then pad=0;changedAt=commits;return end
    pad=earnedStage.sword_pause.pad
    earnedStage.sword_pause=nil
  end
  assert(commits-earnedStage.advanced<450,'Bounded earned-sword stage progress')
  if ending then
    if false and progress=='late-finish-run' and not earnedStage.early_wall then
      local wall=s.x>=1685 and s.x<1744 and 1744 or s.x>=1835 and s.x<1888 and 1888
      if wall then
        earnedStage.early_wall=wall
        ending.climbs[#ending.climbs+1]={wall=s,kind='walker-brick',tiles=finishGeometry(s)}
        switch('late-finish-brake',0)
        return
      end
    end
    if earnedStage.early_wall and s.x>earnedStage.early_wall+48 then earnedStage.early_wall=nil end
    if progress=='late-finish-climb' and support(s) and idle(s) and s.y<=114 then
      local walkers=lateWalkers(s,6)
      local trailing=walkers[#walkers]
      if #walkers==2 and trailing.x+24>=s.x and trailing.x-s.x<200 then
        pad=0;changedAt=commits;ending.advanced=commits
        return
      end
    end
    endingTick(s)
    return
  end
  pad=1
  if s.x>=1580 and s.y>=174 and s.y<=178 and (support(s) or tile(s.x+13,208)==0x54) then
    startEnding(s)
  end
end

local function tick()
  if earnedStage then earnedStageTick();return end
  if combat then combatTick();return end
  if collected then
    if progress:sub(1,7)~='flower-' then routeTick();return end
    if commits==lastCommit then return end
    lastCommit=commits
    local s=state()
    local age=commits-changedAt
    assert(s.lives==2 and s.hp>0,'Alive reaching flower')
    if read(0x15)~=0 and read(0x1c)==0x2e and read(0x39)==1 then flowerSeen=true end
    if #flowerTrace<80 and commits%5==0 then flowerTrace[#flowerTrace+1]={state=s,itemFlag=read(0x15),kind=read(0x39),itemState=read(0x24),sword=source(0x6ee)} end
    if late.flower and late.flower.left then
      late.swordTrace=late.swordTrace or {}
      if commits%8==0 then
        local t=late.swordTrace
        if #t==16 then table.remove(t,1)end
        t[#t+1]={state=s,kind=read(0x39),flag=read(0x15),itemState=read(0x24),
          itemX=read(0x7b)+256*read(0x62),itemY=read(0xc3),status=read(0x75b),phase=progress}
      end
      if source(0x6ee)>=1 then
        assert(late.flower.spawned and read(0x15)==0,'Authored flower erased before sword inventory')
        late.sword={state=s,inventory=source(0x6ee),status=read(0x75b),flag=read(0x15)}
        startSwordCombat();return
      end
      local target=late.flower.left-13
      if progress=='flower-retreat' and idle(s) and floor(s)then
        if s.x<=target then switch('flower-face',1)
        elseif s.facing~=0 then switch('flower-left-face',2)
        else switch('flower-step-left',66)end
      elseif progress=='flower-left-face'then
        if s.facing==0 then pad=0 end
        if age>4 and s.facing==0 and idle(s) and floor(s)then switch('flower-step-left',66)end
      elseif progress=='flower-step-left' and s.action~=0 and s.action~=1 and s.action~=10 then
        switch('flower-step-settle',0)
      elseif progress=='flower-step-settle' and idle(s) and floor(s)then
        switch('flower-retreat',0)
      elseif progress=='flower-face'then
        if s.facing==255 then pad=0 end
        if age>4 and s.facing==255 and idle(s) and floor(s)then
          late.flower.climb=s;switch('flower-climb',0)
        end
      elseif progress=='flower-climb'then
        pad=age<8 and 0 or age<10 and 1 or age<70 and 0 or 8
        if s.y<=114 and(support(s)or s.action==10)then
          late.flower.boarded=s;switch('flower-walk',s.x>1248 and 2 or 1);return
        elseif age>=420 then error('Bounded original flower ledge climb')end
      elseif progress=='flower-walk'then
        pad=s.x>1252 and 2 or s.x<1240 and 1 or 0
        assert(age<120,'Bounded native flower overlap')
      end
      assert(age<(progress=='flower-climb' and 420 or 180),'Bounded original flower collection phase');return
    end

    if progress=='flower-approach' and s.x>=1230 then switch('flower-settle',0)
    elseif progress=='flower-settle' and s.action==0 and s.pose==15 and s.mode==0 and s.lock==0 then switch('flower-up',8)
    elseif progress=='flower-up' then
      if age>=80 then pad=0 end
      if age>=110 then
        late.flower={spawned=flowerSeen,trace=flowerTrace,sword=source(0x6ee)}
        if read(0x24)&128==0 then pad=0;return end
      assert(flowerSeen and read(0x39)==1,'Mature native flower in slot5')
      late.flower.left=1248
      while solid(late.flower.left-16,144)do late.flower.left=late.flower.left-16 end
      assert(late.flower.left>=1152 and late.flower.left<=1248,'Actual connected flower ledge')
      late.flower.geometry={}
      for col=1152,1328,16 do late.flower.geometry[#late.flower.geometry+1]={x=col,tile=tile(col,144)}end
      switch('flower-retreat',0);return
      end
    end
    assert(age<500,'Bounded flower approach');return
  end
  if commits==lastCommit then return end
  lastCommit=commits
  local s=state()
  assert(s.lives==2 and s.hp>0,'Prince survives pickup approach')
  assert(hexHeader(2)==cookie and hexHeader(3)==cookie,'Current Prince headers')
  minimumY=math.min(minimumY,s.y)
  if read(0x15)~=0 and read(0x1c)==0x2e then itemSeen=true end
  if s.hp~=previousHP then
    injuries[#injuries+1]={from=previousHP,to=s.hp,state=s}
    previousHP=s.hp
  end
  if itemSeen and (commits%10==0 or read(0x75b)==1) and #itemTrace<80 then
    itemTrace[#itemTrace+1]={commit=commits,playerX=s.x,playerY=s.y,status=read(0x75b),
      flag=read(0x15),id=read(0x1c),kind=read(0x39),state=read(0x24),
      x=read(0x7b)+256*read(0x62),y=read(0xc3)}
  end
  if itemSeen and read(0x24)>=128 then matureSeen=true end
  if itemSeen and matureSeen and read(0x75b)==1 and read(0x15)==0 then
    late.collection={trace=itemTrace,mature=matureSeen,status=read(0x75b),sword=source(0x6ee)}
    collected=true;switch('pipe-settle',0);return
  end
  local age=commits-changedAt
  if progress=='settle-start' and age>=4 then
    switch('pickup-approach',1)
  elseif progress=='pickup-approach' then
    local enemy=enemyNear(s.x)
    if enemy and enemy.gap>=115 and enemy.gap<=136 and s.action==1 and s.mode==1
      and s.pose>=6 and s.pose<14 and s.lock==0 and s.ground==0 then
      jump={request=s,enemy=enemy,minimumY=s.y};switch('pickup-evade',129)
    end
  elseif progress=='pickup-evade' then
    jump.minimumY=math.min(jump.minimumY,s.y)
    if s.action==4 then jump.admission=jump.admission or s;pad=1 end
    if age>=16 and s.action==1 and s.mode==1 and floor(s) then
      switch('pickup-runout',1)
    end
  elseif progress=='pickup-runout' and s.x>=390 then
    switch('pickup-backtrack',2)
  elseif progress=='pickup-backtrack' and s.action==1 and s.ground==0 and s.facing==0 and s.x<=365 then
    switch('pickup-settle',0)
  elseif progress=='pickup-settle' and s.action==0 and s.ground==0 and s.pose==15 and s.mode==0 and s.lock==0 then
    switch('pickup-turn',1)
  elseif progress=='pickup-turn' then
    if s.facing==255 then pad=0 end
    if age>4 and s.facing==255 and s.action==0 and s.mode==0 and s.pose==15 and s.lock==0 then
      switch('pickup-jump',8)
    end
  elseif progress=='pickup-jump' then
    if age<=100 then
      jumpTrace[#jumpTrace+1]={age=age,x=s.x,y=s.y,action=s.action,pose=s.pose,
        phase=s.phase,foot=s.foot,rawY=source(0x611),lastY=source(0x8b),
        delta=source(0x88),origin=source(0x89),originHigh=source(0x8a),
        surface=source(0x7f)+256*source(0x80)}
    end
    if age>80 then pad=0 end
    if age>100 then
      late.pickup={spawned=itemSeen,minimumY=minimumY,sword=source(0x6ee),trace=jumpTrace,yWrites=yWrites,supportTrace=supportTrace,headCalls=headCalls,headTrace=headTrace,headHits=headHits,returnedHeads=returnedHeads,headLayouts=headLayouts}
      switch('pickup-collect',1)
    end
  end
  if progress=='pickup-collect' then
    if s.x>=420 then pad=0 end
    if age>250 then
      late.collection={trace=itemTrace,mature=matureSeen,status=read(0x75b),sword=source(0x6ee)}
      finish(false,'Bounded natural mushroom collection');return
    end
  end
  assert(commits<1200,'Bounded first pickup approach')
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
assert(rom=='40a11ffb8452c3b54caef56ddd5912e2bdda2c276545f20a589baa053de4d20e','Exact private e418 earned-stage replay')
assert(variant and variant>=0 and variant<=3 and variant%1==0,'Supported Prince route length')
emu.addEventCallback(guarded(function()
  emu.setInput({right=pad&1~=0,left=pad&2~=0,up=pad&8~=0,down=pad&4~=0,start=pad&16~=0,
    select=pad&32~=0,b=pad&64~=0,a=pad&128~=0},0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guarded(function()
  frame=frame+1
  assert(frame<=24000,'Bounded physical first-pipe replay')
  local ok,message=coroutine.resume(route)
  assert(ok,message)
end),emu.eventType.endFrame)


local candidateStaticExtents={{["bank"]=3,["bytes"]={172,177,196,8,138,72,152,72,32,82,197,169,0,141,140,192,141,142,192,141,152,192,173,124,192,205,131,192,48,89,208,101,173,24,198,41,3,201,2,240,92,173,22,198,201,10,240,7,201,24,240,3,238,152,192,173,24,198,201,3,240,4,201,4,208,67,173,145,192,205,134,192,173,146,192,237,135,192,144,53,173,134,192,105,14,41,240,170,173,135,192,105,0,168,204,146,192,144,9,208,32,236,145,192,144,2,208,25,142,143,192,140,144,192,238,142,192,208,14,173,145,192,24,105,63,141,145,192,144,3,238,146,192,169,255,141,151,192,173,164,192,56,233,24,141,107,179,173,165,192,233,0,141,108,179,32,154,164,144,42,173,152,192,240,34,173,105,179,41,240,105,7,56,237,15,198,170,173,106,179,237,16,198,240,10,201,255,208,13,224,241,144,9,176,4,224,16,176,3,238,140,192,174,143,192,172,144,192,204,146,192,144,12,240,3,76,62,191,236,145,192,144,2,208,123,142,107,179,140,108,179,32,16,179,144,97,138,41,240,141,149,192,201,33,144,21,233,1,141,107,179,32,16,179,144,11,173,149,192,233,16,141,149,192,76,212,190,173,152,192,240,47,173,133,192,208,42,173,149,192,9,15,205,132,192,176,32,32,233,197,32,16,179,176,16,173,105,179,105,11,141,105,179,144,3,238,106,179,32,16,179,142,105,179,140,106,179,144,29,173,149,192,205,151,192,176,3,141,151,192,76,62,191,138,41,240,105,16,170,176,3,76,178,190,200,76,178,190,173,105,179,41,16,240,20,173,105,179,24,105,16,141,105,179,176,3,76,108,190,238,106,179,76,108,190,173,151,192,73,255,240,5,173,142,192,208,16,173,140,192,240,4,169,20,208,20,173,151,192,73,255,240,13,173,151,192,141,155,192,169,0,141,156,192,169,1,141,159,192,173,155,192,141,127,192,173,156,192,141,128,192,173,124,192,141,129,192,104,168,104,170,40,173,159,192,96,234,234,234},["offset"]=7650},{["bank"]=2,["bytes"]={32,255,196,32,18,195,169,29,174,22,198,224,3,240,8,224,4,240,4,224,14,208,2,169,36,141,131,192,173,17,198,56,237,131,192,176,2,169,0,74,74,74,74,74,74,141,131,192,162,0,173,124,192,56,237,131,192,16,1,202,142,154,192,162,6,10,46,154,192,202,208,249,141,153,192,173,132,192,24,109,153,192,141,143,192,141,145,192,141,164,192,173,133,192,109,154,192,141,144,192,141,146,192,141,165,192,162,0,169,3,56,237,136,192,16,1,202,24,109,164,192,141,155,192,138,109,165,192,141,156,192,162,0,173,125,192,24,105,24,141,105,179,173,126,192,105,0,141,106,179,96,174,105,179,172,106,179,173,15,198,233,5,141,105,179,173,16,198,233,0,141,106,179,173,149,192,141,107,179,96},["offset"]=1362},{["bank"]=2,["bytes"]={173,166,192,41,3,201,2,240,1,96,32,209,179,169,104,141,216,222,169,255,141,215,222,162,5,181,16,201,1,208,44,181,23,201,7,176,38,181,31,41,32,208,32,32,102,212,201,3,208,25,181,165,201,1,208,19,32,137,222,32,185,163,176,11,205,216,222,176,6,141,216,222,142,215,222,202,16,203,174,215,222,48,103,138,9,128,205,28,198,240,38,72,160,13,185,217,222,153,28,198,136,208,247,104,141,28,198,142,81,192,142,16,199,169,255,141,18,199,140,17,199,140,222,198,169,1,141,208,198,32,137,222,181,190,24,105,21,141,31,198,181,165,105,255,141,32,198,56,173,31,198,237,137,192,141,31,198,173,32,198,237,138,192,141,32,198,169,0,188,63,5,192,1,208,2,169,255,141,35,198,169,1,141,224,198,96,173,224,198,240,3,141,222,198,169,0,141,224,198,141,28,198,96,181,118,24,105,8,141,29,198,181,93,105,0,141,30,198,96},["offset"]=7614},{["bank"]=3,["bytes"]={200,200,200},["offset"]=7232},{["bank"]=2,["bytes"]={9,1},["offset"]=6009},{["bank"]=2,["bytes"]={255,255,26,202,14,199,85,203,176,197,190,197,248,199,204,197,53,131,36,197,5,200,18,200,108,196,90,196,132,203,26,202,108,203,108,203,181,201,255,255,200,200,146,197,218,197,145,131,181,139,213,130,166,131,158,198,31,200,232,197,44,200,44,200,112,202,27,199,97,202,155,202,255,255,187,131,193,202,177,196,144,139,237,130,76,131,119,137,8,138,97,203,220,202,220,202,228,196,180,202,40,199,40,199,40,199,194,196,140,202,208,131,4,203,52,197,52,197,229,131,172,198,172,198,192,137,200,198,186,198,211,196,255,255,225,203,225,203,224,200,4,198,4,198,246,197,246,197,207,202,53,199,130,198,92,199,66,199,57,200,235,202,255,255,255,255,79,199,201,203,201,203,255,255,18,198,17,203,17,203,105,199,105,199,39,202,39,202,54,196,54,196,35,196,35,196,70,202,70,202,255,255,255,255,214,198,68,197,116,197,83,200,96,200,212,201,235,200,86,202,86,202,70,200,131,197,32,198,122,200,109,200,109,200,126,202,118,199,118,199,255,255,168,202,135,200,144,199,131,199,131,199,148,200,31,203,31,203,58,203,46,198,244,196,246,200,255,255,255,255,213,200,157,199,1,201,161,200,67,201,0,199,242,198,161,197,100,197,84,197,55,202,228,198,174,200,144,198,89,201,62,66,99,67,189,130,2,66,222,65,236,75,122,67,5,67,5,67,158,73,158,73,255,255,62,66,255,255,29,67,139,66,255,255,139,66,255,255,32,66,158,73,158,73,214,198,68,197,116,197,255,255,255,255,143,137,60,198,170,199,12,201,248,202,99,201,78,201,255,255,215,203,255,255,255,255,255,255,255,255,255,255,255,255,255,255,169,203,187,200,187,200,74,198,255,255,143,196,44,203,44,203,71,203,4,197,88,198,102,198,160,196,255,255,183,199,196,199,126,196,15,196,255,255,255,255,255,255,255,255,255,255,164,66,209,199,255,255,255,255,116,198,235,199,222,199,120,203,56,201,23,201,45,201,109,201,34,201,222,73,89,66,114,66,242,73,58,76,32,76,6,76,250,67,72,196,20,197,109,20,21,131,3,235,227,234,77,233,234,77,225,234,77,217,83,169,66,167,34,163,18,161,50,165,48,155,32,153,16,151,1,159,64,157,43,20,21,136,1,243,224,232,77,242,67,147,20,149,50,145,18,141,34,143,48,135,32,133,16,131,1,139,64,137,236,20,23,8,131,253,224,233,77,255,233,77,247,233,77,239,244,140,145,10,143,138,109,136,134,132,130,128,16,132,220,20,4,130,0,220,216,77,249,216,77,241,200,97,95,64,93,91,166,88,86,40,84,82,64,80,78,185,20,28,29,4,130,253,220,226,77,251,210,77,251,132,181,193,166,190,188,132,186,184,0,182,185,20,28,29,4,130,253,220,227,77,252,211,77,252,132,181,179,166,202,200,132,196,194,16,198,234,20,22,8,130,3,224,235,77,253,219,77,253,240,188,191,182,186,184,41,182,180,64,178,176,234,20,27,6,130,254,222,229,77,250,229,77,242,244,140,143,58,138,136,104,134,130,65,128,132,41,20,21,133,244,221,67,125,20,129,4,127,50,123,18,119,34,121,48,117,32,115,16,113,105,3,4,135,6,231,83,133,66,129,18,125,3,131,49,123,34,127,32,121,16,119,0,117,105,6,7,136,1,232,67,129,82,127,65,119,50,125,18,123,2,121,48,117,32,115,16,113,169,20,22,6,130,3,222,230,77,2,230,77,250,176,144,147,98,142,140,148,138,136,0,134,233,20,22,7,130,0,223,233,77,0,217,77,0,250,174,170,54,172,168,24,166,164,64,162,25,1,131,254,219,68,93,52,91,35,87,20,89,50,85,18,83,33,81,16,77,1,79,89,7,130,0,234,81,75,66,83,50,81,18,79,2,77,64,73,48,71,32,69,16,67,153,20,9,130,3,225,231,77,251,231,77,243,176,108,111,98,106,104,148,102,100,0,98,248,20,21,22,6,130,252,222,237,77,253,237,77,5,243,196,192,182,194,190,148,188,186,24,3,137,4,225,67,99,51,97,35,95,18,93,49,91,33,89,16,85,1,87,24,4,134,2,230,66,85,2,77,50,83,34,81,18,79,32,75,16,73,0,71,24,5,133,0,221,3,123,67,127,50,121,35,125,18,119,33,117,16,113,1,115,24,9,132,5,220,36,85,3,81,34,79,19,83,17,73,65,77,49,75,32,71,24,9,134,253,222,52,127,19,121,4,125,50,119,35,123,33,117,64,115,48,113,168,20,29,3,129,245,219,225,77,243,132,187,185,166,182,180,132,178,176,16,134,218,26,8,254,216,145,127,125,180,120,123,54,118,116,157,112,114,64,110,108,217,14,126,0,198,173,83,81,133,77,79,112,72,75,37,70,68,0,66,168,13,14,126,0,198,165,129,127,135,125,120,2,123,118,80,116,114,168,29,30,5,246,221,180,134,139,6,137,132,146,128,130,64,126,124,232,1,2,3,0,219,244,104,153,10,107,150,98,148,146,64,144,142,232,1,2,3,4,219,200,141,139,10,137,132,114,134,130,80,128,126,152,26,5,0,221,180,102,107,6,105,100,40,98,96,64,94,92,167,24,25,3,254,219,132,133,131,166,128,126,132,124,122,0,120,167,25,26,4,8,212,80,135,133,182,130,128,41,126,124,64,122,216,6,8,0,216,223,91,88,182,86,82,57,84,80,20,78,76,216,8,3,3,219,64,121,119,251,116,114,98,112,110,148,108,106,231,10,11,7,0,223,10,129,124,114,126,122,92,120,118,128,116,151,8,4,0,220,64,83,81,98,78,76,148,74,72,0,70,151,17,4,0,220,132,127,125,6,123,120,41,118,108,64,106,151,25,4,6,212,64,105,103,98,100,98,148,96,94,0,92,151,30,5,246,221,180,84,75,6,73,82,148,80,78,0,76,215,1,3,2,219,247,104,102,10,107,100,37,98,96,0,94,215,9,6,252,222,199,111,104,14,109,102,185,106,100,192,98,215,14,7,2,223,79,121,118,182,116,114,148,112,108,16,110,215,19,6,242,238,234,92,90,108,88,86,132,84,82,0,80,215,19,8,245,240,234,78,76,104,74,70,64,68,66,192,72,166,14,15,3,254,219,135,133,130,168,128,124,65,122,126,166,15,16,3,255,235,166,132,130,40,128,126,64,124,122,230,2,3,4,2,228,250,134,132,216,130,128,64,126,118,245,4,18,19,12,247,244,236,192,190,132,188,186,0,70,150,0,3,249,219,183,102,100,2,105,98,80,96,94,150,0,4,3,220,183,114,112,2,117,110,80,108,106,150,1,4,3,220,183,72,70,2,75,68,80,66,64,150,3,3,7,227,182,82,80,146,76,78,64,74,72,150,4,5,255,229,162,116,112,104,114,110,64,108,106,150,11,4,2,220,7,93,90,37,100,96,144,98,94,150,11,4,2,220,7,93,90,42,86,88,80,84,82,150,13,126,238,198,98,79,77,74,75,72,104,70,68,150,16,8,255,232,166,80,78,40,76,74,64,72,70,150,17,5,1,221,176,114,117,98,112,110,148,108,106,150,23,10,5,234,166,102,100,40,98,96,64,94,92,150,24,3,254,219,180,116,119,105,114,112,64,110,108,150,25,4,6,212,64,105,103,98,112,110,148,108,106,150,25,4,6,212,64,105,103,98,120,118,148,116,114,150,27,6,1,222,58,100,98,104,96,92,65,90,94,165,11,12,3,245,227,182,132,130,148,128,124,16,126,165,19,20,3,246,227,166,132,130,132,128,126,0,124,214,4,8,2,232,109,92,90,168,94,88,64,86,70,214,10,3,0,227,162,74,70,104,72,66,76,64,68,214,10,6,254,222,58,112,110,117,114,108,200,106,104,214,10,8,2,224,54,102,100,29,96,98,132,94,92,214,14,8,255,224,251,106,104,105,102,100,65,96,98,214,19,9,245,233,166,114,112,200,110,108,64,106,104,229,4,18,14,247,246,236,184,182,132,180,178,0,70,229,4,18,80,241,184,236,184,182,132,180,178,0,70,85,0,3,254,219,112,80,83,37,78,76,0,74,85,5,4,2,220,6,85,82,36,80,78,0,76,85,8,4,0,220,112,102,105,37,100,98,0,96,85,11,8,254,224,112,120,123,37,118,116,0,114,85,12,0,253,208,87,89,84,2,87,82,0,80,85,12,3,252,219,64,121,119,37,116,114,0,112,85,12,5,252,221,70,79,76,36,74,72,0,70,85,13,126,254,198,32,101,99,37,96,94,0,92,85,16,4,2,220,112,118,121,37,116,114,0,112,85,17,5,3,221,64,85,83,98,80,78,64,76,85,17,5,253,221,64,85,83,98,80,78,64,76,85,18,118,1,198,2,89,84,100,86,82,0,80,85,23,5,254,221,112,110,113,37,108,106,0,104,85,26,4,0,220,70,81,78,36,76,74,0,72,85,26,5,255,221,70,91,88,36,86,84,0,82,85,27,4,1,220,2,89,84,100,86,82,0,80,85,27,9,3,225,6,121,118,36,116,114,0,112,85,27,10,3,226,6,111,108,36,106,104,0,102,149,0,5,2,221,183,126,124,37,122,120,0,118,149,1,4,2,220,183,104,114,37,112,110,0,108,149,1,5,2,221,183,124,122,37,120,118,0,116,149,4,3,0,235,98,104,102,148,100,98,0,96,149,4,3,253,227,182,126,124,41,122,120,64,118,149,12,124,247,204,132,99,97,98,94,92,64,90,149,15,3,255,235,150,116,120,36,118,114,0,112,149,15,5,1,221,70,79,76,148,74,72,0,70,149,15,5,1,221,70,89,86,148,84,82,0,80,149,16,3,1,227,182,100,98,148,96,94,0,92,149,16,5,1,229,182,90,88,148,86,84,0,82,149,17,3,252,219,132,75,73,98,70,68,64,66,149,17,6,2,222,131,95,92,166,90,88,128,86,149,18,97,247,185,138,107,104,132,102,100,0,98,149,19,6,245,230,166,122,120,132,118,116,0,104,149,24,3,0,227,166,106,104,132,102,100,0,98,213,2,4,3,228,172,116,124,132,122,120,0,118,20,18,125,0,197,32,79,77,32,74,72,84,11,3,3,219,2,81,78,80,76,74,84,15,4,2,236,98,102,100,64,98,96,84,18,3,255,219,67,71,68,100,66,64,84,18,112,252,192,70,97,94,64,92,90,84,23,3,0,227,114,120,118,80,116,114,84,28,2,2,226,98,80,78,64,76,74,84,28,3,1,235,98,102,100,64,98,96,84,28,4,1,228,38,86,88,64,84,82,84,28,4,255,228,99,70,72,20,68,66,148,18,90,244,186,168,112,110,64,108,98,212,24,4,245,244,200,76,74,65,72,78,19,20,3,5,219,2,75,72,0,70,83,24,4,253,236,82,68,70,0,66,83,28,3,254,235,100,94,92,0,90,26,7,137,0,225,4,103,34,99,18,97,2,95,50,101,65,93,48,91,32,89,16,87,0,85,23,137,1,249,81,91,65,89,48,85,16,83,1,87,169,20,22,3,130,255,219,230,77,2,230,77,250,180,156,161,6,159,154,41,152,150,64,148,2,4,3,220,121,116,114,80,112,110,24,10,136,251,224,20,91,34,89,18,87,65,85,48,81,32,79,16,77,1,83,15,6,4,230,37,94,92,0,90,168,20,28,4,129,253,220,211,77,251,132,181,179,166,176,174,132,172,170,0,168,20,29,4,130,2,220,223,77,1,215,77,249,180,148,151,54,146,144,20,142,140,23,7,129,249,225,34,113,18,111,65,109,48,107,32,105,16,87,0,85,0,3,2,219,112,70,73,37,68,66,0,64,103,12,13,126,255,198,82,175,177,7,173,84,37,170,168,0,166,4,19,3,246,235,166,166,164,40,162,160,64,158,70,167,13,14,118,0,198,133,157,159,112,152,155,37,150,104,0,148,15,3,0,235,149,108,106,32,110,104,215,5,5,1,221,247,96,94,10,99,92,37,90,88,0,86,5,4,2,220,64,75,73,98,70,68,64,66,64,166,15,16,8,254,224,75,175,172,105,170,108,64,168,166,8,9,4,1,220,67,133,130,105,128,126,20,124,122,150,5,6,1,222,183,110,108,41,106,104,80,102,100,16,17,3,1,219,112,126,129,32,124,122,150,8,4,251,220,180,92,95,105,90,88,65,84,86,6,2,255,218,64,75,73,98,70,68,64,66,64,150,11,6,255,222,112,110,113,37,108,104,144,106,102,7,8,3,3,219,64,133,131,98,128,126,64,124,122,150,12,3,244,203,150,109,111,70,107,104,36,102,100,23,24,6,253,230,114,128,126,80,124,122,214,9,5,252,221,122,96,92,53,94,88,216,90,86,13,126,246,198,32,91,87,70,89,84,36,82,80,214,17,6,1,222,244,100,105,10,103,98,104,96,86,25,3,5,211,80,69,79,114,76,74,80,72,70,214,17,6,253,222,244,100,105,10,103,98,104,96,86,25,4,6,212,64,91,89,98,86,84,64,82,80,85,0,3,252,219,112,90,93,37,88,86,0,84,7,4,3,220,6,121,118,32,116,114,85,2,3,2,219,112,106,109,37,104,102,0,100,27,28,8,2,224,54,128,126,20,124,122,149,2,5,0,221,183,98,96,37,94,92,0,90,6,132,253,220,83,111,67,109,18,101,3,107,65,99,50,105,34,103,48,97,32,95,16,93,149,24,4,254,236,166,96,94,132,92,90,0,88,3,131,4,227,83,115,66,113,34,111,18,109,49,107,32,105,16,103,0,101,12,13,3,252,219,64,131,129,38,124,126,0,122,212,24,9,245,249,216,86,82,65,80,84,11,3,3,219,2,73,68,96,70,66,42,20,21,131,131,249,227,243,77,243,243,77,251,251,185,25,251,182,180,41,176,174,100,178,172,0,170,20,29,3,131,245,219,227,77,251,227,77,243,227,77,235,132,187,185,166,182,180,132,178,176,16,170,20,29,4,131,245,220,225,77,245,225,77,237,225,77,229,132,165,163,166,174,172,132,168,166,16,170,20,29,4,131,245,220,224,77,249,224,77,241,224,77,233,132,165,163,166,160,158,132,154,152,16,156,60,151,30,5,246,221,180,20,11,6,9,18,148,16,14,0,12},["offset"]=2048},{["bank"]=2,["bytes"]={162,13,189,225,179,157,14,198,202,16,247,169,5,141,207,198,141,209,198,169,0,141,166,192,169,3,141,136,192,169,77,141,137,192,165,189,56,233,48,141,17,198,141,139,192,165,164,233,1,141,138,192,32,209,179,32,18,195,173,132,192,141,134,192,173,133,192,141,135,192,173,91,7,74,141,238,198,56,96,0},["offset"]=176},{["bank"]=2,["bytes"]={173,207,198,240,49,181,52,74,208,50,181,31,16,40,176,12,173,207,198,201,5,176,42,238,207,198,208,37,138,72,169,2,141,91,7,74,141,238,198,169,91,32,81,170,104,170,32,47,141,169,6,32,181,152,56,96,160,3,208,2,160,2,76,27,218,173,91,7,208,232,238,91,7,208,227,0,0},["offset"]=1971},{["bank"]=2,["bytes"]={235},["offset"]=8060},{["bank"]=3,["bytes"]={234,234,234,234,234,234,234,234},["offset"]=5105}}
emu.addMemoryCallback(guarded(function()
  if not mapped(0xbbc1,3)or newPacketVerified then return end
  assert(hexHeader(2)==cookie and hexHeader(3)==cookie,'Both complete16a cookies')
  local count=0
  for _,row in ipairs(candidateStaticExtents)do
    for i,value in ipairs(row.bytes)do
      assert(emu.read(row.bank*8192+row.offset+i-1,emu.memType.nesWorkRam)==value,'Actual16a static extent before first renderer')
      count=count+1
    end
  end
  local cpu=emu.getState()
  newPacketVerified={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],bytes=count,both_cookies=true,three_body_transition_and_three_graphics_extents=true}
end),emu.callbackType.exec,0xbbc1)


local carefulStepHooks={{["bytes"]={76,81,170},["kind"]="partial",["pc"]=44846},{["bytes"]={76,81,170},["kind"]="full",["pc"]=44867}}
for _,h in ipairs(carefulStepHooks)do
 emu.addMemoryCallback(guarded(function()
  if progress~='late-finish-pipe-step' or not mapped(h.pc,3)then return end
  for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Exact original careful-step selector')end
  local cpu=emu.getState();local action=cpu['cpu.a'];local half=source(0x4f)
  assert(action>=30 and action<=42,'Original admitted careful-step range')
  if h.kind=='partial'then assert(action==29+half and half>=1 and half<=13,'Original partial-step formula')end
  late.careful_step_admissions=late.careful_step_admissions or {}
  local rows=late.careful_step_admissions;assert(#rows<16,'Bounded original step-admission witness')
  rows[#rows+1]={PC=h.pc,SP=cpu['cpu.sp'],completed=verifiedMainReturns,commit=commits,
    kind=h.kind,action=action,half_distance=half,state=state()}
 end),emu.callbackType.exec,h.pc)
end


local freshStepHooks={{["bytes"]={76,81,170},["kind"]="partial",["pc"]=44846},{["bytes"]={76,81,170},["kind"]="full",["pc"]=44867},{["bytes"]={96},["kind"]="no-step",["pc"]=44856}}
for _,h in ipairs(freshStepHooks)do
 emu.addMemoryCallback(guarded(function()
  if progress~='late-finish-pipe-step' or not mapped(h.pc,3)then return end
  for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Exact reached original fresh-step decision')end
  local rows=late.fresh_step_outcomes or {};late.fresh_step_outcomes=rows
  assert(#rows<16,'Bounded fresh original decisions')
  local cpu=emu.getState()
  rows[#rows+1]={PC=h.pc,SP=cpu['cpu.sp'],A=cpu['cpu.a'],half_distance=source(0x4f),
   kind=h.kind,state=state(),completed=verifiedMainReturns,commit=commits,
   source_x=source(0x60f)+256*source(0x610)}
 end),emu.callbackType.exec,h.pc)
end
