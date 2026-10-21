-- Explicit flat-room mechanics matrix, not a controller-only level clear.
-- Mario and Luigi run this independently after real menu selection. Initial
-- fixtures are identical; avatar motion is never written during each trial.
local character=assert(NATIVE_BROTHER)
local frame,index,age,nativeUpdates=0,0,0,0
local current,springPressed
local cases={}
for power=0,2 do for _,action in ipairs({'walk','run','coast','reverse','jump','short','runjump','crouch','water','whirlpool','vine','platform','spring'})do
 cases[#cases+1]={power=power,action=action}
end end
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local out=assert(io.open(OUTPUT..ROM_NAME..'-native-brother-'..character..'.csv','w'))
out:write('case,action,power,tick,x,y,yHigh,state,vx,xFraction,vy,yForce,gravity,fallGravity,brakeLow,brakeHigh,size,crouch,engine,qvx0,qvx1,qvx2,qvy0,qvy1,qvy2,spring,body,platformContact,platformX\n')
local function setup(q)
 current=q;age=0;nativeUpdates=0;springPressed=nil
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,page*208+176+col);w('MmSolidTerrain',1,page*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('Whirlpool_PageLoc',0,i)end
 local water=q.action=='water'or q.action=='whirlpool'
 w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',water and 120 or 176);w('Player_Y_HighPos',1)
 w('Player_X_Speed',0);w('Player_X_MoveForce',0);w('Player_XSpeedAbsolute',0);w('Player_Y_Speed',0)
 w('SprObject_X_MoveForce',0) -- Displacement fraction is separate from velocity fraction.
 w('Player_Y_MoveForce',0);w('Player_YMoveForceFractional',0);w('Player_State',water and 1 or 0)
 w('PlayerFacingDir',1);w('Player_MovingDir',1);w('Player_CollisionBits',255);w('PlayerStatus',q.power);w('PlayerSize',q.power==0 and 1 or 0)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0);w('ScrollLock',1)
 w('Player_Pos_ForScroll',64);w('Player_X_Scroll',0);w('Platform_X_Scroll',0);w('SideCollisionTimer',0)
 w('AreaType',water and 0 or 1);w('SwimmingFlag',water and 1 or 0);w('MarioWaterActive',0);w('MarioWaterPulled',0)
 w('CrouchingFlag',0);w('RgCrouch',0);w('XgLuigiSkid',0);w('PlayerChangeSizeFlag',0);w('GuestPowerupActive',0)
 w('TimerControl',0);w('GameEngineSubroutine',8);w('InjuryTimer',0);w('StarInvincibleTimer',0);w('StompTimer',0)
 w('RunningTimer',0);w('RunningSpeed',0);w('JumpSwimTimer',0);w('VerticalForce',0);w('VerticalForceDown',0x70)
 w('A_B_Buttons',0);w('PreviousA_B_Buttons',0);w('JumpspringAnimCtrl',0);w('JumpspringTimer',0);w('Whirlpool_Flag',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 if q.action=='coast'or q.action=='reverse'then w('Player_X_Speed',32);w('Player_XSpeedAbsolute',32)end
 if q.action=='vine'then
  w('Player_X_Position',120);w('Player_Y_Position',112);w('Player_State',3);w('ClimbSideTimer',24)
  for row=1,10 do w('Block_Buffer_1',0x26,row*16+8)end
 elseif q.action=='platform'then
  -- Native acceleration is keyed to FrameCounter%4 and the primary counter
  -- aliases Enemy_Y_Speed. Initialize both instead of borrowing menu/history.
  w('FrameCounter',0);w('Enemy_Y_Speed',0)
  w('Player_X_Position',112);w('Player_Y_Position',128);w('Player_State',2)
  w('Enemy_Flag',1);w('Enemy_ID',0x28);w('Enemy_State',0);w('Enemy_PageLoc',0)
  w('Enemy_X_Position',96);w('Enemy_Y_Position',160);w('Enemy_Y_HighPos',1);w('Enemy_X_Speed',8);w('Enemy_BoundBoxCtrl',5)
  w('PlatformCollisionFlag',255);w('Platform_X_Scroll',0);w('Enemy_X_MoveForce',0)
 elseif q.action=='spring'then
  w('Player_X_Position',128);w('Player_Y_Position',144);w('Player_State',2)
  w('Block_Buffer_1',0x67,152);w('Block_Buffer_1',0x68,168)
  w('Enemy_Flag',1);w('Enemy_ID',0x32);w('Enemy_State',0);w('Enemy_PageLoc',0)
  w('Enemy_X_Position',128);w('Enemy_Y_Position',176);w('Enemy_Y_HighPos',1);w('Jumpspring_FixedYPos',176)
 elseif q.action=='whirlpool'then
  w('Player_X_Position',120);w('Player_PageLoc',1);w('ScreenLeft_PageLoc',1);w('ScreenRight_PageLoc',1)
  w('Whirlpool_PageLoc',1);w('Whirlpool_LeftExtent',64);w('Whirlpool_Length',128)
 end
end
emu.addMemoryCallback(function()
 if current and r('CurrentBank')%128==1 then nativeUpdates=nativeUpdates+1 end
end,emu.callbackType.exec,assert(L.PlayerPhysicsSub))
emu.addEventCallback(function()
 local b={select=character==8 and frame==180,start=frame==200}
 if current then
  local a=current.action
  if a=='walk'then b.right=age<48
  elseif a=='run'then b.right=age<48;b.b=age<48
  elseif a=='reverse'then b.left=age<48
  elseif a=='jump'then b.a=age<64
  elseif a=='short'then b.a=age<4
  elseif a=='runjump'then b.right=age<96;b.b=age<96;b.a=age>=32 and age<80
  elseif a=='crouch'then b.down=true;b.right=age<48
  elseif a=='water'then b.right=age<80;b.a=age%32>=4 and age%32<8
  elseif a=='vine'then b.up=age<48;b.down=age>=56 and age<96
  elseif a=='spring'then
   if not springPressed and r('JumpspringAnimCtrl')>=2 then springPressed=age end
   b.a=springPressed and age-springPressed<4
  end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if current then
  age=age+1
  out:write(table.concat({index,current.action,current.power,age,r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('Player_Y_HighPos'),r('Player_State'),r('Player_X_Speed'),r('Player_X_MoveForce'),r('Player_Y_Speed'),r('Player_Y_MoveForce'),r('VerticalForce'),r('VerticalForceDown'),r('FrictionAdderLow'),r('FrictionAdderHigh'),r('PlayerSize'),r('CrouchingFlag'),r('GameEngineSubroutine'),r('MmVX'),r('MmVX',1),r('MmVX',2),r('MmVY'),r('MmVY',1),r('MmVY',2),r('JumpspringAnimCtrl'),r('Player_BoundBoxCtrl'),r('PlatformCollisionFlag'),r('Enemy_X_Position')+256*r('Enemy_PageLoc')},',')..'\n')
  assert(r('GameEngineSubroutine')==8 and r('InjuryTimer')==0,'Mechanics arena remains healthy/playable: '..current.action..' form'..current.power)
  for i=0,5 do if(current.action~='spring'and current.action~='platform')or i~=0 then w('Enemy_Flag',0,i)end end
 end
 if frame>=640 and(frame-640)%128==0 then
  if current then
   assert(nativeUpdates>0 or current.action=='water'or current.action=='whirlpool','Dry motion executes Mario native PlayerPhysicsSub: '..current.action)
   print('PASS native brother '..character..' mechanics record '..current.action..', form'..current.power)
  end
  index=index+1
  if not cases[index]then out:close();print('PASS independent native brother '..character..' matrix,39 real-controller trials in all power forms');emu.stop(0);return end
  assert(r('SelectedCharacter')==character,'Real menu selects the independent control character')
  setup(cases[index])
 end
end,emu.eventType.endFrame)
