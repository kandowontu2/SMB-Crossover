-- Actual cold menus and native head-bump/rise/collect/expiry arenas.
-- Scene/health seeds and mature-actor positioning are declared by C.
local C=assert(HEALTH_CFG)
local frame,entered,boot,stage,age=0,false,0,1,0
local revealed,mature,receipt,collected,expiry,starHit=nil,nil,nil,nil,nil,false
local beforeHealth,beforeLife,beforeFood=0,0,0
local records={};local sound={};local actorSlot=nil;local targetBorn=false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function rom(n,i)return emu.read(assert(B[n],n)*8192+assert(L[n],n)%8192+(i or 0),emu.memType.nesPrgRom)end
local function tile(page,col,row,id)
 local function p(a,v)emu.write(a,v,emu.memType.nesPpuDebug)end
 local a=0x2000+page*0x400+row*64+col*2
 p(a,rom('MTileTopLeft',id));p(a+1,rom('MTileTopRight',id));p(a+32,rom('MTileBotLeft',id));p(a+33,rom('MTileBotRight',id))
 a=0x23c0+page*0x400+(row//2)*8+col//2;local shift=row%2*4+col%2*2
 p(a,(emu.read(a,emu.memType.nesPpuDebug)&(~(3<<shift)))|((rom('MTileAttribute',id)>>6)<<shift))
end
local menuPhase=C.hard and'options-focus'or'start'
local function menu()
 if frame<60 or frame%12~=0 then return{}end
 if menuPhase=='options-focus'then menuPhase='options-open';return{down=true}end
 if menuPhase=='options-open'then menuPhase='mode-focus';return{a=true}end
 if menuPhase=='mode-focus'then
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
 if r(C.variantName)~=C.variant then return{select=true}end
 return{a=true}
end
local function arena()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for i=0,5 do assert(r('FloateyNum_Control',i)==0,'Prior popup released');w('Enemy_Flag',0,i);w('Enemy_CollisionBits',0,i)end
 for p=0,1 do
  for row=2,14 do for col=0,15 do tile(p,col,row,row>=13 and 0x54 or 0)end end
  for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col);w('Block_Buffer_1',0x54,p*208+192+col)end
 end
 local step=C.steps[stage];w('Block_Buffer_1',step.block or 0xc1,135);tile(0,7,10,step.block or 0xc1)
 for i=0,3 do w('Block_State',0,i);w('BlockMetasprite',0,i)end
 for i=0,1 do w('Block_RepFlag',0,i);w('MmXFraction',0,i);w('MmYFraction',0,i)end
 for _,n in ipairs({'BlockBounceTimer','RgCooldown','RgShootPose','SmBall','SmCrouch','SmFlip','MmSliding','Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','ScrollThirtyTwo','AreaParserTaskNum','InjuryTimer','StarInvincibleTimer','GamePauseStatus'})do w(n,0)end
 w('ScrollLock',1);w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_X_Position',112);w('Player_PageLoc',0);w('MmOldX',112);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1);w('TimerControl',0);w('GameEngineSubroutine',8)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for _,seed in ipairs(step.seed or{})do w(seed[1],seed[2])end
 beforeHealth=r(C.health);beforeLife=r('NumberofLives');beforeFood=C.food and r(C.food)or -1
 revealed=nil;mature=nil;receipt=nil;collected=nil;expiry=nil;starHit=false;targetBorn=false;actorSlot=nil;sound={}
 records[stage]={kind=step.kind,beforeHealth=beforeHealth,beforeLife=beforeLife,seededSceneStatus=step.sceneStatus or false}
end
local function collectHook(name,health)
 emu.addMemoryCallback(function()
  if not entered or boot<30 or emu.convertAddress(L[name]).address//8192~=B[name]then return end
  local s=emu.getState();local x=s['cpu.x'];local step=C.steps[stage]
  if x>=6 or r('Enemy_Flag',x)==0 or r('Enemy_ID',x)~=0x2e then return end
  if(health and step.kind>=2)or(not health and step.kind<2)then return end
  assert(r('PowerUpType',x)==step.kind,'Native collection retains revealed food kind')
  assert(mature and r('Enemy_State',x)>=128,'Only fully emerged native actor is collected')
  assert(not receipt,'Native actor has one collection receipt')
  receipt=frame;records[stage].receipt=frame
 end,emu.callbackType.exec,assert(L[name],name))
end
collectHook(C.collectHook,true);collectHook('MarioSourcePowerupCollision',false)
emu.addMemoryCallback(function(_,v)
 if not entered or not receipt or frame>receipt+4 then return end
 if(v&32)~=0 or(v&64)~=0 then sound.grab=true end
end,emu.callbackType.write,L.Square2SoundQueue)
emu.addEventCallback(function()
 if not entered then emu.setInput(menu(),0);return end
 emu.setInput({a=boot>=30 and age>=10 and age<30},0)
end,emu.eventType.inputPolled)
local function done()
 local f=assert(io.open(OUTPUT..'health-result.json','w'));f:write('{"passed":true,"items":[')
 for i,v in ipairs(records)do
  if i>1 then f:write(',')end
  f:write('{"kind":'..v.kind..',"beforeHealth":'..v.beforeHealth..',"reveal":'..v.reveal..',"mature":'..v.mature..',"receipt":'..v.receipt..',"afterHealth":'..v.afterHealth..',"afterLife":'..v.afterLife..',"expiry":'..tostring(v.expiry or -1)..',"starDefeatedEnemy":'..tostring(v.starHit or false)..'}')
 end
 f:write(']}\n');f:close();print('PASS '..C.name..' real food/health cap/star/1up progression');emu.stop(0)
end
emu.addEventCallback(function()
 frame=frame+1;assert(frame<9000,'Health fixture deadline stage '..stage..' age '..age)
 if not entered then
  if r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
   assert(r('SelectedCharacter')==C.character and r(C.variantName)==C.variant and r('CrossoverBehaviorVersion')==(C.hard and 1 or 0),'Actual cold identity/mode selected');entered=true
  end
  return
 end
 boot=boot+1;if boot<30 then return end
 if boot==30 then w(C.health,C.initialHealth);age=0;arena()else age=age+1 end
 HEALTH_CASE=stage;HEALTH_AGE=age;local step=C.steps[stage]
 for i=0,3 do if r('Block_State',i)~=0 then assert(r('Block_X_Position',i)==112,'Head-bumped block keeps exact world column')end end
 if age<140 then assert(r('Player_X_Position')==112 and r('Player_PageLoc')==0,'Head bump preserves player X')end
 if C.variantName=='KbVariant'and C.variant==1 then assert(r('KbFloat')==0 and r('KbCopy')==0 and r('KbMouth')==0,'Meta food never grants flight or copied equipment')end
 for i=0,5 do if r('Enemy_Flag',i)~=0 and r('Enemy_ID',i)==0x2e then
  assert(r('PowerUpType',i)==step.kind,'Actual head block reveals expected ordinary food type stage '..stage..' got '..r('PowerUpType',i))
  if not revealed then revealed=frame;actorSlot=i;records[stage].reveal=frame end
  if r('Enemy_State',i)<128 then assert(r(C.health)==beforeHealth and r('NumberofLives')==beforeLife and r('StarInvincibleTimer')==0,'Rising food grants no health/life/invincibility')
  elseif not mature then mature=frame;records[stage].mature=frame end
  if age>=110 and mature then w('Enemy_X_Position',112,i);w('Enemy_PageLoc',0,i);w('Enemy_Y_Position',184,i);w('Enemy_X_Speed',0,i);w('Enemy_Y_Speed',0,i)end
 end end
 if receipt and not collected then
  local expected=step.kind<2 and step.health or beforeHealth
  local life=beforeLife+(step.kind==3 and 1 or 0)
  if r(C.health)==expected and r('NumberofLives')==life and(step.kind~=2 or r('StarInvincibleTimer')>0)then
   assert(revealed and mature and frame>=receipt,'Outcome follows mature physical collection');collected=frame;records[stage].afterHealth=r(C.health);records[stage].afterLife=r('NumberofLives')
   if step.kind<2 then assert(sound.grab,'Healing/cap collection has powerup SFX');if C.food then assert(r(C.food)==1-beforeFood,'Native food art alternates independently of HP')end end
  end
 end
 if collected and step.kind==2 then
  if not targetBorn and frame>=collected+6 then
   targetBorn=true
   for _,v in ipairs({{'Enemy_Flag',1},{'Enemy_ID',6},{'Enemy_State',0},{'Enemy_BoundBoxCtrl',9},{'Enemy_X_Position',112},{'Enemy_PageLoc',0},{'Enemy_Y_Position',184},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_MovingDir',2},{'Enemy_CollisionBits',0}})do w(v[1],v[2])end
  end
  if targetBorn and(r('Enemy_Flag')==0 or(r('Enemy_State')&32)~=0)then starHit=true end
  assert(r(C.health)==beforeHealth,'Star contact preserves native health')
  if r('StarInvincibleTimer')==0 then assert(starHit,'Actual star contact defeats enemy');expiry=frame;records[stage].expiry=frame;records[stage].starHit=true end
 end
 if collected and age>=250 and(step.kind~=2 or expiry)then
  if r('FloateyNum_Control',actorSlot or 5)~=0 then return end
  stage=stage+1;if stage>#C.steps then done();return end
  age=0;arena()
 end
end,emu.eventType.endFrame)
