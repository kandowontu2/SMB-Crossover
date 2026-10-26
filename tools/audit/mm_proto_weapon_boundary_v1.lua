-- One identity/mode profile. Declared B-only component setups are not pickups.
-- Owner, variant, selectable items, indices, art and thresholds are linked data.
local current,selectionCount=nil,0
local function owner()return C.identity.owner end
local function selected()return r('InvSelected',owner())end
local function ammo(item)return r('InvAmmo',C.identity.ammo_indices[item+1])end
local function ammoState()
 local t={};for item=1,8 do t[item]=ammo(item)end;return t
end
local function equal(a,b)
 if #a~=#b then return false end;for i,v in ipairs(a)do if b[i]~=v then return false end end;return true
end
local function primaryCount()
 local n=0;for i=0,3 do if r('MmBulletType',i)~=0 then n=n+1 end end;return n
end
local function specialCount()
 local n=0;for i=0,9 do if r('RgShotType',i)~=0 then n=n+1 end end;return n
end
local function transition(p)
 phase=p;age=0;FINAL_ABILITY_PHASE={name=current and current.q.name,phase=p}
 event('mm-component-phase',{name=current and current.q.name,phase=p,index=index})
end
local function requireOwner()
 assert(r('SelectedCharacter')==owner() and r(C.identity.variant_ram)==C.identity.variant,'Actual selected robot identity/variant')
 assert(r('CrossoverBehaviorVersion')==C.mode_value,'Actual numeric behavior readback')
end
local function checkPrimary(t,charge)
 if t==1 then return end
 if t==2 then assert(charge>=C.charge.weak and charge<C.charge.full,'Weak source charge threshold')
 elseif t==3 then assert(charge==C.charge.full,'Full source charge cap')
 else error('Unexpected tier1 primary type '..t)end
end
local function checkRushDebit(before,after)
 assert(after==math.max(0,before-C.rush.bounce_cost),'Direct source Rush twelve-unit/clamp debit')
end
local function finishCase()
 assert(current and not current.completed,'One cumulative completion per component')
 current.completed=updates;current.finalAmmo=ammoState();current.finalWall=wall
 event('mm-weapon-component-complete',current);capture(current.q.name..'-complete')
 index=index+1
 if index>#C.cases then done=true;return end
 current={q=C.cases[index],primarySpawns={},art={},refillCredits=0}
 records[index]=current;transition('select')
end
local function setupComponent()
 assert(selected()==current.q.item,'Real controller selection precedes setup')
 event('declared-component-reset',{name=current.q.name,prior_ammo=ammoState(),prior_refill=r('InvRefill'),prior_drops={r('InvDropKind'),r('InvDropKind',1),r('InvDropKind',2),r('InvDropKind',3)}})
 writeBoundary=true;arena(false)
 for i=0,C.special_ram_bytes-1 do w('SpecialRamStart',0,i)end
 for _,n in ipairs(C.drop_arrays)do for i=0,3 do w(n,0,i)end end
 for _,n in ipairs({'InvRefill','InvRefillRemain','InvRefillTick','InvDropAmount','AvRefillItem','InvDropEnemy','InvDropSlot','TimerControl','MmChargeFrames','MmCharging','MmFrictionYActive','MmSliding','MmSlideTravel','MmSlideStop','GuestHurtTicks','GuestHurtKind','GamePauseStatus'})do w(n,0)end
 w('PlayerStatus',1);w('InvOwnedLo',current.q.kind=='balance' and 7 or 1,owner());w('InvOwnedHi',7,owner())
 for item=1,8 do w('InvAmmo',0,C.identity.ammo_indices[item+1])end
 w('InvAmmo',current.q.stock,C.identity.ammo_indices[9])
 w('PlayerFacingDir',1);w('Player_MovingDir',1);w('Player_CollisionBits',255);w('InvDirty',1)
 if current.q.kind=='balance' then
  w('InvAmmo',60,C.identity.ammo_indices[2]);w('InvAmmo',4,C.identity.ammo_indices[3])
  -- Complete isolated small-capsule initial actor; collection/refill stay native.
  w('InvDropKind',1);w('InvDropX',r('Player_X_Position')+8);w('InvDropPage',r('Player_PageLoc'));w('InvDropY',r('Player_Y_Position')+16)
 end
 writeBoundary=false
 current.beforeAmmo=ammoState();current.setupUpdate=updates;current.setupWall=wall
 current.expectedPrimary=current.q.expected_primary;transition('use');capture(current.q.name..'-setup')
end
local function rushContactSetup()
 local slot=current.rushSlot
 assert(r('RgShotType',slot)==20 and r('SsMode',slot)==1 and r('RgShotY',slot)==208,'Actual Rush has fallen and landed before controlled contact setup')
 event('declared-descending-player-reset',{rush_slot=slot,rush_x=r('RgShotX',slot),rush_y=r('RgShotY',slot),stock=ammo(8),natural_jump=false})
 writeBoundary=true
 w('Player_X_Position',r('RgShotX',slot)-8);w('MmOldX',r('Player_X_Position'));w('Player_PageLoc',r('RgShotPage',slot))
 w('Player_Y_Position',160);w('Player_Y_HighPos',1);w('Player_State',2);w('Player_Y_Speed',2)
 w('Player_X_Speed',0);w('Player_X_MoveForce',0);w('Player_Y_MoveForce',0);w('MmFrictionYActive',0)
 for i=0,1 do w('MmVY',0,i);w('MmYFraction',0,i);w('MmVX',0,i);w('MmXFraction',0,i)end
 w('MmVY',2,2);w('MmVX',0,2)
 writeBoundary=false;transition('rush-contact');capture(current.q.name..'-contact-setup')
end
hook('InventorySelectionCommit',function()
 if not entered then return end
 local s=emu.getState();local wanted=s['cpu.a'];assert(s['cpu.x']==owner(),'Real inventory selection owner')
 onReturn('mm-selection',function()
  assert(selected()==wanted,'Native controller selection commits actual item')
  assert(wanted~=C.identity.balancer and wanted~=C.identity.charge_item,'Passive upgrades are not selectable weapons')
  selectionCount=selectionCount+1;event('actual-mm-selection',{item=wanted,count=selectionCount})
 end)
end)
hook('MegaManWeapons::Spawn',function()
 if not entered or not current then return end
 local t=emu.getState()['cpu.a'];local charge=r('MmChargeFrames');local before=ammoState();local occupied={}
 for i=0,3 do occupied[i+1]=r('MmBulletType',i)end
 onReturn('mm-primary-spawn',function()
  requireOwner();checkPrimary(t,charge);assert(equal(before,ammoState()),'Ordinary/charged buster does not debit special stock')
  local found=nil
  for i=0,3 do if occupied[i+1]==0 and r('MmBulletType',i)~=0 then
   assert(not found and r('MmBulletType',i)==t and r('MmBulletDir',i)==1,'Actual primary spawn kind/facing/slot')
   assert(r('MmBulletAge',i)==0,'Actual primary begins at native age0');found=i
  end end
  assert(found~=nil,'Funded primary source call actually spawns')
  current.primarySpawns[#current.primarySpawns+1]={type=t,slot=found,charge=charge,update=updates,phase=phase}
  event('actual-mm-primary',current.primarySpawns[#current.primarySpawns]);capture(current.q.name..'-primary-'..#current.primarySpawns)
 end)
end)
hook('PrimaryArtReady',function()
 if not entered or not current then return end
 local slot=r('MmSlot');local t=r('MmBulletType',slot);assert(t>=1 and t<=6,'Actual primary art type domain')
 local length=C.primary.lengths[t];local frame=(r('MmBulletAge',slot)//2)%length
 local q=C.primary.records[t][frame+1][r('MmBulletDir',slot)==2 and 2 or 1]
 assert(r('R0')+256*r('R1')==q.address and bank(0xc000)==q.bank,'Actual linked primary effect pointer and C owner')
 for i,v in ipairs(q.bytes)do assert(emu.read(q.bank*8192+q.address%8192+i-1,emu.memType.nesPrgRom)==v,'Actual primary art record bytes')end
 local key=tostring(t)..':'..frame
 if not current.art[key]then current.art[key]=true;event('actual-mm-primary-art',{type=t,frame=frame,address=q.address,bank=q.bank});capture(current.q.name..'-art-'..key)end
end)
hook('MegaManRushAttack',function()
 if not entered or not current or current.q.kind~='rush' and current.q.kind~='rush-refusal' then return end
 local before=ammo(8);local had=specialCount()
 onReturn('mm-rush-attack',function()
  assert(ammo(8)==before,'Rush summon/existing-Rush buster are free')
  if current.q.kind=='rush-refusal' then
   assert(before==3 and specialCount()==0 and primaryCount()==0,'Native sub-four stock gate refuses summon')
   current.refused=true;event('actual-rush-summon-refusal',{stock=before});return
  end
  if had==0 then
   local slot=r('RgSlot');assert(r('RgShotType',slot)==20 and r('SsMode',slot)==0,'Actual Rush source summon')
   assert(r('RgShotX',slot)==r('Player_X_Position')+28 and r('RgShotPage',slot)==0 and r('RgShotY',slot)==0 and r('RgShotYHigh',slot)==1,'Native right-facing overhead Rush origin')
   current.rushSlot=slot;current.summoned=true;event('actual-rush-free-summon',{slot=slot,stock=before});capture(current.q.name..'-summon')
  else
   current.existingAttack=true;assert(primaryCount()>0,'Existing Rush redirects B to native ordinary buster')
   event('actual-existing-rush-buster',{stock=before});capture(current.q.name..'-existing-buster')
  end
 end)
end)
hook('MegaManRushBounce',function()
 if not entered or not current or current.q.kind~='rush' then return end
 local before=ammo(8);assert(r('StarInvincibleTimer')==0,'Declared non-star Rush stock contract')
 onReturn('mm-rush-direct-bounce',function()
  checkRushDebit(before,ammo(8));assert(before==20 and ammo(8)==8,'One actual normal twelve-unit Rush debit')
  assert(r('MmFrictionYActive')==0 and r('MmJumpReleased')==1 and r('MmRushLandRequest')==1,'Native Rush jump/latch flags')
  assert(not current.bounced,'One source spring contact');current.bounced=updates
  event('actual-rush-direct-debit',{before=before,after=ammo(8),cost=C.rush.bounce_cost,source='MegaManRushBounce full return'});capture(current.q.name..'-bounce')
 end)
end)
hook('SpecialWeapons',function()
 if not entered or not current or current.q.kind~='rush' then return end
 onReturn('mm-rush-full-caller',function()
  if current.bounced and not current.launch then
   assert(r('MmVY',2)==0xf9 and r('Player_Y_Speed')==0xf9 and r('Player_State')==1 and r('SsMode',current.rushSlot)==2,'Full actual Rush caller launches body and starts spring animation')
   current.launch=updates;transition('rush-exit')
  end
 end)
end)
hook('SpecialDrawShots::Coordinates',function()
 if not entered or not current or current.q.kind~='rush' then return end
 local i=r('RgSlot');if r('RgShotType',i)~=20 then return end
 local art=r('SsArt',i);assert(art>0,'Rush uses actual source art')
 local q=C.effect_records[art+1][r('RgShotDir',i)==2 and 2 or 1]
 assert(r('R0')+256*r('R1')==q.address and bank(0xc000)==q.bank,'Actual Rush linked source art pointer')
 current.rushDraws=(current.rushDraws or 0)+1
end)
hook('InventoryRefillAmount',function()
 if not entered or not current or current.q.kind~='balance' then return end
 local amount=emu.getState()['cpu.a'];assert(selected()==0 and amount==8,'Actual small energy capsule under default selection')
 local before=ammoState()
 onReturn('mm-balancer-choice',function()
  assert(r('InvRefill')==C.identity.ammo_indices[3] and r('InvRefillRemain')==8 and r('InvRefillTick')==3,'Passive BALANCE selects least-energy owned METAL at native index')
  assert(equal(before,ammoState()),'Refill admission schedules credits, never collects them immediately')
  current.balanceChoice=true;event('actual-mm-balancer-choice',{index=r('InvRefill'),amount=amount});capture(current.q.name..'-choice')
 end)
end)
hook('InventoryUiTick',function()
 if not entered or not current or current.q.kind~='balance' then return end
 local before=ammo(2);local target,tick,remain=r('InvRefill'),r('InvRefillTick'),r('InvRefillRemain')
 onReturn('mm-balance-credit',function()
  local after=ammo(2);if after==before then return end
  assert(target==C.identity.ammo_indices[3] and tick==1 and remain>=4,'Credit at actual least-weapon refill tick')
  assert(after==math.min(112,before+4) and r('InvRefillRemain')==(remain-4)%256,'Exact native four-unit credit/remaining')
  assert(r('InvRefillTick')==3 and r('InvRefill')==(remain==4 and 0 or target),'Exact native refill continuation')
  current.refillCredits=current.refillCredits+after-before
  event('actual-mm-balancer-credit',{before=before,after=after,index=target,credits=current.refillCredits})
 end)
end)
hook('GameLoop',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 or r('GameEngineSubroutine')~=8 then return end
 if not entered then
  requireOwner();assert(selected()==0,'Cold robot starts at default selection')
  entered=true;current={q=C.cases[1],primarySpawns={},art={},refillCredits=0};records[1]=current;transition('select')
 end
 updates=updates+1;age=age+1;requireOwner()
 if phase=='select' and selected()==current.q.item then transition('setup')
 elseif phase=='setup' then setupComponent()
 elseif phase=='rush-reset-contact' then rushContactSetup()end
end)
local function galleryInput()
 if phase=='select' then return{select=age%6==1}end
 if phase=='use' then
  local k=current.q.kind
  if k=='primary' then return{b=age>=6 and age<current.q.release}end
  if k=='rush' or k=='rush-refusal' then return{b=age>=6 and age<10}end
 end
 if phase=='rush-existing' then return{b=age>=2 and age<6}end
 return{}
end
hook('finish',function()
 if not entered or done then return end
 requireOwner();assert(r('MmDeathFlag')==0 and r('GameEngineSubroutine')==8,'Profile remains in live normal play')
 if phase=='select' then assert(age<90,'Real Select reaches linked selectable item');return end
 if phase=='setup' or phase=='rush-reset-contact' then return end
 if phase=='use' then
  local k=current.q.kind
  if k=='primary' and age>=current.q.finish then
   assert(#current.primarySpawns==#current.q.expected_primary,'Actual primary spawn count')
   for i,t in ipairs(current.q.expected_primary)do assert(current.primarySpawns[i].type==t,'Actual primary order')end
   assert(primaryCount()==0 and r('MmChargeFrames')==0 and r('MmCharging')==0,'Native primary cleanup and charge release')
   assert(equal(current.beforeAmmo,ammoState()),'Default/charge remain free for complete component')
   for _,t in ipairs(current.q.expected_primary)do assert(current.art[tostring(t)..':0'],'Actual primary type has source art witness')end
   finishCase()
  elseif k=='rush' and current.summoned then
   local i=current.rushSlot
   if r('SsMode',i)==1 then
    assert(r('RgShotY',i)==208 and ammo(8)==20,'Native Rush feet land on logical/visible floor, waiting free')
    current.landed=updates;capture(current.q.name..'-landed');transition('rush-existing')
   end
  elseif k=='rush-refusal' and age>=40 then
   assert(current.refused and ammo(8)==3 and primaryCount()==0 and specialCount()==0,'Actual underfunded summon leaves all pools/stock unchanged');finishCase()
  elseif k=='balance' and age>=40 then
   assert(current.balanceChoice and current.refillCredits==8 and ammo(1)==60 and ammo(2)==12 and ammo(8)==8,'Actual BALANCE routes and credits exactly eight to least owned weapon')
   assert(selected()==0 and r('InvDropKind')==0 and r('InvRefill')==0 and r('TimerControl')==0,'Native pickup/refill completes without selecting passive upgrade')
   finishCase()
  end
 elseif phase=='rush-existing' and age>=18 then
  assert(current.existingAttack and ammo(8)==20 and #current.primarySpawns==1 and current.primarySpawns[1].type==1,'Existing Rush native ordinary buster is free')
  transition('rush-reset-contact')
 elseif phase=='rush-exit' and current.launch and r('RgShotType',current.rushSlot)==0 and primaryCount()==0 then
  assert(ammo(8)==8 and current.rushDraws and current.rushDraws>0,'Actual Rush spring/exit/accelerating flight clear with source art and retained stock');finishCase()
 end
 assert(age<240,'Bounded native component '..phase)
end)
