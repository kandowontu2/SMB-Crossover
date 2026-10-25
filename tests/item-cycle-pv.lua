-- Actual Hard menus, then powered fixture + physical arm/metal pickup actors.
local C=assert(ITEM_CFG);local frame,entered,age=0,false,0
local phase='options-focus';local stage='one';local step='press';local sequence={}
local beforeAmmo;local fired=false;local lastPress
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function snap(name)local f=assert(io.open(TEST_DIR..name..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
local function menu()
 if frame<60 or frame%12~=0 then return{}end
 if phase=='options-focus'then phase='options-open';return{down=true}end
 if phase=='options-open'then phase='mode-focus';return{a=true}end
 if phase=='mode-focus'then
  if r('CrossoverMenuState')~=4 then return{}end
  if r('CrossoverOptionsFocus')~=1 then return{down=true}end
  if r('CrossoverBehaviorVersion')==0 then phase='back';return{a=true}end
  phase='back'
 end
 if phase=='back'then phase='start';return{b=true}end
 if phase=='start'then if r('CrossoverMenuState')==2 then phase='select'else return{start=true}end end
 if r('CrossoverMenuState')~=2 then return{}end
 local ix=r('CrossoverMenuIndex');if ix//6~=C.slot//6 then return{down=true}end
 if ix~=C.slot then return{right=true}end
 return{a=true}
end
local function pickup(id)
 w('Enemy_Flag',1,5);w('Enemy_ID',0x2e,5);w('Enemy_State',128,5)
 w('Enemy_X_Position',64,5);w('Enemy_PageLoc',0,5);w('Enemy_Y_Position',184,5);w('Enemy_Y_HighPos',1,5)
 w('InvPickupOwner',C.character,5);w('InvPickup',id,5);w('PowerUpType',1,5)
end
emu.addEventCallback(function()
 if not entered then emu.setInput(menu(),0);return end
 local b={}
 if stage=='cycle'then
  if step=='press'then
   b.select=true
   if r('InvSelected',C.character)~=lastPress then
    sequence[#sequence+1]=r('InvSelected',C.character);lastPress=sequence[#sequence];step='release';snap('selected-'..#sequence)
   end
  elseif (r('InvPrevious')&32)==0 then
   if #sequence==2 then stage='fire';beforeAmmo={};for i=0,191 do beforeAmmo[i]=r('InvAmmo',i)end
   elseif #sequence==3 then stage='normal';age=0
   else step='press'end
  end
 elseif stage=='fire'then b.b=not fired
 elseif stage=='normal'then b.b=age>=20 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if not entered and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
  assert(r('SelectedCharacter')==C.character and r('CrossoverBehaviorVersion')==1,'Actual requested Hard owner')
  entered=true;age=0
  for i=0,5 do w('Enemy_Flag',0,i)end
  for _,q in ipairs({{'Player_X_Position',64},{'Player_PageLoc',0},{'Player_Y_Position',176},{'Player_Y_HighPos',1},{'Player_State',0},{'PlayerFacingDir',1},{'PlayerStatus',1},{'TimerControl',0},{'MmDeathFlag',0},{'ScrollLock',1}})do w(q[1],q[2])end
  w('InvOwnedLo',C.mush_lo,C.character);w('InvOwnedHi',C.mush_hi,C.character)
  pickup(1)
 elseif entered then
  age=age+1
  if stage=='one'and r('Enemy_Flag',5)==0 then
   assert(r('InvOwnedLo',C.character)&2~=0,'Arm pickup physically grants item1');snap('arm-collected');stage='after-one'
  elseif stage=='after-one'and r('FloateyNum_Control',5)==0 then
   -- The native score popup retains this object's slot after pickup. Wait
   -- for that owner to release it before arranging the next mature actor.
   stage='two';pickup(2)
  elseif stage=='two'and r('Enemy_Flag',5)==0 then
   assert(r('InvOwnedLo',C.character)&6==6,'Both physical pickups remain owned: '..r('InvOwnedLo',C.character));snap('metal-collected')
   assert(r('InvSelected',C.character)==0,'Source retains normal buster until Select');lastPress=0;stage='cycle'
  elseif stage=='fire'then
   local now=r('InvAmmo',C.pool)
   if now~=beforeAmmo[C.pool]then
    assert(now==beforeAmmo[C.pool]-C.cost,'Real B press spends the selected Metal pool/cost')
    for i=0,191 do if i~=C.pool then assert(r('InvAmmo',i)==beforeAmmo[i],'Every other ammo pool remains intact')end end
    fired=true;stage='cycle';step='press';lastPress=2;snap('metal-fired')
   end
  elseif stage=='normal'and age>=40 then
   assert(fired and #sequence==3 and sequence[1]==1 and sequence[2]==2 and sequence[3]==0,'Select cycles arm/metal/normal')
   for i=0,191 do assert(r('InvAmmo',i)==beforeAmmo[i]-(i==C.pool and C.cost or 0),'Normal buster consumes no special ammunition')end
   local live=0
   for i=0,3 do if r('MmBulletType',i)~=0 then live=live+1 end end
   for i=0,9 do if r('RgShotType',i)~=0 then live=live+1 end end
   assert(live>0,'Normal B press produces a live projectile')
   snap('normal-buster');local f=assert(io.open(TEST_DIR..'result.json','w'));f:write('{"passed":true,"physical_item_actors":2,"initial_selection":0,"selection_sequence":[1,2,0],"correct_selected_ammo_pool":true,"normal_special_ammo_consumption":0}\n');f:close();emu.stop(0)
  end
 end
 assert(frame<1800,'Physical pickup/cycle/use component is bounded')
end,emu.eventType.endFrame)
