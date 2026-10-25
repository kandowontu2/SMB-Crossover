-- Native small-lift render/contact arena; no ordinary route/clear claim.
local frame,phase,age=0,0,0
local r=function(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local w=function(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local log=assert(io.open(OUTPUT..ROM_NAME..'-source-lift-arena.csv','w'));log:write('frame,phase,age,playerY,playerState,firstY,secondY,flag,otherFirst,otherSecond,timer,engine,mode,task,frac1,frac2,counter\n')
local carried,visible=0,0
local function seed(world,wrap)
 w('OperMode',1);w('OperMode_Task',3);w('CrossoverMenuState',0);w('SelectedCharacter',0);w('CrossoverBehaviorVersion',1)
 w('WorldNumber',world);w('LevelNumber',3);w('AreaNumber',3);w('AreaPointer',0x62);w('AreaType',3)
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i)end
 for i=0,3 do w('Block_State',0,i);w('BlockMetasprite',0,i)end
 for i=0,8 do w('Misc_State',0,i);w('MiscMetasprite',0,i)end
 for i=0,415 do w('Block_Buffer_1',0,i)end
 w('Player_X_Position',96);w('Player_PageLoc',5);w('Player_Y_Position',wrap and 32 or 64);w('Player_Y_HighPos',1);w('Player_State',0)
 w('Player_X_Speed',0);w('Player_Y_Speed',0);w('Player_X_MoveForce',0);w('Player_Y_MoveForce',0)
 w('PlayerSize',0);w('PlayerStatus',1);w('CrouchingFlag',0);w('GameEngineSubroutine',8)
 w('ScreenLeft_X_Pos',226);w('ScreenLeft_PageLoc',4);w('ScreenRight_X_Pos',225);w('ScreenRight_PageLoc',5)
 w('ScrollLock',1);w('ScrollThirtyTwo',0);w('AreaParserTaskNum',0);w('EnemyFrenzyBuffer',0);w('EnemyFrenzyQueue',0)
 w('EnemyDataLow',L.E_GroundArea10%256);w('EnemyDataHigh',L.E_GroundArea10//256)
 w('GameTimerDisplay',3);w('GameTimerDisplay',0,1);w('GameTimerDisplay',0,2);w('GameTimerExpiredFlag',0)
 w('TimerControl',0);w('BlockBounceTimer',0)
 for i=0,1 do
  w('Enemy_Flag',1,i);w('Enemy_ID',wrap and 0x2b or(world==1 and(i==0 and 0x2c or 0x2b)or(i==0 and 0x2b or 0x2c)),i)
  w('Enemy_X_Position',92+i*48,i);w('Enemy_PageLoc',5,i);w('Enemy_Y_HighPos',1,i);w('Enemy_BoundBoxCtrl',4,i)
  w('Enemy_Y_Position',wrap and 64 or(world==4 and i==1 and 64 or 96),i)
  w('Enemy_State',wrap and 180 or(world==4 and i==0 and 224 or 192),i)
  w('Enemy_X_Speed',0,i);w('Enemy_YMoveForceFractional',0,i);w('Enemy_Y_MoveForce',0,i);w('PlatformCollisionFlag',0,i)
 end
 age=0
end
emu.addMemoryCallback(function()
 if phase==0 and frame>=600 then phase=1;seed(1,false)
 elseif phase==2 then phase=3;seed(4,false)
 elseif phase==4 then phase=5;seed(1,true)end
end,emu.callbackType.exec,L.PauseSkip)
emu.addEventCallback(function()emu.setInput({start=frame==60 or frame==240},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if phase==1 or phase==3 or phase==5 then
  age=age+1
  log:write(table.concat({frame,phase,age,r('Player_Y_Position'),r('Player_State'),r('Enemy_Y_Position'),r('Enemy_State'),r('PlatformCollisionFlag'),r('Enemy_Y_Position',1),r('Enemy_State',1),r('TimerControl'),r('GameEngineSubroutine'),r('OperMode'),r('OperMode_Task'),r('Enemy_YMoveForceFractional'),r('Enemy_X_Speed'),r('Enemy_Y_MoveForce')},',')..'\n');log:flush()
  if phase==5 and age==2 then
   assert(r('Enemy_Y_Position')>=239,'Rising platform actually wraps from64 to240')
   assert(r('Player_Y_Position')<100,'A wrapped source lift releases its passenger instead of teleporting them')
   local f=assert(io.open(OUTPUT..ROM_NAME..'-source-lift-arena.json','w'));f:write('{"passed":true,"carry_frames":'..carried..',"visible_checks":'..visible..',"native_frames":'..frame..'}\n');f:close()
   print('PASS native small-lift pair graphics, carry, independent source Y, passenger release at wrap');emu.stop(0)
  end
  if (phase==1 or phase==3)and age>2 and age<20 then
   assert(r('PlatformCollisionFlag')==2,'Native first-platform top collision is exercised')
   assert(r('Player_Y_Position')+32==r('Enemy_Y_Position'),'Native carry follows the same moving first-platform Y')
   carried=carried+1
  end
  if(phase==1 or phase==3)and age==20 then
   local count=0;local x=122
   for i=0,63 do local at=i*4;local sx=emu.read(at+3,emu.memType.nesSpriteRam);local sy=emu.read(at,emu.memType.nesSpriteRam);if sx==x and(math.abs(sy-r('Enemy_Y_Position'))<3 or math.abs(sy-r('Enemy_State'))<3)then count=count+1 end end
   assert(count>=2,'Both original native girder rows reach actual hardware OAM')
   visible=visible+1
   w('Player_Y_Position',r('Enemy_State')-32);w('Player_Y_Speed',0);w('Player_State',0)
  end
  if(phase==1 or phase==3)and age>22 and age<30 then
   assert(r('PlatformCollisionFlag')==1,'Native second-platform collision is exercised')
   assert(r('Player_Y_Position')+32==r('Enemy_State'),'Native second-platform carry uses its independently updated Y')
   carried=carried+1
  end
  if(phase==1 or phase==3)and age==30 then phase=phase+1 end
 end
 if frame>900 then assert(false,'Native lift arena timed out')end
end,emu.eventType.endFrame)
