local C={["menu"]={"left","right","right","right","down","left","left","left","left","right","right","right","","left","left","left","left","right","right","right","up","left","left","left","left","right","right","right","up","left","left","left"},["slot"]=12,["hooks"]={["capture"]={["pc"]=41727,["offset"]=606975,["bytes"]={181,23,24,105,1,141,10,92,173,29,92,141,134}},["inhale"]={["pc"]=41454,["offset"]=606702,["bytes"]={173,11,92,201,5,208,3,76,55}},["erased"]={["pc"]=41754,["offset"]=607002,["bytes"]={169,0,141,11,92}},["init"]={["pc"]=46910,["offset"]=63294,["bytes"]={32,46,183,76,103,183}},["injury"]={["pc"]=42669,["offset"]=591533,["bytes"]={173,22,92}}},["sha"]="c8bd2e2c75015b84fe7bc3c4dba5b24b87e517620ef914ff229b5d4249acbe48",["ram"]={["AreaAddrsLOffset"]=1876,["AreaType"]=1875,["CheatInvincible"]=32763,["CheatStartLevel"]=32764,["CrossoverBehaviorVersion"]=32737,["CrossoverMenuIndex"]=29449,["CrossoverMenuState"]=29447,["CrossoverTitleDrawn"]=24580,["DisableScreenFlag"]=1909,["Enemy_Flag"]=16,["Enemy_ID"]=23,["Enemy_PageLoc"]=93,["Enemy_State"]=31,["Enemy_X_Position"]=118,["Enemy_Y_HighPos"]=165,["Enemy_Y_Position"]=190,["GameEngineSubroutine"]=15,["InjuryTimer"]=1947,["KbAction"]=23563,["KbActionAge"]=23564,["KbCopy"]=23553,["KbFresh"]=23557,["KbHealth"]=23552,["KbHurt"]=23574,["KbMouth"]=23562,["KbMouthCopy"]=23686,["KbVariant"]=24553,["LevelNumber"]=1889,["NumberofLives"]=1887,["OperMode"]=1905,["OperMode_Task"]=1907,["PlayerFacingDir"]=1342,["Player_PageLoc"]=92,["Player_State"]=30,["Player_X_Position"]=117,["Player_Y_Position"]=189,["SavedJoypadBits"]=220,["ScreenRight_PageLoc"]=1822,["ScreenRight_X_Pos"]=1824,["SelectedCharacter"]=24578,["TimerControl"]=1866,["WorldNumber"]=1892}}
C.parent_observer_ROM=C.sha
C.sha=assert(os.getenv('SMB_STDOUT_ROM_SHA'),'Runner must bind exact ROM')
local gapMode=tonumber(os.getenv('SMB_TEST_VARIANT') or '0')
-- v2 keeps the close-startup assertion and restores the original medium-range age0 observer.
local lastIngress
local gapLo,gapHi=10,16
if gapMode==1 then gapLo,gapHi=34,56 elseif gapMode==2 then gapLo,gapHi=11,14 end
-- Normal inputs only. Stop after the first real mouth capture and enemy erase.
local frame,polls,age=0,0,0
local buttons,events={},{}
local firstActive,constructor,launch,fresh,capture,erased,injury
local menuDone,finished=false,false

local function r(name,index)
 return emu.read(assert(C.ram[name],name)+(index or 0),emu.memType.nesDebug)
end
local function pos(lo,hi,index) return r(lo,index)+256*r(hi,index) end
local function x() return pos('Player_X_Position','Player_PageLoc') end
local function active() return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function stage() return r('WorldNumber')==0 and r('LevelNumber')==0 and r('AreaType')==1 and r('AreaAddrsLOffset')==5 end
local function noCheats() return r('CheatStartLevel')==0 and r('CheatInvincible')==0 end
local function identity()
 return r('SelectedCharacter')==13 and r('KbVariant')==0 and r('CrossoverBehaviorVersion')==0 and noCheats()
end
local function player()
 return {frame=frame,poll=polls,x=x(),y=r('Player_Y_Position'),state=r('Player_State'),
         hp=r('KbHealth'),lives=r('NumberofLives'),copy=r('KbCopy'),mouth=r('KbMouth'),
         mouth_copy=r('KbMouthCopy'),injury_timer=r('InjuryTimer'),engine=r('GameEngineSubroutine'),
         world=r('WorldNumber')+1,level=r('LevelNumber')+1}
end
local function actor(slot)
 return {slot=slot,x=pos('Enemy_X_Position','Enemy_PageLoc',slot),y=r('Enemy_Y_Position',slot),
         y_high=r('Enemy_Y_HighPos',slot),flag=r('Enemy_Flag',slot),id=r('Enemy_ID',slot),
         state=r('Enemy_State',slot),frame=frame}
end
local function json(v)
 if type(v)=='string' then return string.format('%q',v) end
 if type(v)~='table' then return tostring(v) end
 local rows={}
 if #v>0 then
  for i,a in ipairs(v) do rows[i]=json(a) end
  return '['..table.concat(rows,',')..']'
 end
 for k,a in pairs(v) do rows[#rows+1]=json(k)..':'..json(a) end
 table.sort(rows)
 return '{'..table.concat(rows,',')..'}'
end
local function finish(reason)
 if finished then return end
 finished=true
 local last=player()
 local passed=reason=='natural-first-inhale' and firstActive and constructor and launch and fresh and capture and erased
    and not injury and identity() and active() and stage() and last.hp==6 and last.lives==2
    and last.mouth==7 and last.mouth_copy==1 and last.copy==0
 print('SMB_NATIVE_RECEIPT '..json({passed=not not passed,reason=reason,ROM_SHA256=C.sha,
  parent_observer_ROM=C.parent_observer_ROM,controller_only=true,script_RAM_writes=false,
  output_files=0,physical_frames=frame,input_polls=polls,gap_mode=gapMode,
  requested_gap={gapLo,gapHi},last_capture_ingress=lastIngress,no_cheats=noCheats(),first_active=firstActive,native_first_goomba=constructor,
  issued_forward_B=launch,actual_fresh_forward_B=fresh,source_capture=capture,
  native_erase_return=erased,injury=injury,terminal=last,menu_events=events}))
 emu.stop(passed and 0 or 1)
end
local function guarded(fn)
 return function(...)
  if finished then return end
  local ok,why=pcall(fn,...)
  if not ok then finish('callback-error:'..tostring(why)) end
 end
end
local function hook(name,callback)
 local h=assert(C.hooks[name])
 emu.addMemoryCallback(guarded(function()
  if finished or not (active() and identity() and stage()) then return end
  local mapped=emu.convertAddress(h.pc)
  if not mapped or mapped.memType~=emu.memType.nesPrgRom or mapped.address~=h.offset then return end
  for i,b in ipairs(h.bytes) do
   assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==b,'Exact native hook '..name)
  end
  callback(emu.getState()['cpu.x'])
 end),emu.callbackType.exec,h.pc)
end

hook('init',function(slot)
 local a=actor(slot)
 if a.id==6 and a.x==352 and a.flag==1 and a.y_high==1 and not constructor then constructor=a end
end)
hook('inhale',function()
 if not launch or fresh or r('SavedJoypadBits')&0x43~=0x41 or r('KbFresh')&0x40==0 then return end
 fresh={player=player(),target=actor(constructor.slot),input=r('SavedJoypadBits'),
        fresh_bits=r('KbFresh'),prior_action=r('KbAction'),facing=r('PlayerFacingDir')}
 if fresh.prior_action~=0 or fresh.facing~=1 or fresh.target.flag~=1 or fresh.target.id~=6 then
  finish('unexpected-fresh-inhale-state')
 end
end)
hook('capture',function(slot)
 local a=actor(slot)
 local gap=a.x-x()
 lastIngress={player=player(),target=a,gap=gap,action=r('KbAction'),age=r('KbActionAge'),
  fresh_frame=fresh and fresh.player.frame or -1}
 if not fresh or slot~=constructor.slot or a.flag~=1 or a.id~=6 or a.state>=2 or
    gap<0 or gap>12 or r('KbAction')~=1 or not (
      (gapMode==0 and r('KbActionAge')>0 and r('KbActionAge')<=8 and frame-fresh.player.frame<=2) or
      (gapMode==1 and r('KbActionAge')==0) or
      (gapMode==2 and r('KbActionAge')<=8 and frame-fresh.player.frame<=2)) or r('KbMouth')~=0 or
    r('PlayerFacingDir')~=1 or r('SavedJoypadBits')&0x43~=0x41 then
  finish('unexpected-capture-ingress');return
 end
 capture={player=player(),target=a,gap=gap,input=r('SavedJoypadBits'),action_age=r('KbActionAge'),
          frames_since_fresh=frame-fresh.player.frame}
end)
hook('erased',function(slot)
 if not capture or slot~=capture.target.slot or r('Enemy_Flag',slot)~=0 or r('Enemy_ID',slot)~=0 or
    r('KbMouth')~=7 or r('KbMouthCopy')~=1 then
  finish('unexpected-erase-return');return
 end
 erased={player=player(),target=actor(slot)}
end)
hook('injury',function() if firstActive and not injury then injury=player() end end)

local function wait(n) coroutine.yield(n) end
local function press(key)
 buttons={[key]=true};wait(2);buttons={};wait(8)
end
local function ready(predicate,limit,name)
 local start=frame
 while not predicate() and frame-start<limit do wait(1) end
 assert(predicate(),'Actual frontend '..name)
end
local menu=coroutine.create(function()
 ready(function()return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end,250,'title')
 assert(r('CrossoverBehaviorVersion')==0 and noCheats(),'Cold default Easy without cheats')
 press('start')
 ready(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end,180,'roster')
 for _=1,16 do
  local slot=r('CrossoverMenuIndex')
  if slot==C.slot then break end
  local direction=assert(C.menu[slot+1],'Bound roster slot')
  assert(direction~='','Only Kirby is the terminal menu route')
  press(direction)
 end
 assert(r('CrossoverMenuIndex')==C.slot and identity(),'Actual Easy Kirby selection')
 events[1]={frame=frame,slot=C.slot,raw=r('SelectedCharacter'),variant=r('KbVariant'),difficulty=r('CrossoverBehaviorVersion')}
 press('start');menuDone=true
end)

emu.addEventCallback(guarded(function()
 polls=polls+1
 local input=buttons
 if firstActive and not finished then
  input={right=true}
  if erased then input={}
  elseif launch then input.b=true
  elseif constructor then
   local a=actor(constructor.slot)
   local gap=a.x-x()
   local visible=a.x<=pos('ScreenRight_X_Pos','ScreenRight_PageLoc')
   if a.flag==1 and a.id==6 and a.state<2 and visible and r('PlayerFacingDir')==1 and
      r('Player_State')==0 and a.y_high==1 and math.abs(a.y-r('Player_Y_Position')-8)<=12 and
      gap>=gapLo and gap<=gapHi then
    launch={player=player(),target=a,gap=gap}
    input.b=true
   end
  end
 end
 emu.setInput(input,0)
end),emu.eventType.inputPolled)

emu.addEventCallback(guarded(function()
 frame=frame+1
 if not menuDone then
  if age>0 then age=age-1;return end
  local ok,n=coroutine.resume(menu);assert(ok,n);age=n or 0
  return
 end
 if not firstActive and active() and stage() and identity() and r('TimerControl')==0 then
  firstActive=player()
  if firstActive.hp~=6 or firstActive.lives~=2 or firstActive.copy~=0 or firstActive.mouth~=0 then
   finish('unexpected-cold-player');return
  end
 end
 if firstActive then
  if injury or r('KbHurt')~=0 or r('InjuryTimer')~=0 or r('KbHealth')~=6 or r('NumberofLives')~=2 or
     not (active() and stage() and identity()) then
   finish('injury-or-stage-change');return
  end
  if erased and frame>=erased.player.frame+2 then finish('natural-first-inhale');return end
  if x()>=400 then finish('passed-first-encounter-without-capture');return end
 end
 if frame>=1600 then finish('bounded-first-encounter-timeout') end
end),emu.eventType.endFrame)
