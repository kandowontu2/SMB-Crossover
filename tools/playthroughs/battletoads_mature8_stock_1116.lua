local function stockActor()
 for i=0,5 do local a=actor(i);if a.flag==1 and a.id==46 and a.kind==C.stock_type then return a end end
end
local function stockObserve()
 local a=stockActor();if not a then return end
 stock.born=stock.born or{state=state(),actor=a}
 assert(stock.born.actor.x==(C.stock_type==3 and 1024 or 1616),'Actual authored stock block')
 if a.state>=128 then stock.mature=stock.mature or{state=state(),actor=a}end
end
local function stockEndpoint()
 if not stock.credit or pendingMain or pendingGuest then return end
 local n=guestReturns-stock.credit.guest;stock.resumed=n;assert(n<=25,'Exactly25 original stock returns')
 if n==25 then
  identity();assert(food.M_scope_passed and stock.born and stock.mature and stock.collector and stock.erase and stock.setup and stock.collected,'Complete genuine stock scope')
  assert(r('PlayerStatus')==stock.collector.state.power and r('GuestPowerupActive')==0,'Stock preserves native food policy')
  if C.stock_type==3 then assert(stock.life_credit and r('NumberofLives')==3 and r('BtLife',r('CurrentPlayer'))==3,'Real delayed life preserved')
  else assert(stock.score_credit and r('StarInvincibleTimer')>0 and r('NumberofLives')==2,'Real delayed1000 and activeStar')end
  assert(mainEntries==mainReturns and guestEntries==guestReturns,'Balanced original Main/worker returns')
  stock.actual_Main_return={pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],state=state()}
  finish(true,'Natural Battletoads '..C.stock_kind..' after genuineM and25 actual returned original workers at Main return')
 end
end
local function drive()
 if not food.M_scope_passed then foodDrive();return end
 if not menuDone or not active()then buttons={};return end
 identity();stockObserve();buttons={};if stock.collected then return end
 local c=context();local a=stockActor()
 if a then
  if a.state<128 then return end
  stock.phase='collect';local dx=a.x-c.x;buttons={right=dx>3,left=dx< -4}
  if c.grounded and a.y<c.y-12 and math.abs(dx)<48 and not c.lastA then stock.chaseJump=guestReturns end
  if stock.chaseJump and guestReturns-stock.chaseJump<35 then buttons.a=true end
  assert(guestReturns-stock.since<1600,'Natural stock collection bound');return
 end
 local approach=C.stock_type==3 and 978 or 1560
 local center=C.stock_type==3 and 1018 or 1610
 if stock.phase=='travel'and c.x<approach then buttons=travel(c);return end
 if stock.phase=='travel'then stock.phase='align';stock.alignSince=guestReturns end
 if stock.phase=='align'then
  assert(guestReturns-stock.alignSince<400,'Ordinary authored stock alignment')
  if not c.grounded or c.y~=176 then return end
  buttons={right=c.x<center-1,left=c.x>center+1}
  if math.abs(c.x-center)<=1 and c.vx==0 and not c.lastA then stock.settle=(stock.settle or 0)+1 else stock.settle=0 end
  if stock.settle>=6 then
   stock.phase='head';stock.headAt=guestReturns;stock.request=state()
   stock.authored_tile=c.block(C.stock_type==3 and 1024 or 1616,C.stock_type==3 and 128 or 144)
   if C.stock_type==3 then assert(stock.authored_tile==96,'Actual authored hidden60')end
   buttons={a=true}
  end
 elseif stock.phase=='head'then
  assert(guestReturns-stock.headAt<160,'Actual stock head admission bound')
  buttons={a=guestReturns-stock.headAt<35}
 end
end
hook('BtPickup',function()
 local cpu=emu.getState();local i=cpu['cpu.x'];local a=actor(i)
 if a.flag~=1 or a.id~=46 or a.kind~=C.stock_type then return end
 stockObserve();assert(stock.mature and a.state>=128 and not stock.collected,'Actual mature stock collector')
 local pb,ib=box('BoundingBox_UL_Corner'),box('EnemyBoundingBoxCoord',i)
 local w=math.min(pb[3],ib[3])-math.max(pb[1],ib[1])+1;local h=math.min(pb[4],ib[4])-math.max(pb[2],ib[2])+1
 assert(w>0 and h>0,'Positive native inclusive stock overlap')
 stock.collector={state=state(),actor=a,player_box=pb,item_box=ib,overlap={w,h},pc=cpu['cpu.pc'],sp=cpu['cpu.sp']}
 returning(function(t)
  local popup=C.stock_type==3 and 11 or 6
  assert(stock.erase and stock.setup and r('Enemy_Flag',i)==0 and r('FloateyNum_Control',i)==popup,'Actual stock erase/popup')
  assert(r('Square2SoundQueue')==32,'Native grabcue32')
  if C.stock_type==2 then assert(r('StarInvincibleTimer')==35 and r('AreaMusicQueue')==64,'NativeStar35/music64')end
  stock.collected={state=state(),pc=t.pc,sp=t.sp};buttons={}
 end)
end)
hook('EraseEnemyObject',function()if stock.collector and not stock.collected then stock.erase=state()end end)
hook('SetupFloateyNumber',function()if stock.collector and not stock.collected then assert(emu.getState()['cpu.a']==6);stock.setup=state()end end)
hook('StockTimerDEC',function()
 if C.stock_type~=2 or not stock.collected or stock.score_credit then return end
 local cpu=emu.getState();local i=cpu['cpu.x']
 if i~=stock.collector.actor.slot or r('FloateyNum_Control',i)~=6 or r('FloateyNum_Timer',i)~=43 then return end
 assert(cpu['cpu.a']==43 and cpu['cpu.y']==6,'ActualStar credit writerA43/Y6')
 stock.credit_writer={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],state=state()};local before=score()
 returning(function(t)
  assert(score()==before+1000,'Actual delayed stock1000 credit')
  stock.score_credit={before=before,after=score(),state=state(),pc=t.pc,sp=t.sp};stock.credit={guest=guestReturns,state=state()}
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
 stock.life_credit={before=stock.life_before,state=state()};stock.credit={guest=guestReturns,state=state()}
end)
