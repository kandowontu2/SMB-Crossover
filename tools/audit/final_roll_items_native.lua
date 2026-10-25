-- PREPARED, NOT NATIVE QUALIFIED. No emulator is launched by the preparer.
local C=assert(FINAL_ROLL_ITEMS)
local L=C.ram
assert(type(C.hard)=='boolean'and C.mode_value==(C.hard and 1 or 0),'Numeric/boolean mode agreement')
local wall,updates,index,age=0,0,0,0
local entered,done,writeBoundary=false,false,false
local phase,menuPhase='menu',C.mode_value==1 and'focus'or'start'
local current,heldDrop=nil,nil
local results,captures={},{}
local minSP,nmis,irqStores,chrChecks,dmaChecks,apuWrites,hudChecks=255,0,0,0,0,0,0
local forbidden={RlHealth=true,RlEnergy=true,RlFoodKind=true,RlCharge=true,RlChargeFired=true,
 RlInvul=true,RlHurt=true,RlReady=true,RlLife=true,RlArea=true,RlWorld=true,
 RlPrevious=true,RlFresh=true,RlVariant=true,SelectedCharacter=true,PlayerStatus=true,
 InvDropKind=true,InvDropAge=true,InvDropAgeHi=true,AvDropItem=true,PseudoRandomBitReg=true,
 PowerUpType=true,InvPickup=true,InvPickupOwner=true,InvRisePhase=true,MmBulletType=true,
 MmEnemyHealthLo=true,MmEnemyHealthHi=true,MmEnemyFlash=true,NumberofLives=true,
 InjuryTimer=true,StarInvincibleTimer=true,MmDeathFlag=true,GameEngineSubroutine=true}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)assert(writeBoundary and not forbidden[n],'Disclosed world/motion/target setup only: '..n);emu.write(assert(L[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
local function json(v)
 if type(v)=='table'then local t={};if #v>0 then for _,x in ipairs(v)do t[#t+1]=json(x)end;return'['..table.concat(t,',')..']'end
  for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..json(x)end;return'{'..table.concat(t,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local log=assert(io.open(OUTPUT..'events.jsonl','w'))
local trace=assert(io.open(OUTPUT..'updates.csv','w'));trace:write('wall,update,step,phase,age,hp,energy,food,charge,hurt,invul,injury,star,lives,x,y,state\n')
local apu=assert(io.open(OUTPUT..'apu.csv','w'));apu:write('wall,update,step,phase,register,value,pc,bank,cycle\n')
local function bank(pc)local p=emu.convertAddress(pc);return p and p.address//8192 or-1 end
local function event(kind,data)local s=emu.getState();log:write(json({kind=kind,data=data,wall=wall,update=updates,step=index,phase=phase,pc=s['cpu.pc'],bank=bank(s['cpu.pc']),sp=s['cpu.sp']})..'\n');log:flush()end
local function capture(name)captures[#captures+1]={name=string.format('%02d-',index)..name,wall=wall,update=updates,frame_counter=r('FrameCounter')}end
local function hook(name,fn)
 local h=assert(C.hooks[name]);emu.addMemoryCallback(function()
  if bank(h.address)~=h.physical_bank then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Exact instruction '..name)end
  minSP=math.min(minSP,emu.getState()['cpu.sp']);fn()
 end,emu.callbackType.exec,h.address)
end
local pendingReturns,installedReturns={},{}
local function onReturn(name,fn)
 local s=emu.getState();local sp=s['cpu.sp'];local ret=(emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 local key=name..':'..ret;pendingReturns[key]={sp=(sp+2)%256,bank=bank(ret),fn=fn}
 if not installedReturns[key]then installedReturns[key]=true;emu.addMemoryCallback(function()
  local q=pendingReturns[key];if not q or emu.getState()['cpu.sp']~=q.sp or bank(ret)~=q.bank then return end
  pendingReturns[key]=nil;q.fn()
 end,emu.callbackType.exec,ret)end
end
local function shots()local n=0;for i=0,3 do if r('MmBulletType',i)~=0 then n=n+1 end end;return n end
local function drops()local n=0;for i=0,3 do if r('InvDropKind',i)~=0 then n=n+1 end end;return n end
local function state()return{hp=r('RlHealth'),energy=r('RlEnergy'),food=r('RlFoodKind'),lives=r('NumberofLives'),star=r('StarInvincibleTimer')}end
local function menu()
 if wall<90 or wall%12~=0 then return{}end
 if menuPhase=='focus'then menuPhase='open';return{down=true}end
 if menuPhase=='open'then menuPhase='mode';return{a=true}end
 if menuPhase=='mode'then
  if r('CrossoverMenuState')~=4 then return{}end
  if r('CrossoverOptionsFocus')~=1 then return{down=true}end
  if r('CrossoverBehaviorVersion')==0 then menuPhase='back';return{a=true}end;menuPhase='back'
 end
 if menuPhase=='back'then menuPhase='start';return{b=true}end
 if menuPhase=='start'then if r('CrossoverMenuState')==2 then menuPhase='select'else return{start=true}end end
 if r('CrossoverMenuState')~=2 then return{}end
 local i=r('CrossoverMenuIndex');if i<6 then return{down=true}end
 if i~=9 then return{right=true}end
 if r('RlVariant')~=1 then return{select=true}end
 return{a=true}
end
local function tile(page,col,row,id)
 local function art(n)local a=C.art[n];return emu.read(a.bank*8192+a.address%8192+id,emu.memType.nesPrgRom)end
 local function put(a,v)assert(writeBoundary);emu.write(a,v,emu.memType.nesPpuDebug)end
 local at=0x2000+page*0x400+row*64+col*2
 put(at,art('MTileTopLeft'));put(at+1,art('MTileTopRight'));put(at+32,art('MTileBotLeft'));put(at+33,art('MTileBotRight'))
 local a=0x23c0+page*0x400+(row//2)*8+col//2;local shift=row%2*4+col%2*2
 put(a,(emu.read(a,emu.memType.nesPpuDebug)&(~(3<<shift)))|((art('MTileAttribute')>>6)<<shift))
end
local function arena(block)
 assert(shots()==0 and r('RlAttack')==0,'Prior projectiles/attack clean up natively')
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do for col=0,15 do for row=11,12 do w('Block_Buffer_1',0x54,p*208+row*16+col)end end end
 for p=0,1 do for row=2,14 do for col=0,15 do tile(p,col,row,row>=13 and 0x54 or 0)end end end
 if block then w('Block_Buffer_1',block,112+7);tile(0,7,9,block)end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_CollisionBits',0,i)end
 for i=0,3 do w('Block_State',0,i);w('BlockMetasprite',0,i)end
 for _,n in ipairs({'Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','ScrollThirtyTwo','AreaParserTaskNum','MmVX','MmVY'})do w(n,0)end
 for i=1,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('ScrollLock',1);w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_X_Position',112);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1)
 for i,v in ipairs({3,9,9})do w('GameTimerDisplay',v,i-1)end
end
local function target(x)
 for _,v in ipairs({{'Enemy_Flag',1},{'Enemy_ID',6},{'Enemy_State',0},{'Enemy_X_Position',x},{'Enemy_PageLoc',0},{'Enemy_Y_Position',184},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_Y_MoveForce',0},{'Enemy_MovingDir',2},{'Enemy_BoundBoxCtrl',9},{'Enemy_CollisionBits',0}})do w(v[1],v[2],0)end
 event('explicit-default-health-native-goomba',{x=x,y=184,high_page=1,no_enemy_health_write=true})
end
local function complete()
 current.finished=updates;current.after=state();event('step-completed',current);capture('complete');phase='cooldown';age=0
end
local function start()
 index=index+1;if index>#C.plan then done=true;phase='complete';return end
 local q=C.plan[index];current={q=q,before=state(),started=updates,injuries=0,charges=0,pellets=0,grants=0,kills=0,attempts=0,unwanted=0}
 results[#results+1]=current -- Additive bookkeeping fix; frozen Hard-v3 is still failed.
 if q.action~='death'then writeBoundary=true;arena(q.tile);writeBoundary=false end
 phase=q.action;age=0;event('step-started',current);capture('start')
 if phase=='block'then assert(r('RlFoodKind')==(q.type==0 and 0 or 1)or q.type>=2,'Source food parity, never injected status')end
 if phase=='charge'then assert(r('RlEnergy')>=4*q.count,'Earned energy available for actual charges')end
 if phase=='refuse'then assert(r('RlEnergy')==q.energy and q.energy<4,'Actual acquired/depleted low energy')end
 if phase=='star'then assert(r('StarInvincibleTimer')>0,'Physically acquired star still active')end
 if phase=='death'then
  assert(r('RlHealth')==4 and heldDrop~=nil and r('InvDropKind',heldDrop)~=0,'Earned low HP and genuine uncollected actor before death')
  current.oldLives=r('NumberofLives');current.hpBefore=r('RlHealth')
 end
end
hook('GameLoop',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then
  if r('GameEngineSubroutine')~=8 then return end
  assert(r('SelectedCharacter')==9 and r('RlVariant')==1 and r('CrossoverBehaviorVersion')==C.mode_value,'Actual cold Roll/numeric mode')
  entered=true;phase='settle';age=0;event('actual-cold-selection',{character=9,variant=1,mode=r('CrossoverBehaviorVersion'),requested_mode=C.mode_value})
 end
 updates=updates+1;age=age+1
 assert(r('SelectedCharacter')==9 and r('RlVariant')==1 and r('CrossoverBehaviorVersion')==C.mode_value,'Actual identity and numeric mode persist')
 if current and current.removeEnemy then writeBoundary=true;w('Enemy_Flag',0,0);writeBoundary=false;current.removeEnemy=nil end
 if phase=='setup'then start()
 elseif phase=='damage'and r('RlInvul')==0 and r('RlHurt')==0 and r('InjuryTimer')==0 and r('Player_State')==0 and r('Enemy_Flag')==0 and current.injuries<current.q.contacts then
  writeBoundary=true;arena(false);target(116);writeBoundary=false;current.contactPending=true
 elseif phase=='capsule'or phase=='expiry'or phase=='hold'then
  if not current.dropSlot and r('Enemy_Flag')==0 and shots()==0 and r('RlAttack')==0 and drops()==0 and age>(current.retryAt or 0)then
   assert(current.attempts<256,'Bounded actual native RNG search; never write RNG')
   writeBoundary=true;arena(false);target(160);writeBoundary=false;current.attempts=current.attempts+1;current.fireAge=age;current.targetActive=true
  elseif current.dropSlot and r('InvDropKind',current.dropSlot)==0 and current.grants==0 then
   event('uncollected-actor-native-cleanup',{slot=current.dropSlot,desired=current.desired});current.dropSlot=nil;current.retryAt=age+11+current.attempts%7
  end
 elseif phase=='death'and age==16 then
  assert(shots()>0 and r('InvDropKind',heldDrop)~=0,'Actual live projectile and earned drop before lethal contact')
  writeBoundary=true;target(116);writeBoundary=false;current.contactPending=true
 end
 if entered and not done and phase~='death'then assert(r('MmDeathFlag')==0 and r('GameEngineSubroutine')==8,'Lifecycle remains playable')end
end)
hook('RlPrepare',function()
 if phase~='block'then return end
 onReturn('actual-reveal',function()
  assert(emu.getState()['cpu.x']==5 and r('PowerUpType',5)==current.q.type,'Actual source reveal/type')
  current.reveal=updates;current.revealY=r('Enemy_Y_Position',5);event('native-reward-reveal',{type=current.q.type,state=state()});capture('reveal')
 end)
end)
hook('RlCollect',function()
 if not entered then return end
 assert(phase=='block'and current.q.type<2 and current.mature and current.headBlock,'Actual head/reveal/rise before food owner')
 onReturn('actual-food',function()
  assert(r('RlHealth')==28 and r('RlEnergy')==28 and r('RlFoodKind')==1,'Source full restore/cap')
  assert(r('Square2SoundQueue')==C.powerup_sfx,'Source food pickup sound')
  current.grants=current.grants+1;event('actual-food-grant',state());capture('food-granted')
 end)
end)
hook('MarioSourcePowerupCollision',function()
 if phase~='block'then return end
 assert(current.mature and current.headBlock,'No rising/premature native pickup collision')
 local kind=r('PowerUpType',emu.getState()['cpu.x'])
 onReturn('native-block-contact',function()
  current.collided=updates
  if kind==2 then assert(r('StarInvincibleTimer')==35,'Actual native star timer');current.grants=current.grants+1
  elseif kind==3 then current.grants=current.grants+1 end
  event('actual-native-block-contact',{type=kind,state=state()});capture('contact')
 end)
end)
hook('RlInjury',function()
 if not entered or not current then return end
 local hp=r('RlHealth');local invul=r('RlInvul')
 onReturn('ordinary-real-injury',function()
  if current.contactPending and invul==0 and hp>4 then
   assert(r('RlHealth')==hp-4 and r('RlInvul')==64 and r('RlHurt')==16,'Real ordinary injury/protection')
   current.injuries=current.injuries+1;current.contactPending=nil;current.removeEnemy=true;event('actual-native-injury',state());capture('injury-'..current.injuries)
  end
 end)
end)
hook('RlWeapons',function()
 if not entered or not current then return end
 local energy=r('RlEnergy');local fired=r('RlChargeFired')
 onReturn('actual-weapon-dispatch',function()
  if r('RlChargeFired')~=fired then
   assert(r('RlChargeFired')==(fired+1)%256 and energy>=4 and r('RlEnergy')==energy-4,'Actual successful charge pays exactly4')
   current.charges=current.charges+1;event('actual-acquired-charge',{before=energy,after=r('RlEnergy'),charge_count=current.charges});capture('charge-'..current.charges)
  end
 end)
end)
hook('RlWeapons::Spawn',function()
 if not entered or not current then return end
 local kind=emu.getState()['cpu.a']
 onReturn('native-shot-spawn',function()
  local s=emu.getState();local flags=s['cpu.ps']or s['cpu.p'];if flags&1~=0 then
   if kind==1 then current.pellets=current.pellets+1 end
   event('actual-native-projectile-spawn',{kind=kind,slot=s['cpu.x'],energy=r('RlEnergy')})
  end
 end)
end)
hook('ShellOrBlockDefeat',function()
 if entered and current and emu.getState()['cpu.x']==0 then current.kills=current.kills+1;current.removeEnemy=true;current.targetActive=false;event('actual-native-defeat',{hp=r('MmEnemyHealthLo'),action=phase})end
end)
hook('RlDropDispatch',function()
 if not entered or not current then return end
 local before={};for i=0,3 do before[i]=r('InvDropKind',i)end
 local rng={r('PseudoRandomBitReg',1),r('PseudoRandomBitReg',2),r('PseudoRandomBitReg',3)}
 onReturn('actual-drop-source',function()
  for i=0,3 do if before[i]==0 and r('InvDropKind',i)~=0 then
   local kind=r('InvDropKind',i);local meter=r('AvDropItem',i)
   assert(rng[1]&3==0 and kind==(rng[2]<192 and 1 or 2)and meter==(rng[3]&1==0 and 0 or 128),'Actual unmodified source RNG drop policy')
   event('actual-native-drop-generated',{slot=i,kind=kind,meter=meter,rng=rng})
   if phase=='capsule'or phase=='expiry'or phase=='hold'then
    assert(current.dropSlot==nil,'One actual drop at a time');current.dropSlot=i;current.dropBorn=updates;current.desired=kind==current.q.kind and meter==current.q.meter
    if current.desired then capture('desired-drop')else current.unwanted=current.unwanted+1 end
   else event('incidental-source-drop',{slot=i,kind=kind,meter=meter})end
  end end
 end)
end)
hook('RlRefillDispatch',function()
 if not entered or not current then return end
 local slot=r('InvDropSlot');local raw=emu.getState()['cpu.a'];local meter=r('AvDropItem',slot);local before=state()
 assert(phase=='capsule'and current.desired or phase=='star','Only desired actual pickup or explicit incidental star drop')
 onReturn('actual-physical-capsule',function()
  local amount=raw//4
  assert(amount==2 or amount==10,'Native capsule amount')
  assert(r('RlHealth')==(meter>=128 and math.min(28,before.hp+amount)or before.hp)and r('RlEnergy')==(meter<128 and math.min(28,before.energy+amount)or before.energy),'Exact source capsule amount/cap/isolation')
  assert(r('Square2SoundQueue')==C.coin_sfx,'Actual capsule feedback')
  current.grants=current.grants+1;event('actual-physical-capsule',{before=before,after=state(),meter=meter,amount=amount});capture('capsule-granted')
 end)
end)
hook('RlDeathStart',function()
 if entered then assert(phase=='death'and r('RlHealth')==0,'Only earned lethal final contact');current.deadAt=updates;event('actual-native-death-start',state());capture('death-start')end
end)
hook('RlDrawRecord',function()
 if phase~='expiry'or not current.desired or current.dropSlot==nil then return end
 local slot=current.dropSlot;local life=r('InvDropAge',slot)+256*r('InvDropAgeHi',slot)
 if life<236 or life>247 then return end
 local pointer=r('R0')+256*r('R1')
 if r('RlSlot')~=slot or pointer~=C.expiry_art_pointer then return end
  local q={age=life,frame_counter=r('FrameCounter'),cursor_before=r('CurrentOAMOffset'),pointer=pointer,x=r('R4'),x_page=r('R5'),y=r('R6'),incoming_r7=r('R7')}
 onReturn('earned-capsule-real-draw-record',function()q.cursor_after=r('CurrentOAMOffset');event('earned-capsule-native-draw-record',q)end)
end)
hook('finish',function()
 if not entered or done then return end
 if phase=='settle'and age>=30 then
  assert(r('RlHealth')==28 and r('RlEnergy')==28 and r('RlFoodKind')==0,'Actual cold defaults');phase='setup';age=0
 elseif phase=='damage'then
  if current.injuries==current.q.contacts and r('RlInvul')==0 and r('RlHurt')==0 and r('InjuryTimer')==0 and r('Player_State')==0 then assert(r('RlHealth')==current.q.hp,'Earned HP, no resource write');complete()end
 elseif phase=='charge'then
  if current.charges==current.q.count and shots()==0 and r('RlAttack')==0 then assert(r('RlEnergy')==current.before.energy-4*current.q.count,'Actual energy depletion');complete()end
 elseif phase=='refuse'and age>=100 and shots()==0 and r('RlAttack')==0 then
  assert(current.pellets>0 and current.charges==0 and r('RlEnergy')==current.q.energy and r('RlCharge')==0,'Free ordinary fire, insufficient energy refusal');complete()
 elseif phase=='block'then
   if updates%4==0 then event('actual-block-navigation',{player_x=r('Player_X_Position')+256*r('Player_PageLoc'),player_y=r('Player_Y_Position'),player_state=r('Player_State'),vx={r('MmVX'),r('MmVX',1),r('MmVX',2)},item_x=r('Enemy_X_Position',5)+256*r('Enemy_PageLoc',5),item_y=r('Enemy_Y_Position',5),item_high=r('Enemy_Y_HighPos',5),item_state=r('Enemy_State',5),item_type=r('PowerUpType',5),buttons=r('SavedJoypadBits'),AB=r('A_B_Buttons')})end
  for i=0,3 do if r('Block_State',i)~=0 then current.headBlock=true end end
  if r('Enemy_Flag',5)~=0 and r('Enemy_ID',5)==46 then
   assert(current.headBlock and current.reveal,'Actual head/block activation before item')
   if r('Enemy_State',5)<128 then assert(current.grants==0 and r('RlHealth')==current.before.hp and r('RlEnergy')==current.before.energy,'No premature grant')
   elseif not current.mature then assert(r('Enemy_Y_Position',5)<current.revealY,'Native rise');current.mature=updates;capture('mature');event('native-full-rise',{})end
  end
  if current.mature and not current.collectPhase and r('Player_State')==0 then current.collectPhase='left' end
  if current.collectPhase=='left'and r('Player_X_Position')<=88 then current.collectPhase='jump';current.jumpAt=updates end
  if current.collided and r('Enemy_Flag',5)==0 then
   if current.q.type==3 then
    assert(r('RlHealth')==current.before.hp and r('RlEnergy')==current.before.energy and r('RlFoodKind')==current.before.food,'Actual 1up changes no resource or food state')
    if r('NumberofLives')==current.before.lives+1 then complete()end
   else assert(current.grants==1,'Exactly one physical block reward');complete()end
  end
 elseif phase=='capsule'or phase=='expiry'or phase=='hold'then
  if current.grants==1 then assert(drops()==0 and r('RlHealth')==current.q.hp and r('RlEnergy')==current.q.energy,'Desired real capsule consumed and expected resource values');complete()
  elseif current.desired and current.dropSlot then
   local slot=current.dropSlot;local life=r('InvDropAge',slot)+256*r('InvDropAgeHi',slot)
    if phase=='expiry'then
     local expected=updates-current.dropBorn
     if r('InvDropKind',slot)~=0 then assert(life==expected,'One global shared actor update per native GameLoop; newborn age0')
     else assert(expected==420 and life==420,'Actual420 single-update expiry, no early cleanup');current.expiryCleanupAt=updates end
     if life>=236 and life<=247 then current.fadeAges=current.fadeAges or{};current.fadeAges[life]=true;capture('expiry-age-'..life)end
    end
    if phase=='expiry'and life>=419 then current.expiryObserved=true;capture('expiry-boundary-'..life)end
   if phase=='hold'and shots()==0 and r('RlAttack')==0 and updates-current.dropBorn>=35 then heldDrop=slot;assert(r('InvDropKind',slot)~=0,'Earned actor stays uncollected');complete()end
  elseif phase=='expiry'and current.expiryObserved and drops()==0 then
   local count=0;for _ in pairs(current.fadeAges or{})do count=count+1 end
   assert(count==12 and current.expiryCleanupAt-current.dropBorn==420,'All12 source-age samples and exact native expiry chronology');complete()
  end
 elseif phase=='star'then
  if not current.contactPending and age==10 then writeBoundary=true;target(116);writeBoundary=false;current.contactPending=true end
  assert(r('RlHealth')==current.before.hp and r('RlEnergy')==current.before.energy,'Real star contact preserves resource meters')
  if current.kills>0 and r('StarInvincibleTimer')==0 and drops()==0 and shots()==0 then current.expired=updates;event('native-star-expiry',state());complete()end
 elseif phase=='death'then
  if current.deadAt and r('MmDeathFlag')==0 and r('GameEngineSubroutine')==8 and r('NumberofLives')==current.oldLives-1 then
   if not current.respawnAt then current.respawnAt=updates;current.respawnX=r('Player_X_Position');capture('respawn')end
   assert(r('RlHealth')==28 and r('RlEnergy')==28 and r('RlFoodKind')==0 and shots()==0 and drops()==0,'Real life-loss full resource and volatile cleanup')
   if updates-current.respawnAt>=25 and r('Player_X_Position')>=current.respawnX+8 then complete()end
  end
 elseif phase=='cooldown'and age>=60 and shots()==0 and r('RlAttack')==0 and r('RlInvul')==0 and r('RlHurt')==0 and r('InjuryTimer')==0 then
  assert(emu.read(0x2006,emu.memType.nesPpuDebug)==r('RlHealth')//10 and emu.read(0x2007,emu.memType.nesPpuDebug)==r('RlHealth')%10,'Committed HP HUD digits')
  assert(emu.read(0x200c,emu.memType.nesPpuDebug)==r('RlEnergy')//10 and emu.read(0x200d,emu.memType.nesPpuDebug)==r('RlEnergy')%10,'Committed EN HUD digits')
  hudChecks=hudChecks+1;event('committed-resource-hud',state());capture('committed-hud');phase='setup';age=0
 end
 if current then trace:write(table.concat({wall,updates,index,phase,age,r('RlHealth'),r('RlEnergy'),r('RlFoodKind'),r('RlCharge'),r('RlHurt'),r('RlInvul'),r('InjuryTimer'),r('StarInvincibleTimer'),r('NumberofLives'),r('Player_X_Position'),r('Player_Y_Position'),r('Player_State')},',')..'\n')end
 assert(age<((phase=='capsule'or phase=='expiry'or phase=='hold')and 150000 or 6000),'Bounded actual lifecycle step')
end)

-- Same committed-publication and exact MMC5 write-time latch guards as the
-- qualified physical progression fixture. No future RAM epoch is a DMA oracle.
local upper,physical,published,dma=0,{},nil,nil
local function bytes(at,kind)local t={};for i=0,255 do t[#t+1]=string.char(emu.read(at+i,kind))end;return table.concat(t)end
emu.addMemoryCallback(function(_,v)upper=v&3 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(a,v)physical[a-0x5120]=v+256*upper end,emu.callbackType.write,0x5120,0x512b)
hook('RosterOamReady',function()if entered and not done then published=bytes(L.Sprite_Data,emu.memType.nesDebug)end end)
emu.addMemoryCallback(function(_,v)dma=nil;if entered and not done and published then local q=bytes(v*256,emu.memType.nesDebug);if q==published then dma=q end end end,emu.callbackType.write,0x4014)
for _,pc in ipairs(C.irq_scroll_stores)do emu.addMemoryCallback(function()if entered and not done then assert(bank(pc)==C.hooks.IrqScrollSplit.physical_bank and emu.getState()['ppu.scanline']==31,'Actual line31 split owner');irqStores=irqStores+1 end end,emu.callbackType.exec,pc)end
local saved=nil
local function store(pc,target)return emu.read(pc,emu.memType.nesDebug)==0x8d and emu.read(pc+1,emu.memType.nesDebug)==target%256 and emu.read(pc+2,emu.memType.nesDebug)==target//256 end
local function window(pc,target,shadow)
 if store(pc,target)then return store(pc-3,shadow)or(emu.read(pc-2,emu.memType.nesDebug)==0xa9 and store(pc-5,shadow))end
 return emu.read(pc,emu.memType.nesDebug)==0xa9 and store(pc+2,target)and store(pc-3,shadow)
end
hook('NonMaskableInterrupt',function()
 if not entered or done then return end;local s=emu.getState();local sp=s['cpu.sp'];local pc=emu.read(256+(sp+2)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+3)%256,emu.memType.nesDebug)
 saved={a=bank(0xa000),c=bank(0xc000),sa=r('CurrentBank')&127,sc=r('CurrentBankC')&127,sp=sp,cpu_a=s['cpu.a'],fields={}}
 saved.wa=saved.a~=saved.sa and window(pc,0x5115,L.CurrentBank);saved.wc=saved.c~=saved.sc and window(pc,0x5116,L.CurrentBankC)
 for _,a in ipairs(C.smc_fields)do saved.fields[#saved.fields+1]=emu.read(a,emu.memType.nesDebug)end;nmis=nmis+1
end)
hook('NmiReturn',function()
 if not saved then return end
 assert(bank(0xa000)==(saved.wa and saved.sa or saved.a)and bank(0xc000)==(saved.wc and saved.sc or saved.c),'NMI actual foreground banks')
 assert(r('CurrentBank')&127==saved.sa and r('CurrentBankC')&127==saved.sc,'NMI shadow banks')
 assert(emu.getState()['cpu.sp']==saved.sp and emu.getState()['cpu.a']==saved.cpu_a,'NMI A/SP restore')
 for i,a in ipairs(C.smc_fields)do assert(emu.read(a,emu.memType.nesDebug)==saved.fields[i],'Five SMC operands restored')end;saved=nil
end)
emu.addMemoryCallback(function()if entered and not done then assert(emu.getState()['cpu.sp']>=128,'Native lower-stack guard')end end,emu.callbackType.write,0x17f)
emu.addMemoryCallback(function(a,v)if entered then local s=emu.getState();apuWrites=apuWrites+1;apu:write(table.concat({wall,updates,index,phase,a,v,s['cpu.pc'],bank(s['cpu.pc']),s['cpu.cycleCount']},',')..'\n')end end,emu.callbackType.write,0x4000,0x4017)
for _,n in ipairs({'RlHealth','RlEnergy','RlFoodKind','RlInvul','RlCharge','RlChargeFired','NumberofLives'})do
 emu.addMemoryCallback(function(a,v)if entered then event('actual-native-resource-write',{name=n,before=emu.read(a,emu.memType.nesDebug),value=v})end end,emu.callbackType.write,L[n])
end
emu.addEventCallback(function()
 local b={}
 if not entered then b=menu()
 elseif phase=='charge'then b.b=current.charges<current.q.count
 elseif phase=='refuse'then b.b=age<75
 elseif phase=='block'then
   local easyMoving=C.mode_value==0 and current.q.type~=1
   if not current.mature then
    b.a=age>=10 and age<35
    -- Classic inertia makes the old late left/jump chase lose a moving item
    -- beyond this fixed viewport. Walk ahead during its real rise instead.
    if easyMoving and current.reveal and age>=35 then b.right=r('Player_X_Position')<176 end
   elseif easyMoving then
    b.right=r('Player_X_Position')<176
    local itemX=r('Enemy_X_Position',5)+256*r('Enemy_PageLoc',5)
    local playerX=r('Player_X_Position')+256*r('Player_PageLoc')
    if current.q.type==2 and r('Player_State')==0 and math.abs(itemX-playerX)<28 and r('Enemy_Y_Position',5)<168 then b.a=true end
  elseif current.collectPhase=='left'then b.left=r('Player_X_Position')>88
  elseif current.collectPhase=='jump'then
   b.a=updates-current.jumpAt<30
   local itemX=r('Enemy_X_Position',5)+256*r('Enemy_PageLoc',5)
   local playerX=r('Player_X_Position')+256*r('Player_PageLoc')
   b.right=playerX<itemX+4;b.left=playerX>itemX+10
  end
 elseif phase=='capsule'or phase=='expiry'or phase=='hold'then
  if current.targetActive then b.b=(age-current.fireAge)%12<2 end
  if phase=='capsule'and current.desired and current.dropSlot and updates-current.dropBorn>=30 then b.right=true end
 elseif phase=='death'then
  b.b=age>=8 and age<12
  if current.respawnAt then b.right=true end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1
 if entered and not done then
  local s=emu.getState();for i=0,11 do assert(s['mapper.chrBanks'..i]==physical[i],'Actual write-time CHR model');chrChecks=chrChecks+1 end
  if dma then assert(bytes(0,emu.memType.nesSpriteRam)==dma,'Completed source OAM publication reaches actual hardware');dmaChecks=dmaChecks+1;dma=nil end
 end
 for _,q in ipairs(captures)do
  local f=assert(io.open(OUTPUT..q.name..'.argb','wb'));for _,v in ipairs(emu.getScreenBuffer())do f:write(string.pack('<I4',v))end;f:close();event('real-ppu-frame',q)
 end;captures={}
 if done then
  assert(#results==#C.plan and hudChecks==#C.plan,'Finite plan and all committed HUD checks complete')
  assert(r('RlHealth')==28 and r('RlEnergy')==28 and r('RlFoodKind')==0 and shots()==0 and drops()==0,'Native death/respawn final resource cleanup')
  local q={passed=true,goal_complete=false,ROM_sha256=C.ROM_sha256,mode=C.mode_value,hard=C.hard,actual_mode_readback=r('CrossoverBehaviorVersion'),steps=results,updates=updates,wall=wall,nmis=nmis,irq_scroll_stores=irqStores,hardware_chr_checks=chrChecks,complete_dma_checks=dmaChecks,committed_hud_checks=hudChecks,minSP=minSP,register_range_writes=apuWrites,scope='Actual cold menu; staged flat world/blocks/motion/default-health Goombas. Real head/reveal/full rise/controller contact; actual injury and charge depletion, source random defeats/drops, no RNG or resource writes. No actor clones or mature pickup placement. Original mobile executable unavailable; explicit production adaptation, not original timing/audio/campaign claim.'}
  local f=assert(io.open(OUTPUT..'native-result.json','w'));f:write(json(q));f:close();log:close();apu:close();trace:close();emu.stop(0)
 end
 assert(wall<1000000,'Bounded whole prepared Roll lifecycle')
end,emu.eventType.endFrame)
local inheritedAssert=assert
function assert(ok,message,...)
 if not ok then
  local s=emu.getState();local q={message=tostring(message),wall=wall,updates=updates,phase=phase,index=index,age=age,pc=s['cpu.pc'],bank=bank(s['cpu.pc']),sp=s['cpu.sp'],current=current,resources=entered and state()or{},body={}}
  if entered then
   for _,n in ipairs({'Player_X_Position','Player_Y_Position','Player_Y_HighPos','Player_State','Enemy_ID','Enemy_Flag','Enemy_X_Position','Enemy_Y_Position','Enemy_Y_HighPos','Enemy_State','Enemy_CollisionBits','InjuryTimer','RlInvul','RlHurt','RlAttack','StarInvincibleTimer','GameEngineSubroutine'})do q.body[n]=r(n)end
    q.body.powerup={};for _,n in ipairs({'Enemy_Flag','Enemy_ID','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_Y_HighPos','Enemy_State','Enemy_X_Speed','PowerUpType'})do q.body.powerup[n]=r(n,5)end
   q.body.projectiles={};for i=0,3 do q.body.projectiles[i+1]=r('MmBulletType',i)end
  end
  local f=io.open(OUTPUT..'first-failure.json','w');if f then f:write(json(q));f:close()end
  local f=io.open(OUTPUT..'first-failure.argb','wb');if f then for _,v in ipairs(emu.getScreenBuffer())do f:write(string.pack('<I4',v))end;f:close()end
 end
 return inheritedAssert(ok,message,...)
end
