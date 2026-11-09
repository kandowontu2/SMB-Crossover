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
 local f=assert(io.open(OUTPUT..'result.json','w'))
 f:write(json({passed=not not passed,reason=reason,ROM_sha256=C.sha,controller_only=true,
  no_cheats=noCheats(),first_active=firstActive,native_first_goomba=constructor,
  issued_forward_B=launch,actual_fresh_forward_B=fresh,source_capture=capture,
  native_erase_return=erased,injury=injury,terminal=last,menu_events=events})..'\n')
 f:close()
 local image=assert(io.open(OUTPUT..'terminal.png','wb'))
 image:write(emu.takeScreenshot());image:close()
 print('Kirby 29aa first inhale '..reason..' X='..last.x)
 emu.stop(passed and 0 or 1)
end
local function hook(name,callback)
 local h=assert(C.hooks[name])
 emu.addMemoryCallback(function()
  if finished or not (active() and identity() and stage()) then return end
  local mapped=emu.convertAddress(h.pc)
  if not mapped or mapped.memType~=emu.memType.nesPrgRom or mapped.address~=h.offset then return end
  for i,b in ipairs(h.bytes) do
   assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==b,'Exact native hook '..name)
  end
  callback(emu.getState()['cpu.x'])
 end,emu.callbackType.exec,h.pc)
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
 if not fresh or slot~=constructor.slot or a.flag~=1 or a.id~=6 or a.state>=2 or
    gap<0 or gap>12 or r('KbAction')~=1 or r('KbActionAge')~=0 or r('KbMouth')~=0 or
    r('PlayerFacingDir')~=1 or r('SavedJoypadBits')&0x43~=0x41 then
  finish('unexpected-capture-ingress');return
 end
 capture={player=player(),target=a,gap=gap,input=r('SavedJoypadBits')}
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

emu.addEventCallback(function()
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
      gap>=34 and gap<=56 then
    launch={player=player(),target=a,gap=gap}
    input.b=true
   end
  end
 end
 emu.setInput(input,0)
end,emu.eventType.inputPolled)

emu.addEventCallback(function()
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
end,emu.eventType.endFrame)
