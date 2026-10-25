-- SOURCE-ONLY PREPARATION. No result is a native pass until this completes.
-- Reuses physical block/rise/contact patterns and committed graphics/NMI guards.
local C=assert(FINAL_TMNT_ITEMS)
for n,a in pairs(C.ram)do L[n]=a end
local wall,updates,age,index=0,0,0,0
local entered,done,writeBoundary=false,false,false
assert(type(C.hard)=='boolean'and(C.mode_value==0 or C.mode_value==1)and C.hard==(C.mode_value==1),'Explicit Lua boolean and numeric mode configuration')
assert(C.plan[2].injure_after_rise==true and C.plan[36].hold==true,'Prepared boolean actions must be enabled')
local phase,menuPhase='menu',C.mode_value==1 and'focus'or'start'
local current,pendingDrop=nil,nil
local results,captures={},{}
local minSP,nmis,irqStores,chrChecks,dmaChecks,apuWrites=255,0,0,0,0,0
local eligibleDefeats,dropGenerations=0,0
local forbidden={TnHealth=true,TnFood=true,TnEquipment=true,TnAmmo=true,TnGearSelected=true,
 TnDropCounter=true,TnDropKind=true,TnDropReceipt=true,TnDropTimer=true,PseudoRandomBitReg=true,
 PlayerStatus=true,TnVariant=true,SelectedCharacter=true,PowerUpType=true,InvPickup=true,TnPickupStamp=true}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)assert(writeBoundary and not forbidden[n],'Only disclosed world/motion/target setup may be written: '..n);emu.write(assert(L[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
local function json(v)
 if type(v)=='table'then local t={};if #v>0 then for _,x in ipairs(v)do t[#t+1]=json(x)end;return'['..table.concat(t,',')..']'end
  for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..json(x)end;return'{'..table.concat(t,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local log=assert(io.open(OUTPUT..'events.jsonl','w'))
local trace=assert(io.open(OUTPUT..'updates.csv','w'));trace:write('wall,update,step,phase,age,hp,food,gear,ammo,selected,dropcounter,eligibledefeats,shot0,shot1,shot2,injury,hurt,x,y,state\n')
local apu=assert(io.open(OUTPUT..'apu.csv','w'));apu:write('wall,update,step,phase,register,value,pc,bank,cycle\n')
local function bank(pc)local p=emu.convertAddress(pc);return p and p.address//8192 or-1 end
local function event(kind,data)local s=emu.getState();log:write(json({kind=kind,data=data,wall=wall,update=updates,step=index,phase=phase,pc=s['cpu.pc'],bank=bank(s['cpu.pc']),sp=s['cpu.sp']})..'\n');log:flush()end
local function capture(name)captures[#captures+1]={name=string.format('%02d-',index)..name,wall=wall,update=updates}end
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
local function shots()local n=0;for i=0,2 do if r('TnShotKind',i)~=0 then n=n+1 end end;return n end
local function persistent()local q={};for i=0,3 do q[i+1]={hp=r('TnHealth',i),gear=r('TnEquipment',i),ammo=r('TnAmmo',i)}end;return q end
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
 local i=r('CrossoverMenuIndex');if(i<12 and i//6 or 2)~=2 then return{down=true}end
 if i~=18 then return{right=true}end
 if r('TnVariant')~=C.variant then return{select=true}end
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
local function arena(delivery)
 assert(r('TnAttack')==0 and r('TnThrow')==0 and shots()==0,'Prior native primary/secondary cleanup')
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do for col=0,15 do for row=11,12 do w('Block_Buffer_1',0x54,p*208+row*16+col)end end end
 for p=0,1 do for row=2,14 do for col=0,15 do tile(p,col,row,row>=13 and 0x54 or 0)end end end
 -- A turtle's native stand top is playerY-8. Put the block above that top,
 -- unlike the zero-head-offset progressive fixture's lower question block.
 if delivery then w('Block_Buffer_1',0xc1,112+7);tile(0,7,9,0xc1)end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_CollisionBits',0,i)end
 for i=0,3 do w('Block_State',0,i);w('BlockMetasprite',0,i)end
 for _,n in ipairs({'Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','ScrollThirtyTwo','AreaParserTaskNum','TnVXHi','TnVXLo','TnVYHi','TnVYLo','TnXFraction','TnYFraction'})do w(n,0)end
 w('ScrollLock',1);w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_X_Position',112);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1);w('TimerControl',0)
 -- Each step is a staged component, not a continuous campaign timer proof.
 for i,v in ipairs({3,9,9})do w('GameTimerDisplay',v,i-1)end
end
local function target(x)
 for _,v in ipairs({{'Enemy_Flag',1},{'Enemy_ID',6},{'Enemy_State',0},{'Enemy_X_Position',x},{'Enemy_PageLoc',0},{'Enemy_Y_Position',184},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_Y_MoveForce',0},{'Enemy_MovingDir',2},{'Enemy_BoundBoxCtrl',9},{'Enemy_CollisionBits',0}})do w(v[1],v[2],0)end
 event('explicit-native-standing-goomba',{x=x,y=184,hp='default source table; no health write'})
end
local function bodyState()
 local q={};for _,n in ipairs({'Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_Y_Position','Enemy_Y_HighPos','Enemy_CollisionBits','EnemyOffscrBitsMasked','Enemy_X_Speed','Enemy_Y_Speed','ObjectOffset','TnHealth','TnHurt','TnHurtMove','TnSeq','TnAttack','TnThrow','TnFood','InjuryTimer','StarInvincibleTimer','CheatInvincible','Player_X_Position','Player_Y_Position','Player_State','Player_Y_Speed','Player_CollisionBits','CrossoverBehaviorVersion','GuestBodyNoStomp'})do q[n]=r(n)end
 q.playerBox={};q.enemyBox={};for i=0,3 do q.playerBox[i+1]=r('BoundingBox_UL_XPos',i);q.enemyBox[i+1]=r('EnemyBoundingBoxCoord',i)end
 q.TnHealth=r('TnHealth',C.variant)
 return q
end
for _,n in ipairs({'PlayerEnemyCollision','EColl','HandlePECollisions','GuestBodyContactBridge','InjurePlayer','ForceInjury','TnInjuryStatus'})do
 hook(n,function()
  if phase=='damage'and current and current.injuries==1 and age>120 and r('ObjectOffset')==0 and age<400 then
   local s=emu.getState();local q=bodyState();q.hook=n;q.a=s['cpu.a'];q.x=s['cpu.x'];q.y=s['cpu.y'];q.p=s['cpu.ps']or s['cpu.p']
   event('repeated-contact-diagnostic',q)
  end
 end)
end
local function rollKind(b)if b&1~=0 then return 0 end;local q=(b>>1)&3;return q<2 and 1 or q end
local function complete()
 current.finished=updates;current.after=persistent();current.foodAfter=r('TnFood')
 event('step-completed',current);capture('complete');phase='cooldown';age=0
end
local function start()
 index=index+1;if index>#C.plan then done=true;phase='complete';return end
 local q=C.plan[index];current={q=q,started=updates,before=persistent(),foodBefore=r('TnFood'),grants=0,heals=0,injuries=0,throws=0,refunds={},kills=0,riseCalls=0}
 results[#results+1]=current
 if q.action~='boom_overcap'then writeBoundary=true;arena(q.action=='block');writeBoundary=false end
 phase=q.action;age=0;event('step-started',current);capture('start')
 if q.action=='block'then assert(r('TnFood')==q.type,'Actual source food parity selects the requested block reward')end
 if q.action=='damage'then assert(r('TnHurt')==0,'Previous actual protection expired')end
 if q.action=='use'then
  assert(r('TnEquipment',C.variant)==q.gear and r('TnAmmo',C.variant)>0,'Use only physically acquired gear')
  current.ammoBefore=r('TnAmmo',C.variant);writeBoundary=true;target(160);writeBoundary=false
 end
 if q.action=='boom_overcap'then
  assert(pendingDrop~=nil and r('TnDropKind',pendingDrop)==3,'Native earned refill actor remains alive')
  assert(r('TnEquipment',C.variant)==3 and r('TnAmmo',C.variant)==99,'Actual duplicate acquisitions reach99 before throwing')
 end
end
hook('GameLoop',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then
  if r('GameEngineSubroutine')~=8 then return end
  assert(r('SelectedCharacter')==19 and r('TnVariant')==C.variant and r('CrossoverBehaviorVersion')==C.mode_value,'Actual cold identity/numeric mode readback')
  event('actual-cold-selection',{character=r('SelectedCharacter'),variant=r('TnVariant'),mode=r('CrossoverBehaviorVersion'),requested_mode=C.mode_value})
  entered=true;phase='settle';age=0
 end
 updates=updates+1;age=age+1
 if current and current.removeEnemy then writeBoundary=true;w('Enemy_Flag',0,0);writeBoundary=false;current.removeEnemy=nil;current.emptySince=updates end
 if phase=='setup'then start()
 elseif phase=='damage'and r('TnHurt')==0 and r('InjuryTimer')==0 and r('Enemy_Flag')==0 and current.injuries<current.q.contacts then
  writeBoundary=true;arena(false);target(116);writeBoundary=false;current.contactPending=true
 elseif phase=='block'and current.mature then
  if current.q.injure_after_rise and current.injuries==0 and not current.contactPending and r('Player_State')==0 then
   writeBoundary=true;target(r('Player_X_Position')+4);writeBoundary=false;current.contactPending=true
  elseif(not current.q.injure_after_rise or current.injuries==1 and r('TnHurt')==0)and age>=150 and not current.contactPlaced then
   assert(r('Enemy_State',5)>=128,'Full actual emergence precedes contact placement')
   writeBoundary=true;w('Enemy_X_Position',r('Player_X_Position'),5);w('Enemy_PageLoc',r('Player_PageLoc'),5);w('Enemy_Y_Position',184,5);w('Enemy_X_Speed',0,5);w('Enemy_Y_Speed',0,5);writeBoundary=false
   current.contactPlaced=updates;event('explicit-post-rise-item-contact-placement',{});capture('contact-placement')
  end
 end
 if entered and not done then assert(r('MmDeathFlag')==0 and r('GameEngineSubroutine')==8,'Physical lifecycle remains playable')end
end)
hook('TnPreparePickupDispatch',function()
 if phase~='block'then return end
 onReturn('prepared',function()
  assert(emu.getState()['cpu.x']==5 and r('PowerUpType',5)==current.q.type,'Actual activated block owns source type')
  current.revealed=updates;current.revealY=r('Enemy_Y_Position',5);current.healthAtReveal=r('TnHealth',C.variant);current.stamp=r('TnPickupStamp',5)
  assert(current.stamp==(current.q.gear==4 and 4 or 0),'Full-health Kiai is frozen at actual reveal')
  event('native-reward-reveal',{hp=current.healthAtReveal,type=r('PowerUpType',5),stamp=current.stamp});capture('reveal')
 end)
end)
hook('TnRisePickupDispatch',function()
 if phase=='block'and current.stamp==4 and r('Enemy_State',5)<128 then current.riseCalls=current.riseCalls+1 end
end)
hook('TnCollectEquipment',function()
 if phase=='block'and current.stamp==4 then assert(r('Enemy_State',5)>=128 and current.contactPlaced,'Never grant a rising or unplaced Kiai')end
end)
hook('TnHeal',function()
 if phase~='block'then return end
 assert(current.q.gear==nil and current.mature and current.contactPlaced and r('Enemy_State',5)>=128,'Food grant follows real head/reveal/rise/contact')
 local before=r('TnHealth',C.variant);local food=r('TnFood');local kind=emu.getState()['cpu.a']
 current.heals=current.heals+1;event('actual-native-food-heal',{hp=before,food=food,type=kind})
 onReturn('actual-food-heal',function()
  assert(r('TnHealth',C.variant)==math.min(128,before+(kind==0 and 32 or 64))and r('TnFood')==food~1,'Actual source food amount, cap and parity')
  assert(r('Square2SoundQueue')&C.powerup_sfx~=0,'Actual physical food sound queued')
 end)
end)
hook('TnGiveEquipment',function()
 if not entered or not current then return end
 local gear=emu.getState()['cpu.a'];local old=r('TnEquipment',C.variant);local ammo=r('TnAmmo',C.variant);local selected=r('TnGearSelected')
 assert(phase=='block'or phase=='drop'or phase=='boom_overcap','Only actual physical actor owners may grant gear')
 if phase=='boom_overcap'then assert(current.throws==3 and shots()==3 and ammo==96,'Three real throws precede duplicate refill')end
 onReturn('gear-grant',function()
  assert(r('TnEquipment',C.variant)==gear and r('TnAmmo',C.variant)==(gear==old and math.min(99,ammo+20)or 20),'Exact native replacement/refill cap')
  assert(r('TnGearSelected')==(gear==old and selected or 1),'Native same-kind selection retention/replacement auto-select')
  assert(r('Square2SoundQueue')&C.powerup_sfx~=0,'Actual physical equipment sound queued')
  current.grants=current.grants+1;current.collected=updates;event('actual-native-equipment-grant',{gear=gear,beforeAmmo=ammo,afterAmmo=r('TnAmmo',C.variant)});capture('equipment-granted')
  if phase=='boom_overcap'then current.refillAt=updates end
 end)
end)
hook('TnInjuryStart',function()
 if not current or not current.contactPending or r('TnHurt')~=0 then return end
 local before=r('TnHealth',C.variant)
 onReturn('real-injury',function()
  assert(r('TnHealth',C.variant)==before-16 and r('TnHurt')==120,'Actual native contact establishes health; no health write')
  current.injuries=current.injuries+1;current.contactPending=nil;current.removeEnemy=true;event('actual-native-injury',{before=before,after=r('TnHealth',C.variant)});capture('injury-'..current.injuries)
 end)
end)
hook('TnWeaponPosition',function()
 if phase~='drop'or r('TnAttack')==0 then return end
 onReturn('native-primary-position',function()
  if phase~='drop'or current.targetForAttack or r('Enemy_Flag')~=0 or r('TnDropReceipt')~=0 or r('TnPose',1)==0 or r('TnGearSelected')~=0 then return end
  if current.emptySince and updates-current.emptySince<4 then return end
  local kind=rollKind(r('PseudoRandomBitReg',1))
  if r('TnDropCounter')==24 and kind~=current.q.gear then return end
  local x=144;local wx=r('TnWeaponX')+256*r('TnWeaponPage');local wy=r('TnWeaponY')
  if math.abs(x+8-wx)>r('TnRadiusX')+8 or math.abs(192-wy)>r('TnRadiusY')+8 then return end
  writeBoundary=true;target(x);writeBoundary=false;current.targetForAttack=true
  event('native-prng-timed-eligible-target',{counter=r('TnDropCounter'),roll=r('PseudoRandomBitReg',1),kind=kind,weaponX=wx,weaponY=wy})
 end)
end)
hook('TnEnemyDropDispatch',function()
 if not entered or not current or emu.getState()['cpu.x']~=0 or r('Enemy_Flag')~=1 or r('Enemy_ID')~=6 or r('Enemy_State')&32~=0 or r('TnDropReceipt')~=0 then return end
 local before=r('TnDropCounter');local actualRoll=r('PseudoRandomBitReg',1)
 onReturn('native-drop-owner',function()
  eligibleDefeats=eligibleDefeats+1
  assert(r('TnDropCounter')==(before+1)%25,'Actual eligible defeat count, with no counter write')
  if before==24 then
   assert(eligibleDefeats%25==0 and phase=='drop'and rollKind(actualRoll)==current.q.gear,'Native25th defeat uses actual unmodified PRNG roll')
   local slot=nil;for i=0,3 do if r('TnDropKind',i)~=0 then assert(slot==nil,'One newly earned native drop');slot=i end end
   assert(slot~=nil and r('TnDropKind',slot)==current.q.gear and r('TnDropTimer',slot)==128,'Actual source drop creates requested physical kind')
   current.dropSlot=slot;current.dropBorn=updates;dropGenerations=dropGenerations+1;event('native-drop-generated',{slot=slot,kind=current.q.gear,roll=actualRoll,eligibleDefeats=eligibleDefeats});capture('drop-generated')
  end
 end)
end)
hook('ShellOrBlockDefeat',function()
 if not current or emu.getState()['cpu.x']~=0 then return end
 if phase=='drop'or phase=='use'then current.kills=current.kills+1;current.removeEnemy=true;event('actual-native-defeat',{action=phase,damage=r('TnDamageNow')})end
end)
hook('TnTrySecondary',function()
 if phase~='use'and phase~='boom_overcap'then return end
 local before=r('TnAmmo',C.variant)
 onReturn('native-secondary',function()
  assert(r('TnSpawned')==current.q.projectiles or phase=='boom_overcap'and r('TnSpawned')==1,'Actual native projectile allocation')
  assert(r('TnAmmo',C.variant)==before-1,'One ammo per real volley')
  current.throws=current.throws+1;event('actual-native-volley',{spawned=r('TnSpawned'),beforeAmmo=before,afterAmmo=r('TnAmmo',C.variant)});capture('throw-'..current.throws)
 end)
end)
hook('TnRestoreBoomerang',function()
 if phase~='use'and phase~='boom_overcap'then return end
 local before=r('TnAmmo',C.variant)
 onReturn('native-return',function()
  assert(r('TnAmmo',C.variant)==before+1,'Uncapped original refund, not a newly invented99 return cap')
  current.refunds[#current.refunds+1]=r('TnAmmo',C.variant);event('actual-native-boomerang-return',{beforeAmmo=before,afterAmmo=r('TnAmmo',C.variant)});capture('catch-'..#current.refunds)
 end)
end)
hook('finish',function()
 if not entered or done then return end
 if phase=='settle'and age>=30 then
  for i=0,3 do assert(r('TnHealth',i)==128 and r('TnEquipment',i)==0 and r('TnAmmo',i)==0,'Cold native initialization, all four records')end
  assert(r('TnFood')==0 and r('TnDropCounter')==0,'Cold source food/counter defaults');phase='setup';age=0
 elseif phase=='block'then
  for i=0,3 do if r('Block_State',i)~=0 then current.headBlock=true end end
  if r('Enemy_Flag',5)~=0 and r('Enemy_ID',5)==0x2e then
   assert(current.headBlock and current.revealed,'Real head/block reveal precedes actor observation')
   if r('Enemy_State',5)<128 then
    assert(current.grants==0 and current.heals==0,'No premature rising grant')
    assert(r('TnEquipment',C.variant)==current.before[C.variant+1].gear and r('TnAmmo',C.variant)==current.before[C.variant+1].ammo,'No gear effect while native item rises')
   elseif not current.mature then
    assert(r('Enemy_Y_Position',5)<current.revealY,'Native visible vertical rise');current.mature=updates;event('native-full-rise',{});capture('mature')
    if current.stamp==4 then assert(current.riseCalls==48,'Actual Kiai48-handler-call emergence')end
   end
  end
  if current.mature and current.contactPlaced and r('Enemy_Flag',5)==0 then
   assert(current.q.gear and current.grants==1 and current.heals==0 or not current.q.gear and current.heals==1 and current.grants==0,'Exactly one real physical owner')
   assert(r('TnHealth',C.variant)==current.q.hp and r('TnFood')==current.q.food,'Source food restoration/cap/parity and frozen Kiai outcome')
   complete()
  end
 elseif phase=='damage'then
  if current.injuries==current.q.contacts and r('TnHurt')==0 and r('InjuryTimer')==0 and r('Player_State')==0 then assert(r('TnHealth',C.variant)==current.q.hp,'Real repeated contacts establish desired hurt state');complete()end
 elseif phase=='drop'then
  if r('TnAttack')==0 then current.targetForAttack=nil end
  if current.dropSlot then
   if current.q.hold then
    if r('TnAttack')==0 and r('TnThrow')==0 then pendingDrop=current.dropSlot;assert(current.grants==0,'Native earned actor remains uncollected');complete()end
   elseif current.grants==1 then assert(r('TnDropKind',current.dropSlot)==0,'Physical contact consumes native drop');complete()end
  end
 elseif phase=='use'and age>=300 then
  assert(current.throws==1 and current.kills==1 and shots()==0 and r('TnThrow')==0,'Real acquired gear hit/native cleanup')
  assert(r('TnAmmo',C.variant)==current.ammoBefore-(current.q.gear==3 and 0 or 1),'Original volley cost and boomerang refund')
  assert(#current.refunds==(current.q.gear==3 and 1 or 0),'Only actual returning boomerang refunds');complete()
 elseif phase=='boom_overcap'then
  if current.refillAt and r('Player_X_Position')<=112 and shots()==0 and r('TnThrow')==0 and age>=300 then
   assert(current.grants==1 and current.throws==3 and #current.refunds==3,'Three actual acquired throws, one real physical refill, three real catches')
   assert(current.refunds[1]==100 and current.refunds[2]==101 and current.refunds[3]==102 and r('TnAmmo',C.variant)==102,'Original99-refill then100..102 source returns')
   assert(emu.read(0x2031,emu.memType.nesPpuDebug)==1 and emu.read(0x2032,emu.memType.nesPpuDebug)==0 and emu.read(0x2033,emu.memType.nesPpuDebug)==2,'Committed actual102 HUD digits');complete()
  end
 elseif phase=='cooldown'then
  if current.q.hold then phase='setup';age=0
  elseif age>=60 and r('TnAttack')==0 and r('TnThrow')==0 and shots()==0 and r('TnHurt')==0 then
   for i=0,3 do if i~=C.variant then local q=current.before[i+1];assert(r('TnHealth',i)==q.hp and r('TnEquipment',i)==q.gear and r('TnAmmo',i)==q.ammo,'Only cold-selected turtle record changes')end end
   phase='setup';age=0
  end
 end
 if current then trace:write(table.concat({wall,updates,index,phase,age,r('TnHealth',C.variant),r('TnFood'),r('TnEquipment',C.variant),r('TnAmmo',C.variant),r('TnGearSelected'),r('TnDropCounter'),eligibleDefeats,r('TnShotKind'),r('TnShotKind',1),r('TnShotKind',2),r('InjuryTimer'),r('TnHurt'),r('Player_X_Position'),r('Player_Y_Position'),r('Player_State')},',')..'\n')end
 local limit=phase=='drop'and 4000 or phase=='damage'and 1500 or phase=='block'and 800 or 650
 assert(age<limit,'Bounded source-only staged step '..phase)
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
for _,n in ipairs({'TnHealth','TnFood','TnEquipment','TnAmmo','TnDropCounter'})do local size=(n=='TnHealth'or n=='TnEquipment'or n=='TnAmmo')and 4 or 1;emu.addMemoryCallback(function(a,v)if entered then event('actual-native-persistent-write',{name=n,index=a-L[n],before=emu.read(a,emu.memType.nesDebug),value=v})end end,emu.callbackType.write,L[n],L[n]+size-1)end
emu.addMemoryCallback(function(_,v)
 if phase=='block'and age<20 and not writeBoundary and r('Player_X_Position')~=v then event('native-player-X-write',{before=r('Player_X_Position'),value=v})end
end,emu.callbackType.write,L.Player_X_Position)
emu.addEventCallback(function()
 local b={};if not entered then b=menu()
 elseif phase=='block'then b.a=age>=10 and age<35;b.right=current.contactPlaced~=nil
 elseif phase=='drop'then
  if r('TnGearSelected')~=0 then b.select=age%20<4
  elseif current.dropSlot and not current.q.hold then b.right=true
  elseif not current.dropSlot then b.b=age%40>=5 and age%40<9 end
 elseif phase=='use'then
  if r('TnGearSelected')==0 then b.select=age<4 else b.b=age>=12 and age<16 end
 elseif phase=='boom_overcap'then
  if current.throws==0 and r('TnGearSelected')==0 then b.select=age<6 end
  b.b=(age>=12 and age<16)or(age>=44 and age<48)or(age>=76 and age<80)
  if current.throws==3 and not current.refillAt then b.right=true
  elseif current.refillAt and r('Player_X_Position')>112 then b.left=true end
 end;emu.setInput(b,0)
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
  assert(#results==37 and eligibleDefeats==475 and dropGenerations==19,'Finite real defeat/drop plan completes')
  local q={passed=true,goal_complete=false,ROM_sha256=C.ROM_sha256,name=C.name,variant=C.variant,hard=C.hard,actual_mode_readback=r('CrossoverBehaviorVersion'),steps=results,eligible_defeats=eligibleDefeats,drop_generations=dropGenerations,updates=updates,wall=wall,nmis=nmis,irq_scroll_stores=irqStores,hardware_chr_checks=chrChecks,complete_dma_checks=dmaChecks,minSP=minSP,apuWrites=apuWrites,scope='Actual cold menu; explicit legal dry world/motion/Goomba setup; no health/food/inventory/ammo/counter/RNG/result writes. Native25-defeat drops, actual head/block/rise, disclosed post-rise item contact placement. No campaign/full-goal claim.'}
  local f=assert(io.open(OUTPUT..'native-result.json','w'));f:write(json(q));f:close();log:close();apu:close();trace:close();emu.stop(0)
 end
 assert(wall<200000,'Bounded whole turtle physical lifecycle')
end,emu.eventType.endFrame)
local inheritedAssert=assert
function assert(ok,message,...)
 if not ok then
  local s=emu.getState();local q={message=tostring(message),wall=wall,updates=updates,phase=phase,index=index,age=age,pc=s['cpu.pc'],bank=bank(s['cpu.pc']),sp=s['cpu.sp'],current=current,body=entered and bodyState()or{}}
  local f=io.open(OUTPUT..'first-failure.json','w');if f then f:write(json(q));f:close()end
  local f=io.open(OUTPUT..'first-failure.argb','wb');if f then for _,v in ipairs(emu.getScreenBuffer())do f:write(string.pack('<I4',v))end;f:close()end
 end;return inheritedAssert(ok,message,...)
end
