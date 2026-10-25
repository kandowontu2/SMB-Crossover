-- Cold menus followed by explicitly seeded native-update component arenas.
local wall,entered,update,stage,age=0,false,0,0,0
local kinds={-1,0,1,2,3,4,5}
local names={'no-flight','slash','triple','lunge','spin','plunge','charge'}
local current,face,hit,armed,seenMove=-1,1,false,false,false
local swordDefeats,minJumpY,lastJumpV=0,176,nil
local hoverY,hoverFrames=nil,0
local seenPoses={};local poseFrames=0
local menuPhase=META_HARD and 'options-focus' or 'start'
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local function save(n,s)local f=assert(io.open(OUTPUT..n,'wb'));f:write(s);f:close()end
local function shot(n)save(n..'.png',emu.takeScreenshot())end
local trace=assert(io.open(OUTPUT..'moves.csv','w'))
trace:write('wall,update,stage,age,face,kind,tick,pose,x,y,vxLo,vxHi,vyLo,vyHi,float,hp,enemy,enemyState,damage,armed,hit,rectX,rectPage,rectY,rectW,rectH\n')
local results={}
local function arena()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col);w('MmSolidTerrain',1,p*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i)end
 for _,n in ipairs({'TimerControl','GamePauseStatus','InjuryTimer','StarInvincibleTimer','GuestInvulTicks','GuestHurtTicks','GuestHurtKind',
  'PlayerChangeSizeFlag','MmDeathFlag','AreaParserTaskNum','ScrollThirtyTwo','EnemyFrenzyBuffer','EnemyFrenzyQueue','BlockBounceTimer',
  'KbFloat','KbHurt','KbHurtMove','KbAction','KbActionAge','KbMouth','KbCopy','Player_X_Speed','Player_Y_Speed','MkMoveTick','MkHitBits','MkBlockHit'})do w(n,0)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('ScrollLock',1);w('Player_X_Position',128);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('Player_CollisionBits',3);w('PlayerFacingDir',face);w('KbHealth',6)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
end
local function start(n)
 stage=n;age=0;face=n>7 and 2 or 1;current=kinds[(n-1)%7+1]
 hit=false;armed=false;seenMove=false;hoverY=nil;hoverFrames=0
 swordDefeats=0;minJumpY=176;lastJumpV=nil
 arena();shot('start-'..stage)
end
local function enemyAtSword()
 local x=r('MkRectX')+256*r('MkRectPage')
 if face==1 then x=x+r('MkRectW')-2 else x=x-12 end
 -- The native enemy falls on its first update. Put its body across the
 -- sword's upper rows, with floor support for grounded attacks, rather than
 -- placing its top below the last sword pixel before that update.
 local y=math.min(192,r('MkRectY')-8)
 if y<40 or y>200 or x<8 or x>232 then return false end
 w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
 w('Enemy_X_Position',x);w('Enemy_PageLoc',0);w('Enemy_Y_Position',y);w('Enemy_Y_HighPos',1)
 w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('Enemy_MovingDir',2);w('Enemy_CollisionBits',0)
 return true
end
emu.addMemoryCallback(function()
 if entered and stage>0 and bank(0xa000)==B.MkWeapons then swordDefeats=swordDefeats+1 end
end,emu.callbackType.exec,L.ShellOrBlockDefeat)
emu.addMemoryCallback(function()
 if not entered or r('OperMode')~=1 or r('GameEngineSubroutine')~=8 then return end
 update=update+1
 if stage==0 then if update>=20 then start(1)end;return end
 age=age+1
 assert(r('KbFloat')==0 and r('KbCopy')==0 and r('KbMouth')==0,'Meta has no flight, inflation or copy state')
 assert(r('MmDeathFlag')==0,'Component remains alive')
 if current==-1 then
  minJumpY=math.min(minJumpY,r('Player_Y_Position'))
  if age>=22 and age<=30 then
   local v=r('MmVY',1)+256*r('MmVY',2);if v>=32768 then v=v-65536 end
   if lastJumpV then assert(v==lastJumpV+21,'Air A/Up cannot reset native ballistic gravity')end
   lastJumpV=v
  end
 end
 if current>=0 and r('KbAction')==7 and r('MkCombo')==current then seenMove=true end
 if current==4 and r('KbAction')==7 and r('MkCombo')==4 and r('MkMoveTick')>=3 and r('MkMoveTick')<=29 then
  if not hoverY then hoverY=r('Player_Y_Position')end
  assert(math.abs(r('Player_Y_Position')-hoverY)<=1,'Downward strike holds its native windup height')
  hoverFrames=hoverFrames+1
 end
 if current>=0 and not armed and r('MkDamage')~=0 and r('MkMoveTick')>=6 then armed=enemyAtSword()end
 if armed and(r('Enemy_Flag')==0 or r('Enemy_State')&32~=0)then hit=true end
 if age==115 then
  if current>=0 then
   assert(seenMove,'Requested native attack starts: '..names[(stage-1)%7+1])
   assert(armed and hit and swordDefeats>0,'Native sword defeats a real Goomba: '..names[(stage-1)%7+1]..' face'..face)
  else
   assert(minJumpY<=112,'Grounded port jump clears64px SMB pipes without flight')
  end
  if current==4 then assert(hoverFrames>=20,'Downward strike windup ran before the fall')end
  assert(r('KbHealth')>0,'Attack fixture survives')
  results[#results+1]=string.format('{"name":"%s","face":%d,"enemyDefeated":%s,"swordDefeats":%d,"hoverUpdates":%d,"minimumY":%d}',names[(stage-1)%7+1],face,tostring(hit),swordDefeats,hoverFrames,minJumpY)
  shot('done-'..stage)
 end
 if age==120 then
  if stage<14 then start(stage+1)
  else
   trace:close();assert(poseFrames>100,'Actual player output exercised')
   save('proof.json',string.format('{"passed":true,"hard":%s,"frames":%d,"updates":%d,"poseFrames":%d,"cases":[%s],"scope":"Cold controller menu; explicitly seeded terrain/player and real Goombas at native GameLoop boundary; both facings, no flight, six source attack adaptations, hover/drop, real enemy defeats and hardware palettes. Not a campaign or every-item pass."}',tostring(META_HARD or false),wall,update,poseFrames,table.concat(results,',')))
   print('PASS Meta NES moves and no-flight arenas');emu.stop(0)
  end
 end
end,emu.callbackType.exec,L.GameLoop)
emu.addMemoryCallback(function()
 if not entered or stage==0 or bank(0xa000)~=B.MetaspriteRenderLoop then return end
 if r('R0')+256*r('R1')~=r('SmPosePtr')+256*r('SmPosePtr',1)then return end
 poseFrames=poseFrames+1
 local key=stage..'-'..r('KbPose')
 if not seenPoses[key]then
  seenPoses[key]=true
  local t={};for a=0x200,0x2ff do t[#t+1]=string.char(emu.read(a,emu.memType.nesDebug))end
  save('pose-'..key..'-staging.bin',table.concat(t))
 end
end,emu.callbackType.exec,L.MetaspriteRenderLoop)
emu.addEventCallback(function()
 local b={}
 if not entered and wall>=60 and wall%12==0 then
  if menuPhase=='options-focus'then menuPhase='options-open';b.down=true
  elseif menuPhase=='options-open'then menuPhase='mode-focus';b.a=true
  elseif menuPhase=='mode-focus'then
   if r('CrossoverMenuState')==4 then if r('CrossoverOptionsFocus')~=1 then b.down=true else menuPhase='mode-set'end end
  elseif menuPhase=='mode-set'then if r('CrossoverBehaviorVersion')==0 then b.a=true else menuPhase='back'end
  elseif menuPhase=='back'then menuPhase='start';b.b=true
  elseif r('CrossoverMenuState')~=2 then b.start=true
  elseif r('CrossoverMenuIndex')~=12 then b.down=true
  elseif r('KbVariant')~=1 then b.select=true
  else b.a=true end
 elseif entered then
  if current==-1 then b.a=(age>=10 and age<20)or(age>=25 and age<29);b.up=age>=25 and age<60
  elseif current==0 then b.b=age>=10 and age<14
  elseif current==1 then b.b=age>=10 and age<14;b.up=b.b
  elseif current==2 then b.select=age>=10 and age<14
  elseif current==3 then b.a=age>=10 and age<35;b.b=age>=20 and age<24
  elseif current==4 then b.a=age>=10 and age<35;b.b=age>=25 and age<29;b.down=b.b
  elseif current==5 then b.b=age>=10 and age<14;b.right=face==1 and age>=10 and age<50;b.left=face==2 and age>=10 and age<50 end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1
 if not entered and r('OperMode')==1 and r('GameEngineSubroutine')==8 then
  entered=true;assert(r('SelectedCharacter')==13 and r('KbVariant')==1,'Real menu starts Meta Knight');shot('entry')
 end
 if entered and stage>0 then
  trace:write(table.concat({wall,update,stage,age,face,r('MkCombo'),r('MkMoveTick'),r('KbPose'),r('Player_X_Position'),r('Player_Y_Position'),r('MmVX',1),r('MmVX',2),r('MmVY',1),r('MmVY',2),r('KbFloat'),r('KbHealth'),r('Enemy_Flag'),r('Enemy_State'),r('MkDamage'),tostring(armed),tostring(hit),r('MkRectX'),r('MkRectPage'),r('MkRectY'),r('MkRectW'),r('MkRectH')},',')..'\n')
  if age==5 then
   assert(emu.read(0x3f11,emu.memType.nesPpuDebug)==54 and emu.read(0x3f12,emu.memType.nesPpuDebug)==20 and emu.read(0x3f13,emu.memType.nesPpuDebug)==15,'Original Meta body palette36/14/0F')
  end
  if age==25 or age==40 or age==60 then shot('action-'..stage..'-'..age)end
 end
 assert(wall<3200,'Bounded Meta NES moves')
end,emu.eventType.endFrame)
