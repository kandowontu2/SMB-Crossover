-- Cold menus, then explicitly seeded terrain at the native GameLoop boundary.
-- Items are produced by controller head bumps and collected by controller input.
local wall,entered,updates,stage,age=0,false,0,0,0
local menuPhase=MAC_HARD and 'options-focus' or 'start'
local spawned,emerged,artChecked={},{},{}
local upper,banks=0,{}
local pending,artFrames=nil,0
local dma=false
local deathStarted,deathLives,respawnX=false,nil,nil
local sounds={}
local sourceRows={'.....#.....','....###....','....###....','...#####...',
 '###########','###########','.#########.','..#######..',
 '..#######..','..###.###..','.###...###.','.##.....##.'}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
local function actual(a)return emu.convertAddress(a).address//8192 end
local function save(n,s)local f=assert(io.open(OUTPUT..n,'wb'));f:write(s);f:close()end
local function shot(n)save(n..'.png',emu.takeScreenshot())end
local trace=assert(io.open(OUTPUT..'native.csv','w'))
trace:write('video,updates,stage,age,x,y,state,hp,hearts,stars,status\n')
local function arena()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for c=0,15 do
  w('Block_Buffer_1',0x54,p*208+176+c);w('MmSolidTerrain',1,p*208+176+c)
 end end
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i)end
 w('Player_X_Position',96);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('PlayerFacingDir',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 for _,n in ipairs({'InjuryTimer','StarInvincibleTimer','TimerControl','ScrollThirtyTwo','AreaParserTaskNum',
  'EnemyFrenzyBuffer','EnemyFrenzyQueue','LmAttack','LmHurt','LmInvul'})do w(n,0)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
end
local function enemy(x)
 w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_CollisionBits',0)
 w('Enemy_X_Position',x);w('Enemy_PageLoc',0);w('Enemy_Y_Position',184);w('Enemy_Y_HighPos',1)
 w('Enemy_X_Speed',0);w('Enemy_MovingDir',2);w('Enemy_BoundBoxCtrl',3)
end
local function startStage(n)
 stage=n;age=0;arena()
 if n<=5 then
  w('PlayerStatus',n==1 and 0 or 1)
  if n==1 then w('LmHealth',48);w('LmStars',0)end
  w('Block_Buffer_1',0xc1,118);w('MmSolidTerrain',1,118)
 else w('PlayerStatus',1);enemy(125)end
 shot('stage-'..stage..'-start')
end
emu.addMemoryCallback(function(_,v)upper=v&3 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(a,v)banks[a-0x5120]=v+upper*256 end,emu.callbackType.write,0x5120,0x5127)
emu.addMemoryCallback(function()dma=true end,emu.callbackType.write,0x4014)
emu.addMemoryCallback(function(_,v)
 if stage>=1 and stage<=5 and v&32~=0 then sounds[stage]=(sounds[stage]or 0)+1 end
end,emu.callbackType.write,L.Square2SoundQueue)
emu.addMemoryCallback(function()
 if entered and stage>=2 and stage<=5 and age>=75 and age<=125
  and r('R0')+256*r('R1')==L.LmStar and actual(0xc000)==B.LmStar then
  pending={stage=stage,x=r('R4'),y=r('R6'),age=age}
 end
end,emu.callbackType.exec,L.MetaspriteRenderLoop)
emu.addMemoryCallback(function()
 local committed=dma;dma=false
 -- A lag NMI may interrupt construction and deliberately skip DMA. Only
 -- compare a completed hardware image against the draw that was committed.
 if not pending or not committed then return end
 local p=pending;pending=nil
 local pixels={};local count,parts=0,0
 local raw={}
 for i=0,255 do raw[#raw+1]=string.char(emu.read(i,emu.memType.nesSpriteRam))end
 for i=0,63 do
  local at=i*4;local y=emu.read(at,emu.memType.nesSpriteRam)
  local tile=emu.read(at+1,emu.memType.nesSpriteRam)
  local attr=emu.read(at+2,emu.memType.nesSpriteRam)
  local x=emu.read(at+3,emu.memType.nesSpriteRam)
  -- The private page704 only contains these two pickup tile pairs.
  if y<240 and (tile==1 or tile==3) and (attr&3)==2 and banks[4]==704 then
   parts=parts+1
   for yy=0,15 do for xx=0,7 do
    local sy=(attr&128)~=0 and 15-yy or yy
    local sx=(attr&64)~=0 and 7-xx or xx
    local a=4096+(tile&254)*16+(sy//8)*16+sy%8
    local function bit(at)return emu.read(assert(banks[at//1024])*1024+at%1024,emu.memType.nesChrRom)>>(7-sx)&1 end
    local q=bit(a)+2*bit(a+8)
    if q>0 then
     assert(emu.read(0x3f10+(attr&3)*4+q,emu.memType.nesPpuDebug)==48,'Original white star palette')
     local key=(x+xx-p.x)..','..(y+yy-p.y)
     if not pixels[key]then count=count+1;pixels[key]=true end
    end
   end end
  end
 end
 local correct=parts==2 and count==73
 for y=1,12 do for x=1,11 do
  if (pixels[(x-1)..','..(y-7)]or false)~=(sourceRows[y]:sub(x,x)=='#')then correct=false end
 end end
 if not artChecked[p.stage]or not correct then
  save('star-'..p.stage..'-oam.bin',table.concat(raw))
  local chr={};for i=0,1023 do chr[#chr+1]=string.char(emu.read(704*1024+i,emu.memType.nesChrRom))end
  save('star-'..p.stage..'-chr.bin',table.concat(chr))
  save('star-'..p.stage..'-pixels.json',string.format('{"correct":%s,"parts":%d,"opaque":%d,"x":%d,"y":%d,"age":%d}',tostring(correct),parts,count,p.x,p.y,p.age))
  shot('star-'..p.stage..'-hardware')
 end
 assert(correct,'Actual uploaded star matches all73 original white pixels, including its right points')
 artChecked[p.stage]=true;artFrames=artFrames+1
end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addMemoryCallback(function()
 if not entered or r('OperMode')~=1 or r('GameEngineSubroutine')~=8 then return end
 updates=updates+1
 if stage==0 then if updates>=20 then startStage(1)end;return end
 age=age+1
 if stage<=5 then
  for i=0,5 do
   if r('Enemy_Flag',i)~=0 and r('Enemy_ID',i)==46 then
    if not spawned[stage]then spawned[stage]=age end
    if age==spawned[stage]+10 then
     assert(r('Enemy_State',i)<128,'A physical item visibly emerges')
     assert(r('PlayerStatus')==(stage==1 and 0 or 1),'Head bump does not automatically collect item')
     assert(r('LmStars')==(stage==1 and 0 or math.min(stage-2,3)),'No automatically awarded star')
     emerged[stage]=true;shot('pickup-'..stage..'-emerging')
    end
   end
  end
  if age==190 then
   assert(emerged[stage],'Real question-block head bump spawns physical pickup')
   assert((sounds[stage]or 0)>0,'Actual pickup queues its powerup sound')
   if stage==1 then assert(r('LmHealth')==72 and r('PlayerStatus')==1,'Physical mushroom heals24')
   else assert(r('LmStars')==math.min(stage-1,3),'Physical star is earned, capped at3');assert(artChecked[stage],'Physical star art observed')end
   shot('pickup-'..stage..'-collected')
  end
  if age==200 then
   assert(emu.read(0x200e,emu.memType.nesPpuDebug)==math.min(stage-1,3),'Actual HUD publishes earned star count')
  end
  if age==220 then startStage(stage+1)end
 else
  if age==50 then assert(r('Enemy_Flag')==0 or r('Enemy_State')&32~=0,'Normal punch defeats native Goomba')end
  if age==100 then assert(r('LmStars')==2 and r('LmSuper')~=0,'Up+B spends one physically earned star');shot('earned-super')end
  if age==150 then arena();w('LmHealth',48);enemy(104)end
  if age==180 then assert(r('LmHealth')>0 and r('LmHealth')<48,'Actual contact damages health');shot('damage')end
  if age==230 then arena();w('LmHealth',4);enemy(104);deathLives=r('NumberofLives')end
  if deathStarted and age==232 then
   assert(r('NumberofLives')==(deathLives-1)%256,'Native death consumes one life')
   save('respawn-state.json',string.format('{"health":%d,"lives":%d,"ready":%d,"lifeShadow":%d,"death":%d}',r('LmHealth'),r('NumberofLives'),emu.read(L.LmHealth+3,emu.memType.nesDebug),emu.read(L.LmHealth+4,emu.memType.nesDebug),r('MmDeathFlag')))
   assert(r('LmHealth')==96,'A new life restores Mac health to96')
   respawnX=r('Player_X_Position');shot('respawn')
  end
 end
end,emu.callbackType.exec,L.GameLoop)
emu.addEventCallback(function()
 local b={}
 if not entered and wall>=60 and wall%12==0 then
  if menuPhase=='options-focus'then menuPhase='options-open';b.down=true
  elseif menuPhase=='options-open'then menuPhase='mode-focus';b.a=true
  elseif menuPhase=='mode-focus'then
   if r('CrossoverMenuState')==4 then
    if r('CrossoverOptionsFocus')~=1 then b.down=true else menuPhase='mode-set'end
   end
  elseif menuPhase=='mode-set'then
   if r('CrossoverBehaviorVersion')==0 then b.a=true else menuPhase='back'end
  elseif menuPhase=='back'then menuPhase='start';b.b=true
  elseif r('CrossoverMenuState')~=2 then b.start=true
  elseif r('CrossoverMenuIndex')<12 then b.down=true
  elseif r('CrossoverMenuIndex')~=14 then b.right=true
  else b.a=true end
 elseif entered then
  if stage>=1 and stage<=5 then
   b.a=age>=20 and age<45
   if stage==1 then b.right=age>=70 and age<155;b.a=b.a or(age>=90 and age<125)
   else
    b.right=age>=70 and age<96;b.a=b.a or(age>=130 and age<180);b.left=age>=134 and age<180
   end
  elseif stage==6 then b.b=age==20 or age==70;b.up=age==70;b.right=deathStarted and age>=233 and age<270 end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1
 if not entered and r('OperMode')==1 and r('GameEngineSubroutine')==8 then
  entered=true;assert(r('SelectedCharacter')==15,'Actual menus choose Little Mac')
  assert(r('CrossoverBehaviorVersion')==(MAC_HARD and 1 or 0),'Actual Options choose requested rules');shot('entry')
 end
 if entered then
  trace:write(table.concat({wall,updates,stage,age,r('Player_X_Position'),r('Player_Y_Position'),r('Player_State'),r('LmHealth'),r('LmHearts'),r('LmStars'),r('PlayerStatus')},',')..'\n')
 end
 if stage==6 and age>=230 and r('MmDeathFlag')~=0 and not deathStarted then
  deathStarted=true;shot('death')
 end
 if stage==6 and age>=270 then
  assert(deathStarted and respawnX and r('Player_X_Position')>respawnX+8,'Real death returns a healthy movable life')
  trace:close();save('proof.json',string.format('{"passed":true,"hard":%s,"videoFrames":%d,"updates":%d,"physicalPickups":5,"starDMAFrames":%d,"scope":"Cold menus; terrain/player/enemy seeds at GameLoop boundary; controller headbumps, actual emergence/pickup/sound queue, full73-pixel uploaded star, stock0..3/max, earned super, damage, death and healthy movable respawn. No full-level or every-powerup certificate."}',tostring(MAC_HARD or false),wall,updates,artFrames))
  print('PASS Little Mac physical powerups and source star');emu.stop(0)
 end
 assert(wall<2600,'Bounded Little Mac physical pickup fixture')
end,emu.eventType.endFrame)
