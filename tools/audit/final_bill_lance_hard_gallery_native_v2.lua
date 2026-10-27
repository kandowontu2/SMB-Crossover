-- Seven legal controlled-use cases. Only complete boundary setup is written;
-- native physical collision/grants, input/emission/contact/expiry own results.
local current=nil
local taskIndex,grantIndex=1,1
local drawScope=nil
local cadence=assert(io.open(OUTPUT..'bill-cadence.csv','w'))
cadence:write('kind,wall,update,case,task,phase,cycle,ppu,scanline,dot,skip,disable\n')
local function timing(kind)
 local s=emu.getState();cadence:write(table.concat({kind,wall,updates,index,taskIndex,phase,s['cpu.cycleCount'],s['ppu.frameCount'],s['ppu.scanline'],s['ppu.cycle'],r('NmiSkipped'),r('NmiDisable')},',')..'\n')
end
local function pool()local n=0;for i=0,9 do if r('RgShotType',i)~=0 then n=n+1 end end;return n end
local function shotRows()
 local z={};for i=0,9 do if r('RgShotType',i)~=0 then z[#z+1]={slot=i,type=r('RgShotType',i),x=r('RgShotX',i),page=r('RgShotPage',i),y=r('RgShotY',i),high=r('RgShotYHigh',i),age=r('RgShotAge',i),hidden=r('SsHidden',i),impact=r('RgShotImpact',i),dir=r('RgShotDir',i),vx=r('RgShotVXLo',i)+256*r('RgShotVXHi',i)}end end;return z
end
local function stateRow()return{variant=r('BillVariant'),mode=r('CrossoverBehaviorVersion'),owned=r('InvOwnedLo',3),selected=r('InvSelected',3),status=r('PlayerStatus'),x=r('Player_X_Position'),y=r('Player_Y_Position'),shots=shotRows()}end
local function change(p)phase=p;age=0;event('bill-gallery-phase',stateRow());FINAL_ABILITY_PHASE={name=current and current.q.name,phase=p}end
local function clearReady()
 if r('VRAM_Buffer1_Offset')~=0 or r('VRAM_Buffer_AddrCtrl')~=0 then return false end
 for i=0,5 do if r('FloateyNum_Control',i)~=0 then return false end end
 return true
end
local function clearArena(face)
 arena(false)
 for _,q in ipairs(C.clear_ranges)do for i=0,q.bytes-1 do w(q.name,0,i)end end
 for _,n in ipairs(C.clear_scalars)do w(n,0)end
 for i=0,9 do for _,n in ipairs(C.shot_arrays)do w(n,0,i)end end
 for i=0,5 do
  w('InvPickup',252,i);w('InvPickupOwner',255,i);w('EnemyMetasprite',0,i)
  w('MmEnemyHealthLo',0,i);w('MmEnemyHealthHi',0,i);w('MmEnemyFlash',0,i);w('RgEnemyStun',0,i)
 end
 for _,n in ipairs(C.drop_arrays)do for i=0,3 do w(n,0,i)end end
 w('PlayerFacingDir',face);w('Player_MovingDir',face);w('Player_CollisionBits',255)
 w('InvDirty',1)
end
local function entity(slot,id,x,y)
 for _,q in ipairs({{'Enemy_Flag',1},{'Enemy_ID',id},{'Enemy_State',0},{'Enemy_X_Position',x%256},{'Enemy_PageLoc',x//256},{'Enemy_Y_Position',y},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_X_MoveForce',0},{'Enemy_Y_MoveForce',0},{'Enemy_MovingDir',1},{'Enemy_BoundBoxCtrl',9},{'EnemyOffscrBitsMasked',0},{'Enemy_CollisionBits',0},{'Enemy_SprAttrib',0},{'MmEnemyHealthLo',0},{'MmEnemyHealthHi',0},{'MmEnemyFlash',0},{'RgEnemyStun',0}})do w(q[1],q[2],slot)end
end
local function stagePickup()
 if not clearReady()then return false end
 local item=current.q.incremental_grants[grantIndex]
 if not item then change('hud');return true end
 writeBoundary=true;clearArena(1)
 entity(5,0x2e,156,176)
 w('Enemy_State',128,5);w('Enemy_BoundBoxCtrl',3,5);w('PowerUpType',1,5)
 w('InvPickup',item,5);w('InvPickupOwner',3,5);w('InvRisePhase',0,5)
 writeBoundary=false
 current.pendingItem=item;current.beforeGrant={owned=r('InvOwnedLo',3),selected=r('InvSelected',3)}
 current.grantAt=nil;current.pickupCue=false;change('pickup');capture(current.q.name..'-controlled-pickup-'..item)
 event('B-mature-physical-item-staged',{item=item,x=156,y=176,state=128,owner=3,disclosure='A complete already-mature native pickup, not a block reveal/rise/random-drop acquisition. Actual Right input, physical collision and InventoryCollect/Grant must grant it.'})
 return true
end
local function setupTask()
 if not clearReady()then return false end
 local t=current.t
 assert(r('InvOwnedLo',3)==current.q.expected_owned and r('InvSelected',3)==current.q.expected_selected,'Actual preceding grants own this case')
 assert((r('InvOwnedLo',3)&60)==0 or ((r('InvOwnedLo',3)&60)&((r('InvOwnedLo',3)&60)-1))==0,'Only one exclusive gun owned')
 writeBoundary=true;clearArena(t.face)
 if t.kind=='terrain'then
  local col=t.face==1 and 10 or 4
  w('Block_Buffer_1',0x54,9*16+col);w('MmSolidTerrain',1,9*16+col);tile(0,col,11,0x54)
 end
 writeBoundary=false
 current.stage={kind=t.kind,face=t.face,started=wall,updateStart=updates,spawns={},draws=0,sourceSfx={},hits=0,damageCalls=0,blockCalls=0,impacts=0}
 current.stages[#current.stages+1]=current.stage
 change('run');capture(current.q.name..'-'..taskIndex..'-setup')
 event('B-complete-native-boundary-setup',{task=t,state=stateRow(),disclosure='Logical/visible arena, motion/input history/pools/drops/actor reset only. Carried inventory/selection is never reset between cases; no outcome, RNG, HP decrement or mode writes.'})
 return true
end
local function target()
 local s=current.stage
 if current.t.kind~='contact' or s.target then return end
 for i=0,9 do
  if r('RgShotType',i)==current.q.shot_type and r('RgShotImpact',i)==0 and (current.q.shot_type~=42 or r('SsHidden',i)==0)then
   local world=r('RgShotX',i)+256*r('RgShotPage',i)
   local dx=math.abs(world-r('Player_X_Position')-256*r('Player_PageLoc'))
   local y=r('RgShotY',i)-8
   if dx>=30 and world>=16 and world<232 and r('RgShotYHigh',i)==1 and y>=48 and y<192 then
    writeBoundary=true;entity(0,6,world-6,y);writeBoundary=false;s.target=wall
    event('B-source-aligned-live-Goomba',{slot=0,shotSlot=i,world=world-6,y=y,disclosure='Complete falling actor aligned at a native boundary; real projectile collision/damage/defeat remain untouched.'});return
   end
  end
 end
end
local function markSpawn(typ,slot)
 local s=current.stage
 assert(typ==current.q.shot_type and r('RgShotDir',slot)==current.t.face,'Real source emission type/facing')
 local row={type=typ,slot=slot,wall=wall,update=updates,phaseAge=age,dir=r('RgShotDir',slot),vx=r('RgShotVXLo',slot)+256*r('RgShotVXHi',slot)}
 s.spawns[#s.spawns+1]=row;event('actual-Bill-emission',row)
 if #s.spawns==1 then capture(current.q.name..'-'..taskIndex..'-first-shot')end
end
for _,name in ipairs({'RosterWeapons::SpawnBill','RemainingWeapons::Spawn'})do
 hook(name,function()
  if not entered or not current or phase~='run'then return end
  local before={};for i=0,9 do before[i]=r('RgShotType',i)end
  onReturn('bill-spawn-'..name,function()
   for i=0,9 do if before[i]==0 and r('RgShotType',i)~=0 then markSpawn(r('RgShotType',i),i)end end
  end)
 end)
end
hook('InventoryCollect',function()
 if not entered or not current or phase~='pickup'then return end
 assert(emu.getState()['cpu.x']==5 and r('InvPickupOwner',5)==3 and r('InvPickup',5)==current.pendingItem,'Actual controlled physical inventory owner')
 current.collectCalls=current.collectCalls+1
end)
hook('InventoryGrant',function()
 if not entered or not current or phase~='pickup'then return end
 local item=emu.getState()['cpu.a'];assert(item==current.pendingItem,'Actual physical requested upgrade')
 local old=r('InvOwnedLo',3);local selected=r('InvSelected',3)
 onReturn('bill-physical-grant',function()
  local expected=(old&(~C.single_masks[item+1]))|(1<<item)
  assert(r('InvOwnedLo',3)==expected,'Actual mutually-exclusive source ownership')
  assert(r('InvSelected',3)==(C.auto_equip[item+1]~=0 and item or selected),'Actual auto-equip versus passive upgrade')
  current.grants[#current.grants+1]={item=item,before=old,after=expected,selected=r('InvSelected',3),wall=wall,update=updates}
  current.grantAt=wall;event('actual-physical-upgrade-grant',current.grants[#current.grants]);capture(current.q.name..'-grant-'..item)
 end)
end)
hook('MegaManWeapons::Blocks',function()if entered and current and phase=='run'then current.stage.blockCalls=current.stage.blockCalls+1 end end)
hook('MegaManWeapons::DamageEnemy',function()
 if not entered or not current or phase~='run' or current.t.kind~='contact' or emu.getState()['cpu.x']~=0 then return end
 assert(r('MmBulletType')==current.q.damage_type,'Source-specific real weapon damage consumer')
 local old=r('Enemy_State');local hp=r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')
 current.stage.damageCalls=current.stage.damageCalls+1
 onReturn('bill-real-contact',function()
  if old~=r('Enemy_State')or hp~=r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')then
   current.stage.hits=current.stage.hits+1;event('actual-Bill-contact',stateRow());capture(current.q.name..'-real-contact')
  end
 end)
end)
hook('RosterDrawShots',function()
 if not entered or not current or phase~='run'then return end
 drawScope={kind='legacy'};onReturn('bill-legacy-draw-scope',function()drawScope=nil end)
end)
hook('RemainingDraw::ArtPointer',function()
 if not entered or not current or phase~='run'then return end
 -- Every source consumer shares Draw, but only AvDrawIndex0..9 is a shot.
 -- World/Drop/HUD reuse AvSlot and must never inherit projectile ownership.
 local owner=nil;drawScope=nil
 local i=r('AvSlot');local index=r('AvDrawIndex')
 if index<10 and i==index and r('RgShotType',i)==current.q.shot_type and current.q.shot_type>=42 then
  assert(current.q.shot_type~=42 or r('SsHidden',i)==0,'Actual visible advanced shot admission')
  local angle=r('SsArt',i);local artIndex
  if r('RgShotImpact',i)~=0 then artIndex=5+(current.q.shot_type==42 and angle or 0)
  else artIndex=current.q.shot_type==42 and 1+angle or 0 end
  local expected=C.advanced_art_indices[artIndex+1]
  assert(expected and r('AvDrawArt')==expected and emu.getState()['cpu.a']==expected,'Actual compiled BillAdvancedDrawArt consumer')
  local sp=emu.getState()['cpu.sp'];local ret=(emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug)+1)%65536
  assert(ret==C.advanced_after_pointer.pc and bank(ret)==C.advanced_after_pointer.bank,'Genuine immediate RemainingDraw ArtPointer return')
  owner={kind='advanced',slot=i,index=index,type=current.q.shot_type,art=expected,expected=C.advanced_records[tostring(expected)]}
 end
 onReturn('bill-advanced-pointer',function()
  local s=emu.getState();local p=s['cpu.ps']or s['cpu.p']
  if owner and p and p&1~=0 then
   assert(r('AvSlot')==owner.slot and r('AvDrawIndex')==owner.index,'Actual successful pointer retains shot owner')
   assert(owner.expected and r('R0')+256*r('R1')==owner.expected.address and bank(0xc000)==owner.expected.bank,'Source-selected advanced weapon pointer/bank')
   drawScope=owner
  end
 end)
end)
hook('MetaspriteRenderLoop',function()
 if not entered or not current or phase~='run' or not drawScope then return end
 local scope=drawScope
 if scope.kind=='advanced'then
  -- Install genuine-return cleanup BEFORE any type/slot rejection. A stale
  -- or rejected observation can never leak admission into the next draw.
  onReturn('bill-advanced-draw-end',function()if drawScope==scope then drawScope=nil end end)
 end
 local i=scope.kind=='advanced'and r('AvSlot')or r('RgSlot')
 if scope.kind=='advanced'and(i~=scope.slot or r('AvDrawIndex')~=scope.index)then return end
 if r('RgShotType',i)~=current.q.shot_type then return end
 local ptr=r('R0')+256*r('R1');local actual=bank(0xc000);local q=C.effect_records[tostring(actual)..':'..tostring(ptr)]
 assert(q,'Real effect pointer belongs to a complete compiled Bill weapon record')
 if scope.kind=='advanced'then assert(ptr==scope.expected.address and actual==scope.expected.bank,'Only the immediate qualified advanced draw consumes its pointer')end
 for j,v in ipairs(q.bytes)do assert(emu.read(actual*8192+ptr%8192+j-1,emu.memType.nesPrgRom)==v,'Exact complete compiled Bill effect art')end
 current.stage.draws=current.stage.draws+1
 if current.stage.draws==1 then event('actual-Bill-effect-art',{ptr=ptr,bank=actual,kind=scope.kind,slot=i,type=r('RgShotType',i)});capture(current.q.name..'-'..taskIndex..'-source-art')end
end)
for _,kind in ipairs({'RgSfx','Square1SoundQueue','Square2SoundQueue','AvAudioRequest'})do
 emu.addMemoryCallback(function(_,v)
  if entered and current then
   local row={kind=kind,value=v,wall=wall,update=updates,pc=emu.getState()['cpu.pc'],bank=bank(emu.getState()['cpu.pc'])}
   if phase=='run'then current.stage.sourceSfx[#current.stage.sourceSfx+1]=row end
   if phase=='pickup'and kind=='Square2SoundQueue'and v&C.powerup_sfx~=0 then current.pickupCue=true end
  end
 end,emu.callbackType.write,assert(L[kind]))
end
hook('GameLoop',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 or r('GameEngineSubroutine')~=8 then return end
 if not entered then
  assert(r('SelectedCharacter')==3 and r('BillVariant')==C.variant and r('CrossoverBehaviorVersion')==1,'Actual cold Bill/Lance Hard numeric1')
  assert(r('PlayerStatus')==0 and r('InvSelected',3)==0,'Cold actual default, before explicit B mushroom state')
  entered=true;phase='settle';age=0
 end
 updates=updates+1;age=age+1;timing('entry')
 assert(r('SelectedCharacter')==3 and r('BillVariant')==C.variant and r('CrossoverBehaviorVersion')==1,'Actual identity/mode remains')
 if phase=='settle'and age>=30 then
  assert(clearReady(),'Initial scene queue clears')
  writeBoundary=true;w('PlayerStatus',1);w('InvOwnedLo',1,3);w('InvOwnedHi',0,3);w('InvDirty',1);writeBoundary=false;change('next')
 elseif phase=='next'then
  if index>#C.cases then done=true;return end
  current={q=C.cases[index],started=wall,stages={},grants={},collectCalls=0};records[#records+1]=current
  grantIndex=1;taskIndex=1;current.t=current.q.tasks[taskIndex];change('grant-setup')
 elseif phase=='grant-setup'then assert(age<180,'Prior real score/VRAM drains');stagePickup()
 elseif phase=='pickup'then assert(age<200,'Real Right input reaches staged physical upgrade')
 elseif phase=='grant-drain'then if age>=50 and clearReady()then grantIndex=grantIndex+1;change('grant-setup')end
 elseif phase=='setup'then assert(age<180,'Prior real score/VRAM drains');setupTask()
 elseif phase=='run'then target()end
end)
local function billInput()
 if phase=='pickup'and current and not current.grantAt then return{right=true}end
 if phase~='run'or not current then return{}end
 local kind=current.t.kind;local b={}
 if kind=='auto-cadence'then b.b=age>=5 and age<50
 else b.b=age>=5 and age<8;if kind=='second-edge'then b.b=b.b or age>=35 and age<38 end end
 return b
end
hook('finish',function()
 if not entered or done then return end
 timing('finish')
 assert(r('MmDeathFlag')==0 and r('InjuryTimer')==0 and r('GuestHurtTicks')==0,'Controlled gallery survives without unrelated injury')
 assert(r('PlayerStatus')==1 and r('GuestPowerupActive')==0,'Weapon upgrade remains the seeded mushroom form; no invented tier transform')
 if not current then return end
 if phase=='pickup'and current.grantAt then
  assert(r('Enemy_Flag',5)==0 and current.collectCalls==#current.grants and current.pickupCue,'Real physical collision removes actor and queues pickup SFX')
  change('grant-drain')
 elseif phase=='hud'and age>=24 then
  assert(r('InvOwnedLo',3)==current.q.expected_owned and r('InvSelected',3)==current.q.expected_selected,'Final legal carried weapon state')
  for i,v in ipairs(current.q.hud_name)do assert(emu.read(0x2023+i-1,emu.memType.nesPpuDebug)==v,'Actual committed selected gun HUD')end
  -- Bill has no weapon ammo/icon bar. The robot-only cells must remain blank.
  for _,at in ipairs({0x2037,0x2038,0x2057,0x2058,0x202b,0x202c,0x202d,0x204a,0x204b,0x204c,0x204d,0x204e,0x204f,0x2050})do assert(emu.read(at,emu.memType.nesPpuDebug)==0x24,'No stale robot icon/ammo/meter cells')end
  capture(current.q.name..'-committed-HUD');change('setup')
 elseif phase=='run'then
  local s=current.stage;local kind=current.t.kind
  for i=0,9 do if r('RgShotType',i)==current.q.shot_type and r('RgShotImpact',i)>0 then s.impacts=s.impacts+1 end end
  if kind=='terrain'and current.q.terrain_behavior=='bypass-plain-ground'then
   for i=0,9 do if r('RgShotType',i)==current.q.shot_type and r('RgShotX',i)>=176 and r('RgShotPage',i)==0 then s.groundCrossed=true end end
  end
  assert(age<400,'Finite actual source effect/contact/terrain/cleanup '..current.q.name..'/'..kind)
  if age>=110 and pool()==0 then
   assert(#s.spawns>0 and s.draws>0,'Actual fresh input emits and renders the correct compiled weapon')
   if kind=='contact'then assert(s.target and s.damageCalls>0 and s.hits>0,'Actual emitted source weapon contacts real Goomba')end
   if kind=='terrain'then
    assert(s.blockCalls>0,'Actual source terrain query executes')
    if current.q.terrain_behavior=='bypass-plain-ground'then assert(s.groundCrossed and s.impacts==0,'Source Laser/Flare passes plain ground without invented impact')
    else assert(s.impacts>0,'Ordinary Bill bullets retain actual ground impact')end
   end
   if kind=='auto-cadence'then
    local times={};for _,v in ipairs(s.spawns)do times[#times+1]=v.update end
    assert(#times>=6,'Held machine input emits its six-shot cadence')
    for i=1,5 do assert(times[i+1]-times[i]==C.machine_first_deltas[i],'Actual source machine110ms fractional cadence')end
   elseif kind=='second-edge'then assert(#s.spawns>=2*current.q.expected_initial_emissions,'Second fresh B edge emits a second legal batch')end
   local cue=false;for _,v in ipairs(s.sourceSfx)do if current.q.shot_type>=42 then cue=cue or(v.kind=='AvAudioRequest'and v.value==current.q.sfx)else cue=cue or(v.kind=='Square1SoundQueue'and v.value&C.fireball_sfx~=0)end end
   assert(cue,'Actual source weapon SFX request observed; waveform remains separate')
   s.passed=true;s.completed=wall;s.naturalPoolEmpty=true;capture(current.q.name..'-'..taskIndex..'-natural-cleanup');event('Bill-component-completed',s)
   taskIndex=taskIndex+1
   if taskIndex>#current.q.tasks then current.completed=wall;index=index+1;change('next')else current.t=current.q.tasks[taskIndex];change('setup')end
  end
 end
end)
