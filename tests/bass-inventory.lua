-- Native question-block reveal -> emergence -> player pickup. No upgrade
-- flags are injected after the initial powered-Bass fixture.
local frame,age,stage=0,0,0
local mode='awards'
local seen={}
local revealed
local cycle=1
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
local function question()
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,415 do w('Block_Buffer_1',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 w('Block_Buffer_1',0xc1,10*16+7)
 for i=0,3 do w('Block_State',0,i);w('BlockMetasprite',0,i);w('MmBulletType',0,i)end
 for i=0,1 do w('Block_RepFlag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 w('BlockBounceTimer',0);w('RgCooldown',0);w('RgShootPose',0)
 w('InvSelected',0,9);w('InvDirty',1)
 w('Player_X_Position',32);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('Player_Y_Speed',0);w('PlayerFacingDir',1)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 revealed=nil
end
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140 or(mode=='pause'and((age>=25 and age<31)or(age>=45 and age<51))),
  left=mode=='pause'and age>=35 and age<41,
  start=frame==200 or(mode=='pause'and((age>=10 and age<16)or(age>=75 and age<81))),
  b=((mode=='awards' or mode=='mushroom' or mode=='restore')and age>=10 and age<16)
   or(mode=='cycle'and cycle<8 and cycle~=5 and age>=30 and age<36)
   or(mode=='hurt_lift'and age>=30 and age<36),
  a=mode=='cycle'and cycle==5 and age>=30 and age<36,
  select=((mode=='cycle'or mode=='hurt_lift')and age>=10 and age<16)
   or(mode=='pause'and age>=55 and age<61)},0)
 if mode=='cycle'and cycle==5 and age>=30 and age<36 then emu.setInput({down=true,a=true},0)end
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==4000 then assert(false,'Inventory watchdog: '..mode..' stage '..stage..' age '..age..' cycle '..cycle)end
 if frame<550 then return end
 age=age+1
 if frame==550 then
  assert(r('SelectedCharacter')==9,'Bass selected')
  assert(r('InvAmmo',145)==112 and r('InvAmmo',151)==112,'Every Bass weapon starts at its 112-unit maximum')
  w('PlayerStatus',1);w('InvOwnedLo',1,9);stage=1;age=0;question()
 end
 if mode=='awards' or mode=='mushroom' or mode=='restore'then
  for i=0,5 do
   if r('Enemy_Flag',i)~=0 and r('Enemy_ID',i)==0x2e then
    local id=r('InvPickup',i)
    if not revealed then
     revealed=id
     if mode=='awards' and stage<=8 then
      assert(id>=1 and id<=8 and not seen[id],'Native block reveals an available, not previously viewed upgrade: '..id)
      seen[id]=true
     elseif mode=='awards'then assert(id==254,'Exhausted inventory awards big weapon energy')
     elseif mode=='mushroom'then assert(id==0,'Damage makes the next block a mushroom')
     elseif mode=='restore'then assert(id==255,'Next flower holds the stored inventory snapshot')end
    end
    if age>=100 and r('Enemy_State',i)>=0x80 then
     w('Enemy_X_Position',r('Player_X_Position'),i);w('Enemy_PageLoc',0,i)
     w('Enemy_Y_Position',184,i);w('Enemy_X_Speed',0,i);w('Enemy_Y_Speed',0,i)
    end
   elseif r('Enemy_Flag',i)~=0 then w('Enemy_Flag',0,i)end
  end
  if age==180 then
   assert(revealed~=nil,'Real buster hit spawned a native powerup')
   if mode=='awards'then
    if stage<=8 then
     local lo=r('InvOwnedLo',9);local hi=r('InvOwnedHi',9)
     assert(((lo+256*hi)&(1<<revealed))~=0,'Collecting the revealed item grants its own ability')
    else assert(r('InvAmmo',146)==112,'Big energy restores forty units')end
    stage=stage+1;age=0
    if stage<=9 then
     if stage==9 then w('InvAmmo',72,146)end
     question()
    else
     assert(r('InvOwnedLo',9)==255 and r('InvOwnedHi',9)==1,'All seven weapons plus Energy Balancer can coexist')
     mode='cycle'
     w('Block_Buffer_1',0x51,160+3)
    end
   elseif mode=='mushroom'then
    assert(r('PlayerStatus')==1 and r('GuestPowerupActive')==0,'Mushroom completes its native powerup animation')
    mode='restore';age=0;question()
   else
    assert(r('InvOwnedLo',9)==255 and r('InvOwnedHi',9)==1,'Recovery flower restores every stored weapon')
    assert(r('InvStoredLo',9)==0 and r('InvStoredHi',9)==0,'Recovery clears the stored snapshot')
    print('PASS Bass native upgrade reveals, no repeats, seven weapon selections/attacks, source HUD, held-brick switching, paused selection/default, energy refill, damage cleanup and mushroom/flower recovery')
    emu.stop(0)
   end
  end
 elseif mode=='cycle'then
  if age==25 then
   assert(r('InvSelected',9)==cycle%8,'Select reaches acquired weapon '..cycle%8)
   assert(r('SsHeld')==0,'Changing weapon clears the held Super Arm brick')
   assert(r('SsFreeze')==0 and r('SsBodyStop')==0,'Changing weapon clears previous attack movement locks')
   if cycle<8 then
    assert(r('InvHudActive')==1,'Every selected weapon enables its source icon')
    assert(emu.read(0x2037,emu.memType.nesPpuDebug)==0x2a and emu.read(0x2058,emu.memType.nesPpuDebug)==0x2d,'Selected weapon has the complete four-tile icon')
    assert(emu.read(0x2023,emu.memType.nesPpuDebug)<0x24,'Weapon name uses NES text glyphs')
    assert(emu.read(0x204a,emu.memType.nesPpuDebug)==0x2f,'Weapon energy has a visible bar')
   else assert(r('InvHudActive')==0,'Default buster clears the special icon and bar')end
  end
  if age==45 then
   if cycle==1 then assert(r('SsHeld')>0,'Super Arm can lift a brick before switching away')
   elseif cycle<8 then
    local expected=({[2]=10,[3]=11,[4]=12,[5]=19,[6]=15,[7]=17})[cycle]
    local found=false
    for i=0,9 do local t=r('RgShotType',i);if t==expected or(cycle==6 and t==16)then found=true end end
    assert(found,'Selected weapon '..cycle..' fires its own projectile')
   end
   local f=assert(io.open(OUTPUT..ROM_NAME..'-bass-inventory-selected-'..(cycle%8)..'.png','wb'));f:write(emu.takeScreenshot());f:close()
  end
  if age~=65 then return end
  cycle=cycle+1;age=0
  if cycle<=8 then return end
  mode='pause';age=0
 elseif mode=='pause'then
  if age==20 then assert(r('GamePauseStatus')&1~=0,'Start pauses for weapon selection')end
  if age==33 then assert(r('InvSelected',9)==1,'Paused Right selects the next owned weapon')end
  if age==43 then assert(r('InvSelected',9)==0,'Paused Left selects the previous weapon')end
  if age==53 then assert(r('InvSelected',9)==1,'Paused Right works again after release')end
  if age==63 then assert(r('InvSelected',9)==0,'Paused Select immediately restores the default buster')end
  if age~=90 then return end
  assert(r('GamePauseStatus')&1==0,'Start resumes after selecting a weapon')
  mode='hurt_lift';age=0
  w('Player_X_Position',32);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_State',0)
  w('Block_Buffer_1',0x51,160+3)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 elseif mode=='hurt_lift'then
  if age~=55 then return end
  assert(r('InvSelected',9)==1 and r('SsHeld')>0,'Bass is carrying a real brick before enemy damage')
  mode='hurt';age=0
  w('InjuryTimer',0);w('StarInvincibleTimer',0)
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
  w('Enemy_X_Position',r('Player_X_Position')+5);w('Enemy_PageLoc',0);w('Enemy_Y_Position',176);w('Enemy_Y_HighPos',1)
 elseif mode=='hurt'then
  if age==30 then
   assert(r('PlayerStatus')==0,'Enemy collision removes mushroom')
   assert(r('InvOwnedLo',9)==0 and r('InvOwnedHi',9)==0,'Damage removes active upgrades')
   assert(r('InvStoredLo',9)==254 and r('InvStoredHi',9)==1,'Damage stores weapons and Energy Balancer')
   assert(r('SsHeld')==0 and r('InvSelected',9)==0,'Damage drops the active Super Arm state and returns to the buster')
   for i=0,9 do assert(r('RgShotType',i)==0,'Damage removes the actual carried projectile')end
  end
  if r('PlayerStatus')>0 then
   w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
   w('Enemy_X_Position',r('Player_X_Position')+5);w('Enemy_PageLoc',0)
   w('Enemy_Y_Position',176);w('Enemy_Y_HighPos',1)
  else for i=0,5 do w('Enemy_Flag',0,i)end end
  if age==150 then mode='mushroom';age=0;question()end
 end
end,emu.eventType.endFrame)
