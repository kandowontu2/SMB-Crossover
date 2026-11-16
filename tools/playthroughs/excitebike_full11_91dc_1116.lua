-- Current full1-1 proof: original v5 inputs, completed return witnesses.
routeState=function()
 local s=state();s.world=r('WorldNumber');s.level=r('LevelNumber');s.area=r('AreaNumber');s.area_type=r('AreaType');s.area_offset=r('AreaAddrsLOffset')
 return s
end
local lastMovement,lastMotor=0,0
local function identity()
 assert(r('SelectedCharacter')==37 and r('FmAlts')&16==0 and r('CrossoverBehaviorVersion')==0,'Current Easy Excitebike')
 assert(r('CheatInvincible')==0 and r('CheatStartLevel')==0 and r('NumberofLives')==2,'Living no-cheat route')
 assert(r('WorldNumber')==0 and r('LevelNumber')<=1 and r('GameEngineSubroutine')~=11 and r('OperMode')~=3,'Actual full-route stage/life boundary')
end
local function platform(slot)
 local owner=r('HpActorOwner',slot)
 local q={slot=slot,id=r('Enemy_ID',slot),flag=r('Enemy_Flag',slot),owner=owner,
  left_x=pos('Enemy_X_Position','Enemy_PageLoc',slot),y=r('Enemy_Y_Position',slot),y_high=r('Enemy_Y_HighPos',slot),
  world=r('WorldNumber'),level=r('LevelNumber')}
 if owner>=1 and owner<=3 then
  q.center_x=r('HpXLo',owner-1)+256*r('HpXHi',owner-1);q.width=r('HpWidth',owner-1)*8;q.source_y=r('HpY',owner-1)
 end
 return q
end
local function helperObserve()
 for i=0,5 do
  local id,flag=r('Enemy_ID',i),r('Enemy_Flag',i)
  if flag>0 and flag<128 and(id==0x25 or id==0x28)then
   local e=platform(i);local k=e.world..':'..e.level..':'..i..':'..id..':'..e.owner
   if not route.helper_seen[k]then route.helper_seen[k]={actor=e,player=routeState(),first_observed_only=true}end
  end
 end
 route.helper_samples=(route.helper_samples or 0)+1
end
local function observe()
 if not menuDone then return end
 if not route.first and active()and r('LevelNumber')==0 then
  identity();assert(r('AreaType')==1 and r('AreaAddrsLOffset')==5 and ram2(0x800)==0xa7,'Actual current1-1 constructor')
  route.first=routeState();route.last_progress=mainReturns;route.last_x=wx();route.last_y=r('Player_Y_Position');phase='full-route'
 end
 if not route.first then return end
 identity();local s=routeState()
 if s.level==0 then
  route.max_x=math.max(route.max_x,s.x)
  if s.x>=256+#route.checkpoints*256 and#route.checkpoints<13 then route.checkpoints[#route.checkpoints+1]=s end
  if s.engine==5 and s.x>=3160 then route.castle=route.castle or s end
 end
 if s.level==1 and s.engine==0 then route.entrance=route.entrance or s end
 if s.level==1 then assert(route.flag and route.castle,'No shortcut/area grant')end
 if s.x~=route.last_x or s.y~=route.last_y then route.last_x=s.x;route.last_y=s.y;route.last_progress=mainReturns end
 local recovery=table.concat({s.crash,s.recovery,s.heat,ram2(0x3c),ram2(0x36),ram2(0x374),ram2(0xb8),ram2(0x390)},':')
 if recovery~=route.recovery_key then route.recovery_key=recovery;route.last_progress=mainReturns end
 assert(mainReturns-route.last_progress<1200,'Bounded terrain/source-recovery progress')
 helperObserve()
end
local function endpoint()
 observe();local dm,dv=movementReturns-lastMovement,motorReturns-lastMotor;lastMovement=movementReturns;lastMotor=motorReturns
 if not route.first then return end
 assert(dm==dv and dm<=1,'One balanced original motor/accepted movement per completed Main')
 local s=routeState()
 local grounded=route.flag and route.castle and route.entrance and s.world==0 and s.level==1 and s.area==0
  and active()and s.high==1 and s.native==0 and s.y==176 and ram2(0x800)==0xa7
 if grounded then
  if dm==1 then
   assert(not pendingMain and not pendingMovement and not pendingMotor,'Completed original returns at completed Main')
   route.next_updates=route.next_updates+1
  end
 else route.next_updates=0 end
 if route.next_updates==25 then
  identity();assert(route.max_x>=3260 and mainEntries==mainReturns and motorEntries==motorReturns and movementEntries==movementReturns,'Full strong endpoint')
  route.complete=true;route.actual_Main_return={pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],state=s}
  route.helpers_added_or_moved=false
  finish(true,'Full ordinary non-shortcut1-1 flag/castle/entrance and25 grounded returned original updates in1-2')
 end
end
hook('GameLoop',function()
 assert(not pendingMain,'Synchronous Main');mainEntries=mainEntries+1
 local cpu=emu.getState();local s=cpu['cpu.sp'];local pc=read(256+((s+1)&255))+256*read(256+((s+2)&255))+1
 assert(pc==C.hooks.MainReturn0.pc or pc==C.hooks.MainReturn1.pc,'Authenticated Main caller')
 pendingMain={pc=pc,sp=(s+2)&255}
end)
for i=0,1 do local name='MainReturn'..i;hook(name,function()
 local cpu=emu.getState();if pendingMain and pendingMain.pc==cpu['cpu.pc']and pendingMain.sp==cpu['cpu.sp']then
  pendingMain=nil;mainReturns=mainReturns+1;endpoint()
 end
end)end
hook('ExHostConstruct',function()
 for i=1,#C.kernel_hex,2 do assert(ram3((i-1)//2)==tonumber(C.kernel_hex:sub(i,i+1),16),'Current6144 kernel before constructor')end
 for i=1,#C.metadata_hex,2 do assert(ram2(0x1000+(i-1)//2)==tonumber(C.metadata_hex:sub(i,i+1),16),'Current2048 metadata before constructor')end
 for bank=2,3 do for i=1,32,2 do assert(emu.read(bank*8192+0x1fe0+(i-1)//2,emu.memType.nesWorkRam)==tonumber(C.cookie:sub(i,i+1),16),'Both complete current16byte cookies')end end
 route.constructors[#route.constructors+1]={pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],state=routeState(),kernel=6144,metadata=2048,both_full16cookies=true}
end)
hook('ExHostMovement',function()
 cached=state()
 assert(not pendingMovement,'Previous original movement returned');local q={accepted=false};pendingMovement=q
 returning(function(t)
  assert(pendingMovement==q and not pendingMotor,'Original motor completed before movement return')
  if q.accepted then movementReturns=movementReturns+1 end;pendingMovement=nil
 end)
end)
hook('ExMovementAccepted',function()
 assert(pendingMovement and not pendingMovement.accepted);pendingMovement.accepted=true;movementEntries=movementEntries+1
end)
hook('ExMotorAll',function()
 assert(pendingMovement and pendingMovement.accepted and not pendingMotor,'Original motor inside accepted real movement')
 motorEntries=motorEntries+1;pendingMotor=returning(function(t)pendingMotor=nil;motorReturns=motorReturns+1 end)
end)
hook('FlagpoleRoutine',function()
 if route.first and r('WorldNumber')==0 and r('LevelNumber')==0 and r('GameEngineSubroutine')==4 and wx()>=3000 then
  route.flag=route.flag or routeState()
 end
end)
hook('ActualPlatformSupport',function()
 if not route.first then return end;local slot=r('ObjectOffset');if slot>5 then return end
 local e=platform(slot)
 if e.flag>0 and e.flag<128 and(e.id==0x25 or e.id==0x28)and r('Player_State')==0 and r('PlatformCollisionFlag',slot)<128 then
  local k=e.world..':'..e.level..':'..slot..':'..e.id..':'..e.owner
  route.helper_support[k]=route.helper_support[k]or{actor=e,player=routeState(),pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],actual_SetCollisionFlag_return=true}
 end
end)
local function frames(n)for _=1,n do coroutine.yield()end end
local function press(bits)buttons=bits;frames(4);buttons=0;frames(8)end
local function ready(fn)for _=1,900 do if fn()then return end;coroutine.yield()end;error('Current frontend readiness bound')end
local menu=coroutine.create(function()
 ready(function()return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end)
 press(16);ready(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end)
 assert(r('CrossoverMenuIndex')==0)
 for _,bits in ipairs(C.navigation)do press(bits)end
 assert(r('CrossoverMenuIndex')==29 and r('SelectedCharacter')==37 and r('FmAlts')&16==0,'Actual compiled base Excitebike')
 press(16);ready(function()return active()end);menuDone=true;cached=state();observe()
 while not stopped do coroutine.yield()end
end)
emu.addEventCallback(guard(function()
 polls=polls+1;local b=buttons;local pad={}
 if menuDone then
  observe()
  if active()and r('LevelNumber')==0 then pad=travel()end
 else
  pad={right=b&1~=0,left=b&2~=0,down=b&4~=0,up=b&8~=0,start=b&16~=0,select=b&32~=0,b=b&64~=0,a=b&128~=0}
 end
 emu.setInput(pad,0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guard(function()
 frame=frame+1;assert(frame<18000 and mainEntries<8500,'Bounded current full route')
 if not CPU_CONTROLLER_OPENING then local ok,why=coroutine.resume(menu);assert(ok,why)end
 observe()
end),emu.eventType.endFrame)
if CPU_CONTROLLER_OPENING then cached=state();observe()end

