-- Actual cold menu, then explicit audio requests or equal-update work arenas.
local C=assert(MAC_NATIVE_CONFIG)
for n,a in pairs(C.ram)do L[n]=a end
local wall,entered,step,index,age=0,false,0,1,0
local phase=C.hard==1 and'options-focus'or'start'
local song,sourceFrame,golden,sourceActive=nil,0,nil,false
local sourceStores,sourceCalls,updates,borrowed,hardware,irqs,allIrqs=0,0,0,0,0,0,0
local saved,actual,events=nil,{},{}
local totalCycles,peakCycles,startCycles,minimumSP=0,0,0,255
local fxSeen,pausedAt,resumed,silenced,restarted=false,nil,false,false,false
local cases={{1,0,20,600},{2,0,22,360},{4,0,1,4200},{8,0,23,360},
 {16,0,2,1000},{32,0,1,180},{64,0,23,180},{0,1,7,400},
 {0,2,9,700},{0,4,6,400},{0,8,4,700},{0,16,9,180},
 {0,32,6,180},{0,64,23,360}}
local names={'idle','walk','enemies','punch','super'}
local phaseIndex,phaseStart,liveEnemies,attacks,supers=0,0,0,0,0
local dma,oamFrames=nil,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local function tick()return emu.getState()['cpu.cycleCount']end
emu.addMemoryCallback(function(_,page)
 if not entered then return end
 dma={};for i=0,255 do dma[i+1]=emu.read(page*256+i,emu.memType.nesDebug)end
end,emu.callbackType.write,0x4014)
local function snapshot()
 local q={}
 for a=0,255 do if a<L.XgAudioPtr or a>=L.XgAudioZeroPageEnd then q[a]=emu.read(a,emu.memType.nesDebug)end end
 for _,n in ipairs({'CurrentBank','CurrentBankC','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','GameEngineSubroutine'})do q[n]=r(n)end
 return q
end
local returns,installed={},{}
local function onReturn(fn)
 local st=emu.getState();local sp=st['cpu.sp']
 local pc=(emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 returns[pc]={sp=(sp+2)%256,bank=bank(pc),fn=fn}
 if not installed[pc]then
  installed[pc]=true
  emu.addMemoryCallback(function()
   local q=returns[pc]
   if not q or emu.getState()['cpu.sp']~=q.sp or bank(pc)~=q.bank then return end
   returns[pc]=nil;q.fn()
  end,emu.callbackType.exec,pc)
 end
end
local function source(kind)
 if not entered or C.music~=1 or bank(L.LmNativeSourcePlay)~=123 then return end
 assert(not sourceActive,'One source call at a time')
 sourceActive=true;events={}
 if kind=='init'then
  song=r('RgAudioSong');sourceFrame=0
  assert(song==cases[index][3],'Declared area/event chooses original Punch-Out song')
  if golden then golden:close()end
  golden=assert(io.open(C.gold..'song-'..song..'.bin','rb'))
 else sourceFrame=sourceFrame+1 end
 onReturn(function()
  local n=assert(golden:read(1),'Original source record'):byte()
  local apu=assert(golden:read(n*2),'Original ordered APU record')
  local state=assert(golden:read(64),'Original channel/zero-page state')
  assert(#events==n,'Original source store count song='..song..' tick='..sourceFrame..' got='..#events..' wanted='..n)
  for i,q in ipairs(events)do
   assert(q[1]==apu:byte(i*2-1)and q[2]==apu:byte(i*2),'Original ordered source APU write song='..song..' tick='..sourceFrame..' store='..i)
  end
  for i=0,47 do assert(r('LmNativeRam',i)==state:byte(i+1),'Original source channel state '..i)end
  for i=0,15 do
   local v=C.direct_zp==1 and i~=8 and i~=9 and r('LmNativeZp',i)or emu.read(240+i,emu.memType.nesDebug)
   if i==9 and v>=160 and v<192 then v=v-32 end
   assert(v==state:byte(49+i),'Original source zero page '..i..' song='..song..' tick='..sourceFrame)
  end
  sourceStores=sourceStores+n;sourceCalls=sourceCalls+1;sourceActive=false
 end)
end
if C.music==1 then
 emu.addMemoryCallback(function()source('init')end,emu.callbackType.exec,L.LmNativeSourceInit)
 emu.addMemoryCallback(function()source('play')end,emu.callbackType.exec,L.LmNativeMusicPlay)
 emu.addMemoryCallback(function(at,v)if sourceActive then events[#events+1]={at-L.GuestNativeApu,v}end end,emu.callbackType.write,L.GuestNativeApu,L.GuestNativeApu+15)
 emu.addMemoryCallback(function(at,v)
  actual[at-0x4000]=v
  if sourceActive then events[#events+1]={at-0x4000,v}end
 end,emu.callbackType.write,0x4000,0x4017)
 emu.addMemoryCallback(function()
  if not entered or bank(L.LmNativeMusicUpdate)~=123 then return end
  assert(not saved,'One music adapter update at a time')
  saved=snapshot();startCycles=tick();updates=updates+1
  minimumSP=math.min(minimumSP,emu.getState()['cpu.sp'])
 end,emu.callbackType.exec,L.LmNativeMusicUpdate)
 emu.addMemoryCallback(function()
  if not saved then return end
  local after=snapshot();for k,v in pairs(saved)do assert(after[k]==v,'Native music restores interrupted state '..tostring(k))end
  assert(bank(0xc000)==38,'Native source retains caller audio C bank')
  borrowed=borrowed+1;saved=nil
  local elapsed=tick()-startCycles;totalCycles=totalCycles+elapsed;peakCycles=math.max(peakCycles,elapsed)
 end,emu.callbackType.exec,L.ExpandedAudioDecoded)
 emu.addMemoryCallback(function()if entered then allIrqs=allIrqs+1;if saved then irqs=irqs+1 end end end,emu.callbackType.exec,L.IrqScrollSplit)
end
local finish
local function progress()
 local f=assert(io.open(OUTPUT..'coverage-progress.json','w'))
 f:write(string.format('{"case":%d,"wall":%d,"source_calls":%d,"stores":%d,"updates":%d,"hardware":%d,"IRQ_splits":%d,"nested_IRQs":%d,"fx":%s,"paused":%s,"resumed":%s,"silenced":%s,"restarted":%s}',index,wall,sourceCalls,sourceStores,updates,hardware,allIrqs,irqs,tostring(fxSeen),tostring(pausedAt~=nil),tostring(resumed),tostring(silenced),tostring(restarted)));f:close()
end
local profile=nil
if C.music~=1 then
 profile=dofile(C.observer)({out=OUTPUT,phase=function()return names[phaseIndex]or'startup'end,
 onGameLoopReturn=function()if step==600 then finish();return true end end})
end
local trace=assert(io.open(OUTPUT..'gameplay.csv','w'))
trace:write('wall,update,phase,x,page,y,state,hp,stars,stamina,attack,super,enemy0,enemyX0,enemyY0,enemy1,enemyX1,enemyY1\n')
local function arena()
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i)end
 for _,n in ipairs({'TimerControl','GamePauseStatus','MmDeathFlag','AreaParserTaskNum','ScrollThirtyTwo','EnemyFrenzyBuffer','EnemyFrenzyQueue','InjuryTimer','StarInvincibleTimer','LmAttack','LmSuper','LmHurt','LmInvul','LmPrevious'})do w(n,0)end
 w('ScrollLock',1);w('CheatInvincible',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('PlayerFacingDir',1)
 w('LmHealth',96);w('LmStars',3);w('LmHearts',20)
 if phaseIndex>=3 then
  for i=0,1 do
   for _,q in ipairs({{'Enemy_Flag',1},{'Enemy_ID',6},{'Enemy_State',0},{'Enemy_BoundBoxCtrl',9},{'Enemy_X_Position',208+i*24},{'Enemy_PageLoc',0},{'Enemy_Y_Position',184},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',248},{'Enemy_Y_Speed',0},{'Enemy_MovingDir',2},{'Enemy_CollisionBits',0},{'EnemyOffscrBitsMasked',0}})do w(q[1],q[2],i)end
  end
 end
end
finish=function()
 if golden then golden:close()end
 if profile then profile.finish();assert(liveEnemies>=100 and attacks>20 and supers>20,'Actual enemy, punch and super-punch work')end
 progress()
 assert(oamFrames>100,'Sustained exact hardware OAM/DMA coverage')
 if C.music==1 then assert(fxSeen and pausedAt and resumed and silenced and restarted and allIrqs>100 and sourceCalls>5000 and hardware>50000,'Complete native source/mixer/paused/SFX/IRQ matrix; see coverage-progress.json')end
 trace:close();local f=assert(io.open(OUTPUT..'proof.json','w'))
 f:write(string.format('{"passed":true,"music":%s,"hard":%s,"frames":%d,"source_calls":%d,"ordered_source_APU_writes":%d,"audio_updates":%d,"hardware_register_comparisons":%d,"borrowed_state_checks":%d,"nested_IRQs":%d,"IRQ_splits":%d,"OAM_DMA_frames":%d,"adapter_cycles_inclusive":%d,"peak_adapter_cycles_inclusive":%d,"minimum_adapter_entry_SP":%d,"completed_game_updates":%d,"live_enemy_samples":%d,"punch_samples":%d,"super_samples":%d,"scope":"Cold native menu followed by explicitly arranged audio requests or an equal-600-update first-screen work arena. Source calls/states and live hardware mixer are checked separately. No campaign clear or universal lag claim."}',tostring(C.music==1),tostring(C.hard==1),wall,sourceCalls,sourceStores,updates,hardware,borrowed,irqs,allIrqs,oamFrames,totalCycles,peakCycles,minimumSP,step,liveEnemies,attacks,supers));f:close();emu.stop(0)
end
local function menu()
 if wall<60 or wall%12~=0 then return{}end
 if phase=='options-focus'then phase='options-open';return{down=true}end
 if phase=='options-open'then phase='mode-focus';return{a=true}end
 if phase=='mode-focus'then
  if r('CrossoverMenuState')~=4 then return{}end
  if r('CrossoverOptionsFocus')~=1 then return{down=true}end
  phase='mode-set'
 end
 if phase=='mode-set'then if r('CrossoverBehaviorVersion')==0 then return{a=true}end;phase='back';return{}end
 if phase=='back'then phase='start';return{b=true}end
 if r('CrossoverMenuState')==2 then
  local ix=r('CrossoverMenuIndex');if ix==C.menu_target then return{a=true}end
  return{[assert(C.menu_moves[ix+1])]=true}
 end
 return{start=true}
end
emu.addEventCallback(function()
 if not entered then emu.setInput(menu(),0);return end
 if C.music==1 then emu.setInput({},0);return end
 local u=(step-phaseStart)%64;local walking=phaseIndex>=2
 emu.setInput({right=walking and u<32,left=walking and u>=32,b=phaseIndex>=4 and step%16<4,up=phaseIndex==5},0)
end,emu.eventType.inputPolled)
if C.music~=1 then
 emu.addMemoryCallback(function()
  if not entered or bank(L.LmMovementGate)~=B.LmMovementGate then return end
  if step%120==0 then phaseIndex=phaseIndex+1;assert(phaseIndex<=5,'Bounded work');phaseStart=step;arena()end
  if phaseIndex==3 and(r('Enemy_Flag')~=0 or r('Enemy_Flag',1)~=0)then liveEnemies=liveEnemies+1 end
  if phaseIndex==4 and r('LmAttack')~=0 then attacks=attacks+1 end
  if phaseIndex==5 and r('LmSuper')~=0 and r('LmAttack')~=0 then supers=supers+1 end
  local q={wall,step,names[phaseIndex],r('Player_X_Position'),r('Player_PageLoc'),r('Player_Y_Position'),r('Player_State'),r('LmHealth'),r('LmStars'),r('LmHearts'),r('LmAttack'),r('LmSuper')}
  for i=0,1 do for _,n in ipairs({'Enemy_Flag','Enemy_X_Position','Enemy_Y_Position'})do q[#q+1]=r(n,i)end end
  trace:write(table.concat(q,',')..'\n');step=step+1
 end,emu.callbackType.exec,L.LmMovementGate)
end
emu.addEventCallback(function()
 wall=wall+1
 if not entered then
  if r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
   assert(r('SelectedCharacter')==15,'Cold menu selected Little Mac')
   assert(r('CrossoverBehaviorVersion')==C.hard,'Cold options selected requested mode')
   entered=true;w('AreaMusicQueue',1)
   if C.music==1 then for i=0,5 do w('Enemy_Flag',0,i)end;w('ScrollLock',1)end
  end
  assert(wall<1200,'Bounded menu entry');return
 end
 if dma then
  for i=0,255 do assert(emu.read(i,emu.memType.nesSpriteRam)==dma[i+1],'Exact source DMA reaches hardware OAM')end
  oamFrames=oamFrames+1
 end
 if C.music~=1 then assert(wall<3000,'Matched work deadline');return end
 age=age+1
 for i=0,5 do w('Enemy_Flag',0,i)end
 w('EnemyFrenzyBuffer',0);w('EnemyFrenzyQueue',0)
 w('GameTimerDisplay',4);w('GameTimerDisplay',0,1);w('GameTimerDisplay',0,2)
 if song and r('GamePauseStatus')%2==0 and r('RgAudioSilenced')==0 and r('GuestNativeEnable')~=0 then
  for reg=0,15 do
   local noise=reg>=12 and(r('GuestMixMask')&8)~=0
   if reg~=9 and reg~=13 and not noise then
    assert(actual[reg]==r('GuestNativeApu',reg),'Hardware mixer publishes original source image register='..reg..' got='..tostring(actual[reg])..' wanted='..r('GuestNativeApu',reg));hardware=hardware+1
   end
  end
 end
 if index==1 then
  if age==100 then w('Square1SoundQueue',2);w('NoiseSoundQueue',1)end
  if age>100 and age<140 and r('GuestMixMask')~=0 then fxSeen=true end
  if age==200 then pausedAt=sourceCalls;w('GamePauseStatus',1)end
  if age==220 then assert(sourceCalls==pausedAt and r('GuestNativeEnable')==0,'Pause holds original source cadence')end
  if age==230 then w('GamePauseStatus',0)end
  if age==245 then assert(sourceCalls>pausedAt,'Unpause resumes native source');resumed=true end
  if age==350 then w('AreaMusicQueue',128)end
  if age==370 then assert(r('RgAudioSilenced')==1 and r('GuestNativeEnable')==0,'Persistent requested silence');silenced=true end
  if age==390 then w('AreaMusicQueue',1)end
  if age==410 then assert(song==20 and sourceFrame<25,'New area restarts after silence');restarted=true end
 end
 if age>=cases[index][4]then
  progress()
  assert(song==cases[index][3],'Completed assigned original music selection')
  index=index+1;age=0
  if index>#cases then finish();return end
  song=nil;w('AreaMusicQueue',cases[index][1]);w('EventMusicQueue',cases[index][2])
 end
 assert(wall<12000,'Native music matrix deadline')
end,emu.eventType.endFrame)
