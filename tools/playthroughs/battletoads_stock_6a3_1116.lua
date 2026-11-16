-- Genuine current Battletoads food, ordinary input and read-only witnesses.
local frame,polls,mainEntries,mainReturns,guestEntries,guestReturns=0,0,0,0,0,0
local menuDone=CPU_CONTROLLER_OPENING or false
local stopped,lastA,buttons=false,false,{}
local pendingMain,pendingGuest,pendingCollect,pendingScore
local dynamic={}
local food={phase='mushroom',pickups={},heads={},births={}}
local function read(at)return emu.read(at,emu.memType.nesDebug)end
local function work(at)return emu.read(3*8192+(at&8191),emu.memType.nesWorkRam)end
local function r(n,i)local at=assert(C.ram[n],n)+(i or 0);return n:sub(1,2)=='Bt'and work(at)or read(at)end
local function pos(lo,hi,i)return r(lo,i)+256*r(hi,i)end
local function score()local n=0;for i=0,5 do local d=r('Player1ScoreDisplay',i);assert(d<10);n=n*10+d end;return n end
local function active()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function state()return{Main=mainReturns,frame=frame,guest=guestReturns,x=pos('Player_X_Position','Player_PageLoc'),y=r('Player_Y_Position'),high=r('Player_Y_HighPos'),native=r('Player_State'),vx=r('Player_X_Speed'),vy=r('Player_Y_Speed'),power=r('PlayerStatus'),HP=r('BtSrc_Objects_Life',r('CurrentPlayer')),lives=r('NumberofLives'),star=r('StarInvincibleTimer'),score=score(),engine=r('GameEngineSubroutine'),phase=food.phase}end
local function actor(i)return{slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),kind=r('PowerUpType',i),state=r('Enemy_State',i),x=pos('Enemy_X_Position','Enemy_PageLoc',i),y=r('Enemy_Y_Position',i)}end
local function box(name,i)local b={};for j=0,3 do b[#b+1]=r(name,(i or 0)*4+j)end;return b end
local function json(v)
 if v==nil then return'null'elseif type(v)=='string'then return string.format('%q',v)elseif type(v)~='table'then return tostring(v)end
 local a={};if#v>0 then for i,x in ipairs(v)do a[i]=json(x)end;return'['..table.concat(a,',')..']'end
 for k,x in pairs(v)do a[#a+1]=json(tostring(k))..':'..json(x)end;table.sort(a);return'{'..table.concat(a,',')..'}'
end
local function finish(ok,why)
 if stopped then return end;stopped=true;buttons={}
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=why,ROM_SHA256=C.sha,identity=C.key,kind=C.kind,physical_frames=frame,input_polls=polls,
  Main_entries=mainEntries,Main_returns=mainReturns,Bt_entries=guestEntries,Bt_returns=guestReturns,food=food,terminal=state(),
  pendingMain=pendingMain~=nil,pendingGuest=pendingGuest~=nil,gameplay_seeds=0,game_state_writes=false,outputs=0,full_stage_claim=false}))
 emu.stop(ok and 0 or 1)
end
local function guard(fn)return function(...)if stopped then return end;local ok,why=pcall(fn,...);if not ok then finish(false,tostring(why))end end end
local function hook(name,fn)
 local h=assert(C.hooks[name]);emu.addMemoryCallback(guard(function()
  local p=emu.convertAddress(h.pc);local kind=h.work and emu.memType.nesWorkRam or emu.memType.nesPrgRom
  if not p or p.memType~=kind or p.address~=h.offset then return end
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
 assert(r('SelectedCharacter')==33 and r('FmGroups')==64+C.variant and r('BtVariant')==C.variant,'Actual Battletoads identity')
 assert(r('CrossoverBehaviorVersion')==0 and r('CheatInvincible')==0 and r('CheatStartLevel')==0,'Easy/no cheats')
 assert(r('WorldNumber')==0 and r('LevelNumber')==0 and r('NumberofLives')==2,'Authored living1-1')
 assert(r('BtHostReady')==1 and r('BtSrc_Objects_Life',r('CurrentPlayer'))<128,'Living original source')
end
local function target()
 for i=0,5 do local a=actor(i);if a.flag==1 and a.id==46 and a.kind<2 then return a end end
end
local function observe()
 local a=target();if not a then return end
 local n=#food.pickups+1
 if not food.births[n]then
  assert(a.x==(n==1 and 336 or 1248),'Actual authored food block')
  food.births[n]={state=state(),actor=a}
 end
 if a.state>=128 then food.births[n].mature=food.births[n].mature or{state=state(),actor=a}end
end
local function context()
 local s=state();local c={frame=guestReturns,poll=guestReturns,char=33,variant=C.variant,r=r,x=s.x,y=s.y,yHigh=s.high,state=s.native,vx=s.vx,vy=s.vy,status=s.power,
  world=r('WorldNumber'),level=r('LevelNumber'),area=r('AreaPointer'),areaType=r('AreaType'),engine=s.engine,camera=pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc'),lastA=(r('SavedJoypadBits')&128)~=0,grounded=s.native==0}
 c.block=function(x,y)if y<32 or y>=240 then return 0 end;return r('Block_Buffer_1',(x//256)%2*208+((y-32)//16)*16+(x%256)//16)end
 c.enemy=function()
  local e;for i=0,5 do local a=actor(i);local dx=a.x-c.x
   if a.flag>0 and a.flag<128 and(a.id<21 or a.id==45 or a.id==51)and a.state<32 and not(a.id==6 and a.state>=2)and dx> -160 and dx<160 and(not e or math.abs(dx)<math.abs(e.dx))then a.dx=dx;e=a end
  end;return e
 end;return c
end
local function drive()
 if not menuDone or not active()then buttons={};return end;identity();observe()
 if pendingCollect or pendingScore or food.pickups[#food.pickups]and not food.pickups[#food.pickups].resumed then buttons={};return end
 local c=context()
 if food.phase=='mushroom'then buttons=travel(c);return end
 if food.phase=='flower-travel'then
  if c.x<1180 then buttons=travel(c);return end
  food.phase='flower-align';food.alignSince=guestReturns;buttons={};return
 end
 if food.phase=='flower-align'then
  assert(guestReturns-food.alignSince<350,'Ordinary flower alignment bound')
  if c.y~=176 or not c.grounded then buttons={};return end
  buttons={right=c.x<1240,left=c.x>1241}
  if c.x>=1240 and c.x<=1241 and not c.lastA then food.phase='flower-head';food.headAt=guestReturns;food.headRequest=state();buttons={a=true}end
 elseif food.phase=='flower-head'then
  assert(guestReturns-food.headAt<160,'Genuine second question head bound')
  buttons={a=guestReturns-food.headAt<35}
  local a=target()
  if a then
   assert(a.kind==1,'Second authored question produced Mushroom because native PlayerStatus stayed0; Flower not acquired')
   food.phase='flower-collect'
  end
 elseif food.phase=='flower-collect'then
  local a=target();buttons={}
  if a and a.state>=128 then
   buttons={right=c.x<a.x-4,left=c.x>a.x+12}
   if c.grounded and not c.lastA then food.collectJump=guestReturns end
   if food.collectJump and guestReturns-food.collectJump<35 then buttons.a=true end
  end
 end
end
local function endpoint()
 if pendingMain or pendingGuest then return end
 local q=food.pickups[#food.pickups];if not q or not q.credit or q.resumed then return end
 local n=guestReturns-q.credit.guest;q.resume_count=n;assert(n<=25,'Exactly25 returned original workers')
 if n==25 then
  identity();assert(q.birth and q.mature and q.erase and q.setup and q.collected and q.score_credit,'All genuine food lifecycle gates')
  assert(r('PlayerStatus')==q.before.power and r('GuestPowerupActive')==0,'Original food preserves native tier, no invented upgrade')
  assert(r('BtSrc_Objects_Life',r('CurrentPlayer'))==q.after.HP,'Food HP retained through25 workers')
  q.resumed={state=state(),pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp']}
  if C.kind=='mushroom'or#food.pickups==2 then
   assert(guestEntries==guestReturns and mainEntries==mainReturns,'Balanced actual returns')
   finish(true,'Natural Battletoads '..C.kind..' food and25 actual returned original workers at returned Main')
  else food.phase='flower-travel' end
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
hook('BtConstruct',function()
 if not food.first_constructor then
  for i=1,#C.cache_hex,2 do assert(work(0xa000+(i-1)//2)==tonumber(C.cache_hex:sub(i,i+1),16),'Whole current BT cache before first worker')end
  for i=1,32,2 do assert(work(0xbfe0+(i-1)//2)==tonumber(C.cookie:sub(i,i+1),16),'Full16 current BT cookie')end
  food.first_constructor={pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],bytes=8160,cookie=true}
 end
end)
hook('BtCoreStep',function()
 if not food.first_worker then
  for _,h in pairs(C.hooks)do if h.work then for i,v in ipairs(h.bytes)do assert(work(h.pc+i-1)==v,'Current private hook preimage')end end end
  for i=1,32,2 do assert(work(0xbfe0+(i-1)//2)==tonumber(C.cookie:sub(i,i+1),16),'Full16 current BT cookie')end
  food.first_worker={pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],cookie=true}
 end
 assert(not pendingGuest,'Previous BT original worker returned');guestEntries=guestEntries+1
 pendingGuest=returning(function(t)pendingGuest=nil;guestReturns=guestReturns+1 end)
end)
hook('BtPickup',function()
 local i=emu.getState()['cpu.x'];local a=actor(i);if a.kind>1 or a.id~=46 or a.flag~=1 or a.state<128 then return end
 observe();local n=#food.pickups+1;assert(n<=2 and food.births[n]and food.births[n].mature,'Actual mature food before collection')
 assert(not pendingCollect,'One physical collector')
 local pb,ib=box('BoundingBox_UL_Corner'),box('EnemyBoundingBoxCoord',i)
 local width=math.min(pb[3],ib[3])-math.max(pb[1],ib[1])+1;local height=math.min(pb[4],ib[4])-math.max(pb[2],ib[2])+1
 assert(width>0 and height>0,'Native inclusive positive physical food overlap')
 local q={before=state(),actor=a,birth=food.births[n],mature=food.births[n].mature,player_box=pb,item_box=ib,overlap={width,height},pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp']}
 food.pickups[n]=q;pendingCollect=q
 returning(function(t)
  q.after=state();q.return_pc=t.pc;q.return_sp=t.sp
  assert(q.erase and q.setup and r('Enemy_Flag',i)==0 and r('FloateyNum_Control',i)==6,'Actual erase and popup6')
  assert(r('Square2SoundQueue')==32,'Actual grab cue32')
  assert(q.after.HP==math.min(47,q.before.HP+8),'Actual source food8 cap47')
  assert(q.after.power==q.before.power and r('GuestPowerupActive')==0 and q.after.engine==8,'Actual food semantics, no Mario upgrade')
  q.collected=state();pendingCollect=nil;buttons={}
 end)
end)
hook('EraseEnemyObject',function()if pendingCollect then pendingCollect.erase=state()end end)
hook('SetupFloateyNumber',function()if pendingCollect then assert(emu.getState()['cpu.a']==6);pendingCollect.setup=state()end end)
hook('FloateyNumbersCore',function()
 local q=food.pickups[#food.pickups];if not q or not q.collected or q.score_credit or pendingScore then return end
 local i=emu.getState()['cpu.x'];if i~=q.actor.slot or r('FloateyNum_Control',i)~=6 or r('FloateyNum_Timer',i)~=43 then return end
 local before=score();pendingScore=returning(function(t)
  assert(score()==before+1000,'Actual delayed food popup1000 credit')
  q.score_credit={before=before,after=score(),state=state(),pc=t.pc,sp=t.sp};q.credit={guest=guestReturns,state=state()};pendingScore=nil
 end)
end)
hook('UnionPwrUpCore',function()
 local i=emu.getState()['cpu.x'];local a=actor(i)
 local q={state=state(),actor=a,pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp']};food.heads[#food.heads+1]=q
 assert(#food.heads<=4,'Narrow authored head events')
 returning(function(t)q.after=actor(i);q.return_pc=t.pc;q.return_sp=t.sp end)
end)
local age=0
local function wait(n)coroutine.yield(n)end
local function press(key)buttons={[key]=true};wait(2);buttons={};wait(8)end
local function ready(fn,limit,label)local start=frame;while not fn()and frame-start<limit do wait(1)end;assert(fn(),'Frontend '..label)end
local menu=coroutine.create(function()
 assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha,'Exact owning6a3 environment')
 ready(function()return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end,250,'title')
 press('start');ready(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end,180,'roster')
 assert(r('CrossoverMenuIndex')==0 and r('SelectedCharacter')==0,'Initial real Mario roster')
 press('left');press('down');press('down');for i=1,C.cycle do press('select')end
 assert(r('CrossoverMenuIndex')==23 and r('SelectedCharacter')==33 and r('FmGroups')==64+C.variant,'Actual compiled Battletoads selection')
 assert(r('CrossoverBehaviorVersion')==0 and r('CheatInvincible')==0 and r('CheatStartLevel')==0,'Easy/default')
 press('start');menuDone=true
end)
emu.addEventCallback(guard(function()
 polls=polls+1;lastA=not not buttons.a;emu.setInput(buttons,0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guard(function()
 frame=frame+1
 if not menuDone then if age>0 then age=age-1;return end;local ok,n=coroutine.resume(menu);assert(ok,n);age=n or 0;return end
 if mainReturns>4000 or frame>14000 then finish(false,'Bounded natural Battletoads food policy')end
end),emu.eventType.endFrame)
