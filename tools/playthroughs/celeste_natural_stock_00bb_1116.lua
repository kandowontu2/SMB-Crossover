-- Ordinary Celeste controls with actual native item and returned-clock witnesses.
local frame,polls,mainEntries,mainReturns,moves,moveEntries,bgs,bgEntries,clocks=0,0,0,0,0,0,0,0,0
local stopped,menuDone,lastA=false,CPU_CONTROLLER_OPENING or false,false
local buttons,dynamic={},{}
local M,stock,readback={},{phase='travel'},{ }
local opening=CPU_CONTROLLER_OPENING and 16 or 0
local openingLastMoves,routeCalls=0,0
local pendingMain,pendingMove,pendingBG,pendingCollect,pendingLeaf,pendingScore
local function read(at)return emu.read(at,emu.memType.nesDebug)end
local function r(n,i)return read(assert(C.ram[n],n)+(i or 0))end
local function pos(lo,hi,i)return r(lo,i)+256*r(hi,i)end
local function score()local n=0;for i=0,5 do local d=r('Player1ScoreDisplay',i);assert(d<10);n=n*10+d end;return n end
local function active()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function state()return{Main=mainReturns,frame=frame,move=moves,bg=bgs,clocks=clocks,clock=r('CmClock'),x=pos('Player_X_Position','Player_PageLoc'),y=r('Player_Y_Position'),high=r('Player_Y_HighPos'),native=r('Player_State'),vx=r('Player_X_Speed'),vy=r('Player_Y_Speed'),power=r('PlayerStatus'),size=r('PlayerSize'),tier=r('CmTier'),life=r('CmLife'),lives=r('NumberofLives'),star=r('StarInvincibleTimer'),score=score(),engine=r('GameEngineSubroutine'),wall=r('CmWallGrace'),dash=r('CmDashStock'),pose=r('CmPose')}end
local function actor(i)return{slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),kind=r('PowerUpType',i),state=r('Enemy_State',i),x=pos('Enemy_X_Position','Enemy_PageLoc',i),y=r('Enemy_Y_Position',i)}end
local function box(n,i)local a={};for j=0,3 do a[#a+1]=r(n,(i or 0)*4+j)end;return a end
local function json(v)
 if v==nil then return'null'elseif type(v)=='string'then return string.format('%q',v)elseif type(v)~='table'then return tostring(v)end
 local a={};if#v>0 then for i,x in ipairs(v)do a[i]=json(x)end;return'['..table.concat(a,',')..']'end
 for k,x in pairs(v)do a[#a+1]=json(tostring(k))..':'..json(x)end;table.sort(a);return'{'..table.concat(a,',')..'}'
end
local function finish(ok,why)
 if stopped then return end;stopped=true;buttons={}
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=why,ROM_SHA256=C.sha,identity='CELESTE MARIO',kind=C.kind,Main_entries=mainEntries,Main_returns=mainReturns,
  CmMovement_entries=moveEntries,CmMovement_returns=moves,CmAfterBG_entries=bgEntries,CmAfterBG_returns=bgs,CmClock_updates=clocks,physical_frames=frame,input_polls=polls,
  M=M,stock=stock,readback=readback,terminal=state(),opening_neutral_updates=opening,source_prefilled_opening=CPU_CONTROLLER_OPENING or false,pendingMain=pendingMain~=nil,pendingMove=pendingMove~=nil,pendingBG=pendingBG~=nil,pendingCollect=pendingCollect~=nil,pendingLeaf=pendingLeaf~=nil,pendingScore=pendingScore~=nil,
  gameplay_seeds=0,game_state_writes=false,outputs=0,full_stage_claim=false}))
 emu.stop(ok and 0 or 1)
end
local function guard(fn)return function(...)if stopped then return end;local ok,why=pcall(fn,...);if not ok then finish(false,tostring(why))end end end
local function hook(name,fn)
 local h=assert(C.hooks[name]);emu.addMemoryCallback(guard(function()
  local p=emu.convertAddress(h.pc);if not p or p.memType~=emu.memType.nesPrgRom or p.address~=h.offset then return end
  for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Actual current '..name)end;fn()
 end),emu.callbackType.exec,h.pc)
end
local function returning(fn)
 local cpu=emu.getState();local sp=cpu['cpu.sp'];local pc=(read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1)&65535
 local q={pc=pc,sp=(sp+2)&255,entryPC=cpu['cpu.pc'],entrySP=sp}
 if not dynamic[pc]then dynamic[pc]={};emu.addMemoryCallback(guard(function()
  local sp=emu.getState()['cpu.sp'];for i=#dynamic[pc],1,-1 do local t=dynamic[pc][i];if t.sp==sp then table.remove(dynamic[pc],i);t.fn(t)end end
 end),emu.callbackType.exec,pc)end
 q.fn=fn;dynamic[pc][#dynamic[pc]+1]=q;return q
end
local function codeReadback(role,pc,hex)
 local cpu=emu.getState();for i=0,#hex//2-1 do assert(read(pc+i)==tonumber(hex:sub(i*2+1,i*2+2),16),'Full owning resident '..role)end
 return{PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],bytes=#hex//2,resident=true}
end
emu.addMemoryCallback(guard(function()
 if readback.core then return end;local cpu=emu.getState();local p=emu.convertAddress(cpu['cpu.pc'])
 if p and p.memType==emu.memType.nesPrgRom and p.address==98*8192+(cpu['cpu.pc']&8191)then readback.core=codeReadback('core',0xb000,C.core_hex)end
end),emu.callbackType.exec,0xb000,0xbe0a)
emu.addMemoryCallback(guard(function()
 if readback.host then return end;local p=emu.convertAddress(0xbb9a)
 if p and p.memType==emu.memType.nesPrgRom and p.address==81*8192+0x1b9a then readback.host=codeReadback('host',0xa000,C.host_hex)end
end),emu.callbackType.exec,0xbb9a)
local function identity()
 assert(r('SelectedCharacter')==0 and r('MarioVariant')==4 and r('PlayerSize')==1,'Actual always-small Celeste')
 assert(r('CrossoverBehaviorVersion')==0 and r('CheatInvincible')==0 and r('CheatStartLevel')==0,'Easy ordinary controls')
 assert(r('WorldNumber')==0 and r('LevelNumber')==0 and r('NumberofLives')==(stock.life_credit and 3 or 2)and r('GameEngineSubroutine')~=11,'Living authored1-1')
 assert(r('CmTier')==r('PlayerStatus'),'Real Celeste tier/native status')
end
local function target(kind)for i=0,5 do local a=actor(i);if a.flag==1 and a.id==46 and a.kind==kind then return a end end end
local function observe(q,kind,x)
 local a=target(kind);if not a then return end
 if not q.born then assert(a.x==x,'Actual authored item column');q.born={state=state(),actor=a}end
 if a.state>=128 then q.mature=q.mature or{state=state(),actor=a}end;return a
end
local function context()
 local s=state();local c={frame=routeCalls,poll=routeCalls,char=0,variant=4,r=r,x=s.x,y=s.y,yHigh=s.high,state=s.native,vx=s.vx,vy=s.vy,status=s.power,world=0,level=0,area=r('AreaPointer'),areaType=r('AreaType'),engine=s.engine,camera=pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc'),lastA=lastA,grounded=s.native==0}
 c.block=function(x,y)if y<32 or y>=240 then return 0 end;return r('Block_Buffer_1',(x//256)%2*208+((y-32)//16)*16+(x%256)//16)end
 c.enemy=function()
  local e;for i=0,5 do local a=actor(i);local dx=a.x-c.x
   if a.flag>0 and a.flag<128 and a.id<21 and a.state<32 and dx> -160 and dx<160 and(not e or math.abs(dx)<math.abs(e.dx))then a.dx=dx;e=a end
  end;return e
 end;return c
end
-- IMMUTABLE_POLICY
local function travel(c)
 local view={};for k,v in pairs(c)do view[k]=v end;view.char=23
 local b=sunnyM(view)
 if c.status>0 and not c.grounded and r('CmWallGrace')>0 and r('CmWallKick')==0 then b.up=true;b.a=r('CmPreviousAB')&128==0 end
 return b
end
local function drive()
 if not menuDone then return end
 if not active()or pendingCollect then buttons={};return end
 identity()
 if opening<16 then if moves>openingLastMoves then opening=opening+1;openingLastMoves=moves end;buttons={};return end
 routeCalls=routeCalls+1;observe(M,0,336);if M.scope_passed then observe(stock,C.stock_type,C.target_x)end
 if not M.scope_passed then buttons=M.collected and{}or travel(context());return end
 if stock.collected then buttons={};return end
 local c=context();local a=target(C.stock_type)
 if a then
  if a.state<128 then buttons={};return end
  stock.phase='collect';local dx=a.x-c.x;buttons={right=dx>3,left=dx< -3}
  if c.grounded and a.y<c.y-12 and math.abs(dx)<48 and(not stock.chaseJump or moves-stock.chaseJump>60)then stock.chaseJump=moves end
  if stock.chaseJump and moves-stock.chaseJump<35 then buttons.a=true end;return
 end
 if stock.phase=='travel'and c.x<(C.stock_type==3 and 960 or 1500)then buttons=travel(c);return end
 if stock.phase=='travel'then stock.phase='align';stock.alignStart=moves end
 if stock.phase=='align'then
  assert(moves-stock.alignStart<320,'One supported Celeste item alignment');local center=C.target_x-8
  buttons={right=c.x<center-1,left=c.x>center+1}
  if c.grounded and c.y>=160 and math.abs(c.x-center)<=2 and c.vx==0 and not lastA then stock.settle=(stock.settle or 0)+1 else stock.settle=0 end
  if stock.settle>=8 then stock.phase='head';stock.headAt=moves;stock.head_request=state();stock.tile=c.block(C.target_x,C.target_y);assert(stock.tile==(C.stock_type==3 and 96 or 87),'Authored native S/L metatile');buttons={a=true}end
  return
 end
 assert(moves-stock.headAt<180,'One actual Celeste head admission');buttons={a=moves-stock.headAt<40}
end
local function endpoint()
 if pendingMain or pendingMove or pendingBG or pendingCollect or pendingLeaf or pendingScore then return end
 local q=M.scope_passed and stock or M;if not q.credit then return end
 q.resumed_move=moves-q.credit.move;q.resumed_BG=bgs-q.credit.bg;q.resumed_clock=clocks-q.credit.clocks
 assert(q.resumed_move<=25 and q.resumed_BG<=25 and q.resumed_clock<=25,'Exactly25 original returned Celeste updates')
 if q.resumed_move==25 and q.resumed_BG==25 and q.resumed_clock==25 then
  identity();assert(q.born and q.mature and q.collector and q.collected and q.erase and q.setup and q.sound.writes32>0)
  assert(mainEntries==mainReturns and moveEntries==moves and bgEntries==bgs and moves==clocks,'Balanced owning calls/clock')
  q.actual_Main_return={PC=emu.getState()['cpu.pc'],SP=emu.getState()['cpu.sp'],state=state()}
  if not M.scope_passed then assert(r('CmTier')==1);M.scope_passed=true;M.earned=state();buttons={}
  else
   assert(q.leaf_return.C==0 and q.fallback_calls==1 and r('CmTier')==q.collector.state.tier,'Exact native fallback and retained real tier')
   if C.stock_type==3 then assert(q.life_credit and r('NumberofLives')==3 and r('CmLife')==3)else assert(q.native_effect and q.star35_writer and r('StarInvincibleTimer')>0)end
   finish(true,'Natural Celeste M then '..C.kind..'/native credit/25 returned movement+postBG+clock at actual Main')
  end
 end
end
hook('GameLoop',function()
 assert(not pendingMain);mainEntries=mainEntries+1;local cpu=emu.getState();local sp=cpu['cpu.sp'];local pc=read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1
 assert(pc==C.hooks.MainReturn0.pc or pc==C.hooks.MainReturn1.pc);pendingMain={pc=pc,sp=(sp+2)&255}
end)
for i=0,1 do hook('MainReturn'..i,function()local cpu=emu.getState();if pendingMain and pendingMain.pc==cpu['cpu.pc']and pendingMain.sp==cpu['cpu.sp']then pendingMain=nil;mainReturns=mainReturns+1;endpoint();if not stopped then drive()end end end)end
hook('CmMovement',function()
 assert(not pendingMove);moveEntries=moveEntries+1;local clock=r('CmClock')
 pendingMove=returning(function()moves=moves+1;assert((r('CmClock')-clock)&255==1,'Actual original CmClock advance');clocks=clocks+1;assert(r('PlayerSize')==1);pendingMove=nil end)
end)
hook('CmAfterBG',function()assert(not pendingBG);bgEntries=bgEntries+1;pendingBG=returning(function()bgs=bgs+1;assert(r('PlayerSize')==1);pendingBG=nil end)end)
hook('HandlePowerUpCollision',function()
 if not menuDone then return end;identity();local cpu=emu.getState();local a=actor(cpu['cpu.x']);local q=M.scope_passed and stock or M;local kind=M.scope_passed and C.stock_type or 0
 assert(a.slot==5 and a.flag==1 and a.id==46 and a.kind==kind and a.state>=128 and q.born and q.mature and not q.collected,'Actual mature intended Celeste item')
 local pb,ib=box('BoundingBox_UL_Corner'),box('EnemyBoundingBoxCoord',a.slot);local w=math.min(pb[3],ib[3])-math.max(pb[1],ib[1])+1;local h=math.min(pb[4],ib[4])-math.max(pb[2],ib[2])+1;assert(w>0 and h>0)
 q.collector={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],state=state(),actor=a,player_box=pb,item_box=ib,overlap={w,h}};q.sound={writes32=0};q.fallback_calls=0
 pendingCollect=returning(function(t)
  assert(q.erase and q.setup and r('Enemy_Flag',a.slot)==0 and q.sound.writes32>0 and r('FloateyNum_Control',a.slot)==(kind==3 and 11 or 6))
  if kind==0 then assert(q.leaf_return.C==1 and q.fallback_calls==0 and r('CmTier')==1)elseif kind==2 then assert(r('StarInvincibleTimer')==35 and r('AreaMusicQueue')==64)end
  q.collected={PC=t.pc,SP=t.sp,state=state()};pendingCollect=nil;buttons={}
 end)
end)
hook('CmPickup',function()if pendingCollect then
 local q=M.scope_passed and stock or M;assert(not pendingLeaf);q.leaf_entry={state=state(),X=emu.getState()['cpu.x']}
 pendingLeaf=returning(function(t)local cpu=emu.getState();assert(cpu['cpu.x']==q.collector.actor.slot);q.leaf_return={PC=t.pc,SP=t.sp,C=cpu['cpu.ps']&1,state=state()};pendingLeaf=nil end)
end end)
hook('MarioSourcePowerupCollision',function()if pendingCollect then local q=M.scope_passed and stock or M;q.fallback_calls=q.fallback_calls+1;assert(q.leaf_return and q.leaf_return.C==0 and emu.getState()['cpu.x']==q.collector.actor.slot)end end)
hook('EraseEnemyObject',function()if pendingCollect then local q=M.scope_passed and stock or M;q.erase=state()end end)
hook('SetupFloateyNumber',function()if pendingCollect then local q=M.scope_passed and stock or M;q.setup={A=emu.getState()['cpu.a'],state=state()}end end)
emu.addMemoryCallback(guard(function(_,v)if pendingCollect and v==32 then local q=M.scope_passed and stock or M;q.sound.writes32=q.sound.writes32+1 end end),emu.callbackType.write,C.ram.Square2SoundQueue)
hook('ScoreDEC',function()
 local q=M.scope_passed and stock or M;if(M.scope_passed and C.stock_type==3)or not q.collected or q.credit or pendingScore then return end
 local cpu=emu.getState();local i=cpu['cpu.x'];if i~=q.collector.actor.slot or r('FloateyNum_Control',i)~=6 or r('FloateyNum_Timer',i)~=43 then return end
 assert(cpu['cpu.a']==43 and cpu['cpu.y']==6);local before=score();q.score_writer={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],state=state()}
 pendingScore=returning(function(t)assert(score()==before+1000);q.credit={move=moves,bg=bgs,clocks=clocks,before=before,after=score(),PC=t.pc,SP=t.sp,state=state()};pendingScore=nil end)
end)
hook('LifeBefore',function()if stock.collected and C.stock_type==3 and not stock.life_credit then local cpu=emu.getState();if cpu['cpu.x']==stock.collector.actor.slot then assert(r('NumberofLives')==2 and cpu['cpu.y']==11);stock.life_before={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],state=state()}end end end)
hook('LifeAfter',function()if stock.life_before and not stock.life_credit then assert(r('NumberofLives')==3 and r('Square2SoundQueue')==64);stock.life_credit={PC=emu.getState()['cpu.pc'],SP=emu.getState()['cpu.sp'],state=state()};stock.credit={move=moves,bg=bgs,clocks=clocks,state=state()}end end)
hook('StarEffect',function()if pendingCollect and M.scope_passed and C.stock_type==2 then local cpu=emu.getState();assert(cpu['cpu.ps']&1==0);stock.native_effect={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],state=state()}end end)
emu.addMemoryCallback(guard(function(_,v)if pendingCollect and M.scope_passed and C.stock_type==2 and v==35 then stock.star35_writer={PC=emu.getState()['cpu.pc'],SP=emu.getState()['cpu.sp'],state=state()}end end),emu.callbackType.write,C.ram.StarInvincibleTimer)
local age=0
local function wait(n)coroutine.yield(n)end
local function press(k)buttons={[k]=true};wait(2);buttons={};wait(8)end
local function ready(fn,n,label)local start=frame;while not fn()and frame-start<n do wait(1)end;assert(fn(),'Frontend '..label)end
local menu=coroutine.create(function()
 assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha)
 ready(function()return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end,250,'title');press('start')
 ready(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end,180,'roster')
 for _=1,6 do press('select')end;assert(r('MarioVariant')==4 and r('SelectedCharacter')==0);press('start');menuDone=true
end)
emu.addEventCallback(guard(function()polls=polls+1;lastA=not not buttons.a;emu.setInput(buttons,0)end),emu.eventType.inputPolled)
emu.addEventCallback(guard(function()
 frame=frame+1;if not menuDone then if age>0 then age=age-1;return end;local ok,n=coroutine.resume(menu);assert(ok,n);age=n or 0;return end
 assert(frame<14000 and mainEntries<4500,'Bounded ordinary Celeste S/L')
end),emu.eventType.endFrame)
