-- Native actor/collision fixtures for the reported hardware failures.
-- No controller-only level-clear claim: positions and terrain are explicit.
local frame,age=0,0
local mode='spring'
local launch=false
local contacted=false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function flat()
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i)end
 for i=0,415 do w('Block_Buffer_1',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 w('Player_X_Position',80);w('Player_PageLoc',0);w('Player_Y_Position',130);w('Player_Y_HighPos',1)
 w('Player_State',2);w('Player_Y_Speed',2);w('Player_X_Speed',0);w('PlayerFacingDir',1)
 w('GameEngineSubroutine',8);w('TimerControl',0);w('ScrollLock',0);w('DisableCollisionDet',0)
 w('Player_CollisionBits',255);w('PlayerSize',0);w('PlayerStatus',0)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('MmVY',2,2)
end
emu.addEventCallback(function()
 emu.setInput({right=frame==100 or frame==120 or frame==140 or(mode=='pole'and age<20),start=frame==200},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==199 then w('WorldNumber',3);w('LevelNumber',0);w('AreaNumber',0)end
 if frame<550 then return end
 age=age+1
 if frame==550 then
  assert(r('SelectedCharacter')==3,'Bill selected')
  flat();age=0
  w('Enemy_Flag',1,2);w('Enemy_ID',0x32,2);w('Enemy_State',0,2)
  w('Enemy_X_Position',80,2);w('Enemy_PageLoc',0,2);w('Enemy_Y_Position',192,2);w('Enemy_Y_HighPos',1,2)
  w('Jumpspring_FixedYPos',192,2);w('JumpspringAnimCtrl',0)
  w('Block_Buffer_1',0x67,160+5);w('Block_Buffer_1',0x68,176+5)
 end
 if mode=='spring'then
  if r('JumpspringAnimCtrl')>0 then contacted=true end
  if contacted and r('JumpspringAnimCtrl')==0 and r('Player_Y_Speed')>=128 then launch=true end
  if age==80 then
   assert(contacted and launch,'Bill lands on the spring and is launched without freezing; spring '..r('JumpspringAnimCtrl')..' engine '..r('GameEngineSubroutine'))
   assert(r('EnemyMetasprite',2)>0 and r('EnemyMetasprite')==0,'Spring rendering stays in its actual enemy slot')
   mode='pole';flat();age=0;contacted=false
   w('Player_X_Position',65);w('Player_Y_Position',80);w('Player_State',1);w('Player_Y_Speed',0)
   w('MmVY',0,2)
   for row=0,9 do w('Block_Buffer_1',row==0 and 0x24 or 0x25,row*16+6)end
   w('Enemy_Flag',1,5);w('Enemy_ID',0x30,5);w('Enemy_State',0,5)
   w('Enemy_X_Position',88,5);w('Enemy_PageLoc',0,5);w('Enemy_Y_Position',48,5);w('Enemy_Y_HighPos',1,5)
  end
 elseif mode=='pole'then
  if r('GameEngineSubroutine')==4 then contacted=true end
  if age==180 then
   assert(contacted,'Bill makes native flagpole contact')
   assert(r('GameEngineSubroutine')==5,'Bill finishes the pole slide: engine '..r('GameEngineSubroutine')..' player state '..r('Player_State')..' y '..r('Player_Y_Position')..' flag '..r('Enemy_Y_Position',5))
   print('PASS Bill native spring landing/launch, enemy slot integrity and 4-1 flagpole slide');emu.stop(0)
  end
 end
end,emu.eventType.endFrame)
