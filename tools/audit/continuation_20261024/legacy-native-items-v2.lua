-- Explicit mature-item arena at a guarded native GameLoop entry. Ownership,
-- collection, transformation, controls and weapon use execute ordinary ROM code.
-- This fixture does not claim random block delivery or full emergence coverage.
local C=assert(LEGACY_ITEMS);local H=assert(LEGACY_HOOKS)
local frame,entered,case,age=0,false,1,0
local stage='boot';local pending=false;local records={};local before=0
local audioWrites=0;local sawAttack=false;local attackAge=0;local writeBoundary=false
local menuPhase=C.hard and 'focus' or 'start'
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)assert(writeBoundary,'All fixture state writes occur at native loop entry');emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function hook(h,f)emu.addMemoryCallback(function()
 local p=emu.convertAddress(h.address);if not p or p.address//8192~=h.physical_bank then return end
 for i,b in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==b,'Actual native instruction bytes')end
 f()
end,emu.callbackType.exec,h.address)end
local function snap(n)local f=assert(io.open(OUTPUT..n..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
local function owned()return r('InvOwnedLo',C.character)+256*r('InvOwnedHi',C.character)end
local function menu()
 if frame<90 or frame%12~=0 then return{}end
 if menuPhase=='focus'then menuPhase='open';return{down=true}end
 if menuPhase=='open'then menuPhase='mode';return{a=true}end
 if menuPhase=='mode'then
  if r('CrossoverMenuState')~=4 then return{}end
  if r('CrossoverOptionsFocus')~=1 then return{down=true}end
  if r('CrossoverBehaviorVersion')==0 then menuPhase='back';return{a=true}end
  menuPhase='back'
 end
 if menuPhase=='back'then menuPhase='start';return{b=true}end
 if menuPhase=='start'then if r('CrossoverMenuState')==2 then menuPhase='select'else return{start=true}end end
 if r('CrossoverMenuState')~=2 then return{}end
 local i=r('CrossoverMenuIndex');local row=i<12 and i//6 or 2;local target=C.slot<12 and C.slot//6 or 2
 if row~=target then return{down=true}end
 if i~=C.slot then return{right=true}end
 if C.variantSymbol and r(C.variantSymbol)~=C.variant then return{select=true}end
 return{a=true}
end
local function arena()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do for col=0,15 do for row=11,12 do w('Block_Buffer_1',0x54,p*208+row*16+col)end end end
 for i=0,5 do assert(r('FloateyNum_Control',i)==0,'Previous score actor released');w('Enemy_Flag',0,i);w('Enemy_CollisionBits',0,i)end
 for i=0,3 do w('Block_State',0,i);w('BlockMetasprite',0,i);w('MmBulletType',0,i)end
 for i=0,1 do w('Block_RepFlag',0,i);w('MmXFraction',0,i);w('MmYFraction',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i);w('SmShotType',0,i);w('SmBombAge',0,i)end
 for _,n in ipairs({'BlockBounceTimer','RgCooldown','RgShootPose','RgAttack','SmBall','SmCrouch','SmFlip','MmSliding','Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','ScrollThirtyTwo','AreaParserTaskNum','InjuryTimer','StarInvincibleTimer','AvStopwatch','SsFreeze','SsBodyStop','SsHeld','SsWaterExpand'})do w(n,0)end
 w('ScrollLock',1);w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_X_Position',64);w('Player_PageLoc',0);w('MmOldX',64);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1);w('TimerControl',0)
end
local function pickup()
 local s=C.steps[case];arena();before=owned()
 -- A fully emerged native actor is arranged ahead of the player. Input
 -- movement and the game's native collision perform the actual collection.
 for _,v in ipairs({{'Enemy_Flag',1},{'Enemy_ID',0x2e},{'Enemy_State',128},{'Enemy_X_Position',88},{'Enemy_PageLoc',0},{'Enemy_Y_Position',184},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_MovingDir',1},{'PowerUpType',s.type},{'InvPickupOwner',C.character},{'InvPickup',s.id}})do w(v[1],v[2],5)end
 records[case]={id=s.id,powerupType=s.type,staged=frame,before=before,attackRequired=s.attack~=nil}
 stage='collect';age=0;sawAttack=false;attackAge=0
end
hook(H.entry,function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 or r('GameEngineSubroutine')~=8 then return end
 if not entered then
  assert(r('SelectedCharacter')==C.character and r('CrossoverBehaviorVersion')==(C.hard and 1 or 0),'Actual cold selected owner/mode')
  if C.variantSymbol then assert(r(C.variantSymbol)==C.variant,'Actual selected alternate')end
  entered=true;stage='settle';age=0
 end
 age=age+1
 if stage=='settle'and age==30 then pending=true end
 if pending then writeBoundary=true;pickup();writeBoundary=false;pending=false end
 if stage=='attack-setup'then
  writeBoundary=true;arena()
  local s=C.steps[case]
  if s.arm then w('Block_Buffer_1',0x51,160+5)end
  writeBoundary=false;stage='attack';attackAge=0;age=0
 end
end)
hook(H.finish,function()
 if not entered or stage=='settle'then return end
 assert(r('MmDeathFlag')==0,'Item/attack scene survives')
 local s=C.steps[case]
 if stage=='collect'then
  if r('Enemy_Flag',5)==0 then
   local after=owned();local mask=1<<s.id
   assert(after&mask~=0,'Physical item grants requested ownership '..s.id)
   local expected=before
   if s.id==0 then expected=before|C.mushroomMask else expected=(before&(~s.exclusive))|mask end
   assert(after==expected,'Physical item preserves exact ownership/exclusivity '..s.id..' actual '..after..' expected '..expected)
   if r('GuestPowerupActive')==0 and r('TimerControl')==0 then
    assert(r('PlayerStatus')>0,'Completed native mushroom animation leaves powered character')
    records[case].collected=frame;records[case].after=after;records[case].audioWrites=audioWrites;snap('collected-'..s.id)
    stage='wait';age=0
   end
  end
  assert(age<600,'Native physical pickup/transform bounded id '..s.id..' x '..r('Player_X_Position')..' item '..r('Enemy_X_Position',5)..' status '..r('PlayerStatus'))
 elseif stage=='wait'and age>=50 and r('FloateyNum_Control',5)==0 then
  if s.attack then stage='choose';age=0 else stage='next'end
 elseif stage=='choose'then
  if not s.selectable or r('InvSelected',C.character)==s.id then stage='attack-setup';age=0 end
  assert(age<300,'Controller selection bounded item '..s.id)
 elseif stage=='attack'then
  attackAge=attackAge+1
  if s.arm and r('SsHeld')>0 then sawAttack=true end
  if s.watch and r('AvStopwatch')>100 then sawAttack=true end
  if s.slash and r('AvSlash')~=0 then sawAttack=true end
  if s.attack>0 then for i=0,9 do if r('RgShotType',i)==s.attack or r('RgShotType',i)==s.alternate then sawAttack=true end end end
  if s.samusBomb then for i=0,2 do if r('SmShotType',i)==3 then sawAttack=true end end end
  if attackAge>=55 then assert(sawAttack,'Acquired source attack observed item '..s.id..' type '..s.attack);records[case].attackObserved=true;snap('used-'..s.id);stage='next'end
 elseif stage=='next'then
  if r('FloateyNum_Control',5)==0 then case=case+1;if case>#C.steps then
   local f=assert(io.open(OUTPUT..'native-legacy-items.json','w'));f:write('{"passed":true,"native_entry_staging":true,"items":[')
   for i,z in ipairs(records)do if i>1 then f:write(',')end;f:write(string.format('{"id":%d,"staged":%d,"collected":%d,"before":%d,"after":%d,"attackRequired":%s,"attackObserved":%s}',z.id,z.staged,z.collected,z.before,z.after,tostring(z.attackRequired),tostring(z.attackObserved or false)))end
   f:write(']}');f:close();print('PASS '..C.name..' native mature pickups and declared controller attacks');emu.stop(0)
  else pending=true end end
 end
end)
emu.addEventCallback(function()
 if not entered then emu.setInput(menu(),0);return end
 local b={};local s=C.steps[case]
 if stage=='collect'then b.right=true
 elseif stage=='choose'then b.select=s.selectable and r('InvSelected',C.character)~=s.id and frame%12<6
 elseif stage=='attack'then
  if s.button=='special'then b.select=attackAge>=5 and attackAge<9 else b.b=attackAge>=5 and attackAge<9 end
  if s.kick then b.b=false;b.down=attackAge>=4 and attackAge<10;b.a=attackAge>=5 and attackAge<9 end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()if entered then audioWrites=audioWrites+1 end end,emu.callbackType.write,0x4000,0x4017)
emu.addEventCallback(function()frame=frame+1;assert(frame<15000,'Bounded all-item scene '..stage..' case '..case..' age '..age)end,emu.eventType.endFrame)
