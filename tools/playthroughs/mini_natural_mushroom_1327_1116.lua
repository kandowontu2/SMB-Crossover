-- Ordinary current Mini M: no game-state writes, only pad inputs/observers.
local read=function(at)return emu.read(at,emu.memType.nesDebug)end
local function r(n,i)return read(assert(C.ram[n],n)+(i or 0))end
local function work(at)return emu.read(2*8192+at-0xc000,emu.memType.nesWorkRam)end
local function word(at)return work(at)+256*work(at+1)end
local function signed(at)local n=word(at);return n>=32768 and n-65536 or n end
local function pos(n,p,i)return r(n,i)+256*r(p,i)end
local frame,polls,mainEntries,mains,moveEntries,moves,stepEntries,steps=0,0,0,0,0,0,0,0
local stopped=false;local menuDone=CPU_CONTROLLER_OPENING or false;local buttons={};local dynamic={};local pendingMain,pendingMove,pendingStep,pendingCollect,pendingLeaf,pendingScore,pendingPower
local opening=CPU_CONTROLLER_OPENING and 16 or 0;local openingLast=0
local item={phase='approach',power_updates=0,native_pickups=0,primary_leaf_entries=0,private_power_entries=0,vector24_entries=0};local readback={source_prefilled_cold=CPU_CONTROLLER_OPENING or false}
local function score()local v=0;for i=0,5 do v=v*10+r('Player1ScoreDisplay',i)end;return v end
local function state()return{Main=mains,move=moves,step=steps,frame=frame,x=pos('Player_X_Position','Player_PageLoc'),y=r('Player_Y_Position'),high=r('Player_Y_HighPos'),native=r('Player_State'),power=r('PlayerStatus'),size=r('PlayerSize'),lives=r('NumberofLives'),engine=r('GameEngineSubroutine'),score=score(),active=r('GuestPowerupActive'),age=r('GuestPowerupAge'),tier=work(0xc244),top=work(0xc256),pose=work(0xc310),ready=work(0xc300),epoch=work(0xc301),sourceX16=word(0xc250),sourceY16=word(0xc252),vx=signed(0xc200),vy=signed(0xc220),current=work(0xc240),queued=work(0xc228),class=work(0xc246),contacts=work(0xc24c),held=work(0xc248),fresh=work(0xc24a),fault=work(0xc247)}end
local function actor(i)return{slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),kind=r('PowerUpType',i),state=r('Enemy_State',i),x=pos('Enemy_X_Position','Enemy_PageLoc',i),y=r('Enemy_Y_Position',i)}end
local function box(n,i)local t={};for j=0,3 do t[#t+1]=r(n,(i or 0)*4+j)end;return t end
local function json(v)
 if v==nil then return'null'elseif type(v)=='string'then return string.format('%q',v)elseif type(v)~='table'then return tostring(v)end
 local a={};if#v>0 then for i,x in ipairs(v)do a[i]=json(x)end;return'['..table.concat(a,',')..']'end
 for k,x in pairs(v)do a[#a+1]=json(tostring(k))..':'..json(x)end;table.sort(a);return'{'..table.concat(a,',')..'}'
end
local function finish(ok,why)
 if stopped then return end;stopped=true;buttons={}
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=why,ROM_SHA256=C.sha,identity='MINI MARIO',kind='mushroom',Main_entries=mainEntries,Main_returns=mains,MiniMovement_entries=moveEntries,MiniMovement_returns=moves,MiniStep_entries=stepEntries,MiniStep_returns=steps,physical_frames=frame,input_polls=polls,item=item,readback=readback,terminal=state(),opening_neutral_updates=opening,source_prefilled_opening=CPU_CONTROLLER_OPENING or false,pendingMain=pendingMain~=nil,pendingMove=pendingMove~=nil,pendingStep=pendingStep~=nil,pendingCollect=pendingCollect~=nil,pendingLeaf=pendingLeaf~=nil,pendingScore=pendingScore~=nil,pendingPower=pendingPower~=nil,gameplay_seeds=0,game_state_writes=false,outputs=0,full_stage_claim=false}))
 emu.stop(ok and 0 or 1)
end
local function guard(fn)return function(...)if stopped then return end;local ok,e=pcall(fn,...);if not ok then finish(false,tostring(e))end end end
local function hook(name,fn)
 local h=assert(C.hooks[name]);emu.addMemoryCallback(guard(function()
  local a=emu.convertAddress(h.pc);local kind=h.work and emu.memType.nesWorkRam or emu.memType.nesPrgRom
  if not a or a.memType~=kind or a.address~=h.offset then return end
  for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Actual current '..name)end;fn()
 end),emu.callbackType.exec,h.pc)
end
local function returning(fn)
 local c=emu.getState();local sp=c['cpu.sp'];local pc=(read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1)&65535
 if not dynamic[pc]then dynamic[pc]={};emu.addMemoryCallback(guard(function()
  local sp=emu.getState()['cpu.sp'];for i=#dynamic[pc],1,-1 do local q=dynamic[pc][i];if q.sp==sp then table.remove(dynamic[pc],i);q.fn(q)end end
 end),emu.callbackType.exec,pc)end
 local q={pc=pc,sp=(sp+2)&255,fn=fn};dynamic[pc][#dynamic[pc]+1]=q;return q
end
if not CPU_CONTROLLER_OPENING then emu.addMemoryCallback(guard(function()
 if readback.kernel or r('SelectedCharacter')~=41 or r('OperMode')~=1 then return end
 local c=emu.getState();local a=emu.convertAddress(c['cpu.pc']);if not a or a.memType~=emu.memType.nesWorkRam or a.address//8192~=3 then return end
 for i=0,5119 do assert(emu.read(3*8192+i,emu.memType.nesWorkRam)==tonumber(C.kernel_hex:sub(i*2+1,i*2+2),16),'Full Mini code before first SMC')end
 for _,bank in ipairs({2,3})do for i=0,15 do assert(emu.read(bank*8192+0x1fe0+i,emu.memType.nesWorkRam)==tonumber(C.cookie:sub(i*2+1,i*2+2),16),'Both full Mini headers')end end
 readback.kernel={PC=c['cpu.pc'],SP=c['cpu.sp'],bytes=5120,both16B_cookies=true}
end),emu.callbackType.exec,0xa000,0xb3ff)end
local function identity()
 assert(r('SelectedCharacter')==41 and r('MarioVariant')==8,'Compiled actual Mini identity')
 assert(r('CrossoverBehaviorVersion')==0 and r('CheatInvincible')==0 and r('CheatStartLevel')==0,'Ordinary Easy/cheats0')
 assert(r('WorldNumber')==0 and r('LevelNumber')==0 and r('NumberofLives')==2 and r('GameEngineSubroutine')~=11,'Living authored1-1')
end
local function observe()
 for i=0,5 do local a=actor(i);if a.flag==1 and a.id==46 and a.kind==0 then
  assert(a.x>=280 and a.x<=440,'First authored Mushroom');if not item.born then assert(a.x==336);item.born={state=state(),actor=a}end
  if a.state>=128 then item.mature=item.mature or{state=state(),actor=a}end;return a
 end end
end
local function solid(x,y)
 if y<32 or y>=240 or x<0 then return false end
 local at=0x300+((x//256)&1)*0xd0+(y&240)-32+((x&255)//16)
 return work(0xd300+read(at))&3==1
end
local function nearbyEnemy(x,y)
 for i=0,5 do if r('Enemy_Flag',i)>0 and r('Enemy_Flag',i)<128 and r('Enemy_State',i)&32==0 then
  local ex=pos('Enemy_X_Position','Enemy_PageLoc',i);local ey=r('Enemy_Y_Position',i)
  if ex-x>=-8 and ex-x<=46 and math.abs(ey-(y-8))<=40 then return true end
 end end;return false
end
local function drive()
 if not menuDone then return end;identity()
 if pendingCollect or r('GuestPowerupActive')~=0 or r('GameEngineSubroutine')~=8 then buttons={};return end
 if opening<16 then if steps>openingLast then opening=opening+1;openingLast=steps end;buttons={};return end
 local a=observe();if item.collected then buttons={};return end
 local s=state();local x,y=s.sourceX16/16,s.sourceY16/16;local floor=s.class==2 and s.contacts&1~=0
 if item.phase=='approach'and x<280 then
  local want=solid(math.floor(x+24),math.floor(y+1))or solid(math.floor(x+24),math.floor(y+7))or not solid(math.floor(x+22),math.floor(y+8))or nearbyEnemy(x,y)
  buttons={right=true,b=true};if s.queued==12 then buttons.a=true elseif floor then buttons.a=want and s.held&128==0 else buttons.a=true end;return
 end
 if item.phase=='approach'then item.phase='runup';item.since=steps end
 assert(steps-item.since<700,'Bounded original Mushroom policy')
 if a then item.phase='collect'end
 if item.phase=='runup'then
  buttons={right=true,b=true};if x>=304 and floor and s.held&128==0 then item.phase='bump';item.takeoff=state();item.jump_since=steps;buttons.a=true end
 elseif item.phase=='bump'then
  buttons={right=true,b=true,a=steps-item.jump_since<40};assert(steps-item.jump_since<100,'One original runjump must release real item')
 elseif item.phase=='collect'then buttons=a and{right=x<a.x+1,left=x>a.x+7}or{}
 else buttons={}end
end
local function endpoint()
 if pendingMain or pendingMove or pendingStep or pendingCollect or pendingLeaf or pendingScore or pendingPower then return end
 if not item.credit or not item.growth_done then return end
 local baseStep=math.max(item.credit.steps,item.growth_done.steps);local baseMove=math.max(item.credit.moves,item.growth_done.moves)
 item.resumed_steps=steps-baseStep;item.resumed_moves=moves-baseMove
 assert(item.resumed_steps<=25 and item.resumed_moves<=25,'Exactly25 completed original/public updates')
 if item.resumed_steps==25 and item.resumed_moves==25 then
  identity();assert(item.born and item.mature and item.collector and item.collected and item.erase and item.setup and item.sound32>0)
  assert(item.native_pickups==1 and item.primary_leaf_entries==1 and item.leaf_return.C==1,'One whole native pickup inside actual Mini vector24')
  assert(item.power_updates==60 and item.private_power_entries==60 and r('GuestPowerupAge')==60 and r('GuestPowerupActive')==0 and r('PlayerStatus')==1)
  assert(work(0xc244)==1 and work(0xc254)==1 and work(0xc255)==6 and work(0xc256)==249 and work(0xc257)==7 and work(0xc310)>=39,'Real powered source tier/standing6x15 form')
  assert(mainEntries==mains and moveEntries==moves and stepEntries==steps)
  item.actual_Main_return={PC=emu.getState()['cpu.pc'],SP=emu.getState()['cpu.sp'],state=state()};finish(true,'Natural Mini mature Mushroom/wholeC1/1000/60growth/25 real MiniStep+public returns')
 end
end
hook('GameLoop',function()
 assert(not pendingMain);mainEntries=mainEntries+1;local c=emu.getState();local sp=c['cpu.sp'];local pc=read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1
 assert(pc==C.hooks.MainReturn0.pc or pc==C.hooks.MainReturn1.pc);pendingMain={pc=pc,sp=(sp+2)&255}
end)
for i=0,1 do hook('MainReturn'..i,function()local c=emu.getState();if pendingMain and pendingMain.pc==c['cpu.pc']and pendingMain.sp==c['cpu.sp']then pendingMain=nil;mains=mains+1;endpoint();if not stopped then drive()end end end)end
hook('MiniMovement',function()assert(not pendingMove);moveEntries=moveEntries+1;pendingMove=returning(function()moves=moves+1;pendingMove=nil end)end)
hook('MiniStep',function()
 assert(not pendingStep);stepEntries=stepEntries+1;pendingStep=returning(function()steps=steps+1;assert(work(0xc247)==0,'Original source fault0');pendingStep=nil end)
end)
hook('PowerMin6',function()local c=emu.getState();if menuDone and c['cpu.x']==5 and r('Enemy_ID',5)==46 then item.last_min6={PC=c['cpu.pc'],SP=c['cpu.sp'],state=r('Enemy_State',5),A=c['cpu.a']}end end)
hook('HandlePowerUpCollision',function()
 if not menuDone then return end;identity();local c=emu.getState();local a=actor(c['cpu.x'])
 assert(not pendingCollect and a.slot==5 and a.id==46 and a.kind==0 and a.flag==1 and a.state>=128 and item.born and item.mature and not item.collected,'Real mature intended Mini Mushroom')
 local pb,ib=box('BoundingBox_UL_Corner'),box('EnemyBoundingBoxCoord',a.slot);local w=math.min(pb[3],ib[3])-math.max(pb[1],ib[1])+1;local h=math.min(pb[4],ib[4])-math.max(pb[2],ib[2])+1;assert(w>0 and h>0)
 item.collector={PC=c['cpu.pc'],SP=c['cpu.sp'],actor=a,state=state(),player_box=pb,item_box=ib,overlap={w,h}};item.sound32=0
 pendingCollect=returning(function(t)assert(item.erase and item.setup and item.sound32>0 and r('Enemy_Flag',5)==0 and r('FloateyNum_Control',5)==6);item.collected={PC=t.pc,SP=t.sp,state=state()};pendingCollect=nil;buttons={}end)
end)
hook('MiniPickupVector',function()if pendingCollect then item.vector24_entries=item.vector24_entries+1 end end)
hook('MiniPickup',function()if pendingCollect then
 local c=emu.getState();if r('Enemy_Flag',c['cpu.x'])==0 then item.erased_reentries=(item.erased_reentries or 0)+1;return end
 assert(not pendingLeaf);item.primary_leaf_entries=item.primary_leaf_entries+1;item.leaf_entry={PC=c['cpu.pc'],SP=c['cpu.sp'],X=c['cpu.x']}
 pendingLeaf=returning(function(t)local z=emu.getState();item.leaf_return={PC=t.pc,SP=t.sp,C=z['cpu.ps']&1,X=z['cpu.x'],state=state()};assert(item.leaf_return.C==1);pendingLeaf=nil end)
end end)
hook('MarioSourcePowerupCollision',function()if pendingCollect then assert(pendingLeaf);item.native_pickups=item.native_pickups+1;assert(item.native_pickups==1);item.native_pickup_entry={PC=emu.getState()['cpu.pc'],SP=emu.getState()['cpu.sp']}end end)
hook('EraseEnemyObject',function()if pendingCollect then item.erase=state()end end)
hook('SetupFloateyNumber',function()if pendingCollect then assert(emu.getState()['cpu.a']==6);item.setup=state()end end)
emu.addMemoryCallback(guard(function(_,v)if pendingCollect and v==32 then item.sound32=item.sound32+1 end end),emu.callbackType.write,C.ram.Square2SoundQueue)
hook('MiniPowerup',function()if item.collector then item.private_power_entries=item.private_power_entries+1 end end)
hook('GuestPowerupUpdate',function()
 if not item.collector or r('GuestPowerupActive')==0 then return end;assert(not pendingPower);local before=r('GuestPowerupAge');item.power_updates=item.power_updates+1
 assert(before==item.power_updates-1,'Actual hosted age sequence0..59')
 pendingPower=returning(function(t)
  assert(r('GuestPowerupAge')==before+1)
  if r('GuestPowerupAge')==60 then assert(r('GuestPowerupActive')==0 and r('PlayerStatus')==1 and r('GameEngineSubroutine')==8);item.growth_done={PC=t.pc,SP=t.sp,steps=steps,moves=moves,state=state()}end
  pendingPower=nil
 end)
end)
hook('ScoreDEC',function()
 if not item.collected or item.credit or pendingScore then return end;local c=emu.getState();local i=c['cpu.x']
 if i~=5 or r('FloateyNum_Control',i)~=6 or r('FloateyNum_Timer',i)~=43 then return end
 assert(c['cpu.a']==43 and c['cpu.y']==6);local before=score();item.score_writer={PC=c['cpu.pc'],SP=c['cpu.sp'],state=state()}
 pendingScore=returning(function(t)assert(score()==before+1000);item.credit={PC=t.pc,SP=t.sp,before=before,after=score(),steps=steps,moves=moves,state=state()};pendingScore=nil end)
end)
local age=0
local function wait(n)coroutine.yield(n)end
local function press(k)buttons={[k]=true};wait(2);buttons={};wait(8)end
local function ready(fn,n,label)local first=frame;while not fn()and frame-first<n do wait(1)end;assert(fn(),'Frontend '..label)end
local menu=coroutine.create(function()
 assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha);ready(function()return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end,250,'title');press('start')
 ready(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end,180,'roster');for _=1,8 do press('select')end
 assert(r('SelectedCharacter')==41 and r('MarioVariant')==8);press('start');menuDone=true
end)
emu.addEventCallback(guard(function()polls=polls+1;emu.setInput(buttons,0)end),emu.eventType.inputPolled)
emu.addEventCallback(guard(function()
 frame=frame+1;if not menuDone then if age>0 then age=age-1;return end;local ok,n=coroutine.resume(menu);assert(ok,n);age=n or 0;return end
 assert(frame<7000 and mainEntries<2200,'Bounded natural Mini first Mushroom')
end),emu.eventType.endFrame)
