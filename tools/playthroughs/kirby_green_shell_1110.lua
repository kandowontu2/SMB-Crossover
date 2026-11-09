-- Normal controls through native 1-1. Stop after one earned green-shell defeat.
local frame,polls,age=0,0,0
local buttons,events={},{}
local menuDone,finished,lastA=false,false,false
local firstActive,koopa,inhaleInput,inhaleFresh,capture,erased,swallow
local shotInput,attack,contact,defeat,hit,combatInjury,failure
local births,checkpoints={},{}
local maxX,nextCheckpoint=0,256
local approachHP
ROSTER_CONFIG={name='kirby'}
local route=assert(dofile(C.policy))

-- FIRST-INHALE HELPERS

local function shot(slot)
 return {slot=slot,x=pos('KbShotX','KbShotPage',slot),y=r('KbShotY',slot),age=r('KbShotAge',slot),
         type=r('KbShotType',slot),kind=r('KbShotKind',slot),vx_hi=r('KbShotVXHi',slot),vx_lo=r('KbShotVXLo',slot)}
end
local function finish(reason)
 if finished then return end
 finished=true
 local last=player()
 local passed=reason=='natural-green-shell-hit' and koopa and inhaleInput and inhaleFresh and capture and erased
    and swallow and shotInput and attack and contact and defeat and hit and not combatInjury
    and active() and identity() and stage() and last.copy==2 and last.lives==2 and last.hp==approachHP
    and r('KbShotType',hit.shell.slot)==0
 local f=assert(io.open(OUTPUT..'result.json','w'))
 f:write(json({passed=not not passed,reason=reason,ROM_sha256=C.sha,controller_only=true,
  no_cheats=noCheats(),first_active=firstActive,max_x=maxX,checkpoints=checkpoints,menu_events=events,
  native_green_koopa=koopa,issued_inhale=inhaleInput,actual_fresh_inhale=inhaleFresh,
  capture=capture,native_erase_return=erased,actual_down_swallow=swallow,issued_shot=shotInput,
  actual_ground_copy_attack=attack,shell_contact=contact,native_defeat_entry=defeat,native_defeat_return=hit,
  injury_at_encounter=combatInjury,terminal=last})..'\n')
 f:close()
 local image=assert(io.open(OUTPUT..'terminal.png','wb'))
 image:write(emu.takeScreenshot());image:close()
 print('Kirby 29aa green-shell '..reason..' X='..last.x)
 emu.stop(passed and 0 or 1)
end
local function hook(name,callback)
 local h=assert(C.hooks[name])
 emu.addMemoryCallback(function()
  if finished or failure or not (active() and identity() and stage()) then return end
  local mapped=emu.convertAddress(h.pc)
  if not mapped or mapped.memType~=emu.memType.nesPrgRom or mapped.address~=h.offset then return end
  for i,b in ipairs(h.bytes) do
   assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==b,'Exact native hook '..name)
  end
  callback(emu.getState())
 end,emu.callbackType.exec,h.pc)
end
local function aligned(a)
 return a.flag==1 and a.y_high==1 and math.abs(a.y-r('Player_Y_Position')-8)<=12
end
hook('init',function(s)
 local a=actor(s['cpu.x'])
 births[a.slot]=a
end)
hook('greenInit',function(s)
 local a=actor(s['cpu.x'])
 if not koopa and a.id==0 and a.x==1712 and a.flag==1 and a.y_high==1 then koopa=a end
end)
hook('inhale',function()
 if not inhaleInput or inhaleFresh or r('SavedJoypadBits')&0x43~=0x41 or r('KbFresh')&0x40==0 then return end
 if r('KbCopy')~=0 or r('KbMouth')~=0 or r('KbAction')~=0 or r('PlayerFacingDir')~=1 then
  failure='unexpected-fresh-inhale-state';return
 end
 inhaleFresh={player=player(),input=r('SavedJoypadBits'),fresh=r('KbFresh'),target=actor(koopa.slot)}
end)
hook('capture',function(s)
 if not inhaleInput or capture then return end
 local a=actor(s['cpu.x'])
 local gap=a.x-x()
 if not inhaleFresh or a.slot~=koopa.slot or a.id~=0 or not aligned(a) or a.state~=0 or
    gap<0 or gap>12 or r('KbAction')~=1 or r('KbActionAge')~=0 or
    r('PlayerFacingDir')~=1 or r('SavedJoypadBits')&0x43~=0x41 then
  failure='unexpected-green-capture';return
 end
 capture={player=player(),target=a,gap=gap}
end)
hook('erased',function()
 if not capture or erased then return end
 local a=actor(capture.target.slot)
 if a.flag~=0 or a.id~=0 or r('KbMouth')~=1 or r('KbMouthCopy')~=2 then
  failure='unexpected-green-erase-return';return
 end
 erased={player=player(),target=a}
end)
hook('swallow',function()
 if not erased or swallow then return end
 if r('SavedJoypadBits')&4==0 or r('KbMouth')~=1 or r('KbMouthCopy')~=2 or r('KbCopy')~=0 then
  failure='unexpected-green-swallow-ingress';return
 end
 swallow={player=player(),input=r('SavedJoypadBits')}
end)
hook('attack',function()
 if not shotInput or attack then return end
 if r('KbCopy')~=2 or r('SavedJoypadBits')&64==0 or r('Player_State')~=0 or
    r('Player_Y_Position')~=176 or r('PlayerFacingDir')~=1 then
  failure='unexpected-green-shot-ingress';return
 end
 attack={player=player(),input=r('SavedJoypadBits'),facing=r('PlayerFacingDir')}
end)
hook('contact',function(s)
 if not attack or hit then return end
 local a=actor(s['cpu.x'])
 local born=births[a.slot]
 local p=shot(r('KbSavedSlot'))
 if p.type~=3 or p.kind~=2 then return end
 if a.id~=6 or a.state~=0 or a.flag~=1 or a.y_high~=1 or a.y~=184 or not born or
    born.id~=6 or born.x<1750 or born.x>2100 or p.vx_hi~=4 or p.vx_lo~=0 or
    math.abs(p.x-a.x)>12 or math.abs(p.y-a.y)>12 then
  failure='unexpected-green-shell-contact';return
 end
 contact={player=player(),target=a,native_goomba=born,shell=p}
end)
hook('defeat',function(s)
 if not contact or defeat then return end
 local sp=s['cpu.sp']
 local function stack(i) return emu.read(256+((sp+i)&255),emu.memType.nesDebug) end
 if stack(1)+256*stack(2)+1~=C.hooks.consumed.pc or s['cpu.x']~=contact.target.slot or
    r('ObjectOffset')~=contact.target.slot then failure='unexpected-native-defeat-caller';return end
 defeat={frame=frame,slot=s['cpu.x'],return_pc=C.hooks.consumed.pc}
end)
hook('consumed',function()
 if not defeat or hit then return end
 local a=actor(defeat.slot)
 if a.id~=6 or a.state&0x20==0 or r('KbShotType',contact.shell.slot)~=3 then
  failure='unexpected-native-defeat-return';return
 end
 hit={player=player(),target=a,shell=shot(contact.shell.slot)}
end)
hook('injury',function() if inhaleInput and not combatInjury then combatInjury=player() end end)

-- FIRST-INHALE MENU

local function nextEnemy(origin)
 local nearest
 for slot=0,5 do
  local a=actor(slot)
  local dx=a.x-origin
  if a.flag>0 and a.flag<128 and (a.id<0x15 or a.id==0x2d or a.id==0x33) and a.state<32 and
     not(a.id==6 and a.state>=2) and dx>-160 and dx<160 and (not nearest or math.abs(dx)<math.abs(nearest.dx)) then
   a.dx=dx;nearest=a
  end
 end
 return nearest
end
local function routeInput()
 local c={frame=frame,poll=polls,char=13,variant=0,r=r,x=x(),y=r('Player_Y_Position'),
          vy=r('Player_Y_Speed'),world=0,level=0,lastA=lastA,grounded=r('Player_State')==0}
 c.block=function(wx,y)
  if y<32 or y>=240 then return 0 end
  return r('Block_Buffer_1',math.floor(wx/256)%2*208+math.floor((y-32)/16)*16+math.floor(wx%256/16))
 end
 c.enemy=function() return nextEnemy(c.x) end
 return route(c)
end
local function naturalControls()
 local wx=x()
 if wx<1430 then return routeInput() end
 if hit then return {} end
 if erased and r('KbMouth')~=0 then return {down=true} end
 if capture and not erased then return {} end
 if inhaleInput and not erased then return {right=true,b=true} end
 if not erased then
  if r('KbMouth')~=0 then return {down=true} end
  if r('KbCopy')~=0 then return {select=true} end
  if koopa then
   local a=actor(koopa.slot)
   local gap=a.x-wx
   if aligned(a) and a.id==0 and a.state==0 and r('PlayerFacingDir')==1 and
      r('Player_State')==0 and r('KbFloat')==0 and r('KbHurt')==0 and r('InjuryTimer')==0 and
      gap>=34 and gap<=56 then
    approachHP=r('KbHealth')
    inhaleInput={player=player(),target=a,gap=gap}
    return {right=true,b=true}
   end
   if a.flag==1 and a.id==0 and gap>=0 and gap<=74 and r('Player_State')~=0 then return {} end
  end
  local input=routeInput()
  input.b,input.down=false,false
  return input
 end
 if r('KbCopy')~=2 then return {} end
 if shotInput and frame-shotInput.player.frame<=18 then return {right=true,b=true} end
 if not shotInput then
  local nearest
  for slot=0,5 do
   local a,born=actor(slot),births[slot]
   local gap=a.x-wx
   if a.flag==1 and a.id==6 and a.state==0 and a.y_high==1 and a.y==184 and born and
      born.x>=1750 and born.x<=2100 and gap>0 and (not nearest or a.x<nearest.x) then nearest=a end
  end
  if nearest and r('PlayerFacingDir')==1 and r('Player_State')==0 and r('Player_Y_Position')==176 and
     r('KbFloat')==0 and nearest.x-wx>=26 and nearest.x-wx<=41 then
   shotInput={player=player(),target=nearest,gap=nearest.x-wx}
   return {right=true,b=true}
  end
 end
 local input=routeInput()
 input.b,input.down=false,false
 return input
end

emu.addEventCallback(function()
 polls=polls+1
 local input=buttons
 if firstActive and not finished then input=active() and naturalControls() or {} end
 lastA=not not input.a
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
  maxX=math.max(maxX,x())
  if maxX>=nextCheckpoint then checkpoints[#checkpoints+1]=player();nextCheckpoint=nextCheckpoint+128 end
  if not identity() or not stage() or r('NumberofLives')~=2 or r('GameEngineSubroutine')==11 then
   finish('life-or-stage-change');return
  end
  if failure or combatInjury or (approachHP and r('KbHealth')~=approachHP) then
   finish(failure or 'injury-during-green-encounter');return
  end
  if hit and r('KbShotType',hit.shell.slot)==0 then finish('natural-green-shell-hit');return end
  if shotInput and frame-shotInput.player.frame>35 then finish('ground-shell-did-not-hit');return end
  if not capture and x()>=1744 then finish('passed-authored-green-without-capture');return end
  if x()>=2070 then finish('passed-shell-target-window');return end
 end
 if frame>=11000 then finish('bounded-green-shell-timeout') end
end,emu.eventType.endFrame)
