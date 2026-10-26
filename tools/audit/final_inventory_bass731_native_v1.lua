-- Controlled B-only gallery. Inventory/resources/arena/actors are declared seeds,
-- never acquisitions. Selection, use, costs, contacts and cleanup are native.
local current=nil
local selectionStart=0
local choiceCount=0
local function recordArt(q,kind,t)
 assert(q and bank(0xc000)==q.bank,'Actual source effect C-bank')
 for i,v in ipairs(q.bytes)do assert(emu.read(q.bank*8192+q.address%8192+i-1,emu.memType.nesPrgRom)==v,'Exact compiled effect record bytes')end
 current.draws[t]=(current.draws[t]or 0)+1
 if current.draws[t]==1 then event('actual-source-effect-draw',{kind=kind,type=t,address=q.address,bank=q.bank,bytes=q.bytes,face=current.q.face});capture(current.q.name..'-art-'..t)end
end
local function stock()return r('InvAmmo',144+current.q.item)end
local function pool()
 local n=0;for i=0,9 do if r('RgShotType',i)~=0 then n=n+1 end end;return n
end
local function stateRow()
 local z={selected=r('InvSelected',9),ammo=current and stock(),held=r('SsHeld'),kick=r('SsKick'),dash=r('XgDash'),radius=r('SsWaterRadius'),expanding=r('SsWaterExpand'),shots={}}
 for i=0,9 do z.shots[#z.shots+1]={slot=i,type=r('RgShotType',i),age=r('RgShotAge',i),x=r('RgShotX',i),page=r('RgShotPage',i),y=r('RgShotY',i),high=r('RgShotYHigh',i),mode=r('SsMode',i),hidden=r('SsHidden',i),art=r('SsArt',i)}end
 return z
end
local function change(p)phase=p;age=0;FINAL_ABILITY_PHASE={name=current and current.q.name,phase=p};event('gallery-phase',stateRow())end
local function clearArena()
 arena(false)
 for _,n in ipairs({'SpecialRamStart'})do for i=0,C.special_ram_bytes-1 do w(n,0,i)end end
 for _,n in ipairs({'XgDash','XgJumpUsed','XgBassDashJump','MmSliding','MmSlideTravel','MmSlideStop','MmChargeFrames','MmCharging','AvStopwatch','AvSlash','SsFreeze','SsBodyStop','SsHeld','SsWaterExpand','Player_X_Scroll','GuestHurtTicks','GuestHurtKind','GamePauseStatus','InvRefill','InvRefillRemain'})do w(n,0)end
 w('Player_MovingDir',current.q.face);w('PlayerFacingDir',current.q.face);w('Player_CollisionBits',255)
 w('PlayerStatus',1);w('InvDirty',1)
 for i=0,5 do w('MmEnemyHealthLo',0,i);w('MmEnemyHealthHi',0,i);w('MmEnemyFlash',0,i);w('RgEnemyStun',0,i);w('Enemy_Y_MoveForce',0,i)end
 for i=0,9 do
  for _,n in ipairs(C.shot_arrays)do w(n,0,i)end
 end
 if current.q.item==1 then
  -- Actual GrabBrick probes PlayerX+8+/-10,Y+20; real map cell51.
  local col=(r('Player_X_Position')+8+(current.q.face==1 and 10 or-10))//16
  w('Block_Buffer_1',0x51,160+col);tile(0,col,12,0x51);current.armCell=160+col
 end
end
local function setup(kind)
 writeBoundary=true;clearArena()
 if kind=='funded'then
  if current.q.item>0 then w('InvAmmo',current.q.initial_stock,144+current.q.item)end
 elseif kind=='pool'then
  if current.q.item>0 then w('InvAmmo',112,144+current.q.item)end
  -- Ten complete ordinary METAL records: native motion remains active. This
  -- is controlled full-pool input, not ten naturally acquired simultaneous shots.
  for i=0,9 do
   w('RgShotType',10,i);w('RgShotX',current.q.face==1 and 56+i*5 or 198-i*5,i)
   w('RgShotPage',0,i);w('RgShotY',72,i);w('RgShotYHigh',1,i);w('RgShotDir',current.q.face,i)
   w('RgShotVXLo',current.q.face==1 and 0xc0 or 0x40,i);w('RgShotVXHi',current.q.face==1 and 3 or 0xfc,i)
  end
 end
 writeBoundary=false
 current.component=kind;current.targetStaged=false;current.componentHitStart=current.hits
 current.componentSpawnStart=#current.spawns;current.componentSpendStart=#current.spends
 current.poolChecked=false;current.emptyChecked=false;current.componentChoiceStart=choiceCount
 current.beforeStock=current.q.item>0 and stock()or 0
 change(kind);capture(current.q.name..'-'..kind..'-setup')
end
local function target()
 if current.targetStaged then return end
 local q=current.q;local x,y
 if q.item==5 then
  if r('SsKick')~=1 or r('XgDash')==0 then return end
  x=r('Player_X_Position')+(q.face==1 and 22 or-10);y=r('Player_Y_Position')+8
 else
  local slot=nil
  for i=0,9 do
   if r('RgShotType',i)==q.contact_type and r('SsHidden',i)==0 and (q.item~=1 or r('SsMode',i)==0) and (q.item~=3 or r('RgShotAge',i)>=10) and (q.item~=7 or r('SsWaterExpand')~=0 and r('SsWaterRadius')>=42)then
    local dx=math.abs(r('RgShotX',i)-r('Player_X_Position'))
    if r('RgShotPage',i)==0 and dx>=30 and r('RgShotX',i)>=16 and r('RgShotX',i)<232 and r('RgShotYHigh',i)==1 and r('RgShotY',i)>=48 and r('RgShotY',i)<216 then slot=i;break end
   end
  end
  if not slot then return end
  x=r('RgShotX',slot)-6;y=r('RgShotY',slot)-8
 end
 assert(x>=0 and x<240 and y>=32 and y<216,'Controlled native target geometry')
 writeBoundary=true
 for _,v in ipairs({{'Enemy_Flag',1},{'Enemy_ID',6},{'Enemy_State',0},{'Enemy_X_Position',x},{'Enemy_PageLoc',0},{'Enemy_Y_Position',y},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_Y_MoveForce',0},{'Enemy_MovingDir',1},{'Enemy_BoundBoxCtrl',9},{'EnemyOffscrBitsMasked',0},{'Enemy_CollisionBits',0},{'MmEnemyHealthLo',0},{'MmEnemyHealthHi',0},{'MmEnemyFlash',0},{'RgEnemyStun',0}})do w(v[1],v[2],0)end
 writeBoundary=false;current.targetStaged=true
 event('controlled-falling-Goomba-target',{x=x,y=y,shot_type=q.contact_type,body_contact=q.item==5,disclosure='Complete source-aligned actor at native boundary, aligned to actual live effect. Native gravity/collision/defeat remain real; this is B contact, not a natural encounter.'})
end
local function cleanReceipt()
 assert(pool()==0 and r('SsHeld')==0 and r('SsKick')==0 and r('SsFreeze')==0 and r('SsBodyStop')==0,'Native selection clears robot effects')
 assert(r('MmBulletType')==0 and r('MmBulletType',1)==0 and r('MmBulletType',2)==0 and r('MmBulletType',3)==0,'Native selection clears primary pool')
end
hook('InventorySelectionCommit',function()
 if not entered then return end
 local wanted=emu.getState()['cpu.a'];local old=r('InvSelected',9)
 assert(emu.getState()['cpu.x']==9,'Real Bass selection owner')
 onReturn('bass-selection',function()
  assert(r('InvSelected',9)==wanted,'Actual controller selection commits requested item')
  if old~=wanted then choiceCount=choiceCount+1;cleanReceipt();event('actual-controller-selection',{before=old,after=wanted})end
 end)
end)
hook('InventorySpend',function()
 if not entered or not current then return end
 local s=emu.getState();local item=s['cpu.a'];local cost=s['cpu.y'];local before=r('InvAmmo',144+item)
 onReturn('bass-spend',function()
  local after=r('InvAmmo',144+item);local paid=before>=cost
  assert(after==(paid and before-cost or before),'Actual source cost/refusal preserves exact stock')
  local p=emu.getState()['cpu.ps']or emu.getState()['cpu.p'];if p then assert((p&1~=0)==paid,'Actual spend carry matches funded admission')end
  current.spends[#current.spends+1]={item=item,cost=cost,before=before,after=after,accepted=paid,component=current.component,wall=wall,update=updates}
  event('actual-source-spend',current.spends[#current.spends]);capture(current.q.name..'-cost-'..#current.spends)
 end)
end)
hook('SpecialWeapons::Spawn',function()
 if not entered or not current then return end
 local t=emu.getState()['cpu.a'];local i=r('RgSlot')
 onReturn('bass-spawn',function()
  assert(r('RgShotType',i)==t and r('RgShotDir',i)==current.q.face,'Actual special spawn type/facing')
  current.spawns[#current.spawns+1]={type=t,slot=i,wall=wall,update=updates,component=current.component}
  event('actual-special-spawn',current.spawns[#current.spawns]);capture(current.q.name..'-spawn-'..#current.spawns)
 end)
end)
hook('SpecialDrawShots::Coordinates',function()
 if not entered or not current or phase~='funded'then return end
 local i=r('RgSlot');local t=r('RgShotType',i);local art=r('SsArt',i)
 local q=art==0 and(t==21 and C.native_chunk or C.native_brick)or C.effect_records[art+1][r('RgShotDir',i)==2 and 2 or 1]
 assert(r('R0')+256*r('R1')==q.address,'Real source effect pointer')
 recordArt(q,'SpecialDrawShots actual pre-emitter',t)
end)
hook('SpecialDrawWaterShot',function()
 if not entered or not current or phase~='funded'then return end
 local i=r('RgSlot');local before=r('CurrentOAMOffset')
 onReturn('bass-water-art',function()
  if r('CurrentOAMOffset')~=before then
   assert(r('RgShotType',i)==17 and r('SsHidden',i)==0,'Real WATER render owner')
   -- Fast emitter writes the same two source parts. Its separate actual CPU
   -- equality proof is historical; current full physical OAM is retained here.
   current.draws[17]=(current.draws[17]or 0)+1
   if current.draws[17]==1 then event('actual-water-effect-emitter',{art=r('SsArt',i),slot=i,logical_before=before,logical_after=r('CurrentOAMOffset')});capture(current.q.name..'-water-art')end
  end
 end)
end)
hook('ExpandedWeaponPointer',function()
 if not entered or not current or phase~='funded'or current.q.item~=0 then return end
 onReturn('bass-primary-art',function()
  assert(r('R0')+256*r('R1')==C.buster_record.address,'Real default buster source pointer')
  recordArt(C.buster_record,'ExpandedWeaponPointer actual return',4)
 end)
end)
hook('ExpandedWeapons::FireShot',function()
 if not entered or not current or current.q.item~=0 then return end
 local before={};for i=0,9 do before[i]=r('RgShotType',i)end
 onReturn('bass-buster',function()
  for i=0,9 do if before[i]==0 and r('RgShotType',i)~=0 then
   assert(r('RgShotType',i)==4 and r('RgShotDir',i)==current.q.face,'Actual default Bass buster/facing')
   current.spawns[#current.spawns+1]={type=4,slot=i,component=current.component,wall=wall};capture(current.q.name..'-buster')
  end end
  if phase=='pool'then assert(pool()==10 and #current.spawns==current.componentSpawnStart,'Actual B input sees full buster pool');current.poolChecked=true;event('actual-buster-full-pool-refusal',{count=10,cost=0})end
 end)
end)
hook('MegaManWeapons::DamageEnemy',function()
 if not entered or not current or phase~='funded'or emu.getState()['cpu.x']~=0 then return end
 assert(r('MmBulletType')==current.q.damage_type,'Weapon-specific real damage owner, not arbitrary shot count')
 local old=r('Enemy_State');local hp=r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')
 current.damageCalls=current.damageCalls+1
 onReturn('bass-contact',function()
  if old~=r('Enemy_State')or hp~=r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')then current.hits=current.hits+1;event('actual-source-contact',stateRow());capture(current.q.name..'-contact')end
 end)
end)
hook('SpecialWeapons::MegaAttack',function()
 if not entered or not current or phase~='pool'then return end
 local n=pool();local ammo=current.q.item>0 and stock()or 0
 onReturn('bass-pool',function()
  assert(n==10,'Attempt sees all ten actual live records')
  local delta=current.q.item==7 and 16 or 0
  assert(stock()==ammo-delta,'Full-pool source spending policy')
  assert(#current.spawns==current.componentSpawnStart,'Full pool cannot create an eleventh record')
  current.poolChecked=true;event('actual-full-pool-refusal',{count=n,cost=delta});capture(current.q.name..'-pool-refusal')
 end)
end)
hook('SpecialWeapons',function()
 if not entered or not current or phase~='pool'or current.q.item~=1 and current.q.item~=5 then return end
 if current.q.item==1 and r('SavedJoypadBits')&64==0 then return end
 if current.q.item==5 and(r('XgDash')==0 or r('SsKick')~=0)then return end
 local n=pool();local ammo=stock()
 onReturn('bass-pool-special',function()
  assert(n==10,'ARM/KICK full-pool attempt sees ten records')
  if current.q.item==5 then assert(stock()==ammo-4 and r('SsKick')==1,'KICK pays for body attack even when effect slot is full')
  else assert(stock()==ammo and r('SsHeld')==0,'ARM requires free slot before lifting and paying')end
  current.poolChecked=true;event('actual-full-pool-special',{cost=ammo-stock()});capture(current.q.name..'-pool-refusal')
 end)
end)
hook('GameLoop',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 or r('GameEngineSubroutine')~=8 then return end
 if not entered then
  assert(r('SelectedCharacter')==9 and r('RlVariant')==0 and r('CrossoverBehaviorVersion')==C.mode_value,'Cold-selected Bass and actual numeric mode')
  entered=true;writeBoundary=true;w('PlayerStatus',1);w('InvOwnedLo',255,9);w('InvOwnedHi',0,9);writeBoundary=false
  phase='next';event('B-only-native-boundary-seeds',{tier=1,owned=255,mode=C.mode_value,acquisition=false})
 end
 updates=updates+1;age=age+1
 assert(r('CrossoverBehaviorVersion')==C.mode_value and r('SelectedCharacter')==9 and r('RlVariant')==0,'Requested owner/mode remains real')
 if phase=='next'then
  if index>#C.cases then done=true;return end
  current={q=C.cases[index],spawns={},spends={},hits=0,damageCalls=0,visibleTypes={},draws={},started=wall};records[#records+1]=current
  selectionStart=choiceCount;change('select')
 elseif phase=='setup-funded'then setup('funded')
 elseif phase=='setup-empty'then setup('empty')
 elseif phase=='setup-pool'then setup('pool')
 elseif phase=='funded'then target()end
end)
local function galleryInput()
 if phase=='select'then return{select=age%6==1}end
 if phase=='clear-after-pool'then return{select=age%6==1}end
 local b={}
 if phase=='funded'or phase=='empty'or phase=='pool'then
  local q=current.q
  if q.item==5 then b.down=age>=4 and age<9;b.a=age>=5 and age<8
  elseif q.item==1 then b.b=(age>=5 and age<9)or(phase=='funded'and age>=16 and age<20)
  elseif q.item==4 and phase=='funded'then b.b=age>=5 and age<84
  elseif q.item==7 and phase=='funded'then b.b=(age>=5 and age<8)or(age>=125 and age<128)
  else b.b=age>=5 and age<8 end
 end
 return b
end
hook('finish',function()
 if not entered or done or not current then return end
 assert(r('MmDeathFlag')==0 and r('InjuryTimer')==0 and r('GuestHurtTicks')==0,'Isolated controlled ability scene survives without unrelated damage')
 local q=current.q
 if phase=='select'then
  if choiceCount>selectionStart and r('InvSelected',9)==q.item then change('hud')end
  assert(age<240,'Real Select cycle reaches requested weapon')
 elseif phase=='hud'then
  if age>=20 then
   for i,v in ipairs(q.hud_name)do assert(emu.read(0x2023+i-1,emu.memType.nesPpuDebug)==v,'Actual committed inventory HUD name')end
   if q.item>0 then
    assert(r('InvHudActive')~=0 and r('InvHudPhysical')==q.icon_bank,'Real selected icon lease')
    for _,v in ipairs({{0x2037,0x2a},{0x2038,0x2b},{0x2057,0x2c},{0x2058,0x2d}})do assert(emu.read(v[1],emu.memType.nesPpuDebug)==v[2],'Actual committed icon tile')end
   end
   capture(q.name..'-selected-HUD');change('setup-funded')
  end
 elseif phase=='funded'then
  for i=0,9 do local t=r('RgShotType',i);if t~=0 and r('SsHidden',i)==0 then current.visibleTypes[t]=true end end
  if q.item==1 and r('SsHeld')>0 then assert(stock()==q.initial_stock,'ARM lift/hold is free');if not current.lifted then current.lifted=true;capture(q.name..'-held')end end
  if q.item==4 then for i=0,9 do if r('RgShotType',i)==18 and r('RgShotAge',i)>=63 then current.charged=true end end end
  if q.item==7 and r('SsWaterExpand')~=0 then current.expanded=true end
  if q.item==5 and r('SsKick')==1 and r('XgDash')~=0 then current.paidKick=true end
  if age>=210 and pool()==0 and r('SsHeld')==0 and r('XgDash')==0 then
   assert(current.hits>0 and current.damageCalls>0,'Actual intended source effect contacts controlled target')
   assert(current.visibleTypes[q.contact_type],'Actual effect reaches visible source-art state')
   assert((current.draws[q.contact_type]or 0)>0,'Actual source effect reaches its real draw owner')
   if q.item>0 then assert(stock()==0,'Funded source actions exhaust exact seeded stock')end
   if q.item==1 then assert(current.lifted,'ARM actual lift before paid throw')end
   if q.item==4 then assert(current.charged and current.visibleTypes[14],'PHARAOH full charge/release')end
   if q.item==7 then assert(current.expanded,'WATER orbit then real second-B expansion')end
   if q.item==5 then assert(current.paidKick,'KICK actual paid native dash and body contact')end
   current.naturalCleanup=true;capture(q.name..'-natural-cleanup');change('setup-empty')
  end
  assert(age<420,'Funded source contact/natural expiry bounded')
 elseif phase=='empty'then
  if age>=25 then
   if q.item>0 then assert(stock()==0 and pool()==0 and r('SsHeld')==0 and r('SsKick')~=1,'Exhausted weapon refuses paid effect')
    if q.item==1 then assert(r('Block_Buffer_1',current.armCell)==0x51,'Underfunded ARM leaves source block intact')end
   else assert(#current.spawns>current.componentSpawnStart,'Default buster remains free without special ammo')end
   current.emptyChecked=true;capture(q.name..'-exhaust-refusal');change('setup-pool')
  end
 elseif phase=='pool'then
  if current.poolChecked then current.poolPassed=true;current.clearChoice=choiceCount;change('clear-after-pool')end
  assert(age<15,'Full-pool source attempt is observed before seeded records leave viewport')
 elseif phase=='clear-after-pool'then
  if choiceCount>current.clearChoice then cleanReceipt();current.selectionCleanup=true;capture(q.name..'-selection-cleanup');current.completed=wall;index=index+1;change('next')end
  assert(age<30,'Actual controller selection owns cleanup')
 end
end)
