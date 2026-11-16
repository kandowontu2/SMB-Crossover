-- Current Metal: ordinary controls, actual native transactions and returned work.
local frame,polls,mainEntries,mainReturns=0,0,0,0
local moveEntries,moveReturns,moveOK,stepEntries,stepReturns,stepOK=0,0,0,0,0,0
local menuDone=CPU_CONTROLLER_OPENING or false
local stopped,lastA,buttons=false,false,{}
local pendingMain,pendingMove,pendingStep,pendingCollect,pendingScore
local dynamic,readback={},{release={}}
local M={phase=0};local stock={phase='pipes',pipe=1}
local function read(a)return emu.read(a,emu.memType.nesDebug)end
local function src(a)return emu.read(2*8192+a,emu.memType.nesWorkRam)end
local function r(n,i)return read(assert(C.ram[n],n)+(i or 0))end
local function pos(lo,hi,i)return r(lo,i)+256*r(hi,i)end
local function score()local n=0;for i=0,5 do local d=r('Player1ScoreDisplay',i);assert(d<10);n=n*10+d end;return n end
local function active()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function state()return{Main=mainReturns,frame=frame,move=moveOK,step=stepOK,x=pos('Player_X_Position','Player_PageLoc'),y=r('Player_Y_Position'),high=r('Player_Y_HighPos'),native=r('Player_State'),vx=r('Player_X_Speed'),vy=r('Player_Y_Speed'),power=r('PlayerStatus'),lives=r('NumberofLives'),star=r('StarInvincibleTimer'),score=score(),engine=r('GameEngineSubroutine'),armor=src(0x5d0),weapon=src(0x718),ready=src(0x800),epoch=src(0x801),saved_life=src(0x83e),actor528=src(0x528),actor34=src(0x34),gravity=src(0x734)}end
local function actor(i)return{slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),kind=r('PowerUpType',i),state=r('Enemy_State',i),x=pos('Enemy_X_Position','Enemy_PageLoc',i),y=r('Enemy_Y_Position',i)}end
local function box(n,i)local b={};for j=0,3 do b[#b+1]=r(n,(i or 0)*4+j)end;return b end
local function json(v)
 if v==nil then return'null'elseif type(v)=='string'then return string.format('%q',v)elseif type(v)~='table'then return tostring(v)end
 local a={};if#v>0 then for i,x in ipairs(v)do a[i]=json(x)end;return'['..table.concat(a,',')..']'end
 for k,x in pairs(v)do a[#a+1]=json(tostring(k))..':'..json(x)end;table.sort(a);return'{'..table.concat(a,',')..'}'
end
local function finish(ok,why)
 if stopped then return end;stopped=true;buttons={}
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=why,ROM_SHA256=C.sha,identity='Metal Storm',kind=C.kind,Main_entries=mainEntries,Main_returns=mainReturns,
  Ms12Movement_entries=moveEntries,Ms12Movement_returns=moveReturns,Ms12Movement_accepted=moveOK,MsHostStep_entries=stepEntries,MsHostStep_returns=stepReturns,MsHostStep_accepted=stepOK,
  physical_frames=frame,input_polls=polls,M=M,stock=stock,readback=readback,terminal=state(),pendingMain=pendingMain~=nil,pendingMove=pendingMove~=nil,pendingStep=pendingStep~=nil,pendingCollect=pendingCollect~=nil,pendingScore=pendingScore~=nil,
  gameplay_seeds=0,game_state_writes=false,outputs=0,full_stage_claim=false}))
 emu.stop(ok and 0 or 1)
end
local function guard(fn)return function(...)if stopped then return end;local ok,why=pcall(fn,...);if not ok then finish(false,tostring(why))end end end
local function hook(name,fn)
 local h=assert(C.hooks[name]);emu.addMemoryCallback(guard(function()
  local p=emu.convertAddress(h.pc);local wanted=h.space=='wram'and emu.memType.nesWorkRam or emu.memType.nesPrgRom
  if not p or p.memType~=wanted or p.address~=h.offset then return end
  for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Actual current '..name)end;fn()
 end),emu.callbackType.exec,h.pc)
end
local function returning(fn)
 local cpu=emu.getState();local sp=cpu['cpu.sp'];local pc=(read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1)&65535
 local q={pc=pc,sp=(sp+2)&255,entryPC=cpu['cpu.pc'],entrySP=sp}
 if not dynamic[pc]then dynamic[pc]={};emu.addMemoryCallback(guard(function()
  local sp=emu.getState()['cpu.sp'];local list=dynamic[pc]
  for i=#list,1,-1 do local t=list[i];if t.sp==sp then table.remove(list,i);t.fn(t)end end
 end),emu.callbackType.exec,pc)end
 q.fn=fn;dynamic[pc][#dynamic[pc]+1]=q;return q
end
local function byte(hex,i)return tonumber(hex:sub(2*i+1,2*i+2),16)end
local function fullReadback(published)
 local headers={};for _,bank in ipairs({2,3})do
  local h={};for i=0,15 do local v=emu.read(bank*8192+0x1fe0+i,emu.memType.nesWorkRam);h[#h+1]=v
   if i==0 and not published then assert(v==0 or v==167)else assert(v==byte(C.cookie,i),'Full16 current Metal header')end
  end;headers[#headers+1]=h
 end
 for i=0,8191 do local expected=byte(C.actor_hex,i);if i>=0x1fe0 and i<0x1ff0 then expected=headers[2][i-0x1fe0+1]end
  assert(emu.read(3*8192+i,emu.memType.nesWorkRam)==expected,'Full8192 owning actor readback')
 end
 for i=0,3071 do assert(emu.read(2*8192+0xd00+i,emu.memType.nesWorkRam)==byte(C.renderer_hex,i),'Full3072 renderer readback')end
 for i=0,1023 do assert(emu.read(2*8192+0x1900+i,emu.memType.nesWorkRam)==byte(C.extra_hex,i),'Full1024 extra carrier readback')end
 return{pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],actor_bytes=8192,renderer_bytes=3072,extra_bytes=1024,both16_headers=headers}
end
hook('HeaderRelease',function()if#readback.release<2 then readback.release[#readback.release+1]=fullReadback(false)end end)
emu.addMemoryCallback(guard(function()
 if readback.first_private then return end;local cpu=emu.getState();local p=emu.convertAddress(cpu['cpu.pc'])
 if not p or p.memType~=emu.memType.nesWorkRam or p.address~=3*8192+(cpu['cpu.pc']&8191)then return end
 assert((cpu['cpu.pc']-0xa000)%3==0,'Actual typed row ingress');readback.first_private=fullReadback(true)
end),emu.callbackType.exec,0xa000,0xa06e)
local function identity()
 assert(r('SelectedCharacter')==35 and r('CrossoverMenuIndex')==11,'Actual compiled Metal owner')
 assert(r('CrossoverBehaviorVersion')==0 and r('CheatInvincible')==0 and r('CheatStartLevel')==0,'Easy/no cheats')
 assert(r('WorldNumber')==0 and r('LevelNumber')==0 and r('NumberofLives')==(stock.life_credit and 3 or 2)and r('GameEngineSubroutine')~=11,'Living authored1-1')
end
local function target(kind)for i=0,5 do local a=actor(i);if a.flag==1 and a.id==46 and a.kind==kind then return a end end end
local function observe(q,kind,x)
 local a=target(kind);if not a then return end
 if not q.born then assert(a.x==x,'Actual authored item column');q.born={state=state(),actor=a}end
 if a.state>=128 then q.mature=q.mature or{state=state(),actor=a}end
 return a
end
local function context()
 local s=state();local c={x=s.x,y=s.y,native=s.native,grounded=s.native==0,vx=s.vx,vy=s.vy,camera=pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc')}
 c.block=function(x,y)if y<32 or y>=240 then return 0 end;return r('Block_Buffer_1',(x//256)%2*208+((y-32)//16)*16+(x%256)//16)end;return c
end
local function mushroom(c)
 local tick=stepOK-(M.phaseStart or 0);local b={b=true}
 if M.phase==0 then b.right=true;if c.x>=105 then M.phase=1;M.phaseStart=stepOK end
 elseif M.phase==1 then b.right=true;b.a=tick<35;if tick>=50 then M.phase=2 end
 elseif M.phase==2 then b.right=c.x<336;if c.x>=336 then M.phase=3;M.phaseStart=stepOK;M.head_request=state()end
 elseif M.phase==3 then b.a=tick<35;if tick>=65 then M.phase=4 end
 else b.right=true end
 return b
end
local PIPES={{448,144},{592,128},{720,112},{896,112}}
local GAPS={{1104,1136},{1376,1424}}
local function navigation(c)
 if stock.pipe<=4 then
  local p=PIPES[stock.pipe];local q=stock.pipeJump
  if not q and c.x>=p[1]-64 and c.grounded and not lastA then
   assert(c.block(p[1],p[2]+32)~=0,'Actual authored pipe cap');q={since=stepOK,request=state(),left=p[1],stand=p[2]};stock.pipeJump=q
  end
  if not q then return{right=true,b=true}end
  assert(stepOK-q.since<200,'One ordinary pipe mount');local center=p[1]+12
  if c.grounded and c.y<=p[2]+2 and c.x>=p[1]-4 and c.x<=p[1]+24 then
   q.landed=state();stock.pipe_proof=stock.pipe_proof or{};stock.pipe_proof[#stock.pipe_proof+1]=q;stock.pipe=stock.pipe+1;stock.pipeJump=nil;return{right=true,b=true}
  end
  return{right=c.x<center-1,left=c.x>center+1,b=true,a=stepOK-q.since<35}
 end
 if not stock.drop4 then
  if not(c.grounded and c.y>=160 and c.x>=944)then return{right=true,b=true}end
  stock.drop4=state()
 end
 if C.stock_type==2 then
  stock.gap=stock.gap or 1
  if stock.gap<=2 then
   local g=GAPS[stock.gap];local q=stock.gapJump
   if not q and c.x>=g[1]-64 and c.grounded and not lastA then
    assert(c.block(g[1],208)==0 and c.block(g[2],208)~=0,'Actual authored pit and far bank');q={since=stepOK,request=state(),left=g[1],far=g[2]};stock.gapJump=q
   end
   if not q then return{right=true,b=true}end
   assert(stepOK-q.since<220,'One ordinary pit crossing');local center=g[2]+24
   if c.grounded and c.y>=160 and c.x>=g[2]then
    q.landed=state();stock.gap_proof=stock.gap_proof or{};stock.gap_proof[#stock.gap_proof+1]=q;stock.gap=stock.gap+1;stock.gapJump=nil;return{right=true,b=true}
   end
   return{right=c.x<center-1,left=c.x>center+1,b=true,a=stepOK-q.since<35}
  end
 end
 local center=C.target_x-6
 if c.x<C.target_x-56 and stock.phase~='align'then return{right=true,b=true}end
 if stock.phase~='align'and stock.phase~='head'then stock.phase='align';stock.alignStart=stepOK end
 if stock.phase=='align'then
  assert(stepOK-stock.alignStart<320,'One supported item alignment')
  local b={right=c.x<center-1,left=c.x>center+1,b=true}
  if c.grounded and c.y>=160 and math.abs(c.x-center)<=2 and c.vx==0 and not lastA then stock.settle=(stock.settle or 0)+1 else stock.settle=0 end
  if stock.settle>=8 then stock.phase='head';stock.headAt=stepOK;stock.head_request=state();stock.authored_tile=c.block(C.target_x,C.target_y);if C.stock_type==3 then assert(stock.authored_tile==96,'Real hidden60')end;b={a=true,b=true}end
  return b
 end
 assert(stepOK-stock.headAt<180,'One actual Metal head admission');return{a=stepOK-stock.headAt<35,b=true}
end
local function drive()
 if not menuDone then return end;identity();observe(M,0,336);if M.scope_passed then observe(stock,C.stock_type,C.target_x)end
 if not active()or pendingCollect then buttons={};return end
 if not M.scope_passed then buttons=M.collected and{}or mushroom(context());return end
 assert(src(0x5d0)==M.earned.armor and src(0x718)==M.earned.weapon and r('PlayerStatus')==M.earned.power,'Earned Metal armor/weapon/form retained')
 if stock.collected then buttons={};return end
 local a=target(C.stock_type);local c=context()
 if a then
  if a.state<128 then buttons={};return end
  stock.phase='collect';local dx=a.x-c.x;buttons={right=dx>3,left=dx< -3,b=true}
  if c.grounded and a.y<c.y-12 and math.abs(dx)<48 and(not stock.chaseJump or stepOK-stock.chaseJump>55)then stock.chaseJump=stepOK end
  if stock.chaseJump and stepOK-stock.chaseJump<35 then buttons.a=true end
 else buttons=navigation(c)end
end
local function endpoint()
 if pendingMain or pendingMove or pendingStep or pendingCollect or pendingScore then return end
 local q=M.scope_passed and stock or M;if not q.credit then return end
 local a,b=moveOK-q.credit.move,stepOK-q.credit.step;q.resumed_move=a;q.resumed_step=b
 assert(a<=25 and b<=25,'Exactly25 actual accepted returned Metal work')
 if a==25 and b==25 then
  identity();assert(active()and q.born and q.mature and q.collector and q.erase and q.setup and q.collected,'Actual mature item lifecycle')
  assert(moveEntries==moveReturns and stepEntries==stepReturns and mainEntries==mainReturns,'Balanced actual worker/Main returns')
  if not M.scope_passed then
   assert(src(0x5d0)==128 and r('PlayerStatus')==1,'Genuine original Metal armor/native tier1');M.scope_passed=true;M.earned=state();stock.since=stepOK;buttons={}
  else
   assert(src(0x5d0)==M.earned.armor and src(0x718)==M.earned.weapon and r('PlayerStatus')==M.earned.power,'Real inventory retained after credit')
   if C.stock_type==2 then assert(stock.native_effect and stock.star35_writer and r('StarInvincibleTimer')>0,'Actual native StarC0/35/music')else assert(stock.life_credit and r('NumberofLives')==3,'Actual delayed life3')end
   stock.actual_Main_return={pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],state=state()};finish(true,'Natural Metal M then '..C.kind..' and25 accepted returned movement+HostStep at completedMain')
  end
 end
end
hook('GameLoop',function()
 assert(not pendingMain,'Synchronous Main');mainEntries=mainEntries+1;local cpu=emu.getState();local sp=cpu['cpu.sp'];local pc=read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1
 assert(pc==C.hooks.MainReturn0.pc or pc==C.hooks.MainReturn1.pc,'Authenticated Main caller');pendingMain={pc=pc,sp=(sp+2)&255}
end)
for i=0,1 do local name='MainReturn'..i;hook(name,function()
 local cpu=emu.getState();if pendingMain and pendingMain.pc==cpu['cpu.pc']and pendingMain.sp==cpu['cpu.sp']then pendingMain=nil;mainReturns=mainReturns+1;endpoint();if not stopped then drive()end end
end)end
hook('Ms12Movement',function()
 assert(not pendingMove,'Movement returned');assert(readback.first_private,'Full payload before worker');moveEntries=moveEntries+1
 pendingMove=returning(function(t)moveReturns=moveReturns+1;moveOK=moveOK+(emu.getState()['cpu.ps']&1);pendingMove=nil end)
end)
hook('MsHostStep',function()
 assert(not pendingStep,'HostStep returned');stepEntries=stepEntries+1
 pendingStep=returning(function(t)stepReturns=stepReturns+1;stepOK=stepOK+(emu.getState()['cpu.ps']&1);pendingStep=nil end)
end)
hook('HandlePowerUpCollision',function()
 if not menuDone then return end;identity();local cpu=emu.getState();local i=cpu['cpu.x'];local a=actor(i);local q=M.scope_passed and stock or M;local kind=M.scope_passed and C.stock_type or 0
 assert(i==5 and a.flag==1 and a.id==46 and a.kind==kind and a.state>=128 and q.born and q.mature and not q.collected,'Actual mature Metal item')
 local pb,ib=box('BoundingBox_UL_Corner'),box('EnemyBoundingBoxCoord',i);local w=math.min(pb[3],ib[3])-math.max(pb[1],ib[1])+1;local h=math.min(pb[4],ib[4])-math.max(pb[2],ib[2])+1;assert(w>0 and h>0,'Actual inclusive overlap')
 q.collector={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],state=state(),actor=a,player_box=pb,item_box=ib,overlap={w,h}};q.sound={writes32=0}
 pendingCollect=returning(function(t)
  assert(q.erase and q.setup and r('Enemy_Flag',i)==0 and r('FloateyNum_Control',i)==(kind==3 and 11 or 6)and q.sound.writes32>0,'Native erase/popup/grab32')
  if kind==0 then assert(src(0x5d0)==128 and r('PlayerStatus')==1,'Actual Metal armor effect')elseif kind==2 then assert(r('StarInvincibleTimer')==35 and r('AreaMusicQueue')==64,'Actual Star35/music64')end
  q.collected={pc=t.pc,sp=t.sp,P=emu.getState()['cpu.ps'],state=state()};pendingCollect=nil;buttons={}
 end)
end)
hook('EraseEnemyObject',function()if pendingCollect then local q=M.scope_passed and stock or M;q.erase=state()end end)
hook('SetupFloateyNumber',function()if pendingCollect then local q=M.scope_passed and stock or M;assert(emu.getState()['cpu.a']==6);q.setup=state()end end)
emu.addMemoryCallback(guard(function(_,v)if pendingCollect and v==32 then local q=M.scope_passed and stock or M;q.sound.writes32=q.sound.writes32+1 end end),emu.callbackType.write,C.ram.Square2SoundQueue)
hook('StockTimerDEC',function()
 local q=M.scope_passed and stock or M;if(M.scope_passed and C.stock_type==3)or not q.collected or q.credit or pendingScore then return end
 local cpu=emu.getState();local i=cpu['cpu.x'];if i~=q.collector.actor.slot or r('FloateyNum_Control',i)~=6 or r('FloateyNum_Timer',i)~=43 then return end
 assert(cpu['cpu.a']==43 and cpu['cpu.y']==6,'Actual delayed1000 branch');local before=score();q.credit_writer={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],state=state()}
 pendingScore=returning(function(t)assert(score()==before+1000,'Actual1000 credit');q.credit={before=before,after=score(),move=moveOK,step=stepOK,pc=t.pc,sp=t.sp,state=state()};pendingScore=nil end)
end)
hook('ActualStarEffect',function()if pendingCollect and M.scope_passed and C.stock_type==2 then local cpu=emu.getState();assert(cpu['cpu.ps']&1==0,'Original StarCMP3 C0');stock.native_effect={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],P=cpu['cpu.ps'],state=state()}end end)
emu.addMemoryCallback(guard(function(_,v)if pendingCollect and M.scope_passed and C.stock_type==2 and v==35 then local cpu=emu.getState();assert(cpu['cpu.ps']&1==0);stock.star35_writer={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],P=cpu['cpu.ps'],state=state()}end end),emu.callbackType.write,C.ram.StarInvincibleTimer)
hook('LifeBefore',function()if C.stock_type==3 and stock.collected and not stock.life_credit then local cpu=emu.getState();if cpu['cpu.x']==stock.collector.actor.slot then assert(cpu['cpu.y']==11 and r('NumberofLives')==2);stock.life_before={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],state=state()}end end end)
hook('LifeAfter',function()if stock.life_before and not stock.life_credit then assert(r('NumberofLives')==3 and r('Square2SoundQueue')==64);stock.life_credit={state=state(),pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp']};stock.credit={move=moveOK,step=stepOK,state=state()}end end)
hook('MsLifeCompare',function()if stock.life_credit and not stock.first_life_compare and r('NumberofLives')~=src(0x83e)then stock.first_life_compare={pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],state=state()}end end)
hook('MsNativeConstruct',function()if stock.life_credit and not stock.earned_life_constructor then local q={pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],before=state()};stock.earned_life_constructor=q;returning(function(t)q.after=state();q.returnPC=t.pc;q.returnSP=t.sp end)end end)
hook('Ms24Injury',function()if M.scope_passed and not stock.injury then local q={pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],before=state()};stock.injury=q;returning(function(t)q.after=state();q.returnPC=t.pc;q.returnSP=t.sp end)end end)
local age=0
local function wait(n)coroutine.yield(n)end
local function press(k)buttons={[k]=true};wait(2);buttons={};wait(8)end
local function ready(fn,n,label)local start=frame;while not fn()and frame-start<n do wait(1)end;assert(fn(),'Frontend '..label)end
local menu=coroutine.create(function()
 assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha,'Exact current Metal image')
 ready(function()return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end,250,'title');press('start')
 ready(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end,180,'roster')
 for _=1,3 do press('right')end;press('down');press('select')
 assert(r('CrossoverMenuIndex')==11 and r('SelectedCharacter')==35,'Actual Metal selection');assert(r('CrossoverBehaviorVersion')==0 and r('CheatInvincible')==0 and r('CheatStartLevel')==0)
 press('start');menuDone=true
end)
emu.addEventCallback(guard(function()polls=polls+1;lastA=not not buttons.a;emu.setInput(buttons,0)end),emu.eventType.inputPolled)
emu.addEventCallback(guard(function()
 frame=frame+1;if not menuDone then if age>0 then age=age-1;return end;local ok,n=coroutine.resume(menu);assert(ok,n);age=n or 0;return end
 assert(frame<18000 and mainEntries<6500,'Bounded natural Metal S/L controls')
end),emu.eventType.endFrame)
