-- Real cold menu and enemy contact, explicitly staged native injury arenas.
local C=assert(CV3_DMC_NATIVE_CONFIG)
for n,a in pairs(C.ram)do L[n]=a end
local wall,index,age,nmis=0,0,0,0
local entered,done=false,false
local current=nil
local results,violations={},{}
local minSP,stackWrites=255,0
local irqStores,chrChecks,dmaChecks,draws,updates=0,0,0,0,0
local frameUpdates,frameDraws=0,0
local r=function(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local w=function(n,v,i)emu.write(assert(L[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
local function json(v)
 if type(v)=='table'then
  local o={};if #v>0 then for _,x in ipairs(v)do o[#o+1]=json(x)end;return'['..table.concat(o,',')..']'end
  for k,x in pairs(v)do o[#o+1]=string.format('%q',k)..':'..json(x)end;return'{'..table.concat(o,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)else return tostring(v)end
end
local function bank(a)local p=emu.convertAddress(a);return p and p.address//8192 or -1 end
local function valid(n)local h=C.hooks[n];return h and bank(h.address)==h.physical_bank end
local function bind(n)local h=C.hooks[n];for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Bound '..n..' opcode')end end
local function native()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function capture(name)
 local f=assert(io.open(OUTPUT..name..'.argb','wb'))
 for _,v in ipairs(emu.getScreenBuffer())do f:write(string.pack('<I4',v))end;f:close()
end
local function problem(message,data)
 violations[#violations+1]={case=index,age=age,wall=wall,message=message,data=data}
 local f=assert(io.open(OUTPUT..'violations.json','w'));f:write(json(violations));f:close()
 capture('failure-'..index..'-'..age);assert(false,message)
end
-- NMI_GUARD_INSERT
local audio=assert(io.open(OUTPUT..'apu.csv','w'))
audio:write('wall,case,age,audioUpdate,register,value,cycle,pc,bank\n')
local cadence=assert(io.open(OUTPUT..'cadence.csv','w'))
cadence:write('wall,case,age,updates,draws,attackAge,shot0,shot1,shot2,shot3,frameCounter,lag,cycle\n')
local actors=assert(io.open(OUTPUT..'actors.csv','w'))
actors:write('wall,case,age,playerX,playerY,state,health,invul,injuryTimer,enemyFlag,enemyX,enemyY,enemyState,injuryCalls,realInjuries\n')
local apuUpdate=-1
local audioEpoch=0
local lastDmcEnable=0
local lastApu={}
local upper=0;local physical={}
emu.addMemoryCallback(function(_,v)upper=v&3 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(a,v)physical[a-0x5120]=v+256*upper end,emu.callbackType.write,0x5120,0x512b)
local published=nil;local dma=nil
local function bytes(at,kind)local s={};for i=0,255 do s[#s+1]=string.char(emu.read(at+i,kind))end;return table.concat(s)end
emu.addMemoryCallback(function()
 if entered and not done and valid('DrawAllMetasprites')then draws=draws+1;frameDraws=frameDraws+1;current.draws=current.draws+1 end
end,emu.callbackType.exec,C.hooks.DrawAllMetasprites.address)
emu.addMemoryCallback(function()
 if entered and not done and valid('RosterOamReady')then published=bytes(L.Sprite_Data,emu.memType.nesDebug)end
end,emu.callbackType.exec,C.hooks.RosterOamReady.address)
emu.addMemoryCallback(function(_,v)
 dma=nil;if entered and not done and published then local s=bytes(v*256,emu.memType.nesDebug);if s==published then dma=s end end
end,emu.callbackType.write,0x4014)
for _,pc in ipairs(C.irq_scroll_stores)do
 emu.addMemoryCallback(function()
  if entered and not done then
   assert(bank(pc)==C.hooks.IrqScrollSplit.physical_bank,'Actual IRQ bank')
   assert(emu.getState()['ppu.scanline']==31,'Visible split scroll remains on line31');irqStores=irqStores+1
  end
 end,emu.callbackType.exec,pc)
end
local pendingReturns,installedReturns={},{}
local function onReturn(name,fn)
 local st=emu.getState();local sp=st['cpu.sp']
 local ret=(emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 local key=name..':'..ret
 pendingReturns[key]={sp=(sp+2)%256,bank=bank(ret),fn=fn}
 if not installedReturns[key]then
  installedReturns[key]=true
  emu.addMemoryCallback(function()
   local v=pendingReturns[key]
   if v and emu.getState()['cpu.sp']==v.sp and bank(ret)==v.bank then pendingReturns[key]=nil;v.fn()end
  end,emu.callbackType.exec,ret)
 end
end
emu.addMemoryCallback(function()
 if not entered or done or not valid('AudioUpdate')then return end
 audioEpoch=audioEpoch+1
 if current and current.cueEpoch then apuUpdate=audioEpoch-current.cueEpoch else apuUpdate=-1 end
 local start=emu.getState()['cpu.cycleCount']
 onReturn('AudioUpdate',function()
  current.audioCycles[#current.audioCycles+1]=emu.getState()['cpu.cycleCount']-start
  if current.dmcStarts>0 and r('BassDmcActive')==0 and r('GamePauseStatus')&1==0 then current.hardwareCompleted=true end
  if current.q.kind=='world'and r('NoiseSoundBuffer')~=0 and r('Cv3NoiseActive')==1 then
   assert(r('GuestMixMask')&8~=0,'Shared world noise retains its established priority')
   for _,i in ipairs({12,14,15})do assert(lastApu[0x4000+i]==r('GuestFxApu',i),'Actual hardware noise equals shared world effect image')end
   current.worldFrames=current.worldFrames+1
  end
 end)
end,emu.callbackType.exec,C.hooks.AudioUpdate.address)
emu.addMemoryCallback(function(_,v)
 if entered and not done and (v==21 or v==22 or v==26) then
  current.requests=current.requests+1
  current.cueEpoch=audioEpoch+1;current.cueSerial=(current.cueSerial or 0)+1
  local st=emu.getState();current.requestTrace[#current.requestTrace+1]={value=v,pc=st['cpu.pc'],bank=bank(st['cpu.pc']),age=age}
 end
end,emu.callbackType.write,L.AvAudioRequest)
emu.addMemoryCallback(function(a,v)
 if not entered or done then return end
 local st=emu.getState();local row={update=apuUpdate,register=a,value=v,age=age,wall=wall,serial=current.cueSerial or 0}
 lastApu[a]=v
 if a==0x4015 then
  if v&16~=0 and lastDmcEnable==0 then
   current.dmcStarts=current.dmcStarts+1;current.firstDmcWall=current.firstDmcWall or wall
   assert(C.expected_dmc==1,'Unchanged Sypha control must not invent source DMC')
   local rate,start,length=lastApu[0x4010],0xc000+64*assert(lastApu[0x4012]),16*assert(lastApu[0x4013])+1
   assert(rate==C.expected_rate and lastApu[0x4011]==0 and length==#C.payload,'Actual source rate/DAC/length')
   assert(bank(start)==127,'DMC payload remains in fixed bank127')
   for i,value in ipairs(C.payload)do assert(emu.read(start+i-1,emu.memType.nesDebug)==value,'Actual mapped DMC source byte')end
   current.sourcePayloadChecks=current.sourcePayloadChecks+length
   if current.q.kind=='attack'and C.variant==3 and r('Cv3NoiseActive')==1 then current.pendingNoise=true end
  end
  lastDmcEnable=v&16
 end
 current.apu[#current.apu+1]=row
 audio:write(table.concat({wall,index,age,apuUpdate,a,v,st['cpu.cycleCount'],st['cpu.pc'],bank(st['cpu.pc'])},',')..'\n')
end,emu.callbackType.write,0x4000,0x4017)
emu.addMemoryCallback(function()
 if not entered or done or not valid('Cv3InjuryStartGate')then return end
 current.injuryCalls=current.injuryCalls+1
 local hp=C.character==5 and C.variant>0 and r('Cv3Health',C.variant-1)or r('PlayerStatus')
 onReturn('Cv3InjuryStartGate',function()
  local after=C.character==5 and C.variant>0 and r('Cv3Health',C.variant-1)or r('PlayerStatus')
  if after<hp then current.realInjuries=current.realInjuries+1;current.contactAge=current.contactAge or age end
 end)
end,emu.callbackType.exec,C.hooks.Cv3InjuryStartGate.address)
emu.addMemoryCallback(function()
 if entered and not done and valid('Cv3WeaponsGate')then
  if r('Cv3Fresh')&0x40~=0 and r('Cv3AttackAge')==0 then current.attacks=current.attacks+1;current.attackAge=age end
  for i=0,3 do if r('Cv3ShotType',i)==6 then current.shotUpdates=current.shotUpdates+1 end end
 end
end,emu.callbackType.exec,C.hooks.Cv3WeaponsGate.address)
if C.hooks.Cv3MusicAndNoiseTick then
 emu.addMemoryCallback(function()
  if not entered or done or not valid('Cv3MusicAndNoiseTick')then return end
  local stopping=r('Cv3NoiseActive')==128
  onReturn('Cv3MusicAndNoiseTick',function()
   if stopping then
    assert(r('Cv3NoiseActive')==0,'Real scene stop cancels source owner')
    assert(r('GuestNativeApu',12)==r('Cv3NoiseMusicVolume')and r('GuestNativeApu',14)==r('Cv3NoiseMusicPeriod')and r('GuestNativeApu',15)==r('Cv3NoiseMusicHigh'),'Scene stop restores actual underlying music noise')
    current.sceneStops=current.sceneStops+1
   end
  end)
 end,emu.callbackType.exec,C.hooks.Cv3MusicAndNoiseTick.address)
end
local function seed(q)
 assert(r('SelectedCharacter')==C.character,'Selected through native character menu')
 if C.character==5 then assert(r('Cv3Variant')==C.variant,'Chosen through real Select alternate')end
 w('CrossoverBehaviorVersion',q.mode or 1)
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i);w('Enemy_State',0,i);w('MmEnemyFlash',0,i)end
 for i=0,1 do w('Block_State',0,i);w('BlockMetasprite',0,i)end
 for i=0,8 do w('Misc_State',0,i);w('MiscMetasprite',0,i)end
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x);w('MmSolidTerrain',1,p*208+176+x)end end
 for _,n in ipairs({'TimerControl','GamePauseStatus','GuestHurtKind','GuestHurtTicks','PlayerChangeSizeFlag','MmDeathFlag','AreaParserTaskNum','ScrollThirtyTwo','EnemyFrenzyBuffer','EnemyFrenzyQueue','BlockBounceTimer','FireballThrowingTimer','CrouchingFlag','RgCrouch','DisableCollisionDet','GameTimerExpiredFlag','AvAudioRequest','AvAudioId','AvAudioMask','AvAudioOldMask','RgSfx','Square1SoundQueue','Square2SoundQueue','NoiseSoundQueue','Cv3AttackAge','Cv3Previous','Cv3Fresh','Cv3Bat','Cv3HurtAge','Cv3JumpActive','Cv3VxLo','Cv3VxHi','Cv3VyLo','Cv3VyHi','Cv3JumpPhase','Cv3Climb'})do w(n,0)end
 for i=0,3 do w('Cv3ShotType',0,i)end
 w('AvAudioChar',C.character);w('InjuryTimer',0);w('Cv3Invul',0);w('GuestInvulTicks',0)
 w('Player_X_Position',q.face==2 and 160 or 64);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('Player_X_Scroll',0);w('PlayerSize',0);w('PlayerStatus',q.kind=='pressure'and 2 or 1);w('Player_CollisionBits',3);w('PlayerFacingDir',q.face or 1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0);w('ScrollLock',1)
 w('EnemyDataLow',L.E_GroundArea10%256);w('EnemyDataHigh',L.E_GroundArea10//256)
 w('GameTimerDisplay',3);w('GameTimerDisplay',0,1);w('GameTimerDisplay',0,2)
 if C.character==5 and C.variant>0 then w('Cv3Power',0,C.variant-1);w('Cv3Subweapon',0,C.variant-1);w('Cv3Health',64,C.variant-1)end
 current={name=q.name,q=q,attacks=0,requests=0,requestTrace={},shotUpdates=0,apu={},draws=0,frames=0,audioCycles={},cueEpoch=nil,cueSerial=0,wallStart=wall,pauseFrames=0,sceneStops=0,dmcStarts=0,worldFrames=0,injuryCalls=0,realInjuries=0,sourcePayloadChecks=0,hardwareCompleted=false}
 if q.kind~='attack'then
  for i=0,(q.kind=='pressure'and 5 or 0)do
   w('Enemy_Flag',1,i);w('Enemy_ID',6,i);w('Enemy_X_Position',92+i*20,i);w('Enemy_PageLoc',0,i)
   w('Enemy_Y_Position',184,i);w('Enemy_Y_HighPos',1,i);w('Enemy_MovingDir',2,i);w('Enemy_X_Speed',248,i);w('Enemy_Y_Speed',0,i)
  end
 end
 lastDmcEnable=0;lastApu={}
 age=0;apuUpdate=-1
 print('CV3_AUDIO_SEED '..json({case=index,name=q.name,wall=wall}))
end
local function finishCase()
 local q=current.q
 local diagnostic=assert(io.open(OUTPUT..'last-case.json','w'));diagnostic:write(json(current));diagnostic:close();capture('case-'..index..'-before-assert')
 assert(current.injuryCalls>0 and current.realInjuries>0,'Real enemy contact reaches actual injury owner and loses health/power')
 current.sourceExact=C.expected_dmc==0 and current.dmcStarts==0 or current.dmcStarts>0 and current.sourcePayloadChecks>0
 if C.observe~=1 or C.new_route~=1 then assert(current.sourceExact,'Actual injury has source-bound DMC hardware')end
 if current.sourceExact and C.expected_dmc==1 then
  assert(current.requests>0 and current.hardwareCompleted,'Actual request and hardware completion are exercised')
  if q.kind=='pause'then assert(current.pauseFrames>=30 and r('BassDmcActive')==0,'Actual Start pause/resume stops DMC and leaves no stale restart')end
 end
 if q.kind=='attack'then assert(current.attacks>0,'Real B precedes contact');if C.variant==3 and C.observe~=1 then assert(current.pendingNoise,'Source fireball noise remains active when injury DMC starts')end end
 current.cueEpoch=current.cueEpoch or -1
 current.durationUpdates=age
 results[#results+1]=current
 capture('case-'..index..'-end')
end
emu.addMemoryCallback(function()
 if done or not valid('PauseSkip')or not native()then return end
 if not entered then
  if r('SelectedCharacter')~=C.character or(C.character==5 and r('Cv3Variant')~=C.variant)then return end
  entered=true;index=1;seed(C.cases[index]);return
 end
 updates=updates+1;frameUpdates=frameUpdates+1;age=age+1
 if age==28 and current.q.kind=='attack'then
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_X_Position',(r('Player_X_Position')-8)&255);w('Enemy_PageLoc',0)
  w('Enemy_Y_Position',184);w('Enemy_Y_HighPos',1);w('Enemy_MovingDir',1);w('Enemy_X_Speed',8);w('Enemy_Y_Speed',0)
 end
 if age>=C.cases[index].updates then
  finishCase();index=index+1
  if index>#C.cases then done=true else seed(C.cases[index])end
 end
end,emu.callbackType.exec,C.hooks.PauseSkip.address)
emu.addEventCallback(function()
 local b={}
 if not entered then
  if wall>=120 and wall%12==0 then
   if r('CrossoverMenuState')~=2 then b.start=true
   elseif r('CrossoverMenuIndex')~=C.menu_index then b[assert(C.menu_next[tostring(r('CrossoverMenuIndex'))])]=true
   elseif C.character==5 and r('Cv3Variant')~=C.variant then b.select=true else b.a=true end
  end
 elseif not done then
  local q=current.q
  if q.kind=='attack'then b.b=age>=4 and age<=6
  else b.right=age<20 and current.realInjuries==0 end
  if q.kind=='pause'and current.firstDmcWall then b.start=wall==current.firstDmcWall+1 or wall==current.firstDmcWall+50 end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1;assert(wall<5500,'Bounded native CV3 sound fixture')
 if entered and not done then
  current.frames=current.frames+1
  actors:write(table.concat({wall,index,age,r('Player_X_Position'),r('Player_Y_Position'),r('Player_State'),r('Cv3Health',math.max(0,C.variant-1)),r('Cv3Invul'),r('InjuryTimer'),r('Enemy_Flag'),r('Enemy_X_Position'),r('Enemy_Y_Position'),r('Enemy_State'),current.injuryCalls,current.realInjuries},',')..'\n');actors:flush()
  if current.q.kind=='pause'and r('GamePauseStatus')&1~=0 then current.pauseFrames=current.pauseFrames+1 end
  local st=emu.getState()
  for i=0,11 do assert(st['mapper.chrBanks'..i]==physical[i],'Actual CHR hardware latch/window agrees');chrChecks=chrChecks+1 end
  if dma then assert(bytes(0,emu.memType.nesSpriteRam)==dma,'Complete committed OAM reaches actual DMA');dmaChecks=dmaChecks+1;dma=nil end
  cadence:write(table.concat({wall,index,age,frameUpdates,frameDraws,r('Cv3AttackAge'),r('Cv3ShotType'),r('Cv3ShotType',1),r('Cv3ShotType',2),r('Cv3ShotType',3),r('FrameCounter'),frameUpdates==0 and 1 or 0,st['cpu.cycleCount']},',')..'\n')
  frameUpdates,frameDraws=0,0
 end
 if done then
  audio:close();cadence:close();actors:close()
  assert(nmis>100 and irqStores>100 and dmaChecks>50,'Native interrupts, IRQ, OAM and CHR exercised')
  local f=assert(io.open(OUTPUT..'proof.json','w'));f:write(json({passed=true,observe=C.observe,cases=results,nmis=nmis,irq_scroll_writes=irqStores,min_sp=minSP,stack_writes=stackWrites,nmi_mapper_store_windows=nmiWindows,hardware_chr_checks=chrChecks,complete_dma_checks=dmaChecks,draws=draws,updates=updates,staged=true}));f:close()
  print('CV3_AUDIO_NATIVE_COMPLETE');emu.stop(0)
 end
end,emu.eventType.endFrame)
