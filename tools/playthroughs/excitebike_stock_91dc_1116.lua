local pendingStock
local function stockObserve()
 for i=0,5 do local a=actor(i);if a.flag==1 and a.id==46 then
  assert(a.kind==C.stock_type,'Actual authored stock type; no forced kind')
  stock.born=stock.born or{state=state(),actor=a};assert(stock.born.actor.x==C.target_x,'Actual authored stock location')
  if a.state>=128 then stock.mature=stock.mature or{state=state(),actor=a}end
  return a
 end end
end
local function bits(b)local n=0;for k,v in pairs({right=1,left=2,down=4,up=8,b=64,a=128})do if b[k]then n=n+v end end;return n end
local function stockDrive()
 identity();stockObserve();buttons=0;routeEpoch=routeEpoch+1
 assert(mainReturns-stock.since<3500,'Bounded ordinary stock route')
 local s=state();stock.last=stock.last or{};stock.last[#stock.last+1]=s;if#stock.last>12 then table.remove(stock.last,1)end
 if stock.collected or not active()then return end
 local a=stockObserve()
 if a then
  if a.state<128 then return end
  phase='stock-collect';stock.phase='collect'
  local dx=a.x-s.x
  if not stock.chase and s.native==0 and s.air==0 and s.crash==0 and s.heat==0 and math.abs(dx)<72 then
   stock.chase={since=mainReturns,dir=dx>=0 and 1 or 2,request=state()}
  end
  if stock.chase then
   local n=mainReturns-stock.chase.since;local dir=stock.chase.dir
   if n<4 then buttons=dir+64+8 elseif n<12 then buttons=dir+64+8+128
   elseif n>=24 and s.native==0 and s.air==0 then stock.chase=nil end
  elseif math.abs(dx)>8 then buttons=(dx>0 and 1 or 2)+64 end
  return
 end
 if stock.phase=='travel'then
  phase='stock-travel';buttons=bits(travel())
  if s.x>=C.target_x+64 then stock.phase='recover';phase='stock-recover';buttons=0;stock.approach=state();travelJump=nil end
 elseif stock.phase=='recover'then
  phase='stock-recover'
  if s.speed==0 and s.crash==0 and s.native==0 and s.air==0 then
   stock.phase='return';phase='stock-return';buttons=66;stock.stand=state()
  end
 elseif stock.phase=='return'then
  phase='stock-return';buttons=66
  if s.x<=C.target_x+29 then stock.phase='prelean';phase='stock-prelean';stock.prelean=mainReturns;stock.prelean_request=state();buttons=74 end
 elseif stock.phase=='prelean'then
  phase='stock-prelean';buttons=74
  if mainReturns-stock.prelean>=4 then
   stock.phase='head';phase='stock-head';stock.head=mainReturns;stock.head_request=state()
   stock.authored_tile=block(C.target_x,C.target_y);if C.stock_type==3 then assert(stock.authored_tile==96,'Actual hidden60 before head')end
   buttons=202
  end
 elseif stock.phase=='head'then
  phase='stock-head';assert(mainReturns-stock.head<240,'Ordinary stock head admission bound')
  buttons=mainReturns-stock.head<8 and 202 or 0
 elseif stock.phase~='collect'then error('Unknown natural stock phase '..stock.phase)end
end
local function drive()
 if not food.M_scope_passed then foodDrive();return end
 if menuDone then stockDrive()end
end
local function endpoint()
 foodEndpoint();if stopped or not food.M_scope_passed or not stock.collected or not stock.credit then return end
 if C.stock_type==1 and not stock.transaction_done then return end
 if pendingMain or pendingMotor or pendingMovement then return end
 if not stock.resumeBase then stock.resumeBase=movementReturns;stock.motorBase=motorReturns end
 local n=movementReturns-stock.resumeBase;stock.resumed=n;assert(n<=25,'Exactly25 resumed original stock returns')
 if n==25 then
  identity();assert(stock.born and stock.mature and stock.collector and stock.erase and stock.setup and stock.sound.writes20>0,'Complete genuine stock lifecycle')
  if C.stock_type==1 then
   assert(stock.ticks==60 and r('PlayerStatus')==2 and r('GuestPowerupAge')==60 and r('GuestPowerupActive')==0 and r('TimerControl')==0,'Natural Flower tier2 after60')
  elseif C.stock_type==2 then assert(r('StarInvincibleTimer')>0 and r('PlayerStatus')==1,'Natural Star and originalM tier retained')
  else assert(stock.life_credit and r('NumberofLives')==3 and r('PlayerStatus')==1,'Real earned life3/tier1 retained')end
  assert(active()and motorReturns-stock.motorBase==25 and motorEntries==motorReturns and movementEntries==movementReturns and mainEntries==mainReturns,'Balanced actual stock Main/motor/movement')
  stock.actual_Main_return={pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],state=state()}
  finish(true,'Natural Excitebike M then '..C.kind..' effect/credit and25 original returned updates at completed Main')
 end
end
hook('HandlePowerUpCollision',function()
 if not food.M_scope_passed then return end;identity();stockObserve()
 local cpu=emu.getState();local i=cpu['cpu.x'];local a=actor(i)
 assert(i==5 and a.flag==1 and a.id==46 and a.kind==C.stock_type and a.state>=128,'Real mature stock collector')
 assert(stock.born and stock.mature and not stock.collected,'Actual stock birth and maturity')
 local pb,ib=box('BoundingBox_UL_Corner'),box('EnemyBoundingBoxCoord',i)
 local w=math.min(pb[3],ib[3])-math.max(pb[1],ib[1])+1;local h=math.min(pb[4],ib[4])-math.max(pb[2],ib[2])+1;assert(w>0 and h>0,'Positive actual native stock overlap')
 stock.collector={state=state(),actor=a,player_box=pb,item_box=ib,overlap={w,h},pc=cpu['cpu.pc'],sp=cpu['cpu.sp']}
 stock.sound={writes20=0,clears=0};stock.ticks=0;pendingStock=true
 returning(function(t)
  assert(stock.erase and stock.setup and r('Enemy_Flag',i)==0 and stock.sound.writes20>0 and emu.getState()['cpu.ps']&1~=0,'Real stock erase/cue20/accepted')
  assert(r('FloateyNum_Control',i)==(C.stock_type==3 and 11 or 6),'Actual stock popup')
  if C.stock_type==1 then
   assert(stock.collector.state.power==1 and r('GuestPowerupTarget')==2 and r('GuestPowerupActive')==1 and r('GuestPowerupAge')==0 and r('TimerControl')==255 and r('GameEngineSubroutine')==9,'Natural Flower hosted tier2')
  elseif C.stock_type==2 then assert(r('StarInvincibleTimer')==35 and r('AreaMusicQueue')==64,'Actual native Star35/music64')end
  stock.collected={state=state(),pc=t.pc,sp=t.sp};pendingStock=nil;buttons=0
 end)
end)
hook('EraseEnemyObject',function()if pendingStock then stock.erase=state()end end)
hook('SetupFloateyNumber',function()if pendingStock then assert(emu.getState()['cpu.a']==6);stock.setup=state()end end)
hook('GuestPowerupUpdate',function()
 if not food.M_scope_passed or C.stock_type~=1 or not stock.collected or r('GuestPowerupActive')==0 then return end
 assert(stock.ticks<60 and r('GuestPowerupAge')==stock.ticks,'Exact Flower native age');stock.ticks=stock.ticks+1;local terminal=stock.ticks==60
 returning(function(t)
  if terminal then
   assert(r('GuestPowerupActive')==0 and r('GuestPowerupAge')==60 and r('PlayerStatus')==2 and r('TimerControl')==0 and active(),'Flower60 actual recovery')
   stock.transaction_done={state=state(),pc=t.pc,sp=t.sp}
  else assert(r('GuestPowerupActive')==1 and r('TimerControl')==255 and r('GameEngineSubroutine')==9)end
 end)
end)
hook('StockTimerDEC',function()
 if C.stock_type==3 or not stock.collected or stock.credit then return end
 local cpu=emu.getState();local i=cpu['cpu.x']
 if i~=stock.collector.actor.slot or r('FloateyNum_Control',i)~=6 or r('FloateyNum_Timer',i)~=43 then return end
 assert(cpu['cpu.a']==43 and cpu['cpu.y']==6,'Actual stock credit branchA43/Y6')
 stock.credit_writer={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],state=state()};local before=score()
 returning(function(t)assert(score()==before+1000,'Actual stock1000 credit')
  stock.credit={before=before,after=score(),state=state(),pc=t.pc,sp=t.sp}
 end)
end)
hook('LifeBefore',function()
 if C.stock_type~=3 or not stock.collected or stock.life_credit then return end
 local cpu=emu.getState();if cpu['cpu.x']~=stock.collector.actor.slot then return end
 assert(cpu['cpu.y']==11 and r('FloateyNum_Control',cpu['cpu.x'])==11 and r('NumberofLives')==2,'Actual target delayed lifeINC')
 stock.life_before={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],state=state()}
end)
hook('LifeAfter',function()
 if not stock.life_before or stock.life_credit then return end
 assert(r('NumberofLives')==3 and r('Square2SoundQueue')==64,'ActualINC2to3/cue64')
 stock.life_credit={state=state(),pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp']};stock.credit=stock.life_credit
end)
emu.addMemoryCallback(guard(function(_,v)
 if pendingStock then if v==32 then stock.sound.writes20=stock.sound.writes20+1 end;if v==0 then stock.sound.clears=stock.sound.clears+1 end end
end),emu.callbackType.write,C.ram.Square2SoundQueue)

