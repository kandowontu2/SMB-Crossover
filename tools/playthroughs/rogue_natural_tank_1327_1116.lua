-- Read-only genuine tank witnesses and normal controller input only.
local frame,polls,entries,updates=0,0,0,0
local counts,pending,returnHooks={},{},{}
local buttons,menuDone,finished={},CPU_CONTROLLER_OPENING or false,false
local first,born,mature,collector,credit,scoreTimer,reset
local grants,collectReturns,popups,sounds,requests,head={},{},{},{},{},{}
local eraseCount=0
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function pos(lo,hi,i)return r(lo,i)+256*r(hi,i)end
local function cpu()return emu.getState()end
local function score()local n=0;for i=0,5 do n=10*n+r('Player1ScoreDisplay',i)end;return n end
local function active()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function identity()return r('SelectedCharacter')==2 and r('RdVariant')==1 and r('CheatInvincible')==0 and r('CheatStartLevel')==0 and r('CrossoverBehaviorVersion')==0 end
local function state()return {Main=updates,motor=counts.RdControlStep_returned or 0,x=pos('Player_X_Position','Player_PageLoc'),y=r('Player_Y_Position'),
 native_state=r('Player_State'),action=r('RdAction'),source_x=pos('RdX','RdRoomHi'),source_y=r('RdY'),VY=r('RdVY'),held=r('RdHeld'),
 health_raw={r('RdHealthLo'),r('RdHealthHi')},tanks=r('RdTanks'),gear=r('RdGear'),missiles=r('RdMissiles'),max_missiles=r('RdMaxMissiles'),
 status=r('PlayerStatus'),lives=r('NumberofLives'),engine=r('GameEngineSubroutine'),score=score(),hosted_growth=r('GuestPowerupActive'),timer_control=r('TimerControl')}end
local function actor(i)return {slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),kind=r('PowerUpType',i),state=r('Enemy_State',i),
 x=pos('Enemy_X_Position','Enemy_PageLoc',i),y=r('Enemy_Y_Position',i),private=r('InvPickup',i),owner=r('InvPickupOwner',i),saved_raw=r('InvPickupSaveLo',i)}end
local function json(v)
 if type(v)=='string'then return string.format('%q',v)end
 if type(v)~='table'then return tostring(v)end
 local out={};if #v>0 then for i,x in ipairs(v)do out[i]=json(x)end;return '['..table.concat(out,',')..']'end
 for k,x in pairs(v)do out[#out+1]=json(tostring(k))..':'..json(x)end;table.sort(out);return '{'..table.concat(out,',')..'}'
end
local function count(n)counts[n]=(counts[n]or 0)+1 end
local function snapshot(suffix)local a={};for _,n in ipairs({'RdControlStep','RdLifeMovement','GameLoop'})do a[n]=counts[n..suffix]or 0 end;return a end
local function finish(reason)
 if finished then return end;finished=true
 local ok=reason=='natural-tank-credit-and25workers'and collector and credit and born and mature and not reset and #pending==0
 print('ROGUE_STOCK_RECEIPT '..json({passed=not not ok,reason=reason,ROM_SHA256=C.sha,physical_frames=frame,input_polls=polls,
  Main_entries=entries,Main_returns=updates,counts=counts,first_active=first,birth=born,mature=mature,collector=collector,score_credit=credit,
  grants=grants,private_C_returns=collectReturns,popups=popups,native_cue_writes=sounds,source_music_requests=requests,head=head,
  first_unexpected_reset=reset,terminal=state(),pending_scopes=#pending,game_state_writes=false,outputs=0,Mesen_images=0}))
 emu.stop(ok and 0 or 1)
end
local function guard(fn)return function(...)if finished then return end;local ok,why=pcall(fn,...);if not ok then finish('callback-error:'..tostring(why))end end end
local function mapped(pc)
 if pc<0x8000 then return -1,pc end
 local a=emu.convertAddress(pc);assert(a,'Mapped actual code')
 return a.memType,a.address
end
local function hook(n,fn)
 local h=assert(C.hooks[n],n)
 emu.addMemoryCallback(guard(function()
  local kind,at=mapped(h.PC);if kind~=emu.memType.nesPrgRom or at~=h.offset then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.PC+i-1,emu.memType.nesDebug)==v,'Exact owning hook '..n)end
  fn()
 end),emu.callbackType.exec,h.PC)
end
local function context()
 local c={frame=updates,poll=updates,char=2,variant=1,r=r,x=pos('Player_X_Position','Player_PageLoc'),y=r('Player_Y_Position'),
  yHigh=r('Player_Y_HighPos'),state=r('Player_State'),vx=r('Player_X_Speed'),vy=r('Player_Y_Speed'),status=r('PlayerStatus'),
  world=r('WorldNumber'),level=r('LevelNumber'),area=r('AreaPointer'),areaType=r('AreaType'),engine=r('GameEngineSubroutine'),
  camera=pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc'),lastA=(r('RdHeld')&128)~=0,grounded=r('Player_State')==0}
 c.block=function(x,y)if y<32 or y>=240 then return 0 end;return r('Block_Buffer_1',math.floor(x/256)%2*208+math.floor((y-32)/16)*16+math.floor(x%256/16))end
 c.enemy=function()
  local near
  for i=0,5 do local a=actor(i);local dx=a.x-c.x
   if a.flag>0 and a.flag<128 and(a.id<21 or a.id==45 or a.id==51)and a.state<32 and not(a.id==6 and a.state>=2)and dx> -160 and dx<160 then
    if not near or math.abs(dx)<math.abs(near.dx)then near={slot=i,id=a.id,x=a.x,y=a.y,state=a.state,dx=dx}end
   end
  end;return near
 end;return c
end
local function afterMain()
 if not first and active()and identity()then first=state()end
 if not first then return end
 assert(identity()and r('WorldNumber')==0 and r('LevelNumber')==0 and r('NumberofLives')==2 and r('GameEngineSubroutine')~=11,'Actual identity/stage/life')
 assert(r('RdHealthLo')+r('RdHealthHi')>0,'Original source health alive')
 for i=0,5 do local a=actor(i);if a.flag>0 and a.id==46 then
  assert(a.private==216 and a.owner==2 and a.saved_raw==0,'Authored first raw0 becomes typedD8')
  born=born or{actor=a,player=state()}
  if(a.state&128)~=0 then mature=mature or{actor=a,player=state()}end
 end end
 if credit then
  local er,rr=snapshot('_entered'),snapshot('_returned');local enough=true
  for n,v in pairs(er)do if v-credit.entered[n]<25 or rr[n]-credit.returned[n]<25 then enough=false end end
  if enough then
   assert(#pending==0 and r('RdTanks')==1 and r('PlayerStatus')==1 and r('RdHealthLo')==153 and r('RdHealthHi')==25,'Earned tank survives completed return gate')
   assert(r('RdGear')==0 and r('RdMissiles')==0 and r('RdMaxMissiles')==0 and not reset,'Source inventory unchanged except earned tank')
   credit.postcredit_entered={};credit.postcredit_returned={};credit.postcollector_returned={}
   for n,v in pairs(er)do credit.postcredit_entered[n]=v-credit.entered[n];credit.postcredit_returned[n]=rr[n]-credit.returned[n];credit.postcollector_returned[n]=rr[n]-collector.returned[n]end
   finish('natural-tank-credit-and25workers');return
  end
 end
 buttons=collector and{}or choose(context())
 assert(updates<1400,'Bounded ordinary first-tank route')
end
local settle
local function enter(n)
 local c=cpu();local sp=c['cpu.sp'];local ret=emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)+1
 ret=ret&65535;local kind,at=mapped(ret)
 count(n..'_entered');if n=='GameLoop'then entries=entries+1 end
 local p={name=n,pc=ret,sp=(sp+2)&255,kind=kind,at=at,A=c['cpu.a']}
 if n=='RdHsGrantType'or n=='RdHsCollectActor'or n=='HandlePowerUpCollision'then p.before=state()end
 if n=='HandlePowerUpCollision'then
  local i=c['cpu.x'];p.actor=actor(i);p.boxes={player={},item={}}
  for k=0,3 do p.boxes.player[k+1]=r('BoundingBox_UL_Corner',k);p.boxes.item[k+1]=r('BoundingBox_UL_Corner',(i+1)*4+k)end
 end
 if n=='AddToScore'then p.score=score();p.timer=scoreTimer;p.writes={};scoreTimer=nil end
 pending[#pending+1]=p
 if not returnHooks[ret]then returnHooks[ret]=true;emu.addMemoryCallback(guard(function()settle(ret)end),emu.callbackType.exec,ret)end
end
settle=function(pc)
 local sp=cpu()['cpu.sp'];local kind,at=mapped(pc)
 while #pending>0 do
  local p=pending[#pending];if p.pc~=pc or p.sp~=sp or p.kind~=kind or p.at~=at then return end
  pending[#pending]=nil;local n=p.name;count(n..'_returned')
  if n=='GameLoop'then updates=updates+1;afterMain()
  elseif n=='RdHsCollectActor'then assert(#collectReturns<8,'Bounded collectors');collectReturns[#collectReturns+1]={C=cpu()['cpu.ps']&1,before=p.before,after=state()}
  elseif n=='RdHsGrantType'then assert(#grants<8,'Bounded grants');grants[#grants+1]={A=p.A,C=cpu()['cpu.ps']&1,before=p.before,after=state()}
  elseif n=='HandlePowerUpCollision'and p.actor.id==46 and r('Enemy_Flag',p.actor.slot)==0 then
   assert(not collector and born and mature and(p.actor.state&128)~=0,'Actual mature collector follows birth')
   assert(collectReturns[#collectReturns].C==1 and grants[#grants].A==8 and grants[#grants].C==1,'Actual original tank grant C1')
   assert(r('RdTanks')==1 and r('PlayerStatus')==1 and r('RdHealthLo')==153 and r('RdHealthHi')==25,'Real tank/refill/status')
   assert(eraseCount>0 and sounds[32]and #requests>0 and popups[#popups]==6,'Actual erase/popup/cues')
   collector={actor=p.actor,before=p.before,after=state(),physical_boxes=p.boxes,returned=snapshot('_returned'),C=1,erase_count=eraseCount}
  elseif n=='AddToScore'and p.timer then
   assert(collector and score()==p.score+1000 and #p.writes==6,'Actual timer43 thousand-point writer')
   credit={writer={timer=p.timer,before=p.score,after=score(),six_decimal_writes=p.writes},state=state(),entered=snapshot('_entered'),returned=snapshot('_returned')}
  end
 end
end
for _,n in ipairs({'GameLoop','RdControlStep','RdLifeMovement','HandlePowerUpCollision','RdHsCollectActor','RdHsGrantType','RdItPickup','RdItPrepare','AddToScore'})do
 hook(n,function()if menuDone and identity()then enter(n)end end)
end
hook('SetupFloateyNumber',function()if first and #popups<16 then popups[#popups+1]=cpu()['cpu.a']end end)
hook('EraseEnemyObject',function()if first then local a=actor(cpu()['cpu.x']);if a.id==46 and a.private==216 and a.owner==2 then eraseCount=eraseCount+1 end end end)
hook('PlayerHeadCollision',function()if first and #head<8 then head[#head+1]={tile=cpu()['cpu.a'],player=state()}end end)
hook('DecNumTimer',function()
 local c=cpu();local i=c['cpu.x'];if born and c['cpu.a']==43 and c['cpu.y']==6 and i==born.actor.slot then
  assert(r('FloateyNum_Timer',i)==43,'Actual old timer43');scoreTimer={slot=i,oldtimer=43,control=6,Main=updates}
 end
end)
local function written(address,value)
 if address==C.ram.Square2SoundQueue and(value==32 or value==64)then sounds[value]=(sounds[value]or 0)+1 end
 if address==C.ram.RdSfx+4 and(value&64)~=0 and #requests<4 then requests[#requests+1]={old=emu.read(address,emu.memType.nesDebug),new=value,Main=updates,PC=cpu()['cpu.pc']}end
 if address>=C.ram.Player1ScoreDisplay and address<C.ram.Player1ScoreDisplay+6 then
  for i=#pending,1,-1 do local p=pending[i];if p.name=='AddToScore'then
   if p.timer then p.writes[#p.writes+1]={offset=address-C.ram.Player1ScoreDisplay,old=emu.read(address,emu.memType.nesDebug),new=value,PC=cpu()['cpu.pc']}end;break
  end end
 end
 if collector and not reset and(address==C.ram.RdTanks or address==C.ram.PlayerStatus)and value==0 then
  reset={address=address,old=emu.read(address,emu.memType.nesDebug),new=value,PC=cpu()['cpu.pc'],player=state()};error('Unexpected earned-resource reset')
 end
end
for _,name in ipairs({'Square2SoundQueue','RdTanks','PlayerStatus'})do emu.addMemoryCallback(guard(written),emu.callbackType.write,C.ram[name])end
emu.addMemoryCallback(guard(written),emu.callbackType.write,C.ram.RdSfx+4)
emu.addMemoryCallback(guard(written),emu.callbackType.write,C.ram.Player1ScoreDisplay,C.ram.Player1ScoreDisplay+5)
local function wait(n)coroutine.yield(n)end
local function press(key)buttons={[key]=true};wait(2);buttons={};wait(8)end
local function ready(fn,limit,label)local at=frame;while not fn()and frame-at<limit do wait(1)end;assert(fn(),label)end
local menu=coroutine.create(function()
 assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha,'Exact owning1327 ROM')
 ready(function()return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end,250,'Actual title')
 press('start');ready(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end,180,'Actual roster')
 assert(r('CrossoverMenuIndex')==0 and r('SelectedCharacter')==0,'Actual initial menu')
 press('right');press('right');press('select')
 assert(identity()and r('CrossoverMenuIndex')==2,'Actual Rogue menu selection')
 press('start');menuDone=true
end)
local age=0
emu.addEventCallback(guard(function()polls=polls+1;emu.setInput(buttons,0)end),emu.eventType.inputPolled)
emu.addEventCallback(guard(function()
 frame=frame+1
 if not menuDone then if age>0 then age=age-1;return end;local ok,n=coroutine.resume(menu);assert(ok,n);age=n or 0 end
 if frame>=6000 then finish('bounded-physical-route')end
end),emu.eventType.endFrame)
