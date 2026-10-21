-- Independent 2.02 source motion/lifecycle oracle. The initial flat arena and
-- enemy are explicit fixtures; all injury, time, input and recovery run normally.
local char=HURT_CHARACTER or 1
local cases={}
for _,dir in ipairs({1,2})do
 for _,p in ipairs({
  {name='dry-ground',ground=true}, {name='water-ground',ground=true,water=true},
  {name='dry-air',y=64}, {name='water-air',y=96,water=true},
  {name='water-surface-transition',y=25,water=true},
  {name='left-page-seam',x=1}, {name='right-page-seam',x=254},
 })do
  local c={};for k,v in pairs(p)do c[k]=v end;c.dir=dir;cases[#cases+1]=c
 end
end
local frame,index,age,model,moves,checks=0,0,0,nil,0,0
local c,needSetup,started,ended,returned,worldX,liveWorld,invulSeen,invulLast,invulDec
local rawLateReceipts,injectedReceipts=0,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function q(n)local v=r(n)+256*r(n,1)+65536*r(n,2);return(v>=0x800000 and v-0x1000000 or v)/65536 end
local function x()return r('Player_X_Position')+256*r('Player_PageLoc')+(r('MmXFraction')+256*r('MmXFraction',1))/65536 end
local function y()return r('Player_Y_Position')+(r('Player_Y_HighPos')-1)*256+(r('MmYFraction')+256*r('MmYFraction',1))/65536 end
local function near(a,b,tol,label)assert(math.abs(a-b)<tol,c.name..' direction'..c.dir..' '..label..' actual'..a..' expected'..b)end
local function setup()
 age=0;model=nil;moves=0;started=false;ended=false;invulSeen=false;invulLast=nil;invulDec=0;liveWorld=false;returned=nil
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_State',0,i);w('Enemy_CollisionBits',0,i);w('AvFrozen',0,i);w('AvFrozenHi',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('MmBulletType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('Player_X_Position',c.x or 128);w('Player_PageLoc',1);w('Player_Y_Position',c.ground and 176 or c.y or 64);w('Player_Y_HighPos',1)
 w('Player_State',c.ground and 0 or 2);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('PlayerFacingDir',c.dir);w('Player_CollisionBits',3)
 w('PlayerStatus',1);w('PlayerSize',0);w('SwimmingFlag',c.water and 1 or 0)
 w('InvOwnedLo',255,char);w('InvSelected',5,char);w('InvAmmo',4,char*16+5);w('InvDirty',1)
 w('GameEngineSubroutine',8);w('TimerControl',0);w('InjuryTimer',0);w('StarInvincibleTimer',0);w('GuestPowerupActive',0);w('MmDeathFlag',0);w('MmDeathAge',0)
 w('GuestHurtKind',0);w('GuestHurtTicks',0);w('GuestInvulTicks',0)
 w('MmSliding',0);w('XgDash',0);w('SsKick',0);w('SsFreeze',0);w('SsBodyStop',0);w('MmStepTimer',0);w('MmPreviousDir',0);w('MmFrictionYActive',0);w('MmLastXSpeed',0)
 w('PreviousA_B_Buttons',0);w('A_B_Buttons',0);w('RgPreviousButtons',0);w('SavedJoypadBits',0)
 local leftPage,leftX=1,0
 if c.name=='left-page-seam'then leftPage,leftX=0,128 elseif c.name=='right-page-seam'then leftX=128 end
 w('ScreenLeft_X_Pos',leftX);w('ScreenLeft_PageLoc',leftPage);w('ScreenRight_X_Pos',(leftX+255)%256);w('ScreenRight_PageLoc',leftPage+math.floor((leftX+255)/256));w('ScrollLock',1);w('AreaParserTaskNum',0);w('ScrollThirtyTwo',0)
 w('EnemyFrenzyBuffer',0);w('EnemyFrenzyQueue',0)
 -- Spiny actual body contact is susceptible to ordinary player injury.
 w('Enemy_Flag',1);w('Enemy_ID',18);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9);w('Enemy_Y_HighPos',1)
 local impact=r('Player_X_Position')+256*r('Player_PageLoc')+8
 w('Enemy_X_Position',impact);w('Enemy_PageLoc',math.floor(impact/256));w('Enemy_Y_Position',r('Player_Y_Position')+8);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
 w('MmEnemyHealthLo',100);w('MmEnemyHealthHi',0)
 -- A separate safe actor proves that world motion continues during recoil.
 w('Enemy_Flag',1,1);w('Enemy_ID',6,1);w('Enemy_State',0,1);w('Enemy_BoundBoxCtrl',9,1);w('Enemy_Y_HighPos',1,1);w('Enemy_PageLoc',leftPage,1)
 w('Enemy_X_Position',leftX+16,1);w('Enemy_Y_Position',184,1);w('Enemy_X_Speed',8,1);w('Enemy_Y_Speed',0,1);worldX=(leftX+16)%256
end
local function capture(kind)
 if not c or r('CurrentBank')%128~=10 then return false end
 local s=emu.getState();assert(not returned,'Injury helper calls are not nested')
 returned={kind=kind,x=s['cpu.x'],y=s['cpu.y'],offset=r('ObjectOffset')}
 return true
end
if HURT_INJECT_INPUT then
 emu.addMemoryCallback(function()
  if not c or not started or r('GuestHurtTicks')==0 or r('CurrentBank')%128~=10 then return end
  -- Deterministic isolated input receipt: an NMI can replace raw controls
  -- after the pre-parser lock mask, leaving freshly parsed buttons as well.
  -- Only input latches are authored; the runtime guard and all actions execute.
  w('SavedJoypadBits',0xe1);w('A_B_Buttons',0xc0);w('Left_Right_Buttons',1);w('Up_Down_Buttons',0)
  injectedReceipts=injectedReceipts+1
 end,emu.callbackType.exec,assert(L.GuestInjuryMovement))
end
for _,pool in ipairs({{'MmBulletType',4},{'RgShotType',10}})do
 emu.addMemoryCallback(function(_,v)
  if c and started and not ended and r('GuestHurtTicks')>0 then assert(v==0,'Locked source injury cannot spawn a shot despite held or newly received B')end
 end,emu.callbackType.write,L[pool[1]],L[pool[1]]+pool[2]-1)
end
emu.addMemoryCallback(function(_,v)
 if c and started and not ended and r('GuestHurtTicks')>0 then assert(v==0,'Locked source injury cannot switch the active weapon')end
end,emu.callbackType.write,L.InvSelected+char)
emu.addMemoryCallback(function()
 if not capture('start')then return end
 assert(not started,'One actual injury receipt');started=true
 assert(r('PlayerFacingDir')==c.dir,'Initial facing reaches the actual impact without stale previous-case input')
 model={x=x(),y=y(),vx=(c.dir==1 and-1 or 1)*80/120,vy=0,ground=c.ground}
end,emu.callbackType.exec,assert(L.MegaManHurtStart))
emu.addMemoryCallback(function()
 if not capture('move')then return end
 assert(started and not ended,'Only source recoil movement inside its lock')
 moves=moves+1
 assert(r('GuestHurtTicks')==27-moves,'450ms interval expires before movement on update27')
 if r('SavedJoypadBits')~=0 then rawLateReceipts=rawLateReceipts+1 end
 assert(r('A_B_Buttons')==0 and r('Left_Right_Buttons')==0 and r('Up_Down_Buttons')==0,'Held player controls are parsed as released while locked')
 assert(r('GameEngineSubroutine')==8 and r('TimerControl')==0,'World stays in the ordinary live engine')
 model.x=model.x+model.vx
 if not model.ground then
  -- Pinned raw takeDamage HRect is48Flashpx, retained even airborne.
  local submerged=c.water and model.y>24
  if submerged then model.vy=math.min(model.vy,250/120)end
  model.vy=math.min(model.vy+(submerged and 500 or 1500)/7200,700/120)
  model.y=model.y+model.vy
 end
end,emu.callbackType.exec,assert(L.MegaManHurtMovement))
emu.addMemoryCallback(function()
 if not c or not model or r('CurrentBank')%128~=10 then return end
 near(q('MmVX'),model.vx,.002,'source recoil VX')
 near(q('MmVY'),model.vy,.002,'source gravity VY')
 near(x(),model.x,.025,'integrated recoil X')
 near(y(),model.y,.025,'integrated recoil Y')
 assert(r('PlayerFacingDir')==c.dir,'Recoil never turns the character toward its motion')
 checks=checks+1
end,emu.callbackType.exec,assert(L.MegaManHurtIntegrated))
emu.addMemoryCallback(function()
 if not capture('end')then return end
 assert(moves==26,'26 locked movements precede the update27 end event')
 ended=true
end,emu.callbackType.exec,assert(L.MegaManHurtEnd))
emu.addMemoryCallback(function()
 if not c or not returned or r('CurrentBank')%128~=10 then return end
 local s=emu.getState();assert(s['cpu.x']==returned.x and s['cpu.y']==returned.y and r('ObjectOffset')==returned.offset,'Injury helper preserves caller X/Y/ObjectOffset')
 if returned.kind=='start'then
  near(q('MmVX'),model.vx,.00002,'entry facing-opposite80 speed');near(q('MmVY'),0,.00002,'entry resets vertical velocity')
  assert(r('GuestHurtTicks')==27 and r('PlayerStatus')==0,'Actual power loss starts its source recoil lock')
  assert(r('InvSelected',char)==0 and r('MmSliding')==0 and r('XgDash')==0 and r('SsKick')==0 and r('MmCharging')==0,'Damage cancels selected special, slide/dash, paidkick and charge')
 elseif returned.kind=='end'then near(q('MmVX'),model.ground and 0 or model.vx,.002,'ground-only end VX reset')end
 returned=nil
end,emu.callbackType.exec,assert(L.MegaManHurtReturned))
emu.addMemoryCallback(function(_,v)
 if not c or not ended then return end
 if v==75 and not invulSeen then invulSeen=true;invulLast=75
 elseif invulSeen and v~=invulLast then assert(v==invulLast-1,'Post-recoil protection decrements once per physics update');invulLast=v;invulDec=invulDec+1 end
end,emu.callbackType.write,assert(L.GuestInvulTicks))
emu.addEventCallback(function()
 local b={}
 if frame<540 then b={down=char==9 and frame==80,right=(char==1 and frame==80)or(char==9 and(frame==100 or frame==120 or frame==140)),start=frame==200}
 elseif c and started then b={right=true,a=true,b=true,select=true}end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<550 then return end
 if frame==550 or needSetup then
  assert(r('SelectedCharacter')==char,'Actual character select');needSetup=false;index=index+1;c=cases[index]
  if not c then
   if HURT_INJECT_INPUT then assert(injectedReceipts==#cases*26,'Every locked physics update received the isolated stale controller receipt')end
   print('PASS MM/Bass source injury '..#cases..' arenas, '..checks..' independent recoil updates, exact lock/immune durations, input/world motion and caller preservation; input receipts injected'..injectedReceipts..' late raw observations'..rawLateReceipts);emu.stop(0);return
  end
  setup();return
 end
 age=age+1
 if started then w('Enemy_Flag',0)end -- Remove only the authored impact actor.
 if started and not ended and r('Enemy_Flag',1)~=0 and r('Enemy_X_Position',1)~=worldX then liveWorld=true end
 if ended and r('GuestInvulTicks')>0 then assert(r('InjuryTimer')~=0,'Native contact guard remains armed throughout source protection')end
 if age>=130 then
  assert(started and ended and liveWorld,'Real hit, source recovery and unrelated live world actor were exercised')
  assert(invulSeen and invulLast==0 and invulDec==75,'Full1250ms post-recoil immunity expires independently of recoil')
  assert(r('GameEngineSubroutine')==8 and r('TimerControl')==0,'Source recovery does not enter native shrink')
  print('PASS MM/Bass source injury char'..char..' '..c.name..' direction'..c.dir);needSetup=true
 end
 assert(age<160,'Source injury fixture makes bounded progress')
end,emu.eventType.endFrame)
