-- Explicit native integration arena; injected positions are not a route replay.
local frame,phase,age=0,0,0
local r=function(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local w=function(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local scenes={
 {key=0,area=37,x=3104,y=64,width=16,axis=0},
 {key=5,area=1,x=2568,y=160,width=48,axis=1},
 {key=25,area=1,x=2568,y=160,width=32,axis=1}}
local rows=assert(io.open(OUTPUT..ROM_NAME..'-helper-native-arena.csv','w'))
rows:write('frame,phase,age,slot,platformX,platformY,playerX,playerY,collision,phaseLo,phaseMid,phaseHi,oamPieces\n')
local carryChecks,drawChecks,detachChecks=0,0,0
local function seed(scene)
 local s=scenes[scene];local camera=s.x-100
 w('OperMode',1);w('OperMode_Task',3);w('CrossoverMenuState',0);w('SelectedCharacter',3);w('BillVariant',0);w('CrossoverBehaviorVersion',1)
 w('WorldNumber',s.key//4);w('LevelNumber',s.key%4);w('AreaNumber',0);w('AreaPointer',s.area);w('AreaType',1)
 w('GameEngineSubroutine',8);w('TimerControl',0);w('Player_State',0);w('PlayerStatus',0);w('PlayerSize',1)
 w('Player_X_Position',s.x);w('Player_PageLoc',s.x//256);w('Player_Y_Position',s.y-32);w('Player_Y_HighPos',1)
 w('Player_X_Speed',0);w('Player_Y_Speed',0);w('Player_X_MoveForce',0);w('Player_Y_MoveForce',0)
 w('ScreenLeft_X_Pos',camera);w('ScreenLeft_PageLoc',camera//256);w('ScreenRight_X_Pos',camera+255);w('ScreenRight_PageLoc',(camera+255)//256)
 w('ScrollLock',1);w('ScrollThirtyTwo',0);w('AreaParserTaskNum',0);w('EnemyFrenzyBuffer',0);w('EnemyFrenzyQueue',0)
 w('EnemyDataLow',L.E_GroundArea10%256);w('EnemyDataHigh',L.E_GroundArea10//256)
 w('GameTimerDisplay',3);w('GameTimerDisplay',0,1);w('GameTimerDisplay',0,2);w('GameTimerExpiredFlag',0)
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i)end
 for i=0,3 do w('Block_State',0,i);w('BlockMetasprite',0,i)end
 for i=0,8 do w('Misc_State',0,i);w('MiscMetasprite',0,i)end
 for i=0,415 do w('Block_Buffer_1',0,i)end
 -- Force only loader invalidation; real HpConfigure/InitEnemyObject execute.
 w('HpValid',0);w('HpCount',1)
 age=0
end
emu.addMemoryCallback(function()
 if phase==0 and frame>=600 then phase=1;seed(1)
 elseif phase==2 then phase=3;seed(2)
 elseif phase==4 then phase=5;seed(3)end
end,emu.callbackType.exec,L.PauseSkip)
emu.addEventCallback(function()
 emu.setInput({start=frame==60 or frame==240,right=frame==100 or frame==120 or frame==140},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if phase==1 or phase==3 or phase==5 then
  age=age+1;local s=scenes[(phase+1)//2]
  if age>=2 and age<=36 then
  local slot=r('HpActorSlot')-1
  assert(slot>=0 and slot<6,'Real native helper was allocated: age='..age..' count='..r('HpCount')..' valid='..r('HpValid')..' engine='..r('GameEngineSubroutine')..' task='..r('OperMode_Task'))
  local px=r('Enemy_X_Position',slot)+256*r('Enemy_PageLoc',slot)
  local py=r('Enemy_Y_Position',slot);local playerX=r('Player_X_Position')+256*r('Player_PageLoc')
  local pieces=0
  for i=0,63 do
   local sy=emu.read(i*4,emu.memType.nesSpriteRam)
   local tile=emu.read(i*4+1,emu.memType.nesSpriteRam)
   if math.abs(sy-py)<3 and tile==(ROM_NAME:find('mmc5') and 0x5a or 0x5b)then pieces=pieces+1 end
  end
  rows:write(table.concat({frame,phase,age,slot,px,py,playerX,r('Player_Y_Position'),r('PlatformCollisionFlag',slot),r('HpPhaseLo'),r('HpPhaseMid'),r('HpPhaseHi'),pieces},',')..'\n');rows:flush()
  if age>2 and age<35 then
   assert(r('PlatformCollisionFlag',slot)<128,'Native top contact remains active')
   assert(r('Player_Y_Position')+32==py,'Player is carried by native platform response')
   carryChecks=carryChecks+1
  end
  if age==20 then
   assert(pieces==s.width//8,'Native OAM width matches authored helper collider')
   drawChecks=drawChecks+1
   local shot=assert(io.open(OUTPUT..ROM_NAME..'-native-helper-'..s.width..'.png','wb'))
   shot:write(emu.takeScreenshot());shot:close()
  end
  if age==36 then
   -- Detach by camera motion while retaining the source phase for reentry.
   w('Player_Y_Position',100);w('Player_Y_Speed',0)
   local camera=s.x+500
   w('ScreenLeft_X_Pos',camera);w('ScreenLeft_PageLoc',camera//256);w('ScreenRight_X_Pos',camera+255);w('ScreenRight_PageLoc',(camera+255)//256)
  end
  end
  if age==39 then
   assert(r('HpActorSlot')==0,'Offscreen helper releases its genuine native slot')
   detachChecks=detachChecks+1
   phase=phase+1
   if phase==6 then
    local f=assert(io.open(OUTPUT..ROM_NAME..'-helper-native-arena.json','w'))
    f:write('{"passed":true,"carry_checks":'..carryChecks..',"OAM_width_checks":'..drawChecks..',"detach_checks":'..detachChecks..',"injected_arena":true,"controller_route":false}\n');f:close()
    print('PASS native helper16/32/48 actual OAM, native carry, detach lifecycle');emu.stop(0)
   end
  end
 end
 if frame>900 then assert(false,'Native helper arena timed out')end
end,emu.eventType.endFrame)
