C.parent_observer_ROM=C.sha
C.sha=assert(os.getenv('SMB_STDOUT_ROM_SHA'),'Runner binds the installed ROM')
local frame,polls,age,updates=0,0,0,0
local buttons,events,trace,attempts={},{},{},{}
local menuDone,finished=false,false
local first,request,capture,erased,swallowed,attack,volley,hit,defeated,injury
local partialRequest,partialStart,partial
local firstSound,partialSound
local born={}
local lastFrameCounter
local resumed,birthCount=0,0
-- COMMON

local function snap()
 local p=player()
 p.update=updates;p.facing=r('PlayerFacingDir');p.action=r('KbAction')
 return p
end

local function actors()
 local out={}
 for slot=0,5 do
  local a=actor(slot)
  if a.flag==1 and a.state&32==0 and a.y_high==1 then
   a.dx=a.x-x();out[#out+1]=a
  end
 end
 return out
end

local function projectile(slot)
 return {slot=slot,x=pos('KbShotX','KbShotPage',slot),y=r('KbShotY',slot),
  kind=r('KbShotKind',slot),type=r('KbShotType',slot),age=r('KbShotAge',slot),
  vx=r('KbShotVXHi',slot),vy=r('KbShotVYHi',slot)}
end

local function finish(reason)
 if finished then return end
 finished=true
 local last=snap()
 local passed=reason=='earned-spiny-needles' and first and capture and erased and swallowed
  and volley and hit and defeated and resumed==25 and not injury and identity() and stage() and active()
  and last.hp==6 and last.lives==2 and last.copy==11 and last.mouth==0
  and firstSound and (not C.pressure or (partial and partial.sound==32 and partialSound))
 print('SMB_NATIVE_RECEIPT '..json({passed=not not passed,reason=reason,ROM_SHA256=C.sha,
  selected_stage='4-1',difficulty=r('CrossoverBehaviorVersion'),
  start_stage_option=r('CheatStartLevel'),invincibility=r('CheatInvincible'),
  controller_only=true,script_RAM_writes=false,output_files=0,physical_frames=frame,input_polls=polls,
  authored_spiny_spawns=birthCount,first_active=first,menu_events=events,inhale_request=request,
  captured_spiny=capture,native_erase=erased,swallowed=swallowed,volley=volley,attempts=attempts,
  hit=hit,defeated=defeated,partial_volley=partial,first_sound=firstSound,partial_sound=partialSound,
  resumed=resumed,injury=injury,terminal=last,diagnostic=trace}))
 emu.stop(passed and 0 or 1)
end

-- BINDINGS
hook('spinyBirth',function(slot)
 local a=actor(slot)
 if a.id==18 and a.flag==1 and a.state==5 and a.y_high==1 then
  birthCount=birthCount+1
  a.serial=birthCount
  born[slot]=a
 end
end)

hook('capture',function(slot)
 local a=actor(slot)
 assert(not capture and born[slot] and a.id==18 and a.flag==1 and a.state&32==0
  and r('KbAction')==1 and r('SavedJoypadBits')&64~=0 and r('KbMouth')==0,
  'Actual B inhale catches a live Spiny thrown by Lakitu')
 capture={target=a,birth=born[slot],player=snap()}
end)

hook('erased',function(slot)
 assert(capture and slot==capture.target.slot and r('Enemy_Flag',slot)==0
  and r('Enemy_ID',slot)==0 and r('KbMouth')==19 and r('KbMouthCopy')==11,
  'Spiny disappears and its needle copy enters the mouth')
 erased=snap()
end)

hook('injury',function(slot)
 if first and not injury then injury={player=snap(),target=actor(slot)} end
end)

hook('copyAttack',function()
 if partialRequest and not partialStart then
  local live={}
  for i=0,2 do
   local a=projectile(i)
   if a.type~=0 then live[#live+1]=a end
  end
  partialStart={player=snap(),older=live,sound=r('Square1SoundQueue')}
 end
end)

hook('weaponUpdate',function()
 if partialStart and not partial then
  local new={}
  for i=0,2 do
   local a=projectile(i)
   if a.type==3 and a.kind==11 and a.age==0 then new[#new+1]=a end
  end
  local older=#partialStart.older
  assert(older>0 and older<3 and #new==3-older,'The second press fills only the available needle slots')
  partial={before=partialStart,shots=new,sound=r('Square1SoundQueue')}
  if partial.sound~=32 then finish('partial-needle-sound-missing') end
  return
 end
 if not attack or hit then return end
 local shots={}
 for slot=0,2 do
  local a=projectile(slot)
  if a.type==3 and a.kind==11 and a.age==0 then shots[#shots+1]=a end
 end
 if #shots==0 then return end
 assert(#shots==3 and r('SavedJoypadBits')&64~=0 and r('KbCopy')==11,
  'B spawns a complete needle fan into an empty pool')
 assert(shots[1].vx==254 and shots[2].vx==0 and shots[3].vx==2
  and shots[1].vy==255 and shots[2].vy==253 and shots[3].vy==255,
  'The native fan throws left, up and right')
 volley={player=snap(),shots=shots,sound=r('Square1SoundQueue'),target=attack.target}
 attempts[#attempts+1]=volley
 attack=nil
end)

hook('needleContact',function(slot)
 if not volley or hit then return end
 local a=actor(slot)
 local shot=projectile(r('KbSavedSlot'))
 if shot.type~=3 or shot.kind~=11 then return end
 local birth=born[slot]
 if a.id==18 then
  assert(birth and birth.serial~=capture.birth.serial,'A second authentic Spiny is the target')
 elseif a.id~=17 then
  finish('unverified-needle-target');return
 end
 assert(a.flag==1 and a.state&32==0 and a.y_high==1 and shot.age>0,
  'Needle reaches the live native enemy defeat path')
 hit={target=a,birth=birth,shot=shot,player=snap()}
end)

hook('needleConsumed',function(slot)
 if not hit or defeated then return end
 local a=actor(slot)
 assert(slot==hit.target.slot and a.state&32~=0,'The exact enemy was defeated by the needle')
 defeated={target=a,player=snap()}
end)

hook('needleAudio',function()
 if not volley or r('GuestWorldQueues')&32==0 then return end
 local cue={frame=frame,mask=r('GuestWorldQueues'),active_copy=r('KbCopy')}
 if partial and not partialSound then partialSound=cue
 elseif not firstSound then firstSound=cue end
end)

hook('weaponDone',function()
 local fc=r('FrameCounter')
 if fc==lastFrameCounter then return end
 lastFrameCounter=fc;updates=updates+1
 if erased and not swallowed and r('KbCopy')==11 then
  assert(r('KbMouth')==0 and r('SavedJoypadBits')&4~=0,'Down swallows the real Spiny')
  swallowed=snap()
 end
 if defeated then
  assert(r('KbCopy')==11 and r('KbHealth')==6,'Keep the copied power after the needle hit')
  if C.pressure and not partial then return end
  resumed=resumed+1
  if resumed==25 then finish('earned-spiny-needles') end
 end
end)

-- FRONTEND
local function face(dx)
 if dx<0 then return {left=true} end
 return {right=true}
end

local function controls()
 if C.pressure and volley and not partial then
  if not partialRequest then
   local older=0
   for i=0,2 do if r('KbShotType',i)~=0 then older=older+1 end end
   if r('KbCooldown')==0 and (older==1 or older==2) then partialRequest=snap() end
  end
  if partialRequest then return {b=true} end
  return {}
 end
 if defeated then return {} end
 if erased and not swallowed then return {down=true} end
 local px,py=x(),r('Player_Y_Position')
 local target,hasLakitu
 for _,a in ipairs(actors()) do
  if a.id==17 then hasLakitu=true end
  if a.id==18 and born[a.slot] and (not target or math.abs(a.dx)<math.abs(target.dx)) then
   target=a
  end
 end
 if not target then
  if px<170 or (not hasLakitu and px<323) then return {right=true} end
  return {}
 end
 local distance=math.abs(target.dx)
 local facing=r('PlayerFacingDir')==(target.dx<0 and 2 or 1)
 if not swallowed then
  if distance>44 then return face(target.dx) end
  if not facing then return face(target.dx) end
  request=request or {player=snap(),target=target}
  return {b=true}
 end
 if r('KbAction')==3 then return {} end
 for i=0,2 do if r('KbShotType',i)~=0 then return {} end end
 if attack then return {b=true} end
 if #attempts>=8 then finish('needles-never-defeated-an-enemy');return {} end
 -- At the first pipe, a right-facing shot would start inside its edge.
 -- The fan fires in both directions, so launch from the left-hand origin.
 local rightOrigin=r('PlayerFacingDir')==1
 if px>=303 and px<336 and rightOrigin then return {left=true} end
 local origin=px+(rightOrigin and 16 or 0)
 local dy=target.y-py
 if math.abs(target.x-origin)<=22 and dy>=-44 and dy<=22
  and r('KbFloat')==0 and r('SavedJoypadBits')&64==0 then
  attack={target=target,player=snap()};return {b=true}
 end
 if distance>35 then return face(target.dx) end
 return {}
end

emu.addEventCallback(guarded(function()
 polls=polls+1
 emu.setInput(first and controls() or buttons,0)
end),emu.eventType.inputPolled)

emu.addEventCallback(guarded(function()
 frame=frame+1
 if not menuDone then
  if age>0 then age=age-1;return end
  local ok,n=coroutine.resume(menu);assert(ok,n);age=n or 0;return
 end
 if not first and active() and stage() and identity() and r('TimerControl')==0 then
  first=snap()
  assert(first.hp==6 and first.lives==2 and first.copy==0 and first.mouth==0,'Normal 4-1 starting state')
 end
 if first and frame%12==0 then
  trace[#trace+1]={p=snap(),enemies=actors()}
  if #trace>16 then table.remove(trace,1) end
 end
 if injury then finish('unexpected-injury');return end
 if frame>=4000 then finish('bounded-4-1-spiny-route') end
end),emu.eventType.endFrame)
