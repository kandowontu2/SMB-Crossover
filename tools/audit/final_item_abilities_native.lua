-- Runs in the same lexical chunk as the immutable progression fixture.
-- Only legal arena/target setup is written; acquired tier and ability state
-- remain owned by actual ROM input, movement, collision and native returns.
local abilityResults,abilityQueue={},{}
local abilityIndex,abilityTier,abilityOrigin=0,0,''
local currentAbility=nil
local abilityTrace=assert(io.open(OUTPUT..'ability-updates.csv','w'))
abilityTrace:write('wall,update,tier,case,age,kind,x,y,state,vyHi,fuel,flight,reach,returning,pogo,enemyFlag,enemyState,enemyHealth,injury\n')
local function health()return r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')end
local function signedV()local v=r('MmVY')+256*r('MmVY',1)+65536*r('MmVY',2);return v>=0x800000 and v-0x1000000 or v end
local pendingReturns,installedReturns={},{}
local function onReturn(name,fn)
 local st=emu.getState();local sp=st['cpu.sp'];local ret=(emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 local key=name..':'..ret;pendingReturns[key]={sp=(sp+2)%256,bank=bank(ret),fn=fn}
 if not installedReturns[key]then installedReturns[key]=true;emu.addMemoryCallback(function()
  local q=pendingReturns[key];if not q or emu.getState()['cpu.sp']~=q.sp or bank(ret)~=q.bank then return end
  pendingReturns[key]=nil;q.fn()
 end,emu.callbackType.exec,ret)end
end
local function stageEnemy(raised)
 -- Native ChkUnderEnemy probes canonicalY+24; EnemyLanding aligns low8.
 -- Thus a Goomba standing on192/208 begins at168/184, not176/192.
 local q=currentAbility.q;local x=112+(q.face==1 and 24 or-24);local y=raised and 168 or 184
 if raised then local col=x//16;w('Block_Buffer_1',0x54,160+col);tile(0,col,12,0x54)end
 if q.kind=='pogo_enemy'then x=112 end
 for _,v in ipairs({{'Enemy_Flag',1},{'Enemy_ID',6},{'Enemy_State',0},{'Enemy_X_Position',x},{'Enemy_PageLoc',0},{'Enemy_Y_Position',y},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_Y_MoveForce',0},{'Enemy_MovingDir',1},{'Enemy_BoundBoxCtrl',9},{'EnemyOffscrBitsMasked',0},{'Enemy_CollisionBits',0},{'MmEnemyHealthLo',0},{'MmEnemyHealthHi',0},{'MmEnemyFlash',0},{'RgEnemyStun',0}})do w(v[1],v[2],0)end
 currentAbility.enemySpawned=true;event('ability-target-staged',{kind='native stationary Goomba/default health',x=x,y=y,raised=raised})
end
abilityBegin=function(tier,origin)
 assert(r('PlayerStatus')==tier,'Ability tier is actual cold/physical result')
 abilityTier=tier;abilityOrigin=origin;abilityQueue={};abilityIndex=0
 for _,q in ipairs(C.abilities)do if q.tier==tier then abilityQueue[#abilityQueue+1]=q end end
 phase='ability-setup';age=0
end
abilityStage=function(tick)
 if tick then
  local a=currentAbility
  if a.q.kind=='pogo_enemy'and not a.enemySpawned and age>=16 then
   if r('Player_State')~=0 and r('Player_Y_Position')+32<192 then
    writeBoundary=true;stageEnemy(false);writeBoundary=false
   else assert(age<30,'Fixture must introduce target below a genuinely airborne body without overlap')end
  end
  return
 end
 abilityIndex=abilityIndex+1;local q=assert(abilityQueue[abilityIndex])
 assert(r('PlayerStatus')==abilityTier,'No tier injection between native abilities')
 assert(r('ScPogo')==0 and r('ScAttack')==0 and r('RgAttack')==0,'Prior native attack/pogo cleanup before next setup')
 if C.family=='rygar'then assert(r('XgDiskReach')==0,'Prior disk really caught before next setup')end
 writeBoundary=true;arena()
 for i=0,5 do w('MmEnemyHealthLo',0,i);w('MmEnemyHealthHi',0,i);w('MmEnemyFlash',0,i);w('RgEnemyStun',0,i)end
 w('PlayerFacingDir',q.face);w('Player_MovingDir',q.face);w('Player_CollisionBits',255);w('MmOldX',112)
 currentAbility={q=q,tier=abilityTier,origin=abilityOrigin,started=wall,samples={},damageCalls=0,hits=0,defeats=0,bounces=0,burn=0,minFuel=60,meleeSeen=false,airSeen=false,flightSeen=false,releaseSeen=false,recharged=false,caught=false}
 abilityResults[#abilityResults+1]=currentAbility
 if q.kind=='hammer'or q.kind=='disk_hit'then stageEnemy(true)end
 writeBoundary=false;phase='ability';age=0;FINAL_ABILITY_PHASE={name=q.name,tier=abilityTier,origin=abilityOrigin}
 event('ability-started',FINAL_ABILITY_PHASE);capture('ability-'..#abilityResults..'-start')
end
abilityInput=function()
 local a=currentAbility;local q=a.q;local b={}
 if q.kind=='hammer'then b.select=age>=5 and age<9
 elseif q.kind=='disk_free'or q.kind=='disk_hit'then b.b=age>=5 and age<9
 elseif q.kind:match('^flight_')then
  b.a=(age>=4 and age<10)or(age>=16 and age<(q.kind=='flight_release'and 35 or 110))
  if q.kind=='flight_full'and a.landedAt then b.a=b.a or(age>=a.landedAt+2 and age<a.landedAt+8)end
 elseif q.kind=='pogo_ground'or q.kind=='pogo_enemy'then
  b.a=age>=4 and age<12
  local hold=age>=14 and(q.kind=='pogo_ground'and age<170 or(q.kind=='pogo_enemy'and a.bounces==0))
  b.down=hold;b.b=hold
 end
 return b
end
hook('MegaManWeapons::DamageEnemy',function()
 if phase~='ability'or not currentAbility or emu.getState()['cpu.x']~=0 then return end
 local a=currentAbility;local kind=a.q.kind
 local expected=kind=='hammer'and 38 or kind=='disk_hit'and 29 or kind=='pogo_enemy'and 10 or-1
 assert(r('MmBulletType')==expected,'Actual source ability owns enemy contact')
 if kind=='hammer'then assert(r('RgAttackAge')>=4 and r('RgAttackAge')<9,'Hammer hits only during source active phases')end
 if kind=='pogo_enemy'then assert(r('ScPogo')==1 and signedV()>0,'Pogo contact requires actual descent')end
 a.damageCalls=a.damageCalls+1;local oldHealth=health();local oldState=r('Enemy_State')
 event('actual-ability-damage-entry',{type=r('MmBulletType'),health=oldHealth,state=oldState,vy=signedV()})
 onReturn('ability-damage',function()
  if r('Enemy_State')~=oldState or health()~=oldHealth then a.hits=a.hits+1;event('actual-ability-damage-return',{health=health(),state=r('Enemy_State'),flag=r('Enemy_Flag')});capture('ability-'..#abilityResults..'-hit')end
 end)
end)
hook('ShellOrBlockDefeat',function()
 if phase=='ability'and currentAbility and emu.getState()['cpu.x']==0 then currentAbility.defeats=currentAbility.defeats+1;event('actual-native-enemy-defeat',{type=r('MmBulletType'),enemy=r('Enemy_ID')})end
end)
hook('ExpandedWeapons::CatchDisk',function()
 if phase~='ability'or C.family~='rygar'then return end
 assert(r('XgDiskReach')==16 and r('XgDiskReturning')==1,'Source catch crosses below20 after full retraction')
 currentAbility.caught=true;event('actual-native-disk-catch',{reach=r('XgDiskReach')});capture('ability-'..#abilityResults..'-catch')
end)
hook('PitFlightUpdate',function()
 if phase~='ability'or C.family~='pit'then return end
 local a=currentAbility;local before={state=r('Player_State'),tier=r('PlayerStatus'),fuel=r('XgPitFuel'),flight=r('XgPitFlight'),a=r('A_B_Buttons')&128,down=r('SavedJoypadBits')&4,water=r('MmUnderwater')}
 if before.state~=0 then a.airSeen=true end
 if before.state~=0 and age>=15 and age<30 and r('XgFresh')&128~=0 then a.secondAirAttempt=true end
 onReturn('pit-flight',function()
  local active=before.state~=0 and before.state~=3 and before.tier==2 and before.water==0 and before.a~=0 and before.down==0 and before.fuel>0 and before.flight~=0
  if active then
   assert(r('XgPitFuel')==before.fuel-1 and r('XgPitFlight')==1,'One actual fuel unit per eligible native flight update')
   assert(r('XgPitBlocked')==0 and r('MmVY')==0 and r('MmVY',1)==128 and r('MmVY',2)==254,'Source lift is exactly1.5px/update in the empty roof arena')
   a.burn=a.burn+1;a.flightSeen=true
   if a.burn==1 or a.burn==30 or r('XgPitFuel')==0 then capture('ability-'..#abilityResults..'-flight-'..a.burn)end
  elseif before.state==0 then
   assert(r('XgPitFuel')==60 and r('XgPitFlight')==0,'Actual ground refresh recharges60')
   if a.burn>0 then a.recharged=true end
  else
   assert(r('XgPitFuel')==before.fuel,'Ineligible flight never consumes fuel')
   if before.tier~=2 or before.water~=0 or before.a==0 or before.down~=0 or before.fuel==0 or before.state==3 then assert(r('XgPitFlight')==0,'Source flight cancels at its actual gate')end
   if before.flight~=0 and before.a==0 and before.fuel>0 then a.releaseSeen=true;capture('ability-'..#abilityResults..'-release')end
  end
  a.minFuel=math.min(a.minFuel,r('XgPitFuel'))
 end)
end)
hook('ScroogeMovement::Bounce',function()
 if phase~='ability'or C.family~='scrooge'then return end
 local a=currentAbility;assert(r('ScPogo')==1,'Actual engaged pogo owns bounce')
 a.bounces=a.bounces+1;local state=r('Player_State');event('actual-native-pogo-bounce-entry',{state=state,vy=signedV(),health=health()})
 if a.q.kind=='pogo_ground'then assert(state==0,'Ground cycle bounce comes from real native support')end
 onReturn('pogo-bounce',function()
  assert(r('Player_State')==1 and r('MmVY')==0 and r('MmVY',1)==37 and r('MmVY',2)==250,'Native dry pogo launch writes exactFA2500 before its ordinary gravity')
  assert(r('InjuryTimer')==0,'Successful pogo never grants body injury');capture('ability-'..#abilityResults..'-bounce-'..a.bounces)
 end)
end)
local function abilityComplete()
 local a=currentAbility;a.finished=wall;a.gameUpdates=age;event('ability-completed',{name=a.q.name,tier=a.tier,hits=a.hits,bounces=a.bounces,burn=a.burn,samples=#a.samples});capture('ability-'..#abilityResults..'-complete')
 if abilityIndex<#abilityQueue then phase='ability-setup';age=0
 elseif abilityTier==0 then phase='next';age=0
 elseif index<#C.steps then index=index+1;phase='next';age=0
 else done=true;phase='complete'end
end
abilityFinish=function()
 local a=currentAbility;local q=a.q;assert(r('PlayerStatus')==a.tier,'Tier remains physically acquired throughout the ability case')
 assert(r('InjuryTimer')==0 and r('MmDeathFlag')==0 and r('GameEngineSubroutine')==8,'Bounded ability remains healthy/playable')
 FINAL_ABILITY_PHASE={name=q.name,tier=a.tier,age=age,origin=a.origin,wall=wall,update=updates}
 abilityTrace:write(table.concat({wall,updates,a.tier,#abilityResults,age,q.kind,r('Player_X_Position'),r('Player_Y_Position'),r('Player_State'),r('MmVY',2),r('XgPitFuel'),r('XgPitFlight'),r('XgDiskReach'),r('XgDiskReturning'),r('ScPogo'),r('Enemy_Flag'),r('Enemy_State'),health(),r('InjuryTimer')},',')..'\n')
 if q.kind=='hammer'then
  if r('RgAttack')>0 then a.meleeSeen=true end
  if age>=q.limit then assert(a.meleeSeen and a.hits==1 and a.defeats==1 and r('RgAttack')==0,'Actual hammer hit, native defeat, single-hit receipt and cleanup');abilityComplete()end
 elseif q.kind=='disk_free'or q.kind=='disk_hit'then
  local slot=nil;for i=0,9 do if r('RgShotType',i)==2 then assert(slot==nil,'Rygar admits one actual disk');slot=i end end
  if slot then
   a.diskSeen=true;local shotAge=r('RgShotAge',slot)
   if shotAge<3 then assert(r('RgShotHits',slot)==0,'Invisible windup has no hit receipt')end
   if shotAge>=3 then
    local sequence={};for v=24,q.reach,4 do sequence[#sequence+1]=v end;for v=q.reach-4,20,-4 do sequence[#sequence+1]=v end
    local reach=r('XgDiskReach');a.samples[#a.samples+1]=reach
    assert(reach==sequence[#a.samples],'Actual disk extension/retraction sequence follows acquired reach')
    local expected=r('Player_X_Position')+256*r('Player_PageLoc')+8+(q.face==1 and reach or 2-reach)
    assert(r('RgShotX',slot)+256*r('RgShotPage',slot)==expected and r('RgShotY',slot)==r('Player_Y_Position')+8,'Actual disk stays on original mirrored hand anchor')
    if reach==q.reach or reach==24 and r('XgDiskReturning')~=0 then capture('ability-'..#abilityResults..'-disk-'..#a.samples)end
   end
  end
  if age>=q.limit then
   local expectedCount=(q.reach-24)//4+1+(q.reach-20)//4
   assert(a.diskSeen and a.caught and slot==nil and #a.samples==expectedCount and r('XgDiskReach')==0 and r('RgShootPose')==0,'Disk fully extends, retracts and really catches')
   assert(q.kind=='disk_free'and a.hits==0 and a.defeats==0 or q.kind=='disk_hit'and a.hits==1 and a.defeats==1,'Disk actual enemy hit and one-hit receipt match case')
   abilityComplete()
  end
 elseif q.kind:match('^flight_')then
  if a.flightSeen and r('XgPitFuel')==0 and r('XgPitFlight')==0 then a.exhausted=true end
  if a.burn>0 and r('Player_State')==0 then a.landedAt=a.landedAt or age;if r('XgPitFuel')==60 then a.recharged=true end end
  if q.kind=='flight_full'and a.landedAt and age>a.landedAt and r('Player_State')~=0 then
   assert(r('XgPitFuel')==60 and r('XgPitFlight')==0,'Next real grounded launch retains source recharge');a.relaunched=true
  end
  if age>=q.limit then
   if q.kind=='flight_gate'then assert(a.airSeen and a.secondAirAttempt and not a.flightSeen and a.burn==0 and r('XgPitFuel')==60 and r('Player_State')==0,'Only acquired tier2 can activate flight on fresh airborne A')
   elseif q.kind=='flight_full'then assert(a.burn==60 and a.minFuel==0 and a.exhausted and a.recharged and a.relaunched and r('Player_State')==0 and r('XgPitFuel')==60,'Full native temporary-flight budget, exhaustion, actual landing recharge and next jump')
   else assert(a.burn>0 and a.burn<60 and a.releaseSeen and a.recharged and r('Player_State')==0 and r('XgPitFuel')==60,'Native A release cancels partial flight and actual landing recharges')end
   abilityComplete()
  end
 elseif q.kind=='pogo_ground'or q.kind=='pogo_enemy'then
  if r('ScPogo')~=0 then a.pogoSeen=true end
  if a.pogoSeen and r('ScPogo')==0 then a.cancelSeen=true end
  if age>=q.limit then
   assert(a.pogoSeen and a.cancelSeen and r('ScPogo')==0 and r('Player_State')==0,'Actual pogo release cancels and returns to support')
   if q.kind=='pogo_ground'then assert(a.bounces>=2 and a.hits==0,'Held pogo chains real ground rebounds')
   else assert(a.enemySpawned and a.hits==1 and a.defeats==1 and a.bounces==1,'Actual descending pogo defeats native Goomba once and rebounds safely')end
   abilityComplete()
  end
 end
 assert(age<400,'Bounded family ability')
end
abilityReport=function()
 abilityTrace:close()
 local f=assert(io.open(OUTPUT..'native-abilities.json','w'));f:write(json({passed=true,goal_complete=false,family=C.family,hard=C.hard,physical_collections=records,abilities=abilityResults,updates=updates,nmis=nmis,minSP=minSP,apuWrites=apuWrites,irq_scroll_stores=irqStores,hardware_chr_checks=chrChecks,complete_dma_checks=dmaChecks,scope='Cold0 and physically acquired1/2; actual head/reveal/full rise/contact/transforms, then native controller abilities. World/target placement disclosed; no tier/fuel/flight/reach/pogo injection. No all-item/campaign/original-pixel/audio-fidelity claim.'}));f:close()
end
for _,name in ipairs({'XgPitFuel','XgPitFlight','XgDiskReach','XgDiskReturning','ScPogo','ScEnemy','MmEnemyHealthLo','MmEnemyHealthHi'})do
 emu.addMemoryCallback(function(_,v)if phase=='ability'and not writeBoundary then event('native-ability-write',{name=name,before=r(name),value=v})end end,emu.callbackType.write,assert(L[name]))
end
