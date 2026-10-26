-- ONE B-only initialized scene; all lift/throw/contact/reward results are native.
-- Initial powered ARM ownership is declared setup, not an acquisition claim.
local record={name='arm-question-face1',heads=0,throws=0,fragments=0,
  spawns={},blockReturns=0,selected=false,questionCell=116,neighborCell=117,liftCell=163}
records[1]=record
local playerFields={'Player_X_Position','Player_PageLoc','Player_Y_Position',
 'Player_Y_HighPos','PlayerSize','CrouchingFlag','Player_Y_Speed'}
local function playerState()
 local z={};for _,n in ipairs(playerFields)do z[#z+1]=r(n)end;return z
end
local function same(a,b)
 if #a~=#b then return false end;for i,v in ipairs(a)do if b[i]~=v then return false end end;return true
end
local function change(p)phase=p;age=0;FINAL_ABILITY_PHASE={name=record.name,phase=p};event('arm-question-phase',{phase=p})end
local function setupScene()
 assert(record.selected and r('InvSelected',9)==1,'Real Select commits ARM before scene')
 writeBoundary=true
 arena(false)
 for i=0,C.special_ram_bytes-1 do w('SpecialRamStart',0,i)end
 w('Player_X_Position',32);w('MmOldX',32);w('Player_PageLoc',0)
 w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
 w('Player_MovingDir',1);w('PlayerFacingDir',1);w('Player_CollisionBits',255)
 w('InvDirty',1)
 for i=0,3 do assert(r('InvDropKind',i)==0,'Fresh isolated scene has no prior earned capsules')end
 assert(r('InvRefill')==0,'Fresh scene has no prior refill lifecycle')
 -- Logical map and visible metatiles agree: lift (48,192), target(64,144).
 w('Block_Buffer_1',0x51,163);tile(0,3,12,0x51)
 w('Block_Buffer_1',0xc1,116);tile(0,4,9,0xc1)
 w('Block_Buffer_1',0x51,117);tile(0,5,9,0x51)
 writeBoundary=false
 assert(r('InvAmmo',145)==112,'Scene preserves declared starting ARM stock')
 record.setupUpdate=updates;record.setupWall=wall
 record.initialPlayer=playerState();change('exercise');capture('arm-question-setup')
end
hook('InventorySelectionCommit',function()
 if not entered or phase~='select' then return end
 local wanted=emu.getState()['cpu.a']
 onReturn('arm-question-selection',function()
  assert(r('InvSelected',9)==wanted,'Controller selection has genuine commit')
  if wanted==1 then record.selected=true;record.selectedUpdate=updates;change('setup')end
 end)
end)
hook('MegaManSuperArmThrow',function()
 if not entered or phase~='exercise' then return end
 local stock=r('InvAmmo',145);local held=r('SsHeld');assert(held>0,'Actual throw has real lifted slot')
 local slot=held-1
 onReturn('arm-question-throw',function()
  assert(stock==112 and r('InvAmmo',145)==104,'Native throw pays eight once')
  assert(r('SsHeld')==0 and r('RgShotType',slot)==9 and r('SsMode',slot)==0,'Native held brick becomes flying ARM')
  assert(r('RgShotVXLo',slot)==0x55 and r('RgShotVXHi',slot)==2,'Native right throw X velocity')
  assert(r('RgShotVYLo',slot)==0x55 and r('RgShotVYHi',slot)==0xfd,'Native throw Y velocity')
  record.throws=record.throws+1;record.throwUpdate=updates;record.throwSlot=slot
  event('actual-arm-throw',{slot=slot,stock_before=stock,stock_after=r('InvAmmo',145)});capture('arm-question-throw')
 end)
end)
hook('SpecialWeapons::Spawn',function()
 if not entered or phase~='exercise' then return end
 local t=emu.getState()['cpu.a'];local slot=r('RgSlot')
 onReturn('arm-question-spawn-'..t..'-'..slot,function()
  assert(r('RgShotType',slot)==t,'Actual special spawn owns its type/slot')
  record.spawns[#record.spawns+1]={type=t,slot=slot,update=updates}
  if t==21 then
   assert(record.heads==1,'Fragments follow actual question transaction')
   record.fragments=record.fragments+1
   if record.fragments==4 then event('actual-four-arm-fragments',record.spawns);capture('arm-question-four-fragments')end
  end
 end)
end)
hook('MegaManWeapons::Blocks',function()
 if not entered or phase~='exercise' or r('MmBulletType')~=42 then return end
 local saved=playerState()
 onReturn('arm-question-block-consumer',function()
  assert(same(saved,playerState()),'Complete native block bridge restores all seven player fields')
  assert(r('MmBlockAttack')==0,'Native block transaction releases its attack owner')
  record.blockReturns=record.blockReturns+1
 end)
end)
hook('PlayerHeadCollision',function()
 if not entered or phase~='exercise' or r('MmBlockAttack')~=1 then return end
 assert(r('MmBulletType')==42,'ARM proxy owns native block transaction')
 assert(r('Player_X_Position')==64 and r('Player_PageLoc')==0 and r('Player_Y_Position')==144,'Exact contacted question cell authors native block origin')
 record.heads=record.heads+1;assert(record.heads==1,'One question activation')
 event('actual-arm-native-question',{player=playerState()});capture('arm-question-contact')
end)
hook('InventoryPreparePickup',function()
 if not entered or phase~='exercise' then return end
 local slot=emu.getState()['cpu.x']
 onReturn('arm-question-reward-stamp',function()
  assert(slot==5 and r('InvPickupOwner',slot)==9,'Real question reward has native actor/owner')
  assert(r('InvPickup',slot)~=0xfc,'Powered Bass question chooses supported inventory reward')
  record.rewardStamp={slot=slot,stamp=r('InvPickup',slot),update=updates}
  event('actual-question-reward-stamp',record.rewardStamp)
 end)
end)
hook('GameLoop',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 or r('GameEngineSubroutine')~=8 then return end
 if not entered then
  assert(r('SelectedCharacter')==9 and r('RlVariant')==0 and r('CrossoverBehaviorVersion')==0,'Actual cold-selected Bass Easy')
  assert(r('InvSelected',9)==0,'Cold default selection precedes real Select')
  entered=true;writeBoundary=true
  w('PlayerStatus',1);w('InvOwnedLo',3,9);w('InvOwnedHi',0,9);w('InvAmmo',112,145)
  writeBoundary=false;change('settle')
  event('B-only-initial-setup',{tier=1,owned=3,stock=112,acquisition=false})
 end
 updates=updates+1;age=age+1
 assert(r('SelectedCharacter')==9 and r('RlVariant')==0 and r('CrossoverBehaviorVersion')==0,'Native owner and numeric mode remain requested')
 if phase=='settle' and age>=30 then change('select')
 elseif phase=='setup' then setupScene()end
end)
local function galleryInput()
 if phase=='select' then return{select=age%6==1}end
 if phase=='exercise' then return{b=(age>=6 and age<20)or(age>=36 and age<40)}end
 return{}
end
hook('finish',function()
 if not entered or done then return end
 assert(r('MmDeathFlag')==0 and r('GameEngineSubroutine')==8,'Controlled question scene survives')
 if phase=='select' then assert(age<90,'Real Select reaches ARM')end
 if phase~='exercise' then return end
 assert(r('Block_Buffer_1',117)==0x51,'Adjacent masonry remains intact throughout observed phase')
 if age==30 then
  assert(r('SsHeld')>0 and r('Block_Buffer_1',163)==0,'Native held B removes/lifts actual masonry')
  assert(r('InvAmmo',145)==112,'Lift remains free before the real throw')
  record.lifted=true;capture('arm-question-held')
 end
 if r('Block_Buffer_1',116)==0xc4 then record.used=true end
 if r('Enemy_Flag',5)~=0 and r('Enemy_ID',5)==0x2e then
  assert(r('Enemy_X_Position',5)==64 and r('Enemy_PageLoc',5)==0,'Actual released reward uses contacted cell')
  if not record.revealed then
   assert(record.heads==1 and record.rewardStamp,'Reward follows actual native head/stamp callbacks')
   record.revealed=updates;record.revealY=r('Enemy_Y_Position',5)
   event('actual-question-reward-created',{state=r('Enemy_State',5),y=record.revealY,stamp=r('InvPickup',5)});capture('arm-question-reveal')
  end
  if r('Enemy_State',5)>=128 and not record.mature then
   assert(record.revealY-r('Enemy_Y_Position',5)==16,'Native inventory reward rises its full sixteen pixels')
   record.mature=updates;event('actual-question-reward-mature',{age=updates-record.revealed});capture('arm-question-mature')
  end
 end
 if record.throwUpdate and updates-record.throwUpdate>=250 then
  assert(record.lifted and record.throws==1 and record.heads==1 and record.blockReturns>0,'Real free lift, paid throw and complete block transaction return')
  assert(record.used and record.revealed and record.mature,'Native question is used and reward emerges completely')
  assert(record.fragments==4,'Exactly four real independent thrown-brick fragments')
  record.continuedUpdates=updates-record.throwUpdate;record.completed=wall
  event('arm-question-regression-complete',record);capture('arm-question-complete');done=true
 end
 assert(age<420,'Bounded question contact/rise and continued main-loop progress')
end)
