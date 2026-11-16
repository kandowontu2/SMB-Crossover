-- Actual Toad first Mushroom: controls and readonly native witnesses only.
local frame,polls,mainEntries,mainReturns,guestEntries,guestReturns=0,0,0,0,0,0
local menuDone=CPU_CONTROLLER_OPENING or false
local stopped,lastA,buttons=false,false,{}
local pendingMain,pendingGuest,pendingCollect
local dynamic,food,readback={},{ticks=0,sound={writes20=0,clears=0}},{}
local function read(at)return emu.read(at,emu.memType.nesDebug)end
local function r(n,i)return read(assert(C.ram[n],n)+(i or 0))end
local function pos(lo,hi,i)return r(lo,i)+256*r(hi,i)end
local function score()local n=0;for i=0,5 do local d=r('Player1ScoreDisplay',i);assert(d<10);n=n*10+d end;return n end
local function active()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function state()return{Main=mainReturns,frame=frame,guest=guestReturns,x=pos('Player_X_Position','Player_PageLoc'),
 y=r('Player_Y_Position'),high=r('Player_Y_HighPos'),native=r('Player_State'),vx=r('Player_X_Speed'),vy=r('Player_Y_Speed'),
 power=r('PlayerStatus'),size=r('PlayerSize'),lives=r('NumberofLives'),star=r('StarInvincibleTimer'),score=score(),
 engine=r('GameEngineSubroutine'),active=r('GuestPowerupActive'),age=r('GuestPowerupAge'),timer=r('TimerControl'),
 variant=r('MarioVariant'),chr_mode=r('X5ChrMode')}
end
local function actor(i)return{slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),kind=r('PowerUpType',i),state=r('Enemy_State',i),
 x=pos('Enemy_X_Position','Enemy_PageLoc',i),y=r('Enemy_Y_Position',i)}end
local function box(name,i)local b={};for j=0,3 do b[#b+1]=r(name,(i or 0)*4+j)end;return b end
local function json(v)
 if v==nil then return'null'elseif type(v)=='string'then return string.format('%q',v)elseif type(v)~='table'then return tostring(v)end
 local a={};if#v>0 then for i,x in ipairs(v)do a[i]=json(x)end;return'['..table.concat(a,',')..']'end
 for k,x in pairs(v)do a[#a+1]=json(tostring(k))..':'..json(x)end;table.sort(a);return'{'..table.concat(a,',')..'}'
end
local function finish(ok,why)
 if stopped then return end;stopped=true;buttons={}
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=why,ROM_SHA256=C.sha,identity='SMB1 Toad',kind='mushroom',
  Main_entries=mainEntries,Main_returns=mainReturns,Mario_entries=guestEntries,Mario_returns=guestReturns,
  physical_frames=frame,input_polls=polls,food=food,readback=readback,terminal=state(),
  pendingMain=pendingMain~=nil,pendingGuest=pendingGuest~=nil,pendingCollect=pendingCollect~=nil,
  gameplay_seeds=0,game_state_writes=false,outputs=0,full_stage_claim=false}))
 emu.stop(ok and 0 or 1)
end
local function guard(fn)return function(...)if stopped then return end;local ok,why=pcall(fn,...);if not ok then finish(false,tostring(why))end end end
local function hook(name,fn)
 local h=assert(C.hooks[name]);emu.addMemoryCallback(guard(function()
  local p=emu.convertAddress(h.pc);if not p or p.memType~=emu.memType.nesPrgRom or p.address~=h.offset then return end
  for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Exact current native '..name)end;fn()
 end),emu.callbackType.exec,h.pc)
end
local function returning(fn)
 local cpu=emu.getState();local sp=cpu['cpu.sp'];local pc=(read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1)&65535
 local q={pc=pc,sp=(sp+2)&255,entryPC=cpu['cpu.pc'],entrySP=sp}
 if not dynamic[pc]then
  dynamic[pc]={};emu.addMemoryCallback(guard(function()
   local s=emu.getState()['cpu.sp'];local list=dynamic[pc]
   for i=#list,1,-1 do local t=list[i];if t.sp==s then table.remove(list,i);t.fn(t)end end
  end),emu.callbackType.exec,pc)
 end
 q.fn=fn;dynamic[pc][#dynamic[pc]+1]=q;return q
end
local function identity()
 assert(r('SelectedCharacter')==0 and r('MarioVariant')==5 and r('X5ChrMode')==131,'Actual compiled SMB1 Toad')
 assert(r('CrossoverBehaviorVersion')==0 and r('CheatInvincible')==0 and r('CheatStartLevel')==0,'Easy ordinary no-cheat controls')
 assert(r('WorldNumber')==0 and r('LevelNumber')==0 and r('NumberofLives')==2 and r('GameEngineSubroutine')~=11,'Living genuine1-1')
end
local function observe()
 for i=0,5 do local a=actor(i);if a.flag==1 and a.id==46 and a.kind==0 then
  if not food.born then assert(a.x==336,'Authored firstM block');food.born={state=state(),actor=a}end
  if a.state>=128 then food.mature=food.mature or{state=state(),actor=a}end
 end end
end
local function context()
 local s=state();local c={frame=frame,poll=guestReturns,char=0,variant=5,r=r,x=s.x,y=s.y,yHigh=s.high,state=s.native,
  vx=s.vx,vy=s.vy,status=s.power,world=r('WorldNumber'),level=r('LevelNumber'),area=r('AreaPointer'),areaType=r('AreaType'),
  engine=s.engine,camera=pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc'),lastA=lastA,grounded=s.native==0}
 c.block=function(x,y)if y<32 or y>=240 then return 0 end;return r('Block_Buffer_1',(x//256)%2*208+((y-32)//16)*16+(x%256)//16)end
 c.enemy=function()
  local e;for i=0,5 do local a=actor(i);local dx=a.x-c.x
   if a.flag>0 and a.flag<128 and(a.id<21 or a.id==45 or a.id==51)and a.state<32 and not(a.id==6 and a.state>=2)and dx> -160 and dx<160 and(not e or math.abs(dx)<math.abs(e.dx))then a.dx=dx;e=a end
  end;return e
 end;return c
end
local function drive()
 if not menuDone then return end;identity();observe()
 if not active()or food.collected then buttons={};return end
 buttons=travel(context());lastA=not not buttons.a
end
local function endpoint()
 if not food.transaction_done or not food.credit or pendingMain or pendingGuest or pendingCollect then return end
 if not food.resumeBase then food.resumeBase=guestReturns end
 local n=guestReturns-food.resumeBase;food.resumed=n;assert(n<=25,'Exactly25 resumed Mario returns')
 if n==25 then
  identity();assert(active()and food.born and food.mature and food.collector and food.erase and food.setup and food.ticks==60,'Complete actual native Mushroom lifecycle')
  assert(r('PlayerStatus')==1 and r('PlayerSize')==0 and r('GuestPowerupActive')==0 and r('GuestPowerupAge')==60 and r('TimerControl')==0,'Actual60-tick native tier1')
  assert(mainEntries==mainReturns and guestEntries==guestReturns,'Balanced completed native calls')
  food.actual_Main_return={pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],state=state()}
  finish(true,'Natural SMB1 Toad M/1000/60tick tier1 and25 returned Mario movements at completedMain')
 end
end
hook('GameLoop',function()
 assert(not pendingMain,'Synchronous Main');mainEntries=mainEntries+1
 local cpu=emu.getState();local sp=cpu['cpu.sp'];local pc=read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1
 assert(pc==C.hooks.MainReturn0.pc or pc==C.hooks.MainReturn1.pc,'Authenticated current Main caller');pendingMain={pc=pc,sp=(sp+2)&255}
end)
for i=0,1 do local name='MainReturn'..i;hook(name,function()
 local cpu=emu.getState();if pendingMain and pendingMain.pc==cpu['cpu.pc']and pendingMain.sp==cpu['cpu.sp']then
  pendingMain=nil;mainReturns=mainReturns+1;endpoint();if not stopped then drive()end
 end
end)end
hook('MarioSourceMovement',function()
 identity();assert(not pendingGuest,'Previous original Mario movement returned')
 if not readback.movement then
  for i=1,#C.movement_hex,2 do assert(read(C.hooks.MarioSourceMovement.pc+(i-1)//2)==tonumber(C.movement_hex:sub(i,i+1),16),'All64 actual current movement PRG bytes')end
  readback.movement={pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],bank=C.hooks.MarioSourceMovement.bank,bytes=64}
 end
 guestEntries=guestEntries+1;pendingGuest=returning(function(t)pendingGuest=nil;guestReturns=guestReturns+1 end)
end)
hook('HandlePowerUpCollision',function()
 if not menuDone then return end;identity();observe();local cpu=emu.getState();local i=cpu['cpu.x'];local a=actor(i)
 assert(i==5 and a.flag==1 and a.id==46 and a.kind==0 and a.state>=128,'Actual mature firstM collector')
 assert(food.born and food.mature and not food.collected,'Genuine lifecycle before unique collection')
 local pb,ib=box('BoundingBox_UL_Corner'),box('EnemyBoundingBoxCoord',i)
 local width=math.min(pb[3],ib[3])-math.max(pb[1],ib[1])+1;local height=math.min(pb[4],ib[4])-math.max(pb[2],ib[2])+1
 assert(width>0 and height>0,'Actual positive inclusive native overlap')
 food.collector={state=state(),actor=a,player_box=pb,item_box=ib,overlap={width,height},pc=cpu['cpu.pc'],sp=cpu['cpu.sp']}
 pendingCollect=returning(function(t)
  assert(food.erase and food.setup and r('Enemy_Flag',i)==0 and r('FloateyNum_Control',i)==6 and food.sound.writes20>0,'Actual erase/popup6/cue20')
  assert(r('GuestPowerupOld')==0 and r('GuestPowerupTarget')==1 and r('GuestPowerupActive')==1 and r('GuestPowerupAge')==0 and r('TimerControl')==255 and r('GameEngineSubroutine')==9,'Actual Mario tier0to1 transaction')
  food.collected={state=state(),pc=t.pc,sp=t.sp,P=emu.getState()['cpu.ps']};pendingCollect=nil;buttons={}
 end)
end)
hook('EraseEnemyObject',function()if pendingCollect then food.erase=state()end end)
hook('SetupFloateyNumber',function()if pendingCollect then assert(emu.getState()['cpu.a']==6);food.setup=state()end end)
hook('MarioSourcePowerupUpdate',function()
 if not food.collected or r('GuestPowerupActive')==0 then return end
 assert(food.ticks<60 and r('GuestPowerupAge')==food.ticks and r('GuestLegacyHurt')==0,'Exact real growth tick')
 food.ticks=food.ticks+1;local final=food.ticks==60
 returning(function(t)
  if final then
   assert(r('GuestPowerupActive')==0 and r('GuestPowerupAge')==60 and r('PlayerStatus')==1 and r('PlayerSize')==0 and active()and r('TimerControl')==0,'Actual growth completed')
   food.transaction_done={state=state(),pc=t.pc,sp=t.sp}
  else assert(r('GuestPowerupActive')==1 and r('GuestPowerupAge')==food.ticks and r('TimerControl')==255)end
 end)
end)
hook('StockTimerDEC',function()
 if not food.collected or food.credit then return end;local cpu=emu.getState();local i=cpu['cpu.x']
 if i~=food.collector.actor.slot or r('FloateyNum_Control',i)~=6 or r('FloateyNum_Timer',i)~=43 then return end
 assert(cpu['cpu.a']==43 and cpu['cpu.y']==6,'Actual delayed native score branch')
 food.credit_writer={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],state=state()};local before=score()
 returning(function(t)assert(score()==before+1000,'Real target delayed1000')
  food.credit={before=before,after=score(),state=state(),pc=t.pc,sp=t.sp}
 end)
end)
emu.addMemoryCallback(guard(function(_,v)
 if pendingCollect then if v==32 then food.sound.writes20=food.sound.writes20+1 end;if v==0 then food.sound.clears=food.sound.clears+1 end end
end),emu.callbackType.write,C.ram.Square2SoundQueue)
local function frames(n)for _=1,n do coroutine.yield()end end
local function press(bits)buttons=bits;frames(4);buttons={};frames(8)end
local function ready(fn)for _=1,900 do if fn()then return end;coroutine.yield()end;error('Actual frontend readiness bound')end
local task=coroutine.create(function()
 ready(function()return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end)
 press({start=true});ready(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end)
 assert(r('CrossoverMenuIndex')==0);for _=1,2 do press({select=true})end
 assert(r('SelectedCharacter')==0 and r('MarioVariant')==5 and r('X5ChrMode')==131,'Compiled Toad Select2')
 press({start=true});ready(active);menuDone=true;drive()
 while not stopped do coroutine.yield()end
end)
emu.addEventCallback(guard(function()polls=polls+1;emu.setInput(buttons,0)end),emu.eventType.inputPolled)
emu.addEventCallback(guard(function()
 frame=frame+1;assert(frame<5000 and mainEntries<3000,'Bounded firstM fixture')
 if not CPU_CONTROLLER_OPENING then local ok,why=coroutine.resume(task);assert(ok,why)end
end),emu.eventType.endFrame)
if CPU_CONTROLLER_OPENING then drive()end
