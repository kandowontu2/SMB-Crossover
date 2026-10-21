-- Explicit impact arenas; independent constants from pinned Samus.as2.02.
-- Only arena initialization and a late raw-input receipt are authored. The real
-- enemy collision, recoil integration, recovery, sound queue and timers run.
local cases={}
for _,facing in ipairs({1,2}) do
 for _,side in ipairs({-1,1}) do
  for _,p in ipairs({
   {name='dry-ground',ground=true},{name='water-ground',ground=true,water=true},
   {name='dry-air-rising',vy=-2,y=80},{name='dry-air-falling',vy=2,y=80},
   {name='water-air',vy=1,y=96,water=true},
   {name='water-surface',vy=-1,y=26,water=true},
   {name='left-page-seam',x=1,vy=-1,y=80},
   {name='right-page-seam',x=254,vy=-1,y=80},
  }) do
   local c={};for k,v in pairs(p) do c[k]=v end
   c.facing=facing;c.side=side;cases[#cases+1]=c
  end
 end
end
local frame,index,age,moves,checks=0,0,0,0,0
local c,setupNext,started,ended,model,worldX,worldLive,immuneLast,immuneDecrements
local injected=0
-- Audio can execute this same CPU address while foreground CurrentBank
-- remains10. Accept only the real Samus bank outside NMI/IRQ; numeric recoil,
-- recovery, protection and one-real-injury-per-arena oracles are unchanged.
local injuryBank,injurySelect,injuryDepth=nil,nil,0
if ROM_NAME:find('mmc5')then
 emu.addMemoryCallback(function(_,v)injuryBank=v%128 end,emu.callbackType.write,0x5115)
else
 emu.addMemoryCallback(function(_,v)injurySelect=v%8 end,emu.callbackType.write,0x8000)
 emu.addMemoryCallback(function(_,v)if injurySelect==7 then injuryBank=v%128 end end,emu.callbackType.write,0x8001)
end
for _,pc in ipairs({L.NonMaskableInterrupt,L.IrqScrollSplit})do emu.addMemoryCallback(function()injuryDepth=injuryDepth+1 end,emu.callbackType.exec,pc)end
for _,pc in ipairs({L.NonMaskableInterrupt_RTI,L.IrqScrollSplit_RTI})do emu.addMemoryCallback(function()injuryDepth=injuryDepth-1 end,emu.callbackType.exec,pc)end
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function q(n)local v=r(n)+256*r(n,1)+65536*r(n,2);return(v>=0x800000 and v-0x1000000 or v)/65536 end
local function x()return r('Player_X_Position')+256*r('Player_PageLoc')+(r('MmXFraction')+256*r('MmXFraction',1))/65536 end
local function y()return r('Player_Y_Position')+(r('Player_Y_HighPos')-1)*256+(r('MmYFraction')+256*r('MmYFraction',1))/65536 end
local function near(actual,expected,tolerance,label)
 assert(math.abs(actual-expected)<tolerance,c.name..' facing'..c.facing..' attacker'..c.side..' '..label..' actual'..actual..' expected'..expected)
end
local function setup()
 age=0;moves=0;started=false;ended=false;model=nil;worldLive=false;immuneLast=nil;immuneDecrements=0
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
 for i=0,5 do
  for _,n in ipairs({'Enemy_Flag','Enemy_State','Enemy_CollisionBits','AvFrozen','AvFrozenHi','MmEnemyFlash'})do w(n,0,i)end
 end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('MmBulletType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i);w('SmShotType',0,i);w('SmBombAge',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 for _,n in ipairs({'InjuryTimer','StarInvincibleTimer','TimerControl','MmDeathFlag','MmDeathAge','GuestPowerupActive','StompTimer','SmBall','SmCrouch','SmFlip','RgCrouch','RgAttack','XgDash','MmSliding','SsKick','SsFreeze','SsBodyStop','Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','PreviousA_B_Buttons','A_B_Buttons','RgPreviousButtons','SavedJoypadBits','MmFrictionYActive','MmLastXSpeed','GuestHurtKind','GuestHurtTicks','GuestInvulTicks','GuestFlickerPhase','GuestBodyNow','GuestBodyPrev'})do w(n,0)end
 w('Player_X_Position',c.x or 128);w('Player_PageLoc',1);w('Player_Y_Position',c.ground and 176 or c.y);w('Player_Y_HighPos',1)
 w('Player_State',c.ground and 0 or 2);w('PlayerFacingDir',c.facing);w('Player_CollisionBits',3)
 w('MmVY',c.vy or 0,2);w('Player_Y_Speed',c.vy or 0)
 w('PlayerStatus',1);w('PlayerSize',0);w('SwimmingFlag',c.water and 1 or 0)
 w('InvOwnedLo',255,2);w('InvSelected',2,2);w('InvAmmo',4,2*16+2);w('InvDirty',1)
 w('GameEngineSubroutine',8);w('EnemyFrenzyBuffer',0);w('EnemyFrenzyQueue',0)
 local leftPage,leftX=1,0
 if c.name=='left-page-seam'then leftPage,leftX=0,128 elseif c.name=='right-page-seam'then leftX=128 end
 w('ScreenLeft_X_Pos',leftX);w('ScreenLeft_PageLoc',leftPage);w('ScreenRight_X_Pos',(leftX+255)%256);w('ScreenRight_PageLoc',leftPage+math.floor((leftX+255)/256));w('ScrollLock',1);w('AreaParserTaskNum',0);w('ScrollThirtyTwo',0)
 local impact=r('Player_X_Position')+256*r('Player_PageLoc')+c.side*8
 w('Enemy_Flag',1);w('Enemy_ID',18);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9);w('Enemy_Y_HighPos',1)
 w('Enemy_X_Position',impact);w('Enemy_PageLoc',math.floor(impact/256));w('Enemy_Y_Position',r('Player_Y_Position')+8);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
 w('MmEnemyHealthLo',100);w('MmEnemyHealthHi',0)
 w('Enemy_Flag',1,1);w('Enemy_ID',6,1);w('Enemy_State',0,1);w('Enemy_BoundBoxCtrl',9,1);w('Enemy_Y_HighPos',1,1);w('Enemy_PageLoc',leftPage,1)
 w('Enemy_X_Position',leftX+16,1);w('Enemy_Y_Position',184,1);w('Enemy_X_Speed',8,1);w('Enemy_Y_Speed',0,1);worldX=(leftX+16)%256
end
emu.addMemoryCallback(function()
 if not c or r('CurrentBank')%128~=10 or injuryBank~=10 or injuryDepth~=0 then return end
 assert(not started,'One actual injury per arena');started=true
 assert(r('PlayerFacingDir')==c.facing,'Facing reaches impact without stale input')
 model={x=x(),y=y(),vx=-c.side*150/120,vy=c.ground and -250/120 or q('MmVY')}
end,emu.callbackType.exec,assert(L.SamusHurtStart))
emu.addMemoryCallback(function()
 if not c or not started or r('CurrentBank')%128~=10 or injuryBank~=10 or injuryDepth~=0 then return end
 near(q('MmVX'),model.vx,.00002,'attacker-relative capped recoil')
 near(q('MmVY'),model.vy,.00002,'ground boost or preserved airborne VY')
 assert(r('GuestHurtKind')==2 and r('GuestHurtTicks')==15,'Source250ms recoil starts without native freeze')
 assert(r('PlayerStatus')==0 and r('PlayerChangeSizeFlag')==0 and r('TimerControl')==0 and r('GameEngineSubroutine')==8,'Normal upgrade loss keeps the world live')
 assert(r('SmBall')==0 and r('SmCrouch')==0 and r('SmFlip')==0 and r('InvSelected',2)==0,'Lost upgrades and old attack modes are cancelled')
 assert(r('Square1SoundQueue')&16~=0,'Actual impact queues injury sound')
end,emu.callbackType.exec,assert(L.GuestInjuryStarted))
emu.addMemoryCallback(function()
 if not c or not started or r('GuestHurtTicks')==0 or r('CurrentBank')%128~=10 or injuryBank~=10 or injuryDepth~=0 then return end
 -- Input only: simulate a scan arriving after the earlier pre-parser mask.
 w('SavedJoypadBits',0xe5);w('A_B_Buttons',0xc0);w('Left_Right_Buttons',1);w('Up_Down_Buttons',4);injected=injected+1
end,emu.callbackType.exec,assert(L.GuestInjuryMovement))
emu.addMemoryCallback(function()
 if not c or not model or r('CurrentBank')%128~=10 or injuryBank~=10 or injuryDepth~=0 then return end
 moves=moves+1
 assert(r('GuestHurtTicks')==15-moves,'Recovery event precedes movement at elapsed update15')
 assert(r('A_B_Buttons')==0 and r('Left_Right_Buttons')==0 and r('Up_Down_Buttons')==0,'Parsed controls remain locked after a late input receipt')
 local submerged=c.water and model.y>25
 if submerged then model.vy=math.min(model.vy,250/120)end
 -- AnimatedObject.gravityPull skips the first pull when the impact landed on
 -- ground, then clears onGround before integrating the already assigned hop.
 local gravity=(c.ground and moves==1) and 0 or (submerged and 400 or 700)/7200
 model.vy=math.min(model.vy+gravity,450/120)
 model.x=model.x+model.vx;model.y=model.y+model.vy
 near(q('MmVX'),model.vx,.002,'source recoil VX');near(q('MmVY'),model.vy,.002,'source gravity VY')
 near(x(),model.x,.025,'integrated recoil X');near(y(),model.y,.025,'integrated recoil Y')
 assert(r('PlayerFacingDir')==c.facing,'Recoil does not turn Samus')
 checks=checks+1
end,emu.callbackType.exec,assert(L.SamusHurtIntegrated))
emu.addMemoryCallback(function()
 if not c or not started or r('CurrentBank')%128~=10 or injuryBank~=10 or injuryDepth~=0 then return end
 assert(moves==14,'14 locked movements precede the elapsed250ms recovery event');ended=true
end,emu.callbackType.exec,assert(L.GuestInjuryRecovered))
for _,pool in ipairs({{'SmShotType',3},{'SmBombAge',3}})do
 emu.addMemoryCallback(function(_,v)
  if c and started and not ended and r('GuestHurtTicks')>0 then assert(v==0,'Locked injury cannot create beam, missile or bomb')end
 end,emu.callbackType.write,L[pool[1]],L[pool[1]]+pool[2]-1)
end
emu.addMemoryCallback(function(_,v)
 if c and started and not ended and r('GuestHurtTicks')>0 then assert(v==0,'Locked injury cannot select a weapon')end
end,emu.callbackType.write,L.InvSelected+2)
emu.addMemoryCallback(function(_,v)
 if not c or not ended then return end
 if v==75 and not immuneLast then immuneLast=75
 elseif immuneLast and v~=immuneLast then assert(v==immuneLast-1,'Separate post-recoil immunity advances once per update');immuneLast=v;immuneDecrements=immuneDecrements+1 end
end,emu.callbackType.write,L.GuestInvulTicks)
emu.addEventCallback(function()
 local b={}
 if frame<540 then b={right=frame==80 or frame==100,start=frame==200}
 elseif c and started then b={right=true,a=true,b=true,down=true,select=true}end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<550 then return end
 if frame==550 or setupNext then
  assert(r('SelectedCharacter')==2,'Actual menu selects Samus');setupNext=false;index=index+1;c=cases[index]
  if not c then
   assert(injected==#cases*14,'Every locked update received the late input fixture')
   print('PASS Samus2.02 source injury '..#cases..' arenas, '..checks..' independent numeric recoil updates,250ms lock,1250ms protection, actual injury cue and live world');emu.stop(0);return
  end
  setup();return
 end
 age=age+1
 if started then w('Enemy_Flag',0)end
 if started and r('GuestHurtKind')==2 then
  local elapsed=r('GuestHurtTicks')>0 and 15-r('GuestHurtTicks') or 15+75-r('GuestInvulTicks')
  assert(r('GuestFlickerPhase')==(elapsed*2)%3,'25ms flash retains its fractional phase across recoil and protection')
  assert(r('GuestHurtVisible')==1-(math.floor(elapsed*2/3)%2),'Source body visibility follows its25ms timer')
 end
 if started and not ended and r('Enemy_Flag',1)~=0 and r('Enemy_X_Position',1)~=worldX then worldLive=true end
 if ended and r('GuestInvulTicks')>0 then
  assert(r('InjuryTimer')~=0,'Native contact guard stays armed throughout protection')
  assert(r('GameEngineSubroutine')==8 and r('TimerControl')==0,'No native shrink state during source protection')
 end
 -- Finish at immunity expiration. Continuing through the original level with
 -- held controls afterwards can spawn an unrelated enemy: its new lethal hit
 -- is correct and is outside this isolated first-impact lifecycle contract.
 if ended and immuneLast==0 then
  assert(started and ended and worldLive,'Real impact, recovery and unrelated actor motion are exercised')
  assert(immuneLast==0 and immuneDecrements==75,'Full1250ms protection expires after recoil')
  print('PASS Samus injury '..c.name..' facing'..c.facing..' attacker'..c.side);setupNext=true
 end
 assert(age<150,'Samus injury fixture makes bounded progress')
end,emu.eventType.endFrame)
