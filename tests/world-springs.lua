-- Native spring landing/compression/launch fixtures. Test both actor-slot
-- extremes, ordinary/boosted timing, twelve characters and Lance.
local frame,age,phase=0,0,0
local interruptDepth=0
local contact,launch,pending=false,false,false
local launchY,minY,startTick
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function character()local c=math.floor(phase/4);return c==12 and 3 or c==13 and 12 or c end
local function slot()return phase%2==0 and 0 or 5 end
local function boosted()return phase%4>=2 end
-- MM uses the user-selected 2.02 MegaManBase DEF/BOOST_SPRING_PWR=475/1000;
-- the independent megaman-physics/environment fixtures cover its source model.
-- Luigi now shares Mario's native spring, verified independently against the
-- pre-rewrite Mario trace; its velocity is native rather than guest Q8.16.
-- Mario uses his source profile (MarioSourceSpring, 400/950) in Q8.16 MmVY.
local expected={{400/120,950/120},{475/120,1000/120},{300/120,700/120},{400/120,800/120},
 {450/120,950/120},{500/120,1000/120},{500/120,1000/120},{660/120,1320/120},
 {7,12},{475/120,1000/120},{500/120,1000/120},{400/120,930/120},{6,12}}
local function setup()
 w('SelectedCharacter',character());w('BillVariant',phase>=48 and phase<52 and 1 or 0)
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i)end
 for i=0,415 do w('Block_Buffer_1',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 w('Player_X_Position',80);w('Player_PageLoc',0);w('Player_Y_Position',130);w('Player_Y_HighPos',1)
 w('Player_State',2);w('Player_Y_Speed',2);w('Player_X_Speed',0);w('PlayerStatus',0)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_Y_MoveForce',0);w('Player_YMoveForceFractional',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('MmVY',2,2);w('MmFrictionYActive',0);w('MmJumpReleased',0);w('MmSliding',0);w('SmBall',0)
 w('XgDash',0);w('XgWall',0);w('XgCeiling',0);w('XgHoverActive',0);w('XgPitFlight',0);w('XgRise',0)
 w('TimerControl',0);w('GameEngineSubroutine',8);w('MmDeathFlag',0);w('Player_CollisionBits',255)
 local s=slot()
 w('Enemy_Flag',1,s);w('Enemy_ID',0x32,s);w('Enemy_State',0,s)
 w('Enemy_X_Position',80,s);w('Enemy_PageLoc',0,s);w('Enemy_Y_Position',192,s);w('Enemy_Y_HighPos',1,s)
 w('Jumpspring_FixedYPos',192,s);w('JumpspringAnimCtrl',0);w('JumpspringTimer',0)
 w('Block_Buffer_1',0x67,160+5);w('Block_Buffer_1',0x68,176+5)
 age=0;contact=false;launch=false;pending=false;launchY=nil;minY=255;startTick=r('FrameCounter')
end
for _,pc in ipairs({assert(L.NonMaskableInterrupt),assert(L.IrqScrollSplit)})do
 emu.addMemoryCallback(function()interruptDepth=interruptDepth+1 end,emu.callbackType.exec,pc)
end
for _,pc in ipairs({assert(L.NonMaskableInterrupt_RTI),assert(L.IrqScrollSplit_RTI)})do
 emu.addMemoryCallback(function()interruptDepth=interruptDepth-1;assert(interruptDepth>=0,'Balanced native spring fixture interrupt scope')end,emu.callbackType.exec,pc)
end
emu.addMemoryCallback(function()
 if frame>=550 and interruptDepth==0 then pending=true end
end,emu.callbackType.exec,L.MegaManSpringVelocity)
emu.addMemoryCallback(function()
 if not pending or interruptDepth~=0 or r('CurrentBank')%128~=0 then return end
 pending=false;launch=true
 assert(emu.getState()['cpu.x']==slot(),'Spring launch preserves its native actor index for character '..character()..' slot '..slot())
 local force=boosted()and 0xf4 or 0xf9
 assert(r('JumpspringForce')==force,'Native fresh A during compression selects the boosted force')
 local velocity=r('Player_Y_Speed');if velocity>=128 then velocity=velocity-256 end
 if character()~=8 then
  local value=r('MmVY')+256*r('MmVY',1)+65536*r('MmVY',2)
  velocity=(value>=0x800000 and value-0x1000000 or value)/65536
 end
 assert(math.abs(velocity+expected[character()+1][boosted()and 2 or 1])<.002,'Character spring force: '..velocity)
 if not launchY then launchY=r('Player_Y_Position')end
end,emu.callbackType.exec,L.DrawJumpSpring)
emu.addEventCallback(function()
 emu.setInput({right=frame==80 or frame==100 or frame==120,start=frame==200,
  a=frame>=550 and boosted()and r('JumpspringAnimCtrl')==2},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if frame==550 then setup();return end
 age=age+1
 if r('JumpspringAnimCtrl')>0 then contact=true end
 if launch then minY=math.min(minY,r('Player_Y_Position'))end
 if age==75 then
  assert(contact and launch and launchY and minY<=launchY-8,'Actual landing, compression and airborne rebound: phase '..phase..' character '..character()..' contact '..tostring(contact)..' launch '..tostring(launch)..' start '..tostring(launchY)..' min '..minY..' y '..r('Player_Y_Position')..' anim '..r('JumpspringAnimCtrl'))
  assert((r('FrameCounter')-startTick)%256>40 and r('GameEngineSubroutine')==8,'Spring cannot freeze the main loop: phase '..phase..' character '..character()..' ticks '..((r('FrameCounter')-startTick)%256)..' engine '..r('GameEngineSubroutine')..' y '..r('Player_Y_Position')..' high '..r('Player_Y_HighPos'))
  phase=phase+1
  if phase==56 then
   print('PASS 56 native spring contacts: all thirteen characters plus Lance, slots 0/5, ordinary/boosted launches, source forces, preserved X and live airborne rebound')
   emu.stop(0)
  else setup()end
 end
end,emu.eventType.endFrame)
