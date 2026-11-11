-- Controller-only route from the cold title to both authored food pickups.
C.sha=assert(os.getenv('SMB_STDOUT_ROM_SHA'))
local frame,polls,age=0,0,0
local buttons,events={},{}
local menuDone,finished=false,false
local firstActive
local phase,step,lastJump='approach',0,-100
local pipes,births,mature,contacts,heals,injuries={},{},{},{},{},{}
local graphics={}
local counter,flowerBirth
local pad=0

-- COMMON
local function foodActor(slot)
 local a=actor(slot)
 a.kind=r('PowerUpType',slot)
 return a
end

local function finish(reason)
 if finished then return end
 finished=true
 local passed=reason=='both-earned-food' and #births==2 and #mature==2 and
   #contacts==2 and #heals==2 and #graphics==2 and r('KbHealth')==6 and r('NumberofLives')==2 and
   r('KbFoodKind')==0 and active() and stage() and identity()
 print('SMB_NATIVE_RECEIPT '..json({passed=not not passed,reason=reason,ROM_SHA256=C.sha,
   controller_only=true,output_files=0,physical_frames=frame,updates=step,input_polls=polls,
   phase=phase,initial=firstActive,terminal=player(),births=births,mature=mature,
   contacts=contacts,heals=heals,graphics=graphics,injuries=injuries,menu=events}))
 emu.stop(passed and 0 or 1)
end

-- BINDINGS
hook('birth',function(slot)
 local a=foodActor(slot)
 local expected=#births==0 and 336 or 1248
 assert(#births<2 and a.x==expected and a.y==136,'Expected authored food block')
 a.kind=nil  -- The stock constructor assigns the new type after this hook.
 births[#births+1]=a
end)
hook('draw',function(slot)
 local a=foodActor(slot)
 if a.id~=46 or a.flag~=1 or a.state<128 or a.kind>1 or graphics[a.kind+1] then return end
 local pose=r('EnemyMetasprite',slot)
 assert(pose==C.foodGfx[a.kind+1],'Native item renderer selects the expected metasprite')
 graphics[a.kind+1]={actor=a,pose=pose,attributes=r('Enemy_SprAttrib',slot)}
end)
hook('injury',function(slot)
 if firstActive then
  injuries[#injuries+1]={actor=actor(slot),player=player()}
  assert(#injuries<=8,'Bounded actual enemy contacts')
 end
end)
hook('heal',function(slot)
 local a=foodActor(slot)
 local kind=#contacts
 assert(kind<2 and a.id==46 and a.flag==1 and a.state>=128 and a.kind==kind,
   'Native pickup uses the mature authored food actor')
 assert(mature[kind+1] and mature[kind+1].slot==slot,'Pickup follows native emergence')
 assert(r('KbHealth')<6 and r('KbFoodKind')==kind,'Earned food restores missing HP')
 contacts[kind+1]={actor=a,player=player()}
end)

-- FRONTEND
local function pickupState()
 local item
 for slot=0,5 do
  local a=foodActor(slot)
  if a.id==46 and a.flag==1 then
   item=a
   if a.state>=128 and not mature[a.kind+1] then mature[a.kind+1]=a end
  end
 end
 local contact=contacts[#contacts]
 if contact and #heals<#contacts and r('KbFoodKind')==#contacts%2 then
  local a=foodActor(contact.actor.slot)
  assert(a.flag==0 and a.id==0 and a.state==0 and r('KbHealth')==6 and r('KbHeal')>0,
    'Native food vanishes and restores Kirby with the heal animation')
  heals[#heals+1]={player=player(),actor=a,remaining=r('KbHeal')}
 end
 return item
end

local function mushroom(x,y,ground,item)
 if phase=='approach' and x>=332 then phase='brake' end
 if phase=='approach' then return 1 end
 local input=0
 if item then
  if item.state>=128 then
   local gap=item.x-x
   input=gap>4 and 1 or gap< -12 and 2 or 0
   if item.y<y-20 and ground and step-lastJump>25 then lastJump=step end
  end
 else
  local gap=334-x
  input=gap>4 and 1 or gap< -4 and 2 or 0
  if math.abs(gap)<=4 and ground and step-lastJump>20 then lastJump=step end
 end
 return input|(step-lastJump<24 and 128 or 0)
end

local function flower(x,y,ground,item)
 local floating=r('KbFloat')~=0
 if item and not flowerBirth then
  assert(item.x==1248 and item.kind==1,'Native flower from its authored block')
  flowerBirth=step
  phase='reveal'
 end
 if phase=='reveal' and step-flowerBirth>=40 then phase='pickup' end
 if phase=='route' and x>=1228 then phase='under' end
 if phase=='route' and x>=800 and r('KbHealth')>4 then phase='meet-goombas' end
 if phase=='meet-goombas' and r('KbHealth')==4 then phase='route' end
 local input=0
 if phase=='route' then
  input=1
  for _,pipe in ipairs({{448,176},{608,160},{736,144},{912,144},{1104,144}}) do
   local left,top=pipe[1],pipe[2]
   if left-55<=x and x<left+30 then
    if ground and not pipes[left] then lastJump=step;pipes[left]=true end
    if y>top-30 and step-lastJump>=23 then input=input|8 end
    break
   end
  end
  if x>=445 and x<=480 and y>144 and not floating and not ground then input=input|8 end
  if floating and input&8==0 and y<=144 and step-lastJump>24 then input=input|64 end
 elseif phase=='meet-goombas' then
  input=x<815 and 1 or x>850 and 2 or 0
  if floating then input=input|64 end
 elseif phase=='under' then
  local gap=1242-x
  input=gap>3 and 1 or gap< -3 and 2 or 0
  if y<=130 and x>1210 then input=2 end
  if ground and y>145 and math.abs(gap)<=4 and step-lastJump>27 then lastJump=step end
 elseif phase=='pickup' then
  assert(item,'Collectible flower still exists')
  if ground and x<=item.x-37 and step-lastJump>32 then lastJump=step end
  if step-lastJump<24 then
   input=1
  elseif x>item.x-37 and y>item.y+20 then
   input=2
  else
   input=x<item.x-8 and 1 or x>item.x+3 and 2 or 0
   if y>item.y-8 and not ground then input=input|8 end
  end
 end
 return input|(step-lastJump<23 and 128 or 0)
end

emu.addEventCallback(guarded(function()
 polls=polls+1
 if not firstActive then emu.setInput(buttons,0);return end
 emu.setInput({right=pad&1~=0,left=pad&2~=0,up=pad&8~=0,b=pad&64~=0,a=pad&128~=0},0)
end),emu.eventType.inputPolled)

emu.addEventCallback(guarded(function()
 frame=frame+1
 assert(frame<=5400,'Bounded physical Kirby food route')
 if not menuDone then
  if age>0 then age=age-1;return end
  local ok,n=coroutine.resume(menu);assert(ok,n);age=n or 0
  return
 end
 if not firstActive then
  if not (active() and stage() and identity() and r('TimerControl')==0) then return end
  firstActive=player()
  assert(firstActive.hp==6 and firstActive.lives==2 and firstActive.copy==0,'Cold normal Kirby')
 end
 assert(active() and stage() and identity() and r('NumberofLives')==2,'Live native World 1-1')
 local now=r('FrameCounter')
 if counter==now then return end
 step=step+(counter and ((now-counter)&255) or 0)
 counter=now
 local item=pickupState()
 if #heals==2 then finish('both-earned-food');return end
 if #heals==1 and phase~='route' and phase~='meet-goombas' and phase~='under'
     and phase~='reveal' and phase~='pickup' then
  phase='route'
  lastJump=-100
 end
 local px,y,ground=x(),r('Player_Y_Position'),r('Player_State')==0
 if #heals==0 then pad=mushroom(px,y,ground,item) else pad=flower(px,y,ground,item) end
end),emu.eventType.endFrame)
