-- Real front end and physical native pickups in explicitly authored arenas.
local wall,t,entered=0,0,false
local pending={};local itemSeen={};local taken={};local initialLives
local rewardNames={'mushroom','flower','star','one-up'}
local tiles={0xc1,0xc1,0x57,0x59}
local dropCases={{1,0,2},{2,0,10},{1,128,2},{2,128,10}}
local dropIndex;local dropMade=false;local dropSeen=false;local dropCollected=false
local soundEvents={};local lastStar=0;local starExpired=false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)pending[#pending+1]={assert(L[n],n)+(i or 0),v&255}end
local function bank(a)return emu.convertAddress(a).address//8192 end
local function shot(n)local f=assert(io.open(OUTPUT..n..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
local menu=dofile(ROLL_MENU_PATH or TEST_DIR..'roll-menu.lua')(r,ROLL_HARD or false,ROLL_OUTLINES or false)
emu.addMemoryCallback(function()
 if not entered or bank(0xa000)~=B.RlFrameReady then return end
 for _,p in ipairs(pending)do emu.write(p[1],p[2],emu.memType.nesDebug)end
 pending={}
end,emu.callbackType.exec,L.RlFrameReady)
emu.addMemoryCallback(function()
 if not entered or not dropIndex or bank(0xa000)~=B.InventoryEnemyDrop then return end
 -- Fix only random choices; the controller must defeat the actual enemy and
 -- the native drop routine must allocate and animate the collectible.
 local c=dropCases[dropIndex]
 emu.write(L.PseudoRandomBitReg+1,0,emu.memType.nesDebug)
 emu.write(L.PseudoRandomBitReg+2,c[1]==1 and 0 or 255,emu.memType.nesDebug)
 emu.write(L.PseudoRandomBitReg+3,c[2]==0 and 0 or 1,emu.memType.nesDebug)
 dropMade=true
end,emu.callbackType.exec,L.InventoryEnemyDrop)
for _,name in ipairs({'Square1SoundQueue','Square2SoundQueue','NoiseSoundQueue'})do
 emu.addMemoryCallback(function(a,v)
  if entered and v~=0 then soundEvents[#soundEvents+1]={t=t,address=a,value=v}end
 end,emu.callbackType.write,L[name])
end
local function arena()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for i=176,207 do w('Block_Buffer_1',0x54,i);w('Block_Buffer_1',0x54,208+i)end
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i);w('Enemy_CollisionBits',0,i);w('MmEnemyHealthLo',0,i);w('MmEnemyHealthHi',0,i);w('MmEnemyFlash',0,i)end
 for i=0,3 do w('MmBulletType',0,i);w('InvDropKind',0,i)end
 for _,n in ipairs({'TimerControl','GamePauseStatus','InjuryTimer','GuestHurtTicks','GuestHurtKind','MmDeathFlag','AreaParserTaskNum','ScrollThirtyTwo','EnemyFrenzyBuffer','EnemyFrenzyQueue','BlockBounceTimer','RlPrevious','RlCharge','RlHurt','RlInvul','Player_X_Speed','Player_Y_Speed','MmUnderwater','SmBall'})do w(n,0)end
 w('ScrollLock',1);w('CheatInvincible',0);w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_X_Position',72);w('Player_PageLoc',0);w('Player_Y_Position',112);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('GameEngineSubroutine',8);w('OperMode',1);w('RlHealth',12);w('RlEnergy',8)
end
local function pickup()
 for i=0,5 do
  if r('Enemy_Flag',i)~=0 and r('Enemy_ID',i)==0x2e then return i end
 end
end
local function positionAtItem(i)
 w('Player_X_Position',r('Enemy_X_Position',i));w('Player_PageLoc',r('Enemy_PageLoc',i))
 w('Player_Y_Position',r('Enemy_Y_Position',i)-8)
 w('Enemy_CollisionBits',0,i)
end
emu.addEventCallback(function()
 local b={}
 if not entered then
  b=menu(wall)
 elseif t<=800 then local a=(t-1)%200;b.b=a>=10 and a<13
 elseif t<=1440 then local a=(t-801)%160;b.b=a>=10 and a<80 and a%12<2 end
 if entered and t>=1440 then b.b=(t>=1460 and t<1463)or(t>=1485 and t<1488)or(t>=1555 and t<1650)end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1
 if not entered then
  if r('OperMode')==1 and r('GameEngineSubroutine')==8 then entered=true;initialLives=r('NumberofLives')end
  assert(wall<1100,'Roll rewards cold entry');return
 end
 t=t+1
 if lastStar>0 and r('StarInvincibleTimer')==0 then starExpired=true end
 assert(r('MmDeathFlag')==0,'Reward arena remains playable')
 if t<=800 then
  local index=(t-1)//200+1;local a=(t-1)%200;local i=pickup()
  if a==0 then arena();w('Block_Buffer_1',0x54,116);w('Block_Buffer_1',0x54,117);w('Block_Buffer_1',tiles[index],103)end
  if i then itemSeen[index]=true;assert(r('PowerUpType',i)==index-1,'Native block produces '..rewardNames[index])end
  if a==90 then assert(itemSeen[index] and i,'Reward physically emerges before collection');shot(rewardNames[index]..'-emerging')end
  if a==100 then assert(i and r('Enemy_State',i)>=128,'Reward finishes native emergence');positionAtItem(i)end
  if a==170 then
   assert(not pickup(),'Physical reward is collected')
   if index<=2 then assert(r('RlHealth')==28 and r('RlEnergy')==28,'Mushroom/flower refill both meters');assert(r('RlFoodKind')==1,'Mushroom permits the next native flower')
   elseif index==3 then assert(r('StarInvincibleTimer')>0,'Star starts native invincibility');lastStar=r('StarInvincibleTimer')
   else assert(r('NumberofLives')==initialLives+1,'1-up awards one actual life')end
   taken[index]=true;shot(rewardNames[index]..'-collected')
  end
 elseif t<=1440 then
  local index=(t-801)//160+1;local a=(t-801)%160;local c=dropCases[index]
  if a==0 then
   arena();dropIndex=index;dropMade=false;dropSeen=false;dropCollected=false
   w('Player_Y_Position',176);w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
   w('Enemy_X_Position',160);w('Enemy_PageLoc',0);w('Enemy_Y_Position',184);w('Enemy_Y_HighPos',1);w('Enemy_X_Speed',0)
  end
  for i=0,3 do if r('InvDropKind',i)~=0 then
   dropSeen=true;assert(r('InvDropKind',i)==c[1] and r('AvDropItem',i)==c[2],'Enemy creates the requested health/energy capsule')
   if a>=80 and not dropCollected then
    w('Player_X_Position',r('InvDropX',i));w('Player_PageLoc',r('InvDropPage',i))
    -- A capsule rests at the floor's top. Keep the player's feet above it.
    w('Player_Y_Position',math.min(176,r('InvDropY',i)-16));dropCollected=true
   end
  end end
  if a==140 then
   assert(dropMade and dropSeen and dropCollected,'Actual buster defeat drops a physically collected capsule')
   for i=0,3 do assert(r('InvDropKind',i)==0,'Collected capsule is consumed by native pickup collision')end
   assert(r(c[2]==0 and 'RlEnergy'or'RlHealth')==(c[2]==0 and 8 or 12)+c[3],'Capsule '..index..' restores the correct meter by its native amount; hp='..r('RlHealth')..' energy='..r('RlEnergy')..' kind='..r('InvDropKind',3)..' player='..r('Player_X_Position')..','..r('Player_Y_Position'))
   shot('capsule-'..index);taken[4+index]=true;dropIndex=nil
  end
 end
 if t==1450 or t==1545 then
  arena();w('Block_Buffer_1',0x54,116);w('Block_Buffer_1',0x54,117);w('Block_Buffer_1',0x51,103);w('Block_Buffer_1',0x54,104)
 end
 if t==1475 then assert(r('Block_Buffer_1',103)==0x51 and r('MmBrickHealth',103)>0,'A brick survives one ordinary buster hit')end
 if t==1515 then assert(r('Block_Buffer_1',103)~=0x51,'The second ordinary buster hit breaks the brick');shot('two-shot-brick')end
 if t==1580 then
  -- The first, ordinary shot is gone. A fresh full-health target is authored
  -- into the arena while B remains held, ahead of the automatic charge.
  w('Block_Buffer_1',0x51,103);w('MmBrickHealth',0,103)
 end
 if t==1655 then
  assert(r('RlEnergy')==4 and r('RlChargeFired')>0,'Charged attack spends energy through the controller path')
  assert(r('Block_Buffer_1',103)~=0x51 and r('Block_Buffer_1',104)==0x54,'One charged buster breaks a full-health brick and preserves adjacent ground')
  shot('charged-brick')
 end
 if t==1670 then
  for i=1,8 do assert(taken[i],'Every Roll reward case is physically exercised')end
  assert(starExpired,'The physically collected star expires through the native timer')
  assert(#soundEvents>8,'Actual reveal, pickup and attack sound queues are exercised')
  local f=assert(io.open(OUTPUT..'rewards-proof.json','w'))
  f:write('{"passed":true,"nativeBlockRewards":4,"enemyCapsules":4,"starExpiredNaturally":true,"twoShotBrick":true,"chargedBrick":true,"soundQueueEvents":'..#soundEvents..',"scope":"Authored block arenas with native emergence/physical pickup; controller defeats and native enemy-drop allocation with fixed random choices. Not a natural all-powerup route or exact mobile audio claim."}');f:close()
  print('PASS Roll native rewards and enemy health/energy capsules');emu.stop(0)
 end
 assert(wall<3100,'Bounded Roll rewards')
end,emu.eventType.endFrame)
