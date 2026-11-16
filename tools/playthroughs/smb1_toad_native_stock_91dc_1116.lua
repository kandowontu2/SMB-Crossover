-- Separate authored stock after the fully asserted genuine M prefix.
local pendingStock
local function stockTarget()
 for i=0,5 do local a=actor(i);if a.flag==1 and a.id==46 and a.kind==C.stock_type then return a end end
end
local function stockObserve()
 local a=stockTarget();if not a then return end
 if not stock.born then assert(a.x==C.target_x,'Actual authored stock column');stock.born={state=state(),actor=a}end
 if a.state>=128 then stock.mature=stock.mature or{state=state(),actor=a}end
 return a
end
local function chooseStock(c)
 local a=stockObserve()
 if a then
  if a.state<128 then return{}end
  stock.phase='collect';local dx=a.x-c.x;local b={right=dx>3,left=dx< -3}
  if c.grounded and a.y<c.y-12 and math.abs(dx)<48 and(not stock.chaseJump or guestReturns-stock.chaseJump>40)then stock.chaseJump=guestReturns end
  if stock.chaseJump and guestReturns-stock.chaseJump<24 then b.a=true end
  return b
 end
 if stock.phase=='travel'and c.x<C.target_x-56 then return travel(c)end
 if stock.phase=='travel'then stock.phase='align';stock.phaseStart=guestReturns end
 if stock.phase=='align'then
  assert(guestReturns-stock.phaseStart<350,'One ordinary stock alignment')
  local v=c.vx<128 and c.vx or c.vx-256;local stop=c.x+v*math.abs(v)/32;local center=C.target_x-6
  local b={right=stop<center-1,left=stop>center+1}
  if math.abs(c.x-center)<=2 and math.abs(v)<=1 and c.grounded and not lastA then stock.settle=(stock.settle or 0)+1 else stock.settle=0 end
  if stock.settle>=8 then
   stock.phase='head';stock.headAt=guestReturns;stock.request=state();stock.authored_tile=c.block(C.target_x,C.target_y)
   if C.stock_type==3 then assert(stock.authored_tile==96,'Real hidden60 before ordinary head jump')end
   b={a=true}
  end
  return b
 elseif stock.phase=='head'then
  assert(guestReturns-stock.headAt<160,'One actual stock head-admission bound')
  if c.state==1 and c.vy>=128 then stock.admission=stock.admission or state()end
  return{a=guestReturns-stock.headAt<24}
 end
 error('Unknown stock control phase '..stock.phase)
end
stockDrive=function()
 if not menuDone then return end;identity();stockObserve()
 if not active()or stock.collected then buttons={};return end
 assert(r('PlayerStatus')==1,'Genuine firstM tier retained before stock')
 assert(guestReturns-stock.since<4200,'Bounded ordinary stock route')
 buttons=chooseStock(context());lastA=not not buttons.a
end
local function endpoint()
 foodEndpoint();if not food.M_scope_passed or not stock.credit or pendingMain or pendingGuest or pendingStock then return end
 if C.stock_type==1 and not stock.transaction_done then return end
 if not stock.resumeBase then stock.resumeBase=guestReturns end
 local n=guestReturns-stock.resumeBase;stock.resumed=n;assert(n<=25,'Exactly25 actual stock native returns')
 if n==25 then
  identity();assert(active()and stock.born and stock.mature and stock.collector and stock.erase and stock.setup and stock.collected,'Complete actual stock lifecycle')
  assert(stock.sound.writes20>0 and mainEntries==mainReturns and guestEntries==guestReturns,'Actual cue and balanced Main/native movement')
  if C.stock_type==1 then assert(stock.ticks==60 and r('PlayerStatus')==2 and r('GuestPowerupAge')==60 and r('GuestPowerupActive')==0 and r('TimerControl')==0,'Real Flower60/native tier2')
  elseif C.stock_type==2 then assert(r('StarInvincibleTimer')>0 and r('PlayerStatus')==1 and r('NumberofLives')==2,'Real Star and firstM retained')
  else assert(stock.life_credit and r('NumberofLives')==3 and r('PlayerStatus')==1,'Genuine delayed earned life3/tier1')end
  stock.actual_Main_return={pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],state=state()}
  finish(true,'Natural SMB1 Toad M then '..C.kind..' and25 returned native movements at completedMain')
 end
end
hook('HandlePowerUpCollision',function()
 if not food.M_scope_passed then return end;identity();stockObserve();local cpu=emu.getState();local i=cpu['cpu.x'];local a=actor(i)
 assert(i==5 and a.flag==1 and a.id==46 and a.kind==C.stock_type and a.state>=128,'Actual mature expected stock')
 assert(stock.born and stock.mature and not stock.collected,'Genuine lifecycle before unique stock collector')
 local pb,ib=box('BoundingBox_UL_Corner'),box('EnemyBoundingBoxCoord',i)
 local w=math.min(pb[3],ib[3])-math.max(pb[1],ib[1])+1;local h=math.min(pb[4],ib[4])-math.max(pb[2],ib[2])+1
 assert(w>0 and h>0,'Actual positive inclusive native stock overlap')
 stock.collector={state=state(),actor=a,player_box=pb,item_box=ib,overlap={w,h},pc=cpu['cpu.pc'],sp=cpu['cpu.sp']}
 stock.sound={writes20=0,clears=0};stock.ticks=0;pendingStock=returning(function(t)
  local wanted=C.stock_type==3 and 11 or 6
  assert(stock.erase and stock.setup and r('Enemy_Flag',i)==0 and r('FloateyNum_Control',i)==wanted and stock.sound.writes20>0,'Actual stock erase/popup/cue20')
  if C.stock_type==1 then assert(r('GuestPowerupOld')==1 and r('GuestPowerupTarget')==2 and r('GuestPowerupActive')==1 and r('GuestPowerupAge')==0 and r('TimerControl')==255 and r('GameEngineSubroutine')==9,'Real tier1to2 Flower transaction')
  elseif C.stock_type==2 then assert(r('StarInvincibleTimer')==35 and r('AreaMusicQueue')==64,'Real native Star35/music64')end
  stock.collected={state=state(),pc=t.pc,sp=t.sp,P=emu.getState()['cpu.ps']};pendingStock=nil;buttons={}
 end)
end)
hook('EraseEnemyObject',function()if pendingStock then stock.erase=state()end end)
hook('SetupFloateyNumber',function()if pendingStock then assert(emu.getState()['cpu.a']==6);stock.setup=state()end end)
hook('MarioSourcePowerupUpdate',function()
 if C.stock_type~=1 or not stock.collected or r('GuestPowerupActive')==0 then return end
 assert(stock.ticks<60 and r('GuestPowerupAge')==stock.ticks and r('GuestLegacyHurt')==0,'Actual Flower growth tick')
 stock.ticks=stock.ticks+1;local final=stock.ticks==60
 returning(function(t)
  if final then
   assert(r('PlayerStatus')==2 and r('GuestPowerupAge')==60 and r('GuestPowerupActive')==0 and r('TimerControl')==0 and active(),'Actual Flower growth returned')
   stock.transaction_done={state=state(),pc=t.pc,sp=t.sp}
  else assert(r('GuestPowerupActive')==1 and r('GuestPowerupAge')==stock.ticks and r('TimerControl')==255)end
 end)
end)
hook('StockTimerDEC',function()
 if C.stock_type==3 or not stock.collected or stock.credit then return end;local cpu=emu.getState();local i=cpu['cpu.x']
 if i~=stock.collector.actor.slot or r('FloateyNum_Control',i)~=6 or r('FloateyNum_Timer',i)~=43 then return end
 assert(cpu['cpu.a']==43 and cpu['cpu.y']==6,'Actual native delayed score branch')
 stock.credit_writer={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],state=state()};local before=score()
 returning(function(t)assert(score()==before+1000,'Real stock1000 credit')
  stock.credit={before=before,after=score(),state=state(),pc=t.pc,sp=t.sp}
 end)
end)
hook('LifeBefore',function()
 if C.stock_type~=3 or not stock.collected or stock.life_credit then return end;local cpu=emu.getState()
 if cpu['cpu.x']~=stock.collector.actor.slot then return end
 assert(cpu['cpu.y']==11 and r('FloateyNum_Control',cpu['cpu.x'])==11 and r('NumberofLives')==2,'Actual target1UP INC boundary')
 stock.life_before={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],state=state()}
end)
hook('LifeAfter',function()
 if not stock.life_before or stock.life_credit then return end
 assert(r('NumberofLives')==3 and r('Square2SoundQueue')==64,'Actual delayed INC2to3/cue64')
 stock.life_credit={state=state(),pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp']};stock.credit=stock.life_credit
end)
emu.addMemoryCallback(guard(function(_,v)
 if pendingStock then if v==32 then stock.sound.writes20=stock.sound.writes20+1 end;if v==0 then stock.sound.clears=stock.sound.clears+1 end end
end),emu.callbackType.write,C.ram.Square2SoundQueue)
