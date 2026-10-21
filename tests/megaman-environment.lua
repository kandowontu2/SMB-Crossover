local frame=0
local x,vx,y,vy
local bounces=0
local injuryChecked=false
local springLaunches=0
local springChecked=0
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
local function pos(n,f) return r(n)+(r(f)+r(f,1)*256)/65536 end
local function vel(n)
  local a=r(n)+r(n,1)*256+r(n,2)*65536
  if a>=0x800000 then a=a-0x1000000 end
  return a/65536
end
emu.addMemoryCallback(function() if frame>790 then bounces=bounces+1 end end,emu.callbackType.exec,L.MegaManBounceVelocity)
emu.addMemoryCallback(function() if frame>850 then springLaunches=springLaunches+1 end end,emu.callbackType.exec,L.MegaManSpringVelocity)
emu.addEventCallback(function()
  emu.setInput({right=frame==80 or (frame>=500 and frame<520) or frame==600,
    start=frame==120,a=(frame>=550 and frame<570) or (frame>=625 and frame<628) or frame==952,
    up=frame>=620 and frame<640,b=frame==630,left=frame==650},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
  frame=frame+1
  if frame>=490 and frame<790 then for i=0,5 do w('Enemy_Flag',0,i) end end
  if frame==500 then
    w('SwimmingFlag',1);w('MmStepTimer',0);w('MmPreviousDir',0)
    vx=0;x=pos('Player_X_Position','MmXFraction')
  end
  if frame>=501 and frame<=520 then
    vx=frame<=506 and 0 or .75;x=x+vx+(frame==501 and 2 or 0)
    assert(math.abs(vel('MmVX')-vx)<0.001,'Underwater ground speed cap')
    assert(math.abs(pos('Player_X_Position','MmXFraction')-x)<0.02,'Underwater horizontal trajectory')
  end
  if frame==550 then vy=-560/120;y=pos('Player_Y_Position','MmYFraction') end
  if frame>=551 and frame<=570 then
    vy=vy+500/7200;y=y+vy
    assert(math.abs(vel('MmVY')-vy)<0.002,'Underwater jump/gravity')
    assert(math.abs(pos('Player_Y_Position','MmYFraction')-y)<0.05,'Underwater jump trajectory')
  end
  if frame==575 then print('PASS 2.02 underwater startup step, immediate speed, jump and gravity') end
  if frame==580 then
    w('Player_Y_Position',90);w('Player_Y_HighPos',1);w('Player_State',2);w('Player_Y_Speed',3)
    w('MmVY',0);w('MmVY',0,1);w('MmVY',3,2)
  end
  if frame==582 then
    assert(math.abs(vel('MmVY')-(250/120+500/7200))<0.002,'Water fall cap precedes gravity, as in the source')
    print('PASS underwater fall-cap ordering')
  end
  if frame==600 then
    w('SwimmingFlag',0);w('Player_X_Position',48);w('Player_PageLoc',0)
    w('Player_Y_Position',130);w('Player_Y_HighPos',1);w('Player_State',3)
    w('MmOnVine',0);w('MmYFraction',0);w('MmYFraction',0,1);w('PlayerStatus',1)
    w('MmStepTimer',6);w('MmPreviousDir',0)
    for row=2,10 do w('Block_Buffer_1',0x26,row*16+3) end
  end
  if frame==620 then y=pos('Player_Y_Position','MmYFraction') end
  if frame==606 then assert(r('MmStepTimer')==0,'2.02 startup timer continues while attached to a vine') end
  if frame>=621 and frame<=640 then
    y=y-130/120
    assert(r('Player_State')==3,'Character stays attached to the vine')
    assert(math.abs(vel('MmVY')+130/120)<0.001,'Source vine climb speed')
    assert(math.abs(pos('Player_Y_Position','MmYFraction')-y)<0.02,'Vine trajectory')
    assert(r('Player_X_Position')==48,'Mega Man centers on the vine')
  end
  if frame==640 then
    assert(r('MmChargeFrames')==0,'A fresh attack press on a vine cannot start charging')
    for i=0,3 do assert(r('MmBulletType',i)==0,'Vine blocks new buster shots') end
  end
  if frame==654 then
    assert(r('Player_State')~=3 and r('PlayerFacingDir')==2,'A fresh direction press leaves the vine')
    print('PASS vine centering, climb speed, ignored jump/attack and directional exit')
    for row=2,10 do w('Block_Buffer_1',0,row*16+3) end
  end
  if frame==800 then
    for i=0,5 do w('Enemy_Flag',0,i) end
    w('Player_X_Position',80);w('Player_PageLoc',0);w('Player_Y_Position',158)
    w('Player_Y_HighPos',1);w('Player_State',2);w('Player_Y_Speed',2)
    w('MmVY',0);w('MmVY',0,1);w('MmVY',2,2);w('MmFrictionYActive',0)
    w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_X_Position',80)
    w('Enemy_PageLoc',0);w('Enemy_Y_Position',184);w('Enemy_Y_HighPos',1)
    w('Enemy_BoundBoxCtrl',9);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
  end
  if frame>800 and frame<850 and r('GuestHurtKind')==1 and r('GuestHurtTicks')>0 then
    assert(bounces==0,'Ordinary Mega Man contact cannot invoke a Mario stomp')
    assert(r('Enemy_Flag')~=0 and r('Enemy_State')&0x20==0,'Ordinary contact does not defeat the Goomba')
    injuryChecked=true
  end
  if frame==850 then
    assert(injuryChecked and bounces==0,'The ordinary-contact fixture enters source recoil without a stomp bounce')
    print('PASS source ordinary contact injures Mega Man without stomping or defeating the Goomba')
    -- The spring arena is independent of the preceding contact/protection window.
    for _,n in ipairs({'GuestHurtKind','GuestHurtTicks','GuestInvulTicks','GuestFlickerPhase','InjuryTimer','GuestBodyPrev','GuestBodyNow'})do w(n,0)end
    w('GuestHurtVisible',1);w('PlayerStatus',1)
    for i=0,5 do w('Enemy_Flag',0,i) end
    w('Player_X_Position',128);w('Player_PageLoc',0);w('Player_Y_Position',160)
    w('Player_Y_HighPos',1);w('Player_State',0);w('Player_Y_Speed',0)
    w('MmVY',0);w('MmVY',0,1);w('MmVY',0,2);w('MmYFraction',0);w('MmYFraction',0,1)
    w('Enemy_Flag',1);w('Enemy_ID',0x32);w('Enemy_State',0)
    w('Enemy_X_Position',128);w('Enemy_PageLoc',0);w('Enemy_Y_Position',192);w('Enemy_Y_HighPos',1)
    w('Jumpspring_FixedYPos',192);w('JumpspringAnimCtrl',0)
    w('Block_Buffer_1',0x67,168);w('Block_Buffer_1',0x68,184)
  end
  if frame==950 then
    assert(springChecked>=1,'Default spring launch occurred')
    w('Player_Y_Position',160);w('Player_State',0);w('Player_Y_Speed',0)
    w('MmVY',0);w('MmVY',0,1);w('MmVY',0,2)
    w('JumpspringAnimCtrl',2);w('JumpspringTimer',3);w('JumpspringForce',0xf9)
  end
  if springLaunches>springChecked then
    local expected=frame<950 and -475/120 or -1000/120
    assert(math.abs(vel('MmVY')-expected)<0.002,'Spring launch uses reference power: '..vel('MmVY'))
    springChecked=springLaunches
    print('PASS '..(frame<950 and 'default' or 'boosted')..' spring launch power')
  end
  if frame==1000 then
    assert(springChecked>=2,'Both spring launch profiles ran')
    emu.stop(0)
  end
end,emu.eventType.endFrame)
