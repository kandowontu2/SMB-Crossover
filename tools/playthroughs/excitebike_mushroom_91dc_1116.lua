-- Ordinary current Excitebike first-M policy; all observations are read-only.
local frame,polls,mainEntries,mainReturns,motorEntries,motorReturns,movementEntries,movementReturns=0,0,0,0,0,0,0,0
local menuDone=CPU_CONTROLLER_OPENING or false
local stopped,buttons,phase,step=false,0,'opening',0
local pendingMain,pendingMovement,pendingMotor,pendingCollection
local dynamic,food,readback={},{births={},pickups={}},{}
local prelean,jump,routeEpoch=nil,nil,0
local function read(at)return emu.read(at,emu.memType.nesDebug)end
local function ram2(at)return emu.read(2*8192+(at&8191),emu.memType.nesWorkRam)end
local function ram3(at)return emu.read(3*8192+(at&8191),emu.memType.nesWorkRam)end
local function r(n,i)return read(assert(C.ram[n],n)+(i or 0))end
local function pos(lo,hi,i)return r(lo,i)+256*r(hi,i)end
local function score()local n=0;for i=0,5 do local d=r('Player1ScoreDisplay',i);assert(d<10);n=n*10+d end;return n end
local function active()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function state()return{frame=frame,Main=mainReturns,motor=motorReturns,guest=movementReturns,route_epoch=routeEpoch,phase=phase,
 x=pos('Player_X_Position','Player_PageLoc'),y=r('Player_Y_Position'),high=r('Player_Y_HighPos'),native=r('Player_State'),
 power=r('PlayerStatus'),engine=r('GameEngineSubroutine'),active=r('GuestPowerupActive'),age=r('GuestPowerupAge'),timer=r('TimerControl'),
 lives=r('NumberofLives'),star=r('StarInvincibleTimer'),score=score(),speed=ram2(0x90)+256*ram2(0x94),crash=ram2(0x98),
 recovery=ram2(0x9c),angle=ram2(0xac),air=ram2(0xb0),heat=ram2(0x3e0)}end
local function actor(i)return{slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),kind=r('PowerUpType',i),state=r('Enemy_State',i),
 x=pos('Enemy_X_Position','Enemy_PageLoc',i),y=r('Enemy_Y_Position',i)}end
local function box(name,i)local q={};for j=0,3 do q[#q+1]=r(name,(i or 0)*4+j)end;return q end
local function json(v)
 if v==nil then return'null'elseif type(v)=='string'then return string.format('%q',v)elseif type(v)~='table'then return tostring(v)end
 local a={};if#v>0 then for i,x in ipairs(v)do a[i]=json(x)end;return'['..table.concat(a,',')..']'end
 for k,x in pairs(v)do a[#a+1]=json(tostring(k))..':'..json(x)end;table.sort(a);return'{'..table.concat(a,',')..'}'
end
local function finish(ok,why)
 if stopped then return end;stopped=true;buttons=0
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=why,ROM_SHA256=C.sha,identity=C.key,kind=C.kind,physical_frames=frame,input_polls=polls,
  Main_entries=mainEntries,Main_returns=mainReturns,Motor_entries=motorEntries,Motor_returns=motorReturns,
  Movement_entries=movementEntries,Movement_returns=movementReturns,pendingMain=pendingMain~=nil,pendingMotor=pendingMotor~=nil,
  pendingMovement=pendingMovement~=nil,food=food,readback=readback,terminal=state(),gameplay_seeds=0,game_state_writes=false,outputs=0,full_stage_claim=false}))
 emu.stop(ok and 0 or 1)
end
local function guard(fn)return function(...)if stopped then return end;local ok,why=pcall(fn,...);if not ok then finish(false,tostring(why))end end end
local function hook(name,fn)
 local h=assert(C.hooks[name]);emu.addMemoryCallback(guard(function()
  local p=emu.convertAddress(h.pc);local kind=h.work and emu.memType.nesWorkRam or emu.memType.nesPrgRom
  if not p or p.memType~=kind or p.address~=h.offset then return end
  if h.work and r('SelectedCharacter')~=37 then return end
  for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Exact '..name)end;fn()
 end),emu.callbackType.exec,h.pc)
end
local function returning(fn)
 local cpu=emu.getState();local s=cpu['cpu.sp'];local pc=(read(256+((s+1)&255))+256*read(256+((s+2)&255))+1)&65535
 local q={pc=pc,sp=(s+2)&255,entryPC=cpu['cpu.pc'],entrySP=s}
 if not dynamic[pc]then dynamic[pc]={};emu.addMemoryCallback(guard(function()
  local list=dynamic[pc];local s=emu.getState()['cpu.sp']
  for i=#list,1,-1 do local t=list[i];if t.sp==s then table.remove(list,i);t.fn(t)end end
 end),emu.callbackType.exec,pc)end
 q.fn=fn;dynamic[pc][#dynamic[pc]+1]=q;return q
end
local function identity()
 assert(r('SelectedCharacter')==37 and r('FmAlts')&16==0 and r('CrossoverBehaviorVersion')==0,'Actual Easy Excitebike')
 assert(r('WorldNumber')==0 and r('LevelNumber')==0,'Actual1-1')
 assert(r('CheatInvincible')==0 and r('CheatStartLevel')==0 and r('NumberofLives')==2,'Living no-cheat route')
 assert(ram2(0x800)==0xa7,'Actual source ready')
end
local function observe()
 for i=0,5 do local a=actor(i);if a.flag==1 and a.id==46 then
  assert(a.kind==0,'Actual first authored mushroom')
  food.births[1]=food.births[1]or{state=state(),actor=a};assert(food.births[1].actor.x==336,'Actual authored first block')
  if a.state>=128 then food.births[1].mature=food.births[1].mature or{state=state(),actor=a}end
 end end
end
local function endpoint()
 if pendingMain or pendingMovement or pendingMotor then return end
 local q=food.pickups[1];if not q or not q.credit or not q.transaction_done then return end
 if not q.resumeBase then q.resumeBase=movementReturns;q.motorBase=motorReturns end
 local n=movementReturns-q.resumeBase;q.resumed=n;assert(n<=25,'Exactly25 returned original movement updates')
 if n==25 then
  identity();assert(q.birth and q.mature and q.collected and q.erase and q.setup and q.sound.writes20>0,'All real M lifecycle gates')
  assert(q.ticks==60 and r('PlayerStatus')==1 and r('GuestPowerupActive')==0 and r('GuestPowerupAge')==60 and r('TimerControl')==0 and active(),'Genuine60-tick tier retained')
  assert(motorReturns-q.motorBase==25 and motorEntries==motorReturns and movementEntries==movementReturns and mainEntries==mainReturns,'Balanced original motor/movement/Main')
  q.actual_Main_return={pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],state=state()}
  finish(true,'Natural Excitebike M/60 native ticks/1000 and25 returned original motor+movement at completed Main')
 end
end
local function drive()
 if not menuDone then return end;identity();observe();assert(routeEpoch<1400,'Bounded ordinary first-M policy')
 local s=state();buttons=0
 if phase=='opening'then
  buttons=step<4 and 0 or step<36 and 1 or step<52 and 129 or 1;step=step+1
  if step==60 then phase='approach';step=0 end
 elseif s.active~=0 then assert(food.pickups[1],'Freeze requires real collection')
 elseif food.pickups[1]then buttons=0
 elseif phase=='approach'then buttons=65;if s.x>=400 then phase='recover';buttons=0 end
 elseif phase=='recover'then if s.speed==0 and s.crash==0 then phase='return';buttons=66 end
 elseif phase=='return'then buttons=66;if s.x<=365 then phase='prelean';prelean=routeEpoch;buttons=74 end
 elseif phase=='prelean'then buttons=74;if routeEpoch-prelean>=4 then phase='jump';jump=routeEpoch;buttons=202 end
 elseif phase=='jump'then buttons=routeEpoch-jump<8 and 202 or 0;if routeEpoch-jump>=8 then phase='wait'end
 elseif phase~='wait'then error('Unknown first-M phase '..phase)end
 routeEpoch=routeEpoch+1
end
hook('GameLoop',function()
 assert(not pendingMain,'Synchronous Main');mainEntries=mainEntries+1
 local cpu=emu.getState();local s=cpu['cpu.sp'];local pc=read(256+((s+1)&255))+256*read(256+((s+2)&255))+1
 assert(pc==C.hooks.MainReturn0.pc or pc==C.hooks.MainReturn1.pc,'Authenticated Main caller');pendingMain={pc=pc,sp=(s+2)&255}
end)
for i=0,1 do local name='MainReturn'..i;hook(name,function()
 local cpu=emu.getState();if pendingMain and pendingMain.pc==cpu['cpu.pc']and pendingMain.sp==cpu['cpu.sp']then
  pendingMain=nil;mainReturns=mainReturns+1;endpoint();if not stopped then drive()end
 end
end)end
hook('ExHostConstruct',function()
 if readback.constructor then return end
 for i=1,#C.kernel_hex,2 do assert(ram3((i-1)//2)==tonumber(C.kernel_hex:sub(i,i+1),16),'All6144 current kernel before constructor')end
 for i=1,#C.metadata_hex,2 do assert(ram2(0x1000+(i-1)//2)==tonumber(C.metadata_hex:sub(i,i+1),16),'All2048 current metadata')end
 for bank=2,3 do for i=1,32,2 do assert(emu.read(bank*8192+0x1fe0+(i-1)//2,emu.memType.nesWorkRam)==tonumber(C.cookie:sub(i,i+1),16),'Both full16 current cookies')end end
 readback.constructor={pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],kernel=6144,metadata=2048,both_full16cookies=true}
end)
hook('ExHostMovement',function()
 assert(not pendingMovement,'Previous movement returned')
 local q={accepted=false};pendingMovement=q
 returning(function(t)
  assert(pendingMovement==q and not pendingMotor,'Motor completed before public movement')
  if q.accepted then movementReturns=movementReturns+1 end;pendingMovement=nil
 end)
end)
hook('ExMovementAccepted',function()assert(pendingMovement and not pendingMovement.accepted);pendingMovement.accepted=true;movementEntries=movementEntries+1 end)
hook('ExMotorAll',function()
 assert(pendingMovement and pendingMovement.accepted and not pendingMotor,'Original motor only in accepted real movement')
 motorEntries=motorEntries+1;pendingMotor=returning(function(t)pendingMotor=nil;motorReturns=motorReturns+1 end)
end)
hook('HandlePowerUpCollision',function()
 if not menuDone then return end;identity();observe()
 local cpu=emu.getState();local i=cpu['cpu.x'];local a=actor(i)
 assert(i==5 and a.flag==1 and a.id==46 and a.kind==0 and a.state>=128,'Real mature M collector')
 assert(not food.pickups[1]and food.births[1]and food.births[1].mature,'Unique genuine lifecycle')
 local pb,ib=box('BoundingBox_UL_Corner'),box('EnemyBoundingBoxCoord',i)
 local w=math.min(pb[3],ib[3])-math.max(pb[1],ib[1])+1;local h=math.min(pb[4],ib[4])-math.max(pb[2],ib[2])+1;assert(w>0 and h>0,'Actual positive native overlap')
 local q={before=state(),actor=a,birth=food.births[1],mature=food.births[1].mature,player_box=pb,item_box=ib,overlap={w,h},pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],ticks=0,sound={writes20=0,clears=0}}
 food.pickups[1]=q;pendingCollection=q
 returning(function(t)
  assert(q.erase and q.setup and r('Enemy_Flag',i)==0 and r('FloateyNum_Control',i)==6,'Physical erase/popup6')
  assert(q.sound.writes20>0 and emu.getState()['cpu.ps']&1~=0,'Native grab cue20 and accepted carry')
  assert(r('GuestPowerupActive')==1 and r('GuestPowerupAge')==0 and r('GuestPowerupTarget')==1 and r('TimerControl')==255 and r('GameEngineSubroutine')==9,'Real earned tier transaction')
  q.collected={state=state(),pc=t.pc,sp=t.sp};pendingCollection=nil;buttons=0
 end)
end)
hook('EraseEnemyObject',function()if pendingCollection then pendingCollection.erase=state()end end)
hook('SetupFloateyNumber',function()if pendingCollection then assert(emu.getState()['cpu.a']==6);pendingCollection.setup=state()end end)
hook('GuestPowerupUpdate',function()
 local q=food.pickups[1];if not q or r('GuestPowerupActive')==0 then return end
 assert(q.collected and q.ticks<60 and r('GuestPowerupAge')==q.ticks,'Exact real transaction age')
 q.ticks=q.ticks+1;local terminal=q.ticks==60
 returning(function(t)if terminal then
  assert(r('GuestPowerupAge')==60 and r('GuestPowerupActive')==0 and r('PlayerStatus')==1 and active()and r('TimerControl')==0,'Real60 tick recovery')
  q.transaction_done={state=state(),pc=t.pc,sp=t.sp}
 else assert(r('GuestPowerupActive')==1 and r('TimerControl')==255 and r('GameEngineSubroutine')==9)end end)
end)
hook('StockTimerDEC',function()
 local q=food.pickups[1];if not q or not q.collected or q.credit then return end
 local cpu=emu.getState();local i=cpu['cpu.x']
 if i~=q.actor.slot or r('FloateyNum_Control',i)~=6 or r('FloateyNum_Timer',i)~=43 then return end
 assert(cpu['cpu.a']==43 and cpu['cpu.y']==6,'Actual delayed score branch')
 q.credit_writer={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],state=state()};local before=score()
 returning(function(t)assert(score()==before+1000,'Actual delayed1000')
  q.credit={before=before,after=score(),state=state(),pc=t.pc,sp=t.sp}
 end)
end)
emu.addMemoryCallback(guard(function(_,v)
 if pendingCollection then if v==32 then pendingCollection.sound.writes20=pendingCollection.sound.writes20+1 end
 if v==0 then pendingCollection.sound.clears=pendingCollection.sound.clears+1 end end
end),emu.callbackType.write,C.ram.Square2SoundQueue)
local function frames(n)for _=1,n do coroutine.yield()end end
local function press(bits)buttons=bits;frames(4);buttons=0;frames(8)end
local function ready(fn)for _=1,900 do if fn()then return end;coroutine.yield()end;error('Frontend readiness bound')end
local task=coroutine.create(function()
 ready(function()return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end)
 press(16);ready(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end)
 assert(r('CrossoverMenuIndex')==0);for _,bits in ipairs(C.navigation)do press(bits)end
 assert(r('CrossoverMenuIndex')==29 and r('SelectedCharacter')==37 and r('FmAlts')&16==0,'Compiled Excitebike')
 press(16);ready(function()return active()end);menuDone=true;assert(r('PlayerStatus')==0);drive()
 while not stopped do coroutine.yield()end
end)
emu.addEventCallback(guard(function()
 polls=polls+1;local b=buttons;emu.setInput({right=b&1~=0,left=b&2~=0,down=b&4~=0,up=b&8~=0,start=b&16~=0,select=b&32~=0,b=b&64~=0,a=b&128~=0},0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guard(function()
 frame=frame+1;assert(frame<5000 and mainEntries<3000,'Bounded physical/Main first-M')
 if not CPU_CONTROLLER_OPENING then local ok,why=coroutine.resume(task);assert(ok,why)end
end),emu.eventType.endFrame)
if CPU_CONTROLLER_OPENING then drive()end

