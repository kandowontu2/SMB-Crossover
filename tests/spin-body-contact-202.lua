-- Explicit source-contact arenas. Initial airborne attack states and targets
-- are fixtures; prepared native hitboxes resolve every damaging contact.
local frame,index,age=0,0,0
local cases={}
for _,char in ipairs({2,10}) do
 for _,enemy in ipairs({0,2,8,18,45,12,21}) do
  cases[#cases+1]={char=char,enemy=enemy}
 end
end
cases[#cases+1]={char=10,enemy=0,gap=true}
local current,bodies,hurt,stomps,initialHP
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function optional(n,v)if L[n]then w(n,v)end end
local function position(far)
 w('Enemy_X_Position',r('Player_X_Position')+(far and 96 or 8))
 w('Enemy_PageLoc',0);w('Enemy_Y_Position',r('Player_Y_Position'))
 w('Enemy_Y_Speed',0);w('Enemy_X_Speed',0)
end
local function setup()
 age,bodies,hurt,stomps=0,0,false,0
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do
  for _,n in ipairs({'Enemy_Flag','Enemy_State','Enemy_CollisionBits','MmEnemyFlash','AvFrozen','AvFrozenHi','RgEnemyStun','MmEnemyHealthLo','MmEnemyHealthHi'})do w(n,0,i)end
 end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('MmBulletType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i);w('SmShotType',0,i);w('SmBombAge',0,i)end
 for i=0,1 do w('MmYFraction',0,i);w('MmXFraction',0,i)end
 for _,n in ipairs({'InjuryTimer','StarInvincibleTimer','TimerControl','MmDeathFlag','GuestPowerupActive','StompTimer','SmBall','SmCrouch','RgCrouch','RgAttack','XgDash','MmSliding','SsKick','SsFreeze','SsBodyStop','AvStopwatch','Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','PreviousA_B_Buttons','A_B_Buttons','RgPreviousButtons','SwimmingFlag','MmFrictionYActive','AvFlipClock'})do w(n,0)end
 optional('GuestBodyNow',0);optional('GuestBodyPrev',0);optional('GuestBodyAttack',0)
 for _,n in ipairs({'GuestHurtKind','GuestHurtTicks','GuestInvulTicks','GuestFlickerPhase'})do optional(n,0)end
 w('SelectedCharacter',current.char);w('PlayerStatus',1);w('PlayerSize',0)
 w('Player_X_Position',112);w('Player_PageLoc',0);w('Player_Y_Position',96);w('Player_Y_HighPos',1)
 w('Player_State',1);w('PlayerFacingDir',1);w('Player_CollisionBits',3)
 w('SmFlip',current.char==2 and 1 or 0);w('SmJumpStartY',128);w('AvSlash',current.char==10 and 1 or 0)
 w('InvOwnedLo',current.char==2 and 0x41 or 0x21,current.char);w('InvSelected',0,current.char)
 w('GameEngineSubroutine',8);w('AreaType',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Enemy_Flag',1);w('Enemy_ID',current.enemy);w('Enemy_BoundBoxCtrl',current.enemy==45 and 10 or 9)
 w('Enemy_Y_HighPos',1);w('Enemy_MovingDir',2);w('Enemy_Y_MoveForce',0);w('BowserFlamePRandomOfs',0)
 initialHP=current.enemy==45 and 600 or 100
 w('MmEnemyHealthLo',initialHP);w('MmEnemyHealthHi',math.floor(initialHP/256));position(false)
 if current.enemy==45 then
  w('Enemy_Flag',0x80,1);w('Enemy_ID',45,1);w('Enemy_State',0,1);w('Enemy_Y_HighPos',1,1)
  w('BowserFront_Offset',0);w('DuplicateObj_Offset',1);w('BowserHitPoints',5)
  w('BowserBodyControls',0);w('BowserFeetCounter',255);w('BowserMovementSpeed',0)
  w('BowserOrigXPos',r('Enemy_X_Position'));w('MaxRangeFromOrigin',32)
  w('EnemyFrameTimer',255);w('BowserFireBreathTimer',255)
 end
end
-- Pin boss placement only; both actual native body halves, duplicate identity,
-- damage and source protection still execute normally.
emu.addMemoryCallback(function()
 if current and current.enemy==45 and r('CurrentBank')%128==0 and r('Enemy_State')==0 then
  position(false);w('Enemy_MovingDir',2)
 end
end,emu.callbackType.exec,L.BowserGfxHandler)
emu.addMemoryCallback(function()if current then bodies=bodies+1 end end,emu.callbackType.exec,L.HandlePECollisions)
emu.addMemoryCallback(function()if current then stomps=stomps+1 end end,emu.callbackType.exec,L.EnemyStomped)
emu.addEventCallback(function()emu.setInput({start=frame==200,right=current~=nil,a=current~=nil},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<600 then return end
 if frame==600 then index=1;current=cases[index];setup();return end
 age=age+1
 if r('PlayerStatus')~=1 or r('GameEngineSubroutine')==10 or r('GameEngineSubroutine')==11 then hurt=true end
 if age<18 and r('Enemy_Flag')~=0 and r('Enemy_State')&32==0 then position(current.gap and age>=5 and age<=8)end
 if age<18 then return end
 local projectile=current.enemy==12 or current.enemy==21
 local expectedHurt=projectile or(current.char==2 and current.enemy==45)
 local armor=current.enemy==2 or current.enemy==8
 local tag=string.format('character%d enemy%d gap%s',current.char,current.enemy,tostring(current.gap))
 assert(bodies>0,'Actual native body contact: '..tag)
 assert(stomps==0,'Spin attack never falls through to Mario stomp: '..tag)
 assert(hurt==expectedHurt,'Source special protection/projectile exclusion: '..tag..' hurt'..tostring(hurt))
 if not expectedHurt then
  if current.char==2 or current.gap then
   assert(r('Enemy_Flag')==0 or r('Enemy_State')&32~=0,'Source Screw defeat or two separated75-damage contacts: '..tag)
  else
   local hp=r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')
   assert(hp==initialHP-(armor and 0 or 75),'Source JumpSlash75, armor and continuous-contact receipt: '..tag..' HP'..hp)
  end
 end
 print('PASS source spin body contact '..tag)
 index=index+1;current=cases[index]
 if current then setup()else print('PASS all15 spin contact arenas, source damage, armor, Bowser exclusion and hostile projectiles');emu.stop(0)end
end,emu.eventType.endFrame)
