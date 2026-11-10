-- Natural controller-only FF route. This source writes no emulated RAM/files.
-- v2 observer correction: real CharactersInit sets optional extra outlinesOFF=1.
-- Frozen v1 SHA1e11e260... failed at natural frame340 on its false flag==0 assumption.
-- This flag controls optional bit32 mask cells; it does not prove source black-pixel fidelity.
-- Root binds the launched ROM to SMB_STDOUT_ROM_SHA before running Mesen.
-- Baseline thresholds port W.run -> F.flower -> A.attack -> S.route.
-- v3 keeps the earned-mushroom prefix and adds bounded source-accepted jump delivery
-- after it: native sampled-input/catch-up behavior is observed, never overwritten.
-- Frozen Python source SHA256s:
-- W c6c3a7dca9cea3bf4577d5038f74a22261be8989edc1ad87ddd8590d0e581de0
-- class adapter e122dc0dc793eeb7aa002389ea1112302f3cc008b19b77d38d75f695cdcc5f7e
-- F e990661e7b9fe754dede187b39dd0dfda6367f051cdd701b01ddc9b03aad50ec
-- A dd8015682993e4a13190e9a9e200a1ae4b227767172b5ad6036831447110b44e
-- S 4081ddb23a5e1c5dd5a59bfa87ae0058b108dc27f0b7fa2c1bb158ed98124439
local env = os.getenv
local variant = tonumber(env('SMB_TEST_VARIANT') or '0')
local rom = env('SMB_STDOUT_ROM_SHA') or ''
local expectedStair = env('SMB_EXPECT_STAIR_STALL') == '1'
local wantImages = env('SMB_STDOUT_IMAGES') == '1'
local classes = {'Fighter', 'White Mage', 'Black Mage', 'Thief'}
local damage = {150, 50, 150, 25}
local L = {
 OperMode=0x771, OperMode_Task=0x773, GameEngineSubroutine=0x0f,
 SelectedCharacter=0x6002, CrossoverTitleDrawn=0x6004, DisableScreenFlag=0x775,
 CrossoverMenuState=0x7307, CrossoverMenuIndex=0x7309, FfVariant=0x5fef,
 Player_X_Position=0x75, Player_PageLoc=0x5c, Player_Y_Position=0xbd,
 Player_State=0x1e, NumberofLives=0x75f, PlayerFacingDir=0x53e,
 Enemy_Flag=0x10, Enemy_ID=0x17, Enemy_State=0x1f, Enemy_X_Position=0x76,
 Enemy_PageLoc=0x5d, Enemy_Y_Position=0xbe, PowerUpType=0x34,
 MmEnemyHealthLo=0x603f, MmEnemyHealthHi=0x6045,
 GuestPowerupActive=0x6bfd, GuestPowerupAge=0x6bfe, TimerControl=0x74a,
 WorldNumber=0x764, LevelNumber=0x761, AreaAddrsLOffset=0x754,
 PlayerOutlinesOff=0x7eb8, CheatStartLevel=0x7ffc, CheatInvincible=0x7ffb,
 CrossoverBehaviorVersion=0x7fe1, ScreenLeft_X_Pos=0x71f, ScreenLeft_PageLoc=0x71d,
 Player_SprAttrib=0x587, ChangeAreaTimer=0x6dc, PlayerEntranceCtrl=0x713,
 AreaType=0x753, NmiSkipped=0x13a, MmVY=0x68a8,
 FfRenderBuffer=0x5c40, MTileAttribute=0xef36,
 SavedJoypadBits=0xdc, A_B_Buttons=0x558, PreviousA_B_Buttons=0x55b,
 FfPrevious=0x5c00, FfFresh=0x5c01, FfJump=0x5c09,
 JumpSwimTimer=0x77f, SwimmingFlag=0x706
}
local frame, updates, completed, polls = 0, 0, 0, 0
local phase, step, padBits, stopped, failed = 'title', 0, 0, false, false
local gameplay, mainLive, requestedFinish = false, nil, nil
local calls, returns, pending = {}, {}, {}
local events, inputSamples, jumps, priority, headSamples = {}, {}, {}, {}, {}
local imageTags, imageQueue = {}, {}
local firstCold, nativeFlag, active12, attackHit, committed
local collectSlot, opening, mushClock, mushJump = 5, 'approach', 0, -100
local flowerBirth, flowerLaunch, flowerRetreat = nil, nil, false
local flowerJump, flowerJumped = -100, {}
local attackJumped, stageJump = {}, -100
local bestX, advancedAt, cameraPrevious, routeStart = 0, 0, nil, nil
local groups = {{ticks=0}, {ticks=0}}
local physics = {ordinary_loops=0, max_world_step=0, min_world_step=0,
 max_camera_step=0, min_camera_step=0, camera_deltas={}, extrema={}}
local cadence = {catchup_updates=0, maximum_updates_per_frame=0,
 gameplay_zero_update_frames=0, gameplay_physical_frames=0,
 physical_frames_without_input_poll=0}
local previousCompleted, previousPolls = 0, 0
local lastInput = nil
local jumpDiagnostics, jumpCueCounts = {}, {}
local activeJump, previousDesiredA, desiredJumpReason = nil, false, nil
local function read(a) return emu.read(a, emu.memType.nesDebug) end
local function r(n, i) return read(assert(L[n], n) + (i or 0)) end
local function pos(lo, hi, i) return r(lo, i) + 256 * r(hi, i) end
local function state()
 return {frame=frame, updates=updates, completed=completed, phase=phase, step=step,
  x=pos('Player_X_Position','Player_PageLoc'), y=r('Player_Y_Position'),
  state=r('Player_State'), engine=r('GameEngineSubroutine'), lives=r('NumberofLives'),
  mode=r('OperMode'), task=r('OperMode_Task'), world=r('WorldNumber'), level=r('LevelNumber'),
  facing=r('PlayerFacingDir'), power=read(0x5fc5), earned=read(0x5fc6), charges=read(0x5fc7),
  action=read(0x5c03), age=read(0x5c04), spell=read(0x5c05),
  hurt=read(0x5c07), knockback=read(0x5c08), active=r('GuestPowerupActive'),
  freeze_age=r('GuestPowerupAge'), timer=r('TimerControl'),
  camera=pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc'), attrib=r('Player_SprAttrib'),
  entrance=r('PlayerEntranceCtrl'), area_type=r('AreaType'), pipe_timer=r('ChangeAreaTimer'),
  optional_outlines_off=r('PlayerOutlinesOff'),
  saved_joypad=r('SavedJoypadBits'), AB=r('A_B_Buttons'), previous_AB=r('PreviousA_B_Buttons'),
  FfPrevious=r('FfPrevious'), FfFresh=r('FfFresh'), FfJump=r('FfJump'),
  jump_swim_timer=r('JumpSwimTimer'), swimming=r('SwimmingFlag'),
  VY={read(L.MmVY),read(L.MmVY+1),read(L.MmVY+2)}}
end
local function actor(i)
 return {slot=i, flag=r('Enemy_Flag',i), id=r('Enemy_ID',i), state=r('Enemy_State',i),
  kind=r('PowerUpType',i), x=pos('Enemy_X_Position','Enemy_PageLoc',i),
  y=r('Enemy_Y_Position',i), HP=r('MmEnemyHealthLo',i)+256*r('MmEnemyHealthHi',i)}
end
local function actors()
 local a={}; for i=0,5 do a[#a+1]=actor(i) end; return a
end
local function active(s) return s.mode==1 and s.task==3 and s.engine==8 end
local function quote(s)
 return '"'..s:gsub('[%z\1-\31\\"]',function(c)
  if c=='"' then return '\\"' elseif c=='\\' then return '\\\\' end
  return string.format('\\u%04x',string.byte(c))
 end)..'"'
end
local function json(v)
 local kind=type(v)
 if kind=='string' then return quote(v) end
 if kind=='nil' then return 'null' end
 if kind=='boolean' or kind=='number' then return tostring(v) end
 assert(kind=='table','JSON type '..kind)
 local out={}
 if #v>0 then
  for _,x in ipairs(v) do out[#out+1]=json(x) end
  return '['..table.concat(out,',')..']'
 end
 for k,x in pairs(v) do out[#out+1]=quote(tostring(k))..':'..json(x) end
 table.sort(out); return '{'..table.concat(out,',')..'}'
end
local function note(kind, value)
 assert(#events<64,'Bounded aggregate events')
 events[#events+1]={event=kind, value=value or state()}
end
local function finish(ok, why)
 if stopped then return end
 stopped=true; failed=not ok; padBits=0
 local good, terminal=pcall(state)
 if not good then terminal={snapshot_error=tostring(terminal)} end
 print('SMB_NATIVE_RECEIPT '..json({passed=ok, reason=why, failed_latched=failed,
  ROM_SHA256=rom, ROM_pin_supplied_by_runner=true, variant=variant,
  class_name=classes[(variant or -1)+1] or 'invalid', controller_only=true,
  script_RAM_writes=false, save_load_or_cheats=false, output_files=0,
  physical_frames=frame, logical_Main_entries=updates, completed_Main=completed,
  input_polls=polls, bounds={physical_frames=12000,logical_updates=6000},
  expected_original_stair_stall=expectedStair, full_1_1=nativeFlag~=nil,
  active_1_2=active12, first_active_1_1=firstCold, mushroom=groups[1], flower=groups[2],
  earned_attack=attackHit, issued_attack=committed, native_flag=nativeFlag,
  terminal=terminal, actors=actors(), calls=calls, cadence=cadence, physics=physics,
  priority_edges=priority, head_samples=headSamples, events=events,
  jump_events=jumps, input_change_samples=inputSamples, image_tags=imageTags,
  jump_delivery=jumpDiagnostics, jump_attempts_by_cue=jumpCueCounts,
  scope='Actual Mesen/controller/physical-NMI route. Runner must bind ROM/script hashes. No RAM writes, stage grants, every-enemy-kill, all-attack, audible-output, exhaustive art or original-source parity claim.'}))
 emu.stop(ok and 0 or 1)
end
local function guarded(name, fn)
 return function(...)
  if stopped then return end
  local ok, why=pcall(fn,...)
  if not ok then finish(false,name..': '..tostring(why)) end
 end
end
local function jumpSample(event)
 return {event=event,frame=frame,Main=updates,completed=completed,polls=polls,
  phase=phase,step=step,x=pos('Player_X_Position','Player_PageLoc'),y=r('Player_Y_Position'),
  state=r('Player_State'),engine=r('GameEngineSubroutine'),pad=padBits,
  saved=r('SavedJoypadBits'),AB=r('A_B_Buttons'),previous_AB=r('PreviousA_B_Buttons'),
  previous_source=r('FfPrevious'),fresh_source=r('FfFresh'),source_jump=r('FfJump'),
  jump_swim_timer=r('JumpSwimTimer'),swimming=r('SwimmingFlag')}
end
local function jumpImage(tag)
 if wantImages and #imageTags+#imageQueue<2 then imageQueue[#imageQueue+1]=tag end
end
local function sampledJump(bits)
 if not gameplay or phase=='mushroom' or requestedFinish then
  if activeJump then activeJump.outcome='phase-ended';activeJump=nil end
  previousDesiredA=false;return bits
 end
 if activeJump and activeJump.phase~=phase then activeJump.outcome='phase-ended';activeJump=nil;previousDesiredA=false end
 local wants=bits&128~=0
 if wants and not previousDesiredA and not activeJump then
  assert(#jumpDiagnostics<64,'Bounded source jump requests64')
  local cue=desiredJumpReason or (phase..'-A')
  local count=(jumpCueCounts[cue] or 0)+1;jumpCueCounts[cue]=count
  if cue:find('flower%-pipe%-')then assert(count<=8,'Bounded flower obstacle attempts8')end
  activeJump={phase=phase,cue=cue,attempt=count,requested=jumpSample('requested'),
   status='release',created_Main=updates,source_reads={}}
  jumpDiagnostics[#jumpDiagnostics+1]=activeJump
 end
 previousDesiredA=wants
 local q=activeJump
 if not q then return bits end
 if q.status=='release' then
  if r('FfPrevious')&128==0 and r('SavedJoypadBits')&128==0 then
   q.status='press';q.press_Main=updates;q.fresh_release=jumpSample('native-release-observed')
  else
   assert(updates-q.created_Main<=16,'Native A release not observed within16 Main')
   return bits&127
  end
 end
 if q.status=='press' then
  assert(updates-q.press_Main<=16,'Requested A not accepted by original FfMovement within16 Main')
  return bits|128
 end
 assert(q.status=='hold','Jump-delivery state')
 if not q.airborne and r('Player_State')~=0 then q.airborne=jumpSample('airborne');q.airborne_Main=updates end
 if not q.airborne and updates-q.accepted_Main>=4 then
  q.outcome='source-accepted-but-no-completed-airborne';q.returned=jumpSample('blocked-after-source-acceptance')
  activeJump=nil;return bits&127
 end
 if q.airborne and updates-q.airborne_Main>=23 then
  q.outcome='source-accepted-airborne-held23';q.returned=jumpSample('release-after23')
  activeJump=nil;return bits&127
 end
 return bits|128
end
local function setPad(bits)
 bits=sampledJump(bits)
 padBits=bits
 if bits~=lastInput then
  if #inputSamples<32 then inputSamples[#inputSamples+1]={frame=frame,Main=updates,phase=phase,step=step,bits=bits} end
  lastInput=bits
 end
end
local function buttons(bits)
 return {right=bits&1~=0,left=bits&2~=0,down=bits&4~=0,up=bits&8~=0,
  start=bits&16~=0,select=bits&32~=0,b=bits&64~=0,a=bits&128~=0}
end
local function mapped(pc, memory, physical)
 local a=emu.convertAddress(pc)
 return a and a.memType==emu.memType[memory] and a.address==physical
end
local function native(pc, bank) return mapped(pc,'nesPrgRom',bank*8192+(pc&8191)) end
local function private(pc) return mapped(pc,'nesWorkRam',3*8192+(pc&8191)) end
local function stackReturn(s)
 local sp=s['cpu.sp']
 return (read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535,(sp+2)&255
end
local function hook(pc, predicate, name, fn)
 emu.addMemoryCallback(guarded(name,function()
  if not predicate(pc) then return end
  calls[name]=(calls[name] or 0)+1
  fn(emu.getState())
 end),emu.callbackType.exec,pc)
end
local function onReturn(s, label, before, action)
 local pc,sp=stackReturn(s)
 assert(#pending<16,'Bounded synchronous returns')
 pending[#pending+1]={pc=pc,sp=sp,label=label,before=before,action=action}
 if not returns[pc] then
  returns[pc]=true
  emu.addMemoryCallback(guarded('return '..string.format('%04x',pc),function()
   local cpu=emu.getState()
   for i=#pending,1,-1 do
    local q=pending[i]
    if q.pc==cpu['cpu.pc'] and q.sp==cpu['cpu.sp'] then
     table.remove(pending,i); q.action(q.before,cpu)
    end
   end
  end),emu.callbackType.exec,pc)
 end
end
local function solid(x,y)
 if x<0 or x>=65536 or y<32 or y>=240 then return false end
 local at=0x300+((x>>8)&1)*208+((y-32)//16)*16+((x>>4)&15)
 return read(L.MTileAttribute+read(at))&1~=0
end
local function common(s)
 assert(r('SelectedCharacter')==22 and r('FfVariant')==variant,'Wrong owner/class')
 assert(r('CheatStartLevel')==0 and r('CheatInvincible')==0,'Unexpected cheats')
 assert(s.lives==2,'Lost a life')
 assert(r('PlayerOutlinesOff')==1,'Natural cold extra-outline option changed')
 assert(s.world==0 and (s.level==0 or s.level==1),'Unexpected world/level')
end
local function validateGroup(index)
 local q=groups[index]
 assert(q.birth and q.collected and q.recovered and q.freeze and q.ticks==60,'Incomplete earned pickup/freeze')
 assert(q.first_tick.freeze_age==0 and q.last_tick.freeze_age==59,'Freeze ages0..59')
 assert(q.last_return.engine==8 and q.last_return.active==0 and q.last_return.timer==0,'Freeze did not recover')
 local expected=variant<2 and {0x16,0x30,0x36} or {0x28,0x18,0x21}
 q.palette={}
 for i=1,3 do
  q.palette[i]=emu.read(0x3f10+i,emu.memType.nesPpuDebug)
  assert(q.palette[i]==expected[i],'Actual earned body palette')
 end
end
local function enterPhase(name)
 phase=name; step=0; setPad(0); note('phase_'..name)
end
local function requestFinish(ok, why)
 assert(not requestedFinish,'Single completion request')
 requestedFinish={ok=ok,why=why}; setPad(0)
 if wantImages and #imageTags+#imageQueue<2 then imageQueue[#imageQueue+1]=ok and 'terminal' or 'failure' end
end
local function drive()
 if not gameplay or requestedFinish then return end
 for _=1,4 do -- Phase boundaries consume no extra artificial native update.
  local s=state(); common(s)
  local a=actors(); local bits=0; local transition=false
  desiredJumpReason=nil
  local item=nil
  for _,v in ipairs(a) do if v.flag==1 and v.id==46 then item=v; break end end
  collectSlot=item and item.slot or 5
  if phase=='mushroom' then
   assert(step<1800,'Mushroom controller bound')
   if active(s) then
    assert(s.level==0 and r('AreaAddrsLOffset')==5,'First mushroom area')
    if not firstCold then
     firstCold=s; assert(s.x==40 and s.power==0 and s.charges==0,'Fresh natural1-1 state')
     local nonzero=false; for at=0x300,0x49f do if read(at)~=0 then nonzero=true;break end end
     assert(nonzero,'Native stage parser did not populate buffers'); note('active_1_1',s)
     if wantImages then imageQueue[#imageQueue+1]='active_1_1' end
    end
    local q=groups[1]
    if q.collected then
     assert(s.power==1 and s.earned==1 and s.charges==(variant==1 and 1 or 0),'Earned mushroom state')
     assert(s.active==0 and s.timer==0,'Mushroom freeze still active')
     q.recovered=q.recovered or s; bits=1
     if s.x>=q.recovered.x+16 then validateGroup(1); enterPhase('flower'); transition=true end
    elseif item then
     q.birth=q.birth or {player=s,actor=item}; assert(item.kind==0,'Expected natural mushroom')
     local gap=item.x-s.x
     if math.abs(gap)<20 and item.y<s.y-16 and s.state==0 and mushClock-mushJump>45 then mushJump=mushClock end
     bits=(gap>3 and 1 or 0)|(gap< -3 and 2 or 0)|(mushClock-mushJump<23 and 128 or 0)
    elseif opening~='clear' then
     local near=false
     for _,v in ipairs(a) do if v.flag==1 and v.id==6 and v.state<32 and v.x-s.x>=20 and v.x-s.x<=40 then near=true end end
     if opening=='approach' and near and s.state==0 then mushJump=mushClock;opening='hop' end
     if opening=='hop' then
      bits=(s.x<300 and 1 or 0)|(mushClock-mushJump<23 and 128 or 0)
      if mushClock-mushJump>10 and s.state==0 and s.y==176 then opening='clear' end
     else bits=1 end
    else
     local gap=330-s.x
     if math.abs(gap)>2 then bits=gap>0 and 1 or 2
     elseif s.state==0 and mushClock-mushJump>45 then mushJump=mushClock end
     bits=bits|(mushClock-mushJump<23 and 128 or 0)
    end
    if not transition then mushClock=mushClock+1 end
   end
  elseif phase=='flower' then
   assert(step<1100,'Flower controller bound')
   assert(s.level==0 and r('AreaAddrsLOffset')==5,'Flower area')
   local q=groups[2]
   if q.collected and s.engine==8 then
    q.recovered=q.recovered or s
    assert(s.power==2 and s.earned==2 and s.charges==(variant==1 and 3 or 0),'Earned flower state')
    assert(s.active==0 and s.timer==0,'Flower freeze still active')
    bits=1
    if s.x>=q.recovered.x+16 then validateGroup(2); enterPhase('attack'); transition=true end
   elseif s.engine==9 then bits=0
   else
    assert(s.engine==8 and s.power==1 and s.earned==1,'Pre-flower state')
    if item then
     assert(item.kind==1,'Expected natural flower')
     if not flowerBirth then flowerBirth={player=s,actor=item};q.birth=flowerBirth;note('natural_flower',flowerBirth) end
     if step-flowerBirth.player.step<40 then bits=0
     elseif flowerLaunch==nil then
      if s.x>item.x-48 then bits=2
      elseif s.state==0 then flowerLaunch=step;bits=129
      else bits=0 end
     else
      bits=1|(step-flowerLaunch<23 and 128 or 0)
      if step-flowerLaunch>75 and s.state==0 then flowerLaunch=nil end
     end
    elseif s.x<1224 then
     bits=1
     if s.state==0 and step-flowerJump>35 then
      local obstacle=false
      for _,left in ipairs({448,608,736,912}) do
       if left-50<=s.x and s.x<left-3 then obstacle=true;flowerJumped[left]=true;desiredJumpReason='flower-pipe-'..left;break end
      end
      local pit=1074<=s.x and s.x<1136
      local ledge=1150<=s.x and s.x<1200 and s.y>=160
      if obstacle or pit or ledge or (s.x>970 and solid(s.x+25,s.y+24)) then
       desiredJumpReason=desiredJumpReason or (pit and 'flower-pit' or ledge and 'flower-ledge' or 'flower-solid-lookahead')
       bits=bits|128;flowerJump=step
      end
     end
    else
     local gap=1242-s.x;bits=(gap>2 and 1 or 0)|(gap< -2 and 2 or 0)
     if math.abs(gap)<=2 and s.state==0 and step-flowerJump>35 then bits=bits|128;flowerJump=step end
    end
    if not item then
     if s.x>=1224 and s.state==0 and s.y<=112 then flowerRetreat=true end
     if flowerRetreat then
      bits=s.x>1212 and 2 or 0
      if s.x<=1212 and s.state==0 and s.y>=160 then flowerRetreat=false end
     elseif s.x>1140 and s.state==0 and step-flowerJump>35 then
      local near=false
      for _,v in ipairs(a) do if v.flag==1 and v.id==6 and v.state<32 and v.x-s.x>=12 and v.x-s.x<=45 and math.abs(v.y-s.y-8)<24 then near=true end end
      if near then bits=bits|128;flowerJump=step end
     end
    end
   end
  elseif phase=='attack' then
   assert(step<900,'Attack controller bound')
   assert(s.power==2 and s.earned==2 and s.engine==8,'Earned attack state')
   if attackHit then
    assert(committed,'Accepted damage without controller commitment')
    local before,after=attackHit.before.actor,attackHit.after.actor
    local defeated=after.state&32~=0 or after.flag==0
    assert(defeated or after.HP>0,'Invalid native enemy outcome')
    assert(before.HP==0 or after.HP<before.HP,'Native attack did not lower HP')
    attackHit.native_defeated=defeated;note('earned_attack',attackHit)
    enterPhase('stage');transition=true
   else
    local aligned={}
    for _,v in ipairs(a) do
     if v.flag==1 and (v.id==0 or v.id==3 or v.id==6) and v.state<2 and math.abs(v.y-s.y-8)<20 and math.abs(v.x-s.x)<100 then aligned[#aligned+1]=v end
    end
    bits=1
    if committed then
     bits=committed.facing==1 and 1 or 2
     if step-committed.step>75 and s.action==0 then committed=nil end
    elseif #aligned>0 and (variant~=2 or s.state==0) then
     table.sort(aligned,function(x,y) return math.abs(x.x-s.x)<math.abs(y.x-s.x) end)
     local target=aligned[1];local face=target.x>=s.x and 1 or 2
     bits=face
     if math.abs(target.x-s.x)<=(variant==2 and 70 or 26) and s.facing==face then
      bits=bits|64;committed={step=step,facing=face,player=s,actor=target}
     end
    elseif s.state==0 then
     for _,pit in ipairs({{1376,1424},{2448,2480}}) do
      if not attackJumped[pit[1]] and pit[1]-30<=s.x and s.x<pit[2] then bits=bits|128;attackJumped[pit[1]]=true;break end
     end
    end
   end
  elseif phase=='stage' then
   assert(step<4500,'Full-stage controller bound')
   if s.level==1 and active(s) then
    assert(nativeFlag,'Missing actual native flagpole witness')
    active12=s;note('active_1_2',s)
    requestFinish(not expectedStair,expectedStair and 'Unexpected clear in expected original-stair negative' or 'Earned pickups/attack, full native1-1 and active1-2')
    return
   end
   assert(s.earned==2,'Lost earned power before transition')
   routeStart=routeStart or s
   if s.x>bestX then bestX=s.x;advancedAt=step
   elseif s.engine==8 and step-advancedAt>120 then
    if expectedStair then
     assert(rom=='c10b7d87f466bf028096bddd33b7ac2baee242870ee83ccc4eebd529af57bd7f','Original stair negative requires exact c10 runner pin')
     assert(s.x==2225 and s.level==0 and nativeFlag==nil,'Wrong expected stair stall')
     note('expected_original_stair_stall',s);requestFinish(true,'Witnessed expected unchanged-c10 X2225 stair stall');return
    end
    error('Stalled controller at X'..s.x..'/Y'..s.y)
   end
   if s.level==0 and s.engine==8 then
    if cameraPrevious then assert(s.camera>=cameraPrevious,'Backward ordinary camera') end
    cameraPrevious=s.camera;bits=1
    if s.state==0 and step-stageJump>5 then
     local near=false
     for _,v in ipairs(a) do if v.flag==1 and v.id<21 and v.state<2 and v.x-s.x>=0 and v.x-s.x<=60 and math.abs(v.y-s.y-8)<24 then near=true end end
     local foot=s.y+32
     local wall=solid(s.x+18,foot-1) or solid(s.x+30,foot-1) or solid(s.x+42,foot-1)
     local ledge=not solid(s.x+30,foot+1)
     if near or wall or ledge then
      bits=bits|128;stageJump=step
      assert(#jumps<128,'Bounded jump events');jumps[#jumps+1]={reason=near and 'enemy' or wall and 'wall' or 'ledge',player=s}
     end
    end
    if step==0 and s.state==0 then bits=bits|128;stageJump=step end
   end
  else error('Unknown gameplay phase '..phase) end
  if not transition then setPad(bits);step=step+1;return end
 end
 error('Unexpected repeated phase transitions')
end

local function capturePhysics(before, after)
 if not gameplay or before.level~=0 or after.level~=0 or before.engine~=8 or after.engine~=8 then return end
 physics.ordinary_loops=physics.ordinary_loops+1
 local dx,dc=after.x-before.x,after.camera-before.camera
 physics.max_world_step=math.max(physics.max_world_step,dx)
 physics.min_world_step=math.min(physics.min_world_step,dx)
 physics.min_camera_step=math.min(physics.min_camera_step,dc)
 local key=tostring(dc);physics.camera_deltas[key]=(physics.camera_deltas[key] or 0)+1
 if dc>physics.max_camera_step then
  physics.max_camera_step=dc
  if #physics.extrema<12 then physics.extrema[#physics.extrema+1]={delta=dc,before=before,after=after} end
 end
end
local function install()
 assert(variant and variant%1==0 and variant>=0 and variant<=3,'SMB_TEST_VARIANT must be0..3')
 assert(#rom==64 and not rom:find('[^0-9a-f]'),'SMB_STDOUT_ROM_SHA must be exact lower-case SHA256 bound by root')
 if expectedStair then assert(rom=='c10b7d87f466bf028096bddd33b7ac2baee242870ee83ccc4eebd529af57bd7f','Expected-stall pin') end
 hook(0x82d9,function(pc) return native(pc,126) end,'GameLoop',function(cpu)
  assert(read(0x82d9)==0xa9 and read(0x82da)==0xff and read(0x82db)==0x8d,'Actual native Main opcode')
  assert(not mainLive,'Synchronous native Main ownership')
  updates=updates+1;assert(updates<=6000,'Logical Main bound6000')
  local ret,sp=stackReturn(cpu)
  assert(ret==0x82be or ret==0x82d0,'Actual native IdleLoop/catch-up caller')
  mainLive={ret=ret,sp=sp,before=state()}
  if ret==0x82d0 then cadence.catchup_updates=cadence.catchup_updates+1 end
 end)
 for _,pc in ipairs({0x82be,0x82d0}) do
  hook(pc,function(at) return native(at,126) end,'GameLoopReturn',function(cpu)
   if not mainLive or cpu['cpu.sp']~=mainLive.sp or cpu['cpu.pc']~=mainLive.ret then return end
   local before=mainLive.before;mainLive=nil;completed=completed+1
   capturePhysics(before,state());drive()
  end)
 end
 hook(0xbb60,private,'FfHostCollect',function(cpu)
  if not gameplay then return end
  local before={player=state(),slot=collectSlot,actor=actor(collectSlot)}
  onReturn(cpu,'collect',before,function(q,returned)
   local s=state()
   if s.active~=0 then
    local g=assert(groups[s.power],'Unexpected collected power')
    assert(not g.collected,'Duplicate tier collection')
    local p=returned['cpu.ps'] or returned['cpu.p'];assert(p and p&1~=0,'Native collector carry')
    assert(r('Square2SoundQueue')==0x20,'Native pickup sound')
    assert(r('Enemy_Flag',q.slot)==0 and r('FloateyNum_Control',q.slot)==6,'Native collector erase/floaty')
    g.collected={player=s,actor=q.actor,carry=true,sound=0x20,erased_flag=0,floaty=6}
    note('tier'..s.power..'_collected',g.collected)
   end
  end)
 end)
 hook(0xbc1d,private,'FfHostBeginFreeze',function()
  if gameplay then local g=assert(groups[read(0x5fc5)],'Freeze tier');assert(not g.freeze,'Duplicate freeze');g.freeze=state() end
 end)
 hook(0xbc40,private,'FfHostPowerupTick',function(cpu)
  if not gameplay or r('GuestPowerupActive')==0 then return end
  local g=assert(groups[read(0x5fc5)],'Tick tier');local s=state()
  assert(g.ticks<60 and s.freeze_age==g.ticks and s.engine==9 and s.active==1,'Exact earned freeze clock')
  g.ticks=g.ticks+1;g.first_tick=g.first_tick or s;g.last_tick=s
  onReturn(cpu,'tick',{group=g,last=g.ticks==60},function(q)
   local after=state();q.group.last_return=after
   if q.last then assert(after.engine==8 and after.active==0 and after.timer==0,'Last freeze return')
   else assert(after.engine==9 and after.active==1 and after.timer==255,'Intermediate freeze return') end
  end)
 end)
 hook(0xb7ae,private,'FfHostDamage',function(cpu)
  if not gameplay or phase~='attack' then return end
  local slot=cpu['cpu.x'];assert(slot and slot<6,'Native damage slot')
  local a=actor(slot);local s=state();local attackSlot=read(0x5c0f)
  local q={player=s,actor=a,damage=read(0x5c15),attack_slot=attackSlot}
  assert(q.damage==damage[variant+1],'Earned class damage')
  assert(a.flag==1 and (a.id==0 or a.id==3 or a.id==6) and a.state<2,'Naturally streamed damage target')
  if attackSlot~=255 then
   assert(attackSlot==0 or attackSlot==12 or attackSlot==24,'Source projectile slot')
   local base=0x5c1c+attackSlot;q.projectile={kind=read(base),tier=read(base+10)}
  end
  if variant==2 then assert(q.projectile and q.projectile.kind==1 and q.projectile.tier==2,'Earned Black Fire')
  else assert(attackSlot==255 and s.action==1,'Original FF melee') end
  onReturn(cpu,'damage',q,function(before,returned)
   local p=returned['cpu.ps'] or returned['cpu.p'];assert(p,'Actual native return flags')
   if p&1~=0 then attackHit={before=before,after={player=state(),actor=actor(before.actor.slot)}} end
  end)
 end)
 hook(0xaacc,private,'FfMovementSavedInput',function()
  if not gameplay or not activeJump then return end
  assert(read(0xaacc)==0xa5 and read(0xaacd)==0xdc,'Original FfMovement SavedJoypadBits read')
  local q=activeJump
  if #q.source_reads<6 then q.source_reads[#q.source_reads+1]=jumpSample('source-SavedJoypadBits-read')end
 end)
 hook(0xab6d,private,'FfOriginalJumpAccepted',function()
  if not gameplay or not activeJump then return end
  assert(read(0xab6d)==0xa9 and read(0xab6e)==1,'Original source ground jump acceptance')
  assert(r('FfFresh')&128~=0 and r('Player_State')==0,'Actual fresh source ground A acceptance')
  local q=activeJump
  assert(not q.accepted,'One source acceptance per request')
  q.accepted=jumpSample('source-ground-A-accepted');q.accepted_Main=updates;q.status='hold'
  if phase=='flower'and q.accepted.x>=540 and q.accepted.x<=640 then jumpImage('pipe608_source_jump_takeoff')end
 end)
 hook(0xadd8,private,'FfInjuryStart',function() if gameplay then error('Natural injury before full-stage qualification') end end)
 hook(0x97d6,function(pc) return native(pc,126) end,'KillPlayer',function() if gameplay then error('Native death') end end)
 for _,h in ipairs({{0x8651,126,'FlagpoleRoutine'},{0x9e47,126,'FlagpoleCollision'}}) do
  hook(h[1],function(pc) return native(pc,h[2]) end,h[3],function()
   local s=state()
   if gameplay and not nativeFlag and s.engine==4 and s.x>=3000 then nativeFlag=s;note('native_flagpole',s) end
  end)
 end
 for _,h in ipairs({{0xb900,'FfHostMovement'},{0xb9fe,'FfHostFeet'},{0xba1e,'FfHostSide'},
                     {0xba4c,'FfHostWall'},{0xba9d,'FfHostAfterTerrain'},{0xb620,'FfCornerHeadRead'}}) do
  hook(h[1],private,h[2],function() end)
 end
 hook(0xb988,private,'FfHostHead',function(cpu)
  if not gameplay or phase~='stage' or #headSamples>=12 then return end
  local s=state();if s.x<2180 or s.x>2260 then return end
  local q={before=s,previous_body_x=read(0x5c48)+256*read(0x5c49)}
  headSamples[#headSamples+1]=q
  onReturn(cpu,'head',q,function(before) before.after=state() end)
 end)
 hook(0x9b5b,function(pc) return native(pc,126) end,'PlayerBGCollision',function() end)
 hook(0xa040,function(pc) return native(pc,1) end,'PlayerEntrance',function() end)
 hook(0xa24a,function(pc) return native(pc,1) end,'EnterSidePipe',function() end)
 emu.addMemoryCallback(guarded('entrance priority',function(_,value)
  if not gameplay or r('LevelNumber')~=1 or r('GameEngineSubroutine')~=7 then return end
  local old=r('Player_SprAttrib')
  if (old~value)&0x20~=0 and #priority<128 then
   local cpu=emu.getState();local a=emu.convertAddress(cpu['cpu.pc'])
   priority[#priority+1]={old=old,new=value,state=state(),pc=cpu['cpu.pc'],
    mapped=a and a.address or -1,memory=a and tostring(a.memType) or 'unmapped'}
  end
 end),emu.callbackType.write,L.Player_SprAttrib)
 emu.addEventCallback(guarded('inputPolled',function()
  polls=polls+1
  if activeJump and not activeJump.first_poll then activeJump.first_poll=jumpSample('inputPolled-delivery')end
  emu.setInput(buttons(padBits),0)
 end),emu.eventType.inputPolled)
end

-- These two native addresses are read-only constants from the same bundle.
L.Square2SoundQueue=0x104
L.FloateyNum_Control=0x10d
local function frames(n) for _=1,n do coroutine.yield() end end
local function press(bits) setPad(bits);frames(4);setPad(0);frames(8) end
local function ready(predicate)
 for _=1,900 do if predicate() then return end;coroutine.yield() end
 error('Natural title/menu/gameplay readiness timeout')
end
local task=coroutine.create(function()
 ready(function() return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end)
 press(16)
 ready(function() return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end)
 assert(r('CrossoverMenuIndex')==0,'Natural menu initial index')
 for _,bits in ipairs({4,4,1,1,1,1,1}) do press(bits) end
 assert(r('CrossoverMenuIndex')==21 and r('SelectedCharacter')==22 and r('FfVariant')==0,'Natural slot21 FF')
 for _=1,variant do press(32) end
 assert(r('FfVariant')==variant,'Actual menu Select class')
 note('class_selected',{variant=variant,index=r('CrossoverMenuIndex'),owner=r('SelectedCharacter')})
 press(16)
 ready(function() return active(state()) end)
 gameplay=true;enterPhase('mushroom');drive()
 -- Gameplay is driven only by actual native Main completion callbacks.
 while not stopped do coroutine.yield() end
end)
local alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
local function base64(bytes)
 local out={}
 for i=1,#bytes,3 do
  local a,b,c=bytes:byte(i),bytes:byte(i+1),bytes:byte(i+2)
  local n=(a<<16)|((b or 0)<<8)|(c or 0)
  out[#out+1]=alphabet:sub((n>>18)+1,(n>>18)+1)
  local j=(n>>12)&63;out[#out+1]=alphabet:sub(j+1,j+1)
  j=(n>>6)&63;out[#out+1]=b and alphabet:sub(j+1,j+1) or '='
  j=n&63;out[#out+1]=c and alphabet:sub(j+1,j+1) or '='
 end
 return table.concat(out)
end
guarded('setup',function()
 install()
 emu.addEventCallback(guarded('endFrame',function()
  frame=frame+1;assert(frame<=12000,'Physical frame bound12000')
  local count=completed-previousCompleted
  cadence.maximum_updates_per_frame=math.max(cadence.maximum_updates_per_frame,count)
  if gameplay then
   cadence.gameplay_physical_frames=cadence.gameplay_physical_frames+1
   if count==0 then cadence.gameplay_zero_update_frames=cadence.gameplay_zero_update_frames+1 end
   if polls==previousPolls then cadence.physical_frames_without_input_poll=cadence.physical_frames_without_input_poll+1 end
  end
  previousCompleted=completed;previousPolls=polls
  while #imageQueue>0 do
   local tag=table.remove(imageQueue,1)
   assert(#imageTags<2,'At most two stdout PNGs')
   local png=emu.takeScreenshot();assert(type(png)=='string' and png:sub(1,8)=='\137PNG\r\n\26\n','Actual in-memory PNG')
   imageTags[#imageTags+1]={tag=tag,frame=frame,bytes=#png}
   print('SMB_NATIVE_IMAGE '..base64(png))
  end
  if requestedFinish then finish(requestedFinish.ok,requestedFinish.why);return end
  local ok,why=coroutine.resume(task)
  assert(ok,why)
 end),emu.eventType.endFrame)
end)()
