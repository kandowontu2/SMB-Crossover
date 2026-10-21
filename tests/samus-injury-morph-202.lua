-- Source Samus.takeDamageStart/exitMorphBall contact arenas. A lost Morph Ball
-- exits only when the taller rectangle fits; blocked exits retain ball form.
local cases={}
for _,ground in ipairs({false,true})do for _,blocked in ipairs({false,true})do
 for _,water in ipairs({false,true})do for _,facing in ipairs({1,2})do for _,side in ipairs({-1,1})do
  cases[#cases+1]={ground=ground,blocked=blocked,water=water,facing=facing,side=side}
 end end end
end end
local frame,index,age,started,firstMove,entry,profiles=0,0,0,false,false,nil,0
local c,nextCase,returnPC,pendingSP
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function q(n)local v=r(n)+256*r(n,1)+65536*r(n,2);return(v>=0x800000 and v-0x1000000 or v)/65536 end
local function px()return r('Player_X_Position')+256*r('Player_PageLoc')+(r('MmXFraction')+256*r('MmXFraction',1))/65536 end
local function py()return r('Player_Y_Position')+(r('Player_Y_HighPos')-1)*256+(r('MmYFraction')+256*r('MmYFraction',1))/65536 end
local function near(a,b,t,label)assert(math.abs(a-b)<t,label..' actual'..a..' expected'..b)end
local function setup()
 age=0;started=false;firstMove=false;entry=nil;profiles=0;pendingSP=nil
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
 if c.blocked then
  local row=(c.ground and 176 or 112)-32
  for col=4,11 do w('Block_Buffer_1',0x54,208+row+col)end
 end
 for i=0,5 do for _,n in ipairs({'Enemy_Flag','Enemy_State','Enemy_CollisionBits','MmEnemyFlash','AvFrozen','AvFrozenHi'})do w(n,0,i)end end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('MmBulletType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i);w('SmShotType',0,i);w('SmBombAge',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 for _,n in ipairs({'TimerControl','InjuryTimer','StarInvincibleTimer','GuestPowerupActive','GuestHurtKind','GuestHurtTicks','GuestInvulTicks','GuestBodyNow','GuestBodyPrev','MmDeathFlag','MmDeathAge','SmCrouch','SmFlip','SmPreviousDirections','PreviousA_B_Buttons','A_B_Buttons','SavedJoypadBits','Player_X_Speed','Player_Y_Speed','MmFrictionYActive','RgAttack','SsKick','XgDash','MmSliding'})do w(n,0)end
 w('PlayerStatus',1);w('PlayerSize',0);w('Player_State',c.ground and 0 or 2);w('PlayerFacingDir',c.facing);w('Player_CollisionBits',3)
 w('Player_X_Position',128);w('Player_PageLoc',1);w('Player_Y_Position',c.ground and 176 or 112);w('Player_Y_HighPos',1)
 w('SmBall',1);w('CrouchingFlag',4);w('SwimmingFlag',c.water and 1 or 0)
 w('InvOwnedLo',255,2);w('InvOwnedHi',0,2);w('InvSelected',0,2);w('GameEngineSubroutine',8)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',1);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',1);w('ScrollLock',1);w('AreaParserTaskNum',0);w('ScrollThirtyTwo',0);w('EnemyFrenzyBuffer',0);w('EnemyFrenzyQueue',0)
 w('Enemy_Flag',1);w('Enemy_ID',18);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9);w('Enemy_Y_HighPos',1)
 w('Enemy_X_Position',128+c.side*8);w('Enemy_PageLoc',1);w('Enemy_Y_Position',r('Player_Y_Position')+8);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
 w('MmEnemyHealthLo',100);w('MmEnemyHealthHi',0)
end
emu.addMemoryCallback(function()
 if not c or r('CurrentBank')%128~=10 then return end
 assert(not started and r('SmBall')==1,'Actual authored ball reaches the injury handler')
 started=true;entry={x=px(),y=py(),vy=q('MmVY')}
end,emu.callbackType.exec,L.SamusHurtStart)
emu.addMemoryCallback(function()
 if not c or not started or r('CurrentBank')%128~=10 then return end
 assert(r('SmBall')==(c.blocked and 1 or 0),'Source injury retains a blocked ball and exits an open one')
 near(py(),entry.y-((c.ground and not c.blocked)and 5 or 0),.00002,'Grounded open exit lifts exactly5NESpx')
 near(px(),entry.x,.00002,'Morph exit never shifts sideways')
 near(q('MmVY'),c.ground and -250/120 or entry.vy,.00002,'Exit preserves the assigned ground hop or air velocity')
 assert(r('PlayerStatus')==0 and r('InvOwnedLo',2)==0,'The short retained shape does not retain its removed upgrade')
end,emu.callbackType.exec,L.GuestInjuryStarted)
emu.addMemoryCallback(function()
 if not c or not started or r('CurrentBank')%128~=10 then return end
 if not firstMove then
  local vy=c.ground and -250/120 or entry.vy
  local startY=entry.y-((c.ground and not c.blocked)and 5 or 0)
  local submerged=c.water and startY>(c.blocked and 13 or 25)
  if submerged then vy=math.min(vy,250/120)end
  if not(c.ground and c.blocked)then vy=vy+(submerged and 400 or 700)/7200 end
  near(q('MmVY'),vy,.002,'First source gravity pull respects exit/onGround ordering')
  near(py(),startY+vy,.025,'First source displacement after morph injury')
  firstMove=true
 end
 assert(r('SmBall')==(c.blocked and 1 or 0),'Shape is stable during recoil')
 near(px(),entry.x-c.side*1.25*(15-r('GuestHurtTicks')),.025,'Ball injury has ordinary attacker-relative recoil')
end,emu.callbackType.exec,L.SamusHurtIntegrated)
emu.addMemoryCallback(function()
 if not c or not started or r('GuestHurtTicks')==0 or pendingSP then return end
 local s=emu.getState();local sp=s['cpu.sp']
 local pc=emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1
 if not returnPC then
  returnPC=pc
  emu.addMemoryCallback(function()
   if not c or not pendingSP or emu.getState()['cpu.sp']~=pendingSP+2 then return end
   local actual=emu.getState()['cpu.y']
   assert(actual==(c.blocked and 17 or 16),'Real returned body profile retains13px ball or25px jump')
   profiles=profiles+1;pendingSP=nil
  end,emu.callbackType.exec,pc)
 end
 assert(pc==returnPC,'Stable real profile caller');pendingSP=sp
end,emu.callbackType.exec,L.MegaManCollisionBox)
emu.addEventCallback(function()emu.setInput({right=frame==80 or frame==100,start=frame==200},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<550 then return end
 if frame==550 or nextCase then
  assert(r('SelectedCharacter')==2,'Menu-selected Samus');nextCase=false;index=index+1;c=cases[index]
  if not c then print('PASS32 source Samus Morph Ball injury arenas: open/blocked exits, ground/air, wet/dry, both facing and attacker directions; first gravity, full/short bounds and art');emu.stop(0);return end
  setup();return
 end
 age=age+1
 if started then w('Enemy_Flag',0)end
 if age>=9 then
  assert(started and firstMove and profiles>0,'Real injury, integration and body profile are observed')
  assert(r('GameEngineSubroutine')==8 and r('TimerControl')==0,'Morph injury leaves the world live')
  assert((c.blocked and r('SmPose')>=27 and r('SmPose')<=30)or(not c.blocked and r('SmPose')==16),'Retained ball art or frozen jump art follows source')
  print('PASS Samus morph injury '..index..' blocked'..tostring(c.blocked)..' ground'..tostring(c.ground)..' water'..tostring(c.water));nextCase=true
 end
 assert(age<25,'Bounded morph injury fixture')
end,emu.eventType.endFrame)
