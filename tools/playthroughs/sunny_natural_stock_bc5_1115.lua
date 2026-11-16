-- Actual native Sunny stock, read-only witnesses and ordinary controller input.
local frame,polls,mainEntries,mainReturns,guestEntries,guestReturns=0,0,0,0,0,0
local menuDone=CPU_CONTROLLER_OPENING or false
local stopped,lastA,buttons=false,false,{}
local pendingMain,pendingGuest,pendingCollect,pendingScore
local dynamic,events={},{}
local stock={phase='travel',samples={}}
local function read(at)return emu.read(at,emu.memType.nesDebug)end
local function r(n,i)return read(assert(C.ram[n],n)+(i or 0))end
local function pos(lo,hi,i)return r(lo,i)+256*r(hi,i)end
local function signed(v)return v<128 and v or v-256 end
local function score()local n=0;for i=0,5 do local d=r('Player1ScoreDisplay',i);assert(d<10);n=n*10+d end;return n end
local function active()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function state()return{Main=mainReturns,frame=frame,guest=guestReturns,x=pos('Player_X_Position','Player_PageLoc'),y=r('Player_Y_Position'),high=r('Player_Y_HighPos'),native=r('Player_State'),vx=r('Player_X_Speed'),vy=r('Player_Y_Speed'),power=r('PlayerStatus'),form=r('SunnyForm'),life=r('SunnyLife'),lives=r('NumberofLives'),star=r('StarInvincibleTimer'),score=score(),engine=r('GameEngineSubroutine'),phase=stock.phase}end
local function actor(i)return{slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),kind=r('PowerUpType',i),state=r('Enemy_State',i),x=pos('Enemy_X_Position','Enemy_PageLoc',i),y=r('Enemy_Y_Position',i)}end
local function box(name,i)local b={};for j=0,3 do b[#b+1]=r(name,(i or 0)*4+j)end;return b end
local function json(v)
 if v==nil then return'null'elseif type(v)=='string'then return string.format('%q',v)elseif type(v)~='table'then return tostring(v)end
 local a={};if#v>0 then for i,x in ipairs(v)do a[i]=json(x)end;return'['..table.concat(a,',')..']'end
 for k,x in pairs(v)do a[#a+1]=json(tostring(k))..':'..json(x)end;table.sort(a);return'{'..table.concat(a,',')..'}'
end
local function finish(ok,why)
 if stopped then return end;stopped=true;buttons={}
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=why,ROM_SHA256=C.sha,identity='Sunny',kind=C.key,physical_frames=frame,input_polls=polls,
  Main_entries=mainEntries,Main_returns=mainReturns,Sunny_entries=guestEntries,Sunny_returns=guestReturns,stock=stock,events=events,terminal=state(),
  pendingMain=pendingMain~=nil,pendingGuest=pendingGuest~=nil,gameplay_seeds=0,game_state_writes=false,outputs=0,full_stage_claim=false}))
 emu.stop(ok and 0 or 1)
end
local function guard(fn)return function(...)if stopped then return end;local ok,why=pcall(fn,...);if not ok then finish(false,tostring(why))end end end
local function hook(name,fn)
 local h=assert(C.hooks[name]);emu.addMemoryCallback(guard(function()
  local p=emu.convertAddress(h.pc);if not p or p.memType~=emu.memType.nesPrgRom or p.address~=h.offset then return end
  for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Exact '..name)end;fn()
 end),emu.callbackType.exec,h.pc)
end
local function returning(fn)
 local s=emu.getState()['cpu.sp'];local pc=(read(256+((s+1)&255))+256*read(256+((s+2)&255))+1)&65535
 local q={pc=pc,sp=(s+2)&255,entrySP=s,entryPC=emu.getState()['cpu.pc']}
 if not dynamic[pc]then
  dynamic[pc]={};emu.addMemoryCallback(guard(function()
   local sp=emu.getState()['cpu.sp'];local list=dynamic[pc]
   for i=#list,1,-1 do local t=list[i];if t.sp==sp then table.remove(list,i);t.fn(t)end end
  end),emu.callbackType.exec,pc)
 end
 q.fn=fn;dynamic[pc][#dynamic[pc]+1]=q;return q
end
local function identity()
 assert(r('SelectedCharacter')==23 and r('MarioVariant')==0,'Actual Sunny')
 assert(r('CrossoverBehaviorVersion')==0 and r('CheatInvincible')==0 and r('CheatStartLevel')==0,'Easy/no cheats')
 assert(r('WorldNumber')==0 and r('LevelNumber')==0,'Authored1-1')
 assert(r('NumberofLives')==(stock.life_credit and 3 or 2),'No death or invented life')
end
local function target()
 for i=0,5 do local a=actor(i);if a.flag==1 and a.id==46 and a.kind==C.kind then return a end end
end
local function observe()
 local a=target();if not a then return end
 if not stock.born then
  assert(a.x==(C.kind==3 and 1024 or 1616),'Authored stock block')
  stock.born={state=state(),actor=a}
 end
 if a.state>=128 then stock.mature=stock.mature or{state=state(),actor=a}end
 if guestReturns%8==0 then
  stock.samples[#stock.samples+1]={state=state(),actor=a};if#stock.samples>16 then table.remove(stock.samples,9)end
 end
end
local function context()
 local s=state();local c={frame=frame,poll=mainReturns,char=23,variant=0,r=r,x=s.x,y=s.y,yHigh=s.high,state=s.native,vx=s.vx,vy=s.vy,status=s.power,
  world=r('WorldNumber'),level=r('LevelNumber'),area=r('AreaPointer'),areaType=r('AreaType'),engine=s.engine,camera=pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc'),lastA=lastA,grounded=s.native==0}
 c.block=function(x,y)if y<32 or y>=240 then return 0 end;return r('Block_Buffer_1',(x//256)%2*208+((y-32)//16)*16+(x%256)//16)end
 c.enemy=function()
  local e;for i=0,5 do local a=actor(i);local dx=a.x-c.x
   if a.flag>0 and a.flag<128 and(a.id<21 or a.id==45 or a.id==51)and a.state<32 and not(a.id==6 and a.state>=2)and dx> -160 and dx<160 and(not e or math.abs(dx)<math.abs(e.dx))then a.dx=dx;e=a end
  end;return e
 end;return c
end
local function drive()
 if not menuDone or not active()then buttons={};return end;identity();observe()
 if stock.collected then buttons={};return end
 local c=context();local a=target()
 if a then
  if a.state<128 then buttons={};return end
  stock.phase='collect';local dx=a.x-c.x
  buttons={right=dx>3,left=dx< -3}
  if c.grounded and a.y<c.y-12 and math.abs(dx)<48 and(not stock.chaseJump or guestReturns-stock.chaseJump>40)then stock.chaseJump=guestReturns end
  if stock.chaseJump and guestReturns-stock.chaseJump<24 then buttons.a=true end
  return
 end
 local approach=C.kind==3 and 978 or 1560
 local center=C.kind==3 and 1018 or 1610
 if stock.phase=='travel'and c.x<approach then buttons=travel(c);return end
 if stock.phase=='travel'then stock.phase='align';stock.phaseStart=guestReturns;events[#events+1]=state()end
 if stock.phase=='align'then
  assert(guestReturns-stock.phaseStart<350,'Stock alignment bound')
  local velocity=signed(c.vx);local stopping=c.x+velocity*math.abs(velocity)/32
  buttons={right=stopping<center-1,left=stopping>center+1}
  if math.abs(c.x-center)<=2 and math.abs(velocity)<=1 and c.grounded and not lastA then stock.settle=(stock.settle or 0)+1 else stock.settle=0 end
  if stock.settle>=8 then
   stock.phase='head';stock.headAt=guestReturns;stock.request=state()
   stock.hidden_tile=c.block(C.kind==3 and 1024 or 1616,C.kind==3 and 128 or 144)
   assert(C.kind~=3 or stock.hidden_tile==96,'Actual hidden60 tile');buttons={a=true}
  end
 elseif stock.phase=='head'then
  assert(guestReturns-stock.headAt<160,'Actual ordinary head-bump bound')
  if c.state==1 and c.vy>=128 then stock.admission=stock.admission or state()end
  buttons={a=guestReturns-stock.headAt<24}
 end
end
local function endpoint()
 if not stock.credit or pendingMain or pendingGuest then return end
 local n=guestReturns-stock.credit.guest;stock.resumed=n
 assert(n<=25,'Do not overshoot25 actual Sunny returns')
 if n==25 then
  identity();assert(stock.born and stock.mature and stock.collector and stock.erase and stock.setup and stock.collected,'Complete actual stock lifecycle')
  assert(r('GuestPowerupActive')==0 and r('PlayerStatus')==stock.collector.state.power and r('SunnyForm')==stock.collector.state.form,'Stock preserves Sunny form')
  if C.kind==3 then assert(stock.life_credit and r('NumberofLives')==3 and r('SunnyLife')==3,'INC preserved through SunnyEnsure')
  else assert(stock.score_credit and r('StarInvincibleTimer')>0 and r('NumberofLives')==2,'Delayed1000 and active Star')end
  stock.actual_Main_return={pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],Main=mainReturns,guest=guestReturns}
  finish(true,'Natural '..C.key..' and25 actual returned Sunny updates at Main return')
 end
end
hook('GameLoop',function()
 assert(not pendingMain,'Main entry/return nesting');mainEntries=mainEntries+1
 local s=emu.getState()['cpu.sp'];local pc=read(256+((s+1)&255))+256*read(256+((s+2)&255))+1
 assert(pc==C.hooks.MainReturn0.pc or pc==C.hooks.MainReturn1.pc,'Authenticated Main caller');pendingMain={pc=pc,sp=(s+2)&255}
end)
for i=0,1 do local name='MainReturn'..i;hook(name,function()
 assert(pendingMain and pendingMain.pc==C.hooks[name].pc and pendingMain.sp==emu.getState()['cpu.sp'],'Actual Main return')
 pendingMain=nil;mainReturns=mainReturns+1;endpoint();if not stopped then drive()end
end)end
hook('SunnyNativeMovement',function()
 assert(not pendingGuest,'Previous Sunny movement returned');guestEntries=guestEntries+1
 pendingGuest=returning(function(t)pendingGuest=nil;guestReturns=guestReturns+1 end)
end)
hook('SunnyCollectIntegrated',function()
 local i=emu.getState()['cpu.x'];local a=actor(i);if a.kind~=C.kind or a.id~=46 or a.flag~=1 then return end
 assert(not pendingCollect and not stock.collected and stock.born and stock.mature and a.state>=128,'Actual mature item collector')
 local pb,ib=box('BoundingBox_UL_Corner'),box('EnemyBoundingBoxCoord',i)
 local width=math.min(pb[3],ib[3])-math.max(pb[1],ib[1])+1;local height=math.min(pb[4],ib[4])-math.max(pb[2],ib[2])+1
 assert(width>0 and height>0,'Native inclusive body overlap')
 stock.collector={state=state(),actor=a,player_box=pb,item_box=ib,overlap={width,height},pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp']}
 pendingCollect=returning(function(t)
  local wanted=C.kind==3 and 11 or 6
  assert(stock.erase and stock.setup and r('Enemy_Flag',i)==0 and r('FloateyNum_Control',i)==wanted,'Actual erase/popup')
  assert(r('Square2SoundQueue')==32,'Actual grab cue32')
  if C.kind==2 then assert(r('StarInvincibleTimer')==35 and r('AreaMusicQueue')==64,'Actual Star35/music64')end
  stock.collected={state=state(),pc=t.pc,sp=t.sp,popup=wanted};pendingCollect=nil;buttons={}
 end)
end)
hook('EraseEnemyObject',function()if pendingCollect then stock.erase=state()end end)
hook('SetupFloateyNumber',function()if pendingCollect then assert(emu.getState()['cpu.a']==6);stock.setup=state()end end)
hook('FloateyNumbersCore',function()
 if C.kind~=2 or not stock.collected or stock.score_credit or pendingScore then return end
 local i=emu.getState()['cpu.x'];if i~=stock.collector.actor.slot or r('FloateyNum_Control',i)~=6 or r('FloateyNum_Timer',i)~=43 then return end
 local before=score();pendingScore=returning(function(t)
  assert(score()==before+1000,'Actual delayed popup1000 writer')
  stock.score_credit={before=before,after=score(),state=state(),pc=t.pc,sp=t.sp}
  stock.credit={guest=guestReturns,state=state()};pendingScore=nil
 end)
end)
hook('LifeBefore',function()
 if C.kind~=3 or not stock.collected or stock.life_credit then return end
 local cpu=emu.getState();if cpu['cpu.x']~=stock.collector.actor.slot then return end
 assert(cpu['cpu.y']==11 and r('FloateyNum_Control',cpu['cpu.x'])==11 and r('NumberofLives')==2,'Actual delayed INC target')
 stock.lifeBefore={state=state(),pc=cpu['cpu.pc'],sp=cpu['cpu.sp']}
end)
hook('LifeAfter',function()
 if not stock.lifeBefore or stock.life_credit then return end
 assert(r('NumberofLives')==3 and r('Square2SoundQueue')==64,'Actual INC2->3 and cue64')
 stock.life_credit={before=stock.lifeBefore,state=state(),cue=64};stock.credit={guest=guestReturns,state=state()}
end)
local age=0
local function wait(n)coroutine.yield(n)end
local function press(key)buttons={[key]=true};wait(2);buttons={};wait(8)end
local function ready(fn,limit,label)local start=frame;while not fn()and frame-start<limit do wait(1)end;assert(fn(),'Frontend '..label)end
local menu=coroutine.create(function()
 assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha,'Exact owning bc5 environment')
 ready(function()return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end,250,'title')
 press('start');ready(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end,180,'roster')
 assert(r('CrossoverMenuIndex')==0 and r('SelectedCharacter')==0 and r('MarioVariant')==0,'Initial real Mario roster')
 for _,bits in ipairs(C.navigation)do press(bits==4 and'down'or'right')end
 assert(r('CrossoverMenuIndex')==22 and r('SelectedCharacter')==23 and r('MarioVariant')==0,'Actual compiled Sunny selection')
 assert(r('CrossoverBehaviorVersion')==0 and r('CheatInvincible')==0 and r('CheatStartLevel')==0,'Easy/default')
 press('start');menuDone=true
end)
emu.addEventCallback(guard(function()
 polls=polls+1;lastA=not not buttons.a;emu.setInput(buttons,0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guard(function()
 frame=frame+1
 if not menuDone then if age>0 then age=age-1;return end;local ok,n=coroutine.resume(menu);assert(ok,n);age=n or 0;return end
 if mainReturns>4500 or frame>14000 then finish(false,'Bounded natural Sunny stock policy')end
end),emu.eventType.endFrame)
