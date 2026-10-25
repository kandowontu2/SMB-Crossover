-- Cold menus, then complete player/terrain arenas at native GameLoop entry.
-- Both food kinds emerge from real head bumps; no equipment grant injection.
local wall,entered,updates,stage,age=0,false,0,0,0
local menuPhase=META_HARD and'options-focus'or'start'
local born,emerged,pickups,chunks,noise={},{},{},{},{}
local death,deathLives,respawnX=false,nil,nil
local nmis,context=0,nil
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local function save(n,s)local f=assert(io.open(OUTPUT..n,'wb'));f:write(s);f:close()end
local function shot(n)save(n..'.png',emu.takeScreenshot())end
local trace=assert(io.open(OUTPUT..'physical.csv','w'))
trace:write('wall,updates,stage,age,x,y,hp,food,action,pose,block,adjacent,death\n')
local function arena()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col);w('MmSolidTerrain',1,p*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i)end
 for i=0,1 do w('Block_State',0,i);w('Block_RepFlag',0,i)end
 for _,n in ipairs({'TimerControl','GamePauseStatus','InjuryTimer','StarInvincibleTimer','GuestInvulTicks','GuestHurtTicks','GuestHurtKind',
 'PlayerChangeSizeFlag','MmDeathFlag','AreaParserTaskNum','ScrollThirtyTwo','EnemyFrenzyBuffer','EnemyFrenzyQueue','BlockBounceTimer',
 'KbFloat','KbHurt','KbHurtMove','KbAction','KbActionAge','KbMouth','KbCopy','Player_X_Speed','Player_Y_Speed','KbJumpPhase','MkMoveTick','MkHitBits','MkBlockHit'})do w(n,0)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('ScrollLock',1);w('Player_X_Position',96);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('Player_CollisionBits',3);w('PlayerFacingDir',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
end
local function start(n)
 stage=n;age=0;arena()
 if n<=3 then
  if n==1 then w('KbHealth',2);w('KbFoodKind',0)end
  w('Block_Buffer_1',0xc1,118);w('MmSolidTerrain',1,118)
 elseif n<=6 then
  w('Block_Buffer_1',n==4 and 0xc1 or n==5 and 0x51 or 0x52,168)
  w('MmSolidTerrain',n==6 and 1 or 0,168);w('Block_Buffer_1',0x54,169);w('MmSolidTerrain',1,169)
 else
  if n==7 then w('KbHealth',6)end
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
  w('Enemy_X_Position',102);w('Enemy_PageLoc',0);w('Enemy_Y_Position',176);w('Enemy_Y_HighPos',1)
  w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('Enemy_MovingDir',2);w('Enemy_CollisionBits',0)
  if n==12 then deathLives=r('NumberofLives')end
 end
 shot('stage-'..stage..'-start')
end
emu.addMemoryCallback(function()context={a=bank(0xa000),c=bank(0xc000)};nmis=nmis+1 end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()
 assert(context and bank(0xc000)==context.c,'NMI restores graphics ownership')
 assert(bank(0xa000)==r('CurrentBank')%128,'NMI restores work-bank ownership');context=nil
end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addMemoryCallback(function(_,v)if v&32~=0 then pickups[stage]=(pickups[stage]or 0)+1 end end,emu.callbackType.write,L.Square2SoundQueue)
emu.addMemoryCallback(function()chunks[stage]=(chunks[stage]or 0)+1 end,emu.callbackType.exec,L.SpawnBrickChunks)
emu.addMemoryCallback(function(_,v)if v~=0 then noise[stage]=true end end,emu.callbackType.write,L.NoiseSoundQueue)
emu.addMemoryCallback(function()
 if not entered or r('OperMode')~=1 or r('GameEngineSubroutine')~=8 then return end
 updates=updates+1
 if stage==0 then if updates>=20 then start(1)end;return end
 age=age+1
 assert(r('KbCopy')==0 and r('KbMouth')==0 and r('KbFloat')==0,'Health food never grants copy or flight')
 if stage<=3 then
  for i=0,5 do if r('Enemy_Flag',i)~=0 and r('Enemy_ID',i)==46 then
   if not born[stage]then born[stage]=age;assert(r('PowerUpType',i)==(stage==2 and 1 or 0),'Natural food appearance alternates mushroom/flower')end
   if age==born[stage]+10 then
    assert(r('Enemy_State',i)<128 and r('KbHealth')==(stage==1 and 2 or stage==2 and 4 or 6),'Food emerges before any healing')
    emerged[stage]=true;shot('food-'..stage..'-emerging')
   end
  end end
  if age==205 then
   assert(emerged[stage]and(pickups[stage]or 0)>0,'Head bump, emergence, actual pickup and sound execute')
   assert(r('KbHealth')==(stage==1 and 4 or 6),'Real food heals two and caps six')
   shot('food-'..stage..'-collected')
  end
  if age==220 then start(stage+1)end
 elseif stage<=6 then
  if age==100 then
   assert(r('Block_Buffer_1',169)==0x54,'Sword preserves adjacent protected terrain')
   if stage==4 then assert(r('Block_Buffer_1',168)==0xc4,'Sword activates question block')
   elseif stage==5 then assert(r('Block_Buffer_1',168)==0 and(chunks[stage]or 0)>0 and noise[stage],'Sword brick keeps native debris and SFX')
   else assert(r('Block_Buffer_1',168)==0x52,'Sword cannot destroy foundation')end
   assert(r('Player_X_Position')==96 and r('Player_PageLoc')==0,'Standing sword cannot displace the player')
   shot('block-'..stage..'-result');start(stage+1)
  end
 else
  if stage<12 and age==45 then assert(r('KbHealth')==12-stage,'Native contact removes exactly one health');start(stage+1)end
  if stage==12 and death and not respawnX then
   assert(r('NumberofLives')==(deathLives-1)%256 and r('KbHealth')==6,'Native respawn restores six health and consumes one life')
   respawnX=r('Player_X_Position');shot('healthy-respawn')
  end
 end
end,emu.callbackType.exec,L.GameLoop)
emu.addEventCallback(function()
 local b={}
 if not entered and wall>=60 and wall%12==0 then
  if menuPhase=='options-focus'then menuPhase='options-open';b.down=true
  elseif menuPhase=='options-open'then menuPhase='mode-focus';b.a=true
  elseif menuPhase=='mode-focus'then if r('CrossoverMenuState')==4 then if r('CrossoverOptionsFocus')~=1 then b.down=true else menuPhase='mode-set'end end
  elseif menuPhase=='mode-set'then if r('CrossoverBehaviorVersion')==0 then b.a=true else menuPhase='back'end
  elseif menuPhase=='back'then menuPhase='start';b.b=true
  elseif r('CrossoverMenuState')~=2 then b.start=true
  elseif r('CrossoverMenuIndex')~=12 then b.down=true
  elseif r('KbVariant')~=1 then b.select=true
  else b.a=true end
 elseif entered then
  if stage<=3 then
   b.a=age>=20 and age<45
   if stage~=2 then b.right=age>=70 and age<155;b.a=b.a or(age>=90 and age<125)
   else b.right=age>=70 and age<96;b.a=b.a or(age>=130 and age<180);b.left=age>=134 and age<180 end
  elseif stage<=6 then b.b=age==20
  elseif stage==12 then b.right=respawnX~=nil end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1
 if not entered and r('OperMode')==1 and r('GameEngineSubroutine')==8 then
  entered=true;assert(r('SelectedCharacter')==13 and r('KbVariant')==1,'Actual menu selects Meta Knight')
  assert(r('CrossoverBehaviorVersion')==(META_HARD and 1 or 0),'Actual Options select requested mode');shot('entry')
 end
 if entered then trace:write(table.concat({wall,updates,stage,age,r('Player_X_Position'),r('Player_Y_Position'),r('KbHealth'),r('KbFoodKind'),r('KbAction'),r('KbPose'),r('Block_Buffer_1',168),r('Block_Buffer_1',169),r('MmDeathFlag')},',')..'\n')end
 if stage==12 and r('MmDeathFlag')~=0 and not death then death=true;shot('death')end
 if respawnX and r('Player_X_Position')>respawnX+12 then
  assert(nmis>1200,'Sustained interrupt ownership check');trace:close()
  save('proof.json',string.format('{"passed":true,"hard":%s,"frames":%d,"updates":%d,"nmis":%d,"foods":3,"scope":"Cold menus; complete arenas at GameLoop boundary. Actual head bumps, both naturally alternating food kinds, emergence/pickup/heal/cap/SFX, sword question/brick/debris/protected foundation, six contacts, death, healthy movable respawn and NMI bank restoration. Not a campaign or every-item pass."}',tostring(META_HARD or false),wall,updates,nmis))
  print('PASS Meta physical food, native block effects and health lifecycle');emu.stop(0)
 end
 assert(wall<3300,'Bounded Meta physical fixture')
end,emu.eventType.endFrame)
