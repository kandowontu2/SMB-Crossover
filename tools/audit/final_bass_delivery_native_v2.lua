-- Four physical rewards, acquired from a cold Bass start. No tier, inventory,
-- pickup, ammo, RNG, or collection-result seeds. World/position staging and
-- explicitly disclosed contact alignment happen only at GameLoop boundaries.
local current=nil
local seen={}
local function owned()return r('InvOwnedLo',9)+256*r('InvOwnedHi',9)end
local function shots()
 local n=0;for i=0,9 do if r('RgShotType',i)~=0 then n=n+1 end end;return n
end
local function change(p)
 phase=p;age=0;FINAL_ABILITY_PHASE={reward=index,phase=p}
 event('delivery-phase',{owned=owned(),selected=r('InvSelected',9),status=r('PlayerStatus')})
end
local function stage()
 assert(index<=4 and r('PlayerStatus')==(index==1 and 0 or 1),'Previous physical collection owns power state')
 assert(r('GuestPowerupActive')==0 and r('InvRefill')==0 and shots()==0,'Previous native effects settled')
 writeBoundary=true;arena(true);writeBoundary=false
 current={number=index,staged=wall,before=owned(),statusBefore=r('PlayerStatus'),ownerCalls=0,prepareCalls=0,grantCalls=0,transformCalls=0,riseCalls=0,drawCalls=0,spends={},selections={}}
 records[index]=current;change('collect');capture('reward-'..index..'-block')
end
hook('InventoryPreparePickup',function()
 if not entered or phase~='collect'then return end
 assert(emu.getState()['cpu.x']==5,'Native block powerup slot5')
 current.prepareCalls=current.prepareCalls+1
 local before=owned();local prng=r('PseudoRandomBitReg',1)
 onReturn('delivery-prepare',function()
  assert(owned()==before,'Reveal does not grant ownership')
  local item=r('InvPickup',5)
  if index==1 then assert(item==0,'Cold first physical block is mushroom')
  else
   assert(item>=1 and item<=8 and(before&(1<<item))==0 and not seen[item],'Native roll excludes owned/revealed rewards')
   if item==8 then assert(before&254~=0,'Passive BALANCE requires an acquired weapon')end
  end
  current.item=item;current.prngAtPrepare=prng;current.prepareAt=wall
  current.nativeType=r('PowerUpType',5);assert(current.nativeType==(item==0 and 0 or 1),'Actual native mushroom/flower adapter')
  event('actual-reward-prepared',{item=item,prng=prng,before=before,nativeType=current.nativeType})
 end)
end)
hook('InventoryRisePickup',function()
 if not entered or phase~='collect'or not current or current.item==nil then return end
 if emu.getState()['cpu.x']==5 and current.item>0 and r('TimerControl')==0 then
  current.riseCalls=current.riseCalls+1
 end
end)
hook('InventoryCollect',function()
 if not entered or phase~='collect'then return end
 assert(emu.getState()['cpu.x']==5 and current.mature and current.contactAligned,'Real owner only after recorded full rise/contact alignment')
 current.ownerCalls=current.ownerCalls+1
 assert(current.ownerCalls==1 and r('InvPickup',5)==current.item,'One stamped physical collection owner')
 event('actual-physical-collect',{item=current.item,before=owned(),status=r('PlayerStatus')})
end)
hook('InventoryGrant',function()
 if not entered or phase~='collect'then return end
 assert(emu.getState()['cpu.a']==current.item and current.item>0,'Actual granted item is the physical source reward')
 current.grantCalls=current.grantCalls+1
end)
hook('GuestBeginPowerup',function()
 if not entered or phase~='collect'then return end
 assert(current.item==0 and current.ownerCalls==1,'Only physical mushroom begins hosted power transition')
 current.beginCalls=(current.beginCalls or 0)+1
 current.holdX=r('Player_X_Position');current.holdY=r('Player_Y_Position');current.holdPage=r('Player_PageLoc')
 event('actual-powerup-begin',{item=current.item});capture('reward-'..index..'-transform-begin')
end)
hook('GuestPowerupUpdate',function()
 if not entered or phase~='collect'or r('GuestPowerupActive')==0 then return end
 current.transformCalls=current.transformCalls+1
 assert(current.item==0 and r('GuestPowerupAge')==current.transformCalls-1 and r('PlayerStatus')==0,'Consecutive native mushroom transform updates')
 assert(r('GuestPowerupTarget')==1 and r('TimerControl')==254,'Native target/freeze retained')
 assert(r('Player_X_Position')==current.holdX and r('Player_PageLoc')==current.holdPage and r('Player_Y_Position')==current.holdY,'Source transform holds physical position')
 if current.transformCalls==6 or current.transformCalls==30 then capture('reward-'..index..'-transform-'..current.transformCalls)end
end)
hook('SpecialPickupArt',function()
 if not entered or not current or phase~='collect'or current.item==nil or current.item==0 or r('InvDrawSlot')~=5 then return end
 local art=emu.getState()['cpu.a'];local allowed=C.pickup_art[current.item]
 assert(art==allowed[1]or art==allowed[2],'Physical reward uses its compiled source icon, including BALANCE animation')
 onReturn('delivery-art',function()
  local p=emu.getState()['cpu.ps']or emu.getState()['cpu.p']
  if p&1==0 then return end -- Another genuine sprite family owns this draw.
  local q=C.pickup_records[art+1]
  assert(r('R0')+256*r('R1')==q.address and bank(0xc000)==q.bank,'Actual admitted source pickup record')
  for i,v in ipairs(q.bytes)do assert(emu.read(q.bank*8192+q.address%8192+i-1,emu.memType.nesPrgRom)==v,'Exact source pickup record bytes')end
  current.drawCalls=current.drawCalls+1
  if current.drawCalls==1 then event('actual-admitted-pickup-art',{item=current.item,art=art,record=q});capture('reward-'..index..'-source-icon')end
 end)
end)
hook('InventorySelectionCommit',function()
 if not entered or not current then return end
 local wanted=emu.getState()['cpu.a'];local before=r('InvSelected',9)
 assert(emu.getState()['cpu.x']==9 and wanted>=0 and wanted<=7,'Controller never selects passive BALANCE')
 assert(wanted==0 or owned()&(1<<wanted)~=0,'Selection uses genuinely acquired inventory')
 onReturn('delivery-selection',function()
  assert(r('InvSelected',9)==wanted,'Real controller selection committed')
  if wanted~=before then
   assert(shots()==0 and r('SsHeld')==0 and r('SsKick')==0 and r('SsFreeze')==0 and r('SsBodyStop')==0,'Immediate native selection cleanup')
   current.selections[#current.selections+1]={before=before,after=wanted,wall=wall}
   event('actual-acquired-selection',current.selections[#current.selections])
  end
 end)
end)
hook('InventorySpend',function()
 if not entered or not current or phase~='use'then return end
 local s=emu.getState();local item,cost=s['cpu.a'],s['cpu.y'];local before=r('InvAmmo',144+item)
 assert(item==current.item and item>=1 and item<=7,'Actual acquired weapon owns use debit')
 onReturn('delivery-spend',function()
  local after=r('InvAmmo',144+item);assert(before>=cost and after==before-cost,'Funded acquired source debit')
  current.spends[#current.spends+1]={item=item,before=before,cost=cost,after=after,wall=wall}
  event('actual-acquired-use-debit',current.spends[#current.spends]);capture('reward-'..index..'-actual-cost')
 end)
end)
hook('GameLoop',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then
  if r('GameEngineSubroutine')~=8 then return end
  assert(r('SelectedCharacter')==9 and r('RlVariant')==0 and r('CrossoverBehaviorVersion')==0,'Cold selected actual Bass/Easy0')
  assert(r('PlayerStatus')==0 and owned()==0 and r('InvStoredLo',9)==0 and r('InvStoredHi',9)==0,'No starting acquired outcomes')
  entered=true;phase='settle';age=0
 end
 updates=updates+1;age=age+1
 if phase=='settle'and age>=30 or phase=='next'then stage()
 elseif phase=='collect'and current.mature and age>=110 and not current.contactAligned then
  assert(r('Enemy_Flag',5)~=0 and r('Enemy_State',5)>=128,'Existing source actor fully risen before alignment')
  writeBoundary=true
  w('Enemy_X_Position',r('Player_X_Position'),5);w('Enemy_PageLoc',r('Player_PageLoc'),5);w('Enemy_Y_Position',184,5);w('Enemy_X_Speed',0,5);w('Enemy_Y_Speed',0,5)
  writeBoundary=false;current.contactAligned=wall
  event('explicit-post-rise-contact-alignment',{disclosure='Existing fully risen actor is aligned to the player at a native boundary. No new pickup, stamp, inventory, status or collection result is created.'})
 elseif phase=='use-setup'then
  assert(shots()==0,'No previous projectile overwritten by use arena')
  writeBoundary=true;arena(false)
  if current.item==1 then
   local col=(r('Player_X_Position')+18)//16;w('Block_Buffer_1',0x51,160+col);tile(0,col,12,0x51)
  end
  writeBoundary=false
  change('select');current.wanted=current.item==8 and 0 or current.item;current.selectionStart=#current.selections
 end
 assert(r('MmDeathFlag')==0,'Physical delivery scene survives')
end)
hook('finish',function()
 if not entered or done then return end
 if phase=='collect'then
  assert(age<650,'Bounded native reveal/rise/collection')
  for i=0,3 do if r('Block_State',i)~=0 then assert(r('Block_X_Position',i)==112,'Real head hit activates staged block');current.headObserved=true end end
  if r('Enemy_Flag',5)~=0 and r('Enemy_ID',5)==0x2e then
   assert(current.item~=nil and current.prepareCalls==1,'Reward created by actual native prepare owner')
   if not current.revealed then
    assert(current.headObserved and r('Enemy_X_Position',5)==112 and r('Enemy_PageLoc',5)==0,'Actual block owns revealed actor')
    current.revealed=wall;current.revealY=r('Enemy_Y_Position',5);capture('reward-'..index..'-reveal');event('actual-block-reveal',{item=current.item,y=current.revealY})
   end
   if not current.mature then
    assert(owned()==current.before and current.ownerCalls==0 and r('GuestPowerupActive')==0,'Under-block fixture never grants prematurely during rise')
    if r('Enemy_State',5)>=128 then
     assert(r('Enemy_Y_Position',5)<current.revealY,'Native vertical emergence')
     if current.item>0 then assert(current.riseCalls==48 and current.revealY-r('Enemy_Y_Position',5)==16,'Exact private48-active-update/16pixel rise')end
     current.mature=wall;event('actual-full-rise',{item=current.item,calls=current.riseCalls,y=r('Enemy_Y_Position',5)});capture('reward-'..index..'-mature')
    end
   end
  end
  if current.revealed and r('Enemy_Flag',5)==0 and r('GuestPowerupActive')==0 and r('TimerControl')==0 then
   assert(current.mature and current.contactAligned and current.ownerCalls==1,'Full rise then actual unique collection')
   assert(owned()==(current.before|(1<<current.item))and r('PlayerStatus')==1,'Exact physical ownership commit; no invented third power tier')
   assert(current.transformCalls==(current.item==0 and 60 or 0),'Only mushroom performs native60-update transform')
   assert(current.grantCalls==(current.item==0 and 0 or 1),'Exact native item grant count')
   if current.item>0 then assert(current.drawCalls>0,'World reward source icon admitted before collection');seen[current.item]=true end
   current.collected=wall;current.after=owned();capture('reward-'..index..'-collected');change('score-release')
  end
 elseif phase=='score-release'and age>=50 and r('FloateyNum_Control',5)==0 then change('use-setup')
 elseif phase=='select'then
  assert(age<180,'Bounded acquired selection')
  if r('InvSelected',9)==current.wanted and age>=8 and(current.item~=8 or #current.selections>current.selectionStart)then
   if current.item==8 then
    current.passiveSkipped=true;event('actual-passive-retained-not-selected',{owned=owned(),selected=r('InvSelected',9)});capture('reward-'..index..'-passive');change('complete-reward')
   else capture('reward-'..index..'-selected-HUD');change('use')end
  end
 elseif phase=='use'then
  assert(age<650,'Bounded actual acquired use/cleanup')
  local expected=C.use_types[current.item+1]
  for i=0,9 do if r('RgShotType',i)==expected then
   if not current.useObserved then current.useObserved=wall;event('actual-acquired-effect',{item=current.item,type=expected});capture('reward-'..index..'-effect')end
  end end
  if current.useObserved and age>=220 and shots()==0 and r('SsHeld')==0 and r('SsFreeze')==0 and r('SsBodyStop')==0 then
   assert(current.item==0 or #current.spends>0,'Acquired special actually uses source energy')
   current.naturalCleanup=wall;capture('reward-'..index..'-cleanup');change('return-default')
  end
 elseif phase=='return-default'then
  assert(age<180,'Bounded native return to buster')
  if r('InvSelected',9)==0 and age>=8 then change('complete-reward')end
 elseif phase=='complete-reward'then
  assert(current.item==8 and current.passiveSkipped or current.useObserved and current.naturalCleanup,'Every actual reward has its appropriate control assertion')
  current.complete=wall;event('physical-reward-completed',current);index=index+1
  if index>4 then assert(nmis>0 and minSP>=128,'Native NMI/stack exercised');done=true;phase='complete'else change('next')end
 end
end)
local function deliveryInput()
 if phase=='collect'then return{a=age>=10 and age<22}
 elseif phase=='select'then return{select=(current.item==8 or r('InvSelected',9)~=current.wanted)and age%12==0}
 elseif phase=='return-default'then return{select=r('InvSelected',9)~=0 and age%12==0}
 elseif phase=='use'then
  if current.item==5 then return{down=age>=5 and age<12,a=age>=5 and age<10}end
  return{b=age>=5 and age<12 or current.item==1 and age>=30 and age<35 or current.item==7 and age>=75 and age<80}
 end
 return{}
end
