-- Source-prepared lifecycle instrumentation/controller helpers, never game code.
-- Every game-RAM write is inside the one prearena seed scope. Runtime is read-only.
local lifeLog=assert(io.open(OUTPUT..'lifecycle.jsonl','w'))
local function lifeRow(kind,data)
 if not entered or done then return end
 data=data or{};data.kind=kind;data.wall=wall;data.age=age;data.audioEpoch=audioEpoch
 local s=emu.getState();data.cpuCycle=s['cpu.cycleCount'];data.pc=s['cpu.pc'];data.bank=bank(data.pc)
 lifeLog:write(json(data)..'\n');lifeLog:flush()
end
local function lifeHook(n,fn)
 local h=assert(C.hooks[n],n)
 emu.addMemoryCallback(function()if entered and not done and valid(n)then bind(n);fn()end end,emu.callbackType.exec,h.address)
end
local function lifeVoice()
 return{owned=voice('Cv3FxOwned'),noise=voice('Cv3FxNoiseID'),pulse=voice('Cv3FxPulseID'),noiseActive=r('Cv3NoiseActive'),noiseIndex=r('Cv3NoiseIndex'),paused=r('GamePauseStatus')&1,silenced=r('RgAudioSilenced'),operMode=r('OperMode'),task=r('OperMode_Task'),gameSub=r('GameEngineSubroutine')}
end
local function lifeEnemy(x,speed,id,bbox)
 for n,v in pairs{Enemy_Flag=1,Enemy_ID=id,Enemy_State=0,Enemy_X_Position=x,Enemy_PageLoc=0,Enemy_Y_Position=184,Enemy_Y_HighPos=1,Enemy_MovingDir=1,Enemy_X_Speed=speed,Enemy_Y_Speed=0,Enemy_BoundBoxCtrl=bbox}do w(n,v,0)end
end
local function lifeStage(q)
 assert(lifeStaging,'Only the initial arena seed may stage actors')
 current.life={pickups=0,sceneResets=0,musicResets=0,activeSceneCancel=0,audioTicks=0,pausedAudioTicks=0,sourceDmcOverlap={},dmcCount=0,pipeEntries=0,areaLoads=0,bonusNativeFrames=0}
 if q.profile=='mixed'then
  lifeEnemy(24,16,2,3) -- normal armoredBuzzy, original InitNormalEnemy bbox3.
 elseif q.profile=='priority'then
  for n,v in pairs{Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,Enemy_X_Position=80,Enemy_PageLoc=0,Enemy_Y_Position=184,Enemy_Y_HighPos=1,Enemy_BoundBoxCtrl=3,PowerUpType=1,InvPickup=0xd3,InvPickupOwner=5,Cv3PickupVariant=2,InvRisePhase=0}do w(n,v,5)end
 elseif q.profile=='death'then
  w('Cv3Health',1,C.variant-1);lifeEnemy(32,16,6,9)
 elseif q.profile=='scene'then
  -- Original1-1 normal pipe destination: E_GroundArea6 starts1E,C2,00.
  -- Isolated original pipe topology/scene setup; no controller traversal claim.
  w('Player_X_Position',72);w('AreaPointer',0xc2);w('AreaType',1);w('WarpZoneControl',0);w('Cv3LastArea',0xc2)
  w('Block_Buffer_1',0x10,176+4);w('Block_Buffer_1',0x11,176+5)
 elseif q.profile=='pressure'then
  -- All six actors are seeded once. No periodic respawn/outcome writes.
  for i=0,5 do w('Enemy_X_Speed',0,i);w('Enemy_BoundBoxCtrl',9,i)end
 end
 lifeRow('seed',{profile=q.profile,variant=C.variant,mode=r('CrossoverBehaviorVersion'),voice=lifeVoice(),health=r('Cv3Health',C.variant-1),subweapon=r('Cv3Subweapon',C.variant-1)})
end
local function lifeInput()
 local q=current.q;local b={};local t=age;local physical=wall-current.wallStart
 local pressed=t>=4 and t<=6
 if q.profile=='scene'then pressed=physical>=4 and physical<=6 end
 if q.profile=='priority'then pressed=pressed or t>=36 and t<=38;b.right=t>=18 and t<=34 end
 if q.profile=='pressure'and q.kind=='fireball'then pressed=t%32>=4 and t%32<=6 end
 if q.kind=='sub'then b.b=pressed;b.up=pressed
 elseif q.kind=='fireball'then b.b=pressed
 elseif q.kind=='bat'then b.a=pressed;b.down=pressed end
 if q.profile=='mixed'and t>=26 and t<=28 then b.b=true;b.up=false end
 if q.profile=='pause'and current.firstActionWall then b.start=wall==current.firstActionWall+1 or wall==current.firstActionWall+50 end
 return b
end
local function lifeFinish()
 local q=current.q;local x=current.life
 if q.kind=='idle'then assert(current.requests==0 and current.spawnCalls==0 and current.realInjuries==0,'Cue-free pressure remains genuine no-source control')
 elseif q.kind=='bat'then assert(current.batEntries==1,'Exactly one actual Down+A bat entry, no held-input retrigger')
 else assert(current.spawnCalls>0,'Real B/Up+B releases an actual actor')end
 if q.profile=='mixed'then
  assert(current.realInjuries>0 and r('Cv3Health',C.variant-1)>0,'Natural nonfatal armored-enemy contact reaches genuine injury owner')
  local attack,injury=false,false
  for _,d in ipairs(current.dmcRecords)do
   assert(d.reads>0,'Actual physical DMC payload reads, not request-only evidence')
   attack=attack or d.descriptor.sound==0x72;injury=injury or d.descriptor.sound==0x74
  end
  assert(attack and injury,'Actual source72 attack and74 injury play through real priority owner')
  if C.new_fx==1 then assert(x.sourceDmcOverlap['114']and x.sourceDmcOverlap['116'],'BOTH real DMC starts overlap authentic active source15 noise, not only pulse')end
 elseif q.profile=='priority'then
  assert(x.pickups==1 and r('Cv3Subweapon',C.variant-1)==3,'Actual seeded physical lightning pickup changes the carried item')
  local ice,lightning=0,0;for _,s in ipairs(current.spawnTypes)do if s.type==4 then ice=ice+1 elseif s.type==5 then lightning=lightning+1 end end
  assert(ice==3 and lightning>=1 and lightning<=3,'Real repeated controller casts execute both original triple spawn callsites')
  if C.new_fx==1 then assert(current.mixedPriority>0,'Original lower-priority lightning retains active ice noise')end
 elseif q.profile=='pause'then
  assert(current.pauseFrames>=30 and x.pausedAudioTicks>=30,'Actual Start pauses/resumes, not a staged pause flag')
 elseif q.profile=='death'then
  assert(current.deathCalls and current.realInjuries>0,'Natural preseeded enemy contact reaches actual KillPlayer')
  if C.new_fx==1 then assert(voice('Cv3FxOwned')==0 and r('Cv3NoiseActive')==0,'Actual death lifecycle cancels source voices')end
 elseif q.profile=='scene'then
  assert(x.pipeEntries>0 and x.areaLoads>0 and x.bonusNativeFrames>0,'Actual pipeâ†’loaderâ†’bonus-room native transition')
  if C.new_fx==1 then assert(x.activeSceneCancel>0 and voice('Cv3FxOwned')==0,'Real reset/music scene owner cancels a still-active source voice')end
 end
 lifeRow('finish',{profile=q.profile,counts=x,requests=current.requests,spawnCalls=current.spawnCalls,voice=lifeVoice()})
end
lifeHook('AudioUpdate',function()
 current.life.audioTicks=current.life.audioTicks+1;local before=lifeVoice()
 if before.paused~=0 then current.life.pausedAudioTicks=current.life.pausedAudioTicks+1 end
 lifeRow('audio-entry',before)
 onReturn('life-audio',function()lifeRow('audio-return',lifeVoice())end)
end)
lifeHook('Cv3CollectPickupGate',function()
 local x=emu.getState()['cpu.x'];local before=r('Cv3Subweapon',C.variant-1)
 onReturn('life-pickup',function()
  local after=r('Cv3Subweapon',C.variant-1)
  if after~=before then current.life.pickups=current.life.pickups+1;lifeRow('actual-pickup',{actor=x,before=before,after=after})end
 end)
end)
lifeHook('Cv3NoiseSceneReset',function()
 local before=lifeVoice();onReturn('life-scene-reset',function()
  current.life.sceneResets=current.life.sceneResets+1
  if before.owned~=0 and(before.noise~=0 or before.pulse~=0)then current.life.activeSceneCancel=current.life.activeSceneCancel+1 end
  lifeRow('actual-scene-reset',{before=before,after=lifeVoice(),protocol='Main commits CANCEL; actual NMI consumes before next source tick. No false immediate-ID-clear claim.'})
 end)
end)
if C.new_fx==1 then
 lifeHook('Cv3FxMusicInit',function()
  local before=lifeVoice();current.life.musicResets=current.life.musicResets+1
  if before.owned~=0 and(before.noise~=0 or before.pulse~=0)then current.life.activeSceneCancel=current.life.activeSceneCancel+1 end
  lifeRow('actual-music-init',{before=before})
 end)
end
lifeHook('NativeRareHandlePipeEntryCore',function()
 local prior=r('GameEngineSubroutine');onReturn('life-pipe',function()
  if prior==8 and r('GameEngineSubroutine')==3 then current.life.pipeEntries=current.life.pipeEntries+1;lifeRow('actual-pipe-entry',{timer=r('ChangeAreaTimer'),areaPointer=r('AreaPointer')})end
 end)
end)
emu.addMemoryCallback(function(_,v)
 if not entered or done or lifeStaging then return end
 if current.q.profile=='scene'and v==0 then current.life.areaLoads=current.life.areaLoads+1;lifeRow('actual-loader-task',{task=v,areaPointer=r('AreaPointer'),areaType=r('AreaType')})end
end,emu.callbackType.write,L.OperMode_Task)
emu.addEventCallback(function()
 if entered and not done and current.q.profile=='scene'and native()and r('AreaType')==2 then current.life.bonusNativeFrames=current.life.bonusNativeFrames+1 end
end,emu.eventType.endFrame)
emu.addMemoryCallback(function(_,v)
 if not entered or done or v&16==0 then return end
 local count=#current.dmcRecords;if count<=current.life.dmcCount then return end;current.life.dmcCount=count
 local d=current.dmcRecords[count];local source=lifeVoice()
 if C.new_fx==1 and source.owned&8~=0 and source.noise==0x15 then current.life.sourceDmcOverlap[tostring(d.descriptor.sound)]=true end
 lifeRow('actual-DMC-start',{sound=d.descriptor.sound,voice=source,bank=d.descriptor.bank,rate=d.descriptor.rate,address=d.descriptor.address,payloadBytes=#d.descriptor.payload})
end,emu.callbackType.write,0x4015)

-- Read-only mixer oracle: hardware expectation is composed from actual prior
-- complete register image/last/dirty and shared-noise owner, never a value mask.
local lifeMix=nil
local function lifeArray(n)
 local a={};for i=0,15 do a[#a+1]=r(n,i)end;return a
end
local function lifeMixEntry(owner)
 assert(lifeMix==nil,'One bounded native mixer flush at a time')
 local z={owner=owner,mask=r('GuestMixMask'),changed=r('GuestMixChanged'),image=lifeArray('GuestNativeApu'),last=lifeArray('GuestApuLast'),dirty=lifeArray('GuestNativeDirty'),fx=lifeArray('GuestFxApu'),fxDirty=lifeArray('GuestFxDirty'),hardware={}}
 lifeMix=z
 onReturn('life-mixer-flush',function()assert(lifeMix==z,'Mixer return owner');lifeRow('actual-mixer-flush',z);lifeMix=nil end)
end
lifeHook('GuestAudioNativeFlush',function()lifeMixEntry('native')end)
lifeHook('GuestAudioFinish::MixedChannels',function()lifeMixEntry('mixed')end)
emu.addMemoryCallback(function(at,v)
 if entered and not done and lifeMix then lifeMix.hardware[#lifeMix.hardware+1]={at,v}end
end,emu.callbackType.write,0x4000,0x400f)
if C.new_fx==1 then
 lifeHook('Cv3FxTick',function()
  local before=lifeVoice();lifeRow('source-tick-entry',before)
  onReturn('life-source-tick',function()lifeRow('source-tick-return',{before=before,after=lifeVoice()})end)
 end)
 lifeHook('Cv3FxMuteGate',function()lifeRow('source-mute-entry',lifeVoice())end)
end
