L.TnUpdateTick=0x5c7a;L.TnTickValid=0x5c7d;L.TnTickFrame=0x5c7c
-- Native TMNT equipment components. Cold real menus, then explicitly seeded
-- HP/food stage, targets/counter/RNG arenas. Equipment is granted ONLY by real
-- physical actor collision. This is not an untouched campaign/25-kill proof.
local finishObserver=dofile(assert(TMNT_CFG.observer));local C=assert(TMNT_CFG);local f=0;local phase=C.mode=='hard'and'options-focus'or'start';local entry=nil;local age=0
local collectPhase='left';local stage='approach';local clock=0;local revealed=false;local full=false;local scrollCollected=false;local shown=false;local drops={};local targetKind=0;local kill=false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function k(a)return emu.read(a,emu.memType.nesDebug)end
local function put(a,v)emu.write(a,v%256,emu.memType.nesDebug)end
local function screen(n)local h=assert(io.open(TEST_DIR..n..'.png','wb'));h:write(emu.takeScreenshot());h:close()end
local function bank(a)return emu.convertAddress(a).address//8192 end
local csv=assert(io.open(TEST_DIR..'native.csv','w'));csv:write('frame,age,stage,x,y,hp,food,gear,ammo,selected,throw,seq,shot0,shot1,shot2,drop0,drop1,drop2,drop3,scroll5,state5\n')
local oam=assert(io.open(TEST_DIR..'oam.bin','wb'));local pals=assert(io.open(TEST_DIR..'palettes.bin','wb'));local meta=assert(io.open(TEST_DIR..'hardware.csv','w'));meta:write('frame,stage,chr4,first,rotation,bodyPose,face\n')
local function snapshot()
 local bytes={};for i=0,255 do bytes[#bytes+1]=string.char(emu.read(i,emu.memType.nesSpriteRam))end;oam:write(table.concat(bytes));bytes={};for i=0,31 do bytes[#bytes+1]=string.char(emu.read(0x3f00+i,emu.memType.nesPpuDebug))end;pals:write(table.concat(bytes));local st=emu.getState();meta:write(table.concat({f,stage,st['mapper.chrBanks4'],r('RgOamFirst'),r('RgOamRotation'),r('TnPose'),r('PlayerFacingDir')},',')..'\n')
end
local function menu()
 if f<60 or f%12~=0 then return{}end
 if phase=='options-focus'then phase='options-open';return{down=true}end
 if phase=='options-open'then phase='mode-focus';return{a=true}end
 if phase=='mode-focus'then
  if r('CrossoverMenuState')~=4 then return{}end
  if r('CrossoverOptionsFocus')~=1 then return{down=true}end
  phase='mode-set'
 end
 if phase=='mode-set'then if r('CrossoverBehaviorVersion')==0 then return{a=true}end;phase='back';return{}end
 if phase=='back'then phase='start';return{b=true}end
 if phase=='start'then if r('CrossoverMenuState')==2 then phase='select'else return{start=true}end end
 if r('CrossoverMenuState')~=2 then return{}end
 local ix=r('CrossoverMenuIndex');local row=ix<12 and ix//6 or 2
 if row~=2 then return{down=true}end
 if ix~=18 then return{right=true}end
 if r('TnVariant')~=C.variant then return{select=true}end
 return{a=true}
end

local function arena()
 for a=0x5c00,0x5cff do put(a,0)end
 put(0x5c70,0x80);put(0x5c74,6);put(0x5c76,9);put(0x5c07,8);put(0x5c0b,0xff);put(0x5c10,120)
 w('TnHealth',128,C.variant);w('TnEquipment',0,C.variant);w('TnAmmo',0,C.variant)
 w('Player_X_Position',80);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('PlayerFacingDir',1);w('InjuryTimer',0);w('TimerControl',0)
 -- Keep the camera near initial ground so the component doesn't meet route pipes.
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 for i=0,5 do w('Enemy_Flag',0,i)end
end
emu.addMemoryCallback(function()
 if entry and targetKind>0 and bank(L.TnEnemyDropDispatch)==B.TnEnemyDropDispatch then
  w('TnDropCounter',24);w('PseudoRandomBitReg',targetKind==1 and 0 or targetKind==2 and 4 or 6,1);kill=true
 end
end,emu.callbackType.exec,L.TnEnemyDropDispatch)
emu.addMemoryCallback(function()
 if entry and bank(L.TnPreparePickupDispatch)==B.TnPreparePickupDispatch then revealed=true end
end,emu.callbackType.exec,L.TnPreparePickupDispatch)
local calls=assert(io.open(TEST_DIR..'calls.csv','w'));calls:write('frame,fn,bank,expected,tick,valid,cached,framecounter,timer,engine,death,dropTimer,x,y,px,py\n')
for _,n in ipairs({'TnAllWeapons','TnUpdateDrops','TnDropOverlap','TnGiveEquipment'})do emu.addMemoryCallback(function()
 if entry and stage=='drop-collect'and bank(L[n])==B[n]then calls:write(table.concat({f,n,bank(L[n]),B[n],r('TnUpdateTick'),r('TnTickValid'),r('TnTickFrame'),r('FrameCounter'),r('TimerControl'),r('GameEngineSubroutine'),r('MmDeathFlag'),r('TnDropTimer',3),r('TnDropX',3),r('TnDropY',3),r('Player_X_Position'),r('Player_Y_Position')},',')..'\n');calls:flush()end
end,emu.callbackType.exec,L[n])end
emu.addEventCallback(function()
 local b={}
 if not entry then b=menu()
 elseif stage=='approach'then b.right=true;b.b=age%32==0
 elseif stage=='bump'then b.a=f-clock>=16 and f-clock<45
 elseif stage=='rise'then
 elseif stage=='collect'then
  local ix=r('Enemy_X_Position',5)+256*r('Enemy_PageLoc',5);local x=r('Player_X_Position')+256*r('Player_PageLoc');local t=f-clock
  if collectPhase=='left'then b.left=x>300;if x<=300 then collectPhase='jump';clock=f end
  else local a=f-clock;b.a=a<38;b.right=a>=12 and x<ix+4;if a>95 then collectPhase='left'end end
 elseif stage=='scroll-use'then b.b=(f-clock)%28==0;b.left=(f-clock)>=32 and(f-clock)<36
 elseif stage=='drop-kill'then b.b=(f-clock)%32==0
 elseif stage=='drop-collect'then
  for i=0,3 do if r('TnDropKind',i)>0 then local dx=r('TnDropX',i)+256*r('TnDropPage',i)-(r('Player_X_Position')+256*r('Player_PageLoc')+8);b.right=dx>2;b.left=dx< -2 end end
 elseif stage=='gear-use'then
  local t=f-clock;b.select=(t>=18 and t<22)or(t>=30 and t<34);b.b=t==6 or t==44 or t==76;b.down=t>=72 and t<95;b.left=t>=38 and t<42
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 f=f+1
 if not entry and r('SelectedCharacter')==19 and r('GameEngineSubroutine')==8 and r('OperMode')==1 and r('OperMode_Task')==3 then
  assert(r('TnVariant')==C.variant and r('CrossoverBehaviorVersion')==(C.mode=='hard'and 1 or 0),'cold identity/mode');entry=f
  w('TnFood',1);w('TnHealth',128,C.variant)
 end
 if entry then
  if f%12==0 and stage=='collect'then screen('collect-'..f)end
  age=f-entry
  local x=r('Player_X_Position')+256*r('Player_PageLoc')
  if stage=='approach'and x>=332 then stage='bump';clock=f;w('TnHealth',128,C.variant);w('TnFood',1)end
  if stage=='bump'and revealed then
   assert(r('TnEquipment',C.variant)==0,'not automatically granted at reveal');stage='rise';clock=f;screen('scroll-reveal')
  end
  if stage=='rise'then
   assert(r('TnEquipment',C.variant)==0,'no automatic rising pickup')
   if r('TnPickupStamp',5)==4 and r('Enemy_State',5)>=128 then full=true;stage='collect';clock=f;screen('scroll-emerged')end
  end
  if stage=='collect'and r('TnEquipment',C.variant)==4 then
   assert(full and r('TnAmmo',C.variant)==20,'physical full-health scroll20');scrollCollected=true;stage='scroll-use';clock=f;screen('scroll-collected')
  end
  if stage=='scroll-use'and f-clock==70 then
   assert(r('TnAmmo',C.variant)<20,'actual scroll B fire');screen('scroll-used');targetKind=1;arena();stage='drop-kill';clock=f
  end
  if stage=='drop-kill'then
   if f-clock==2 then
    -- A real source primary hits a weak explicit component target.
    w('Enemy_Flag',1,0);w('Enemy_ID',0,0);w('Enemy_State',0,0);w('Enemy_BoundBoxCtrl',9,0);w('Enemy_X_Position',100,0);w('Enemy_PageLoc',0,0);w('Enemy_Y_Position',176,0);w('Enemy_Y_HighPos',1,0);w('Enemy_X_Speed',0,0);w('Enemy_MovingDir',2,0)
    put(0x5c38,0);put(0x5c30,1)
   end
   for i=0,3 do if r('TnDropKind',i)==targetKind then
    assert(kill,'real native primary defeat/drop hook');screen('drop-'..targetKind..'-spawned');stage='drop-collect';clock=f;break
   end end
  end
  if stage=='drop-collect'and r('TnEquipment',C.variant)==targetKind then
   assert(r('TnAmmo',C.variant)==20 and r('TnGearSelected')==1,'physical drop grants20');drops[#drops+1]=targetKind;stage='gear-wait';clock=f;screen('drop-'..targetKind..'-collected')
  end
  if stage=='gear-wait'and r('TnAttack')==0 and r('TnThrow')==0 then stage='gear-use';clock=f end
  if stage=='gear-use'then
   local t=f-clock
   if t==12 then assert(r('TnAmmo',C.variant)==19,'one ammo per volley');screen('gear-'..targetKind..'-fired')end
   if t==24 then assert(r('TnGearSelected')==0,'Select returns primary')end
   if t==36 then assert(r('TnGearSelected')==1,'Select returns secondary')end
   if t==84 then screen('gear-'..targetKind..'-crouch')end
   if t==115 then
    if targetKind<3 then targetKind=targetKind+1;kill=false;arena();stage='drop-kill';clock=f
    else
     assert(scrollCollected and #drops==3,'all physically collected gear');csv:close();oam:close();pals:close();meta:close();local h=assert(io.open(TEST_DIR..'result.json','w'));h:write(string.format('{"passed":true,"variant":%d,"mode":"%s","frames":%d,"scroll_physical":true,"enemy_drop_kinds_collected":3,"seeded_component_arena":true,"campaign_clear":false}',C.variant,C.mode,f));h:close();finishObserver();print('PASS native physical TMNT gear');emu.stop(0);return
    end
   end
  end
  csv:write(table.concat({f,age,stage,x,r('Player_Y_Position'),r('TnHealth',C.variant),r('TnFood'),r('TnEquipment',C.variant),r('TnAmmo',C.variant),r('TnGearSelected'),r('TnThrow'),r('TnSeq'),r('TnShotKind',0),r('TnShotKind',1),r('TnShotKind',2),r('TnDropKind',0),r('TnDropKind',1),r('TnDropKind',2),r('TnDropKind',3),r('TnPickupStamp',5),r('Enemy_State',5)},',')..'\n');csv:flush();snapshot()
 end
 assert(f<2600,'component timeout stage='..stage..' x='..tostring(r('Player_X_Position')+256*r('Player_PageLoc')))
end,emu.eventType.endFrame)
