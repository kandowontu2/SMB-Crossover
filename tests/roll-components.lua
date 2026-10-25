-- Real menu/controller inputs; deliberately seeded and positioned arenas.
local t,wall,entered=0,0,false;local pending={};local peak=0;local charged=false;local palette=false
local captures=0;local lifeBefore;local pickupSeen=false;local blockCamera;local blockPlayer
local deathSeen=false;local respawnAt;local respawnX;local startLives
local headAt
local trace=assert(io.open(OUTPUT..'injury-timeline.csv','w'))
trace:write('t,hp,invul,injury,death,engine,lives,x,y,state,enemyFlag,enemyState,enemyX,enemyY,collision\n')
local bodyObserver=dofile(ROLL_OBSERVER_PATH or TEST_DIR..'../tools/audit/roll_render_observer.lua')({out=OUTPUT})
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)pending[#pending+1]={assert(L[n],n)+(i or 0),v&255}end
local function bank(a)return emu.convertAddress(a).address//8192 end
local function shot(n)local f=assert(io.open(OUTPUT..n..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
local menu=dofile(ROLL_MENU_PATH or TEST_DIR..'roll-menu.lua')(r,ROLL_HARD or false,ROLL_OUTLINES or false)
local performance
if ROLL_PROFILE then
 performance=dofile(ROLL_PERFORMANCE_PATH)({out=OUTPUT,phase=function()
  if t<90 then return'pellets'elseif t<220 then return'charge'elseif t<390 then return'block'
  elseif t<500 then return'capsules'elseif t<580 then return'jump'elseif t<610 then return'left-fire'
  elseif t<690 then return'hurt'elseif headAt then return'head'else return'death-respawn'end
 end})
end
emu.addMemoryCallback(function()
 if entered and bank(0xa000)==B.PlayerRemoveOutlines then assert(r('SelectedCharacter')~=9 or r('RlVariant')==0,'Roll own outline records never enter the legacy cached mask buffer')end
end,emu.callbackType.exec,L.PlayerRemoveOutlines)
emu.addMemoryCallback(function()
 if entered then local b=bank(0xa000);assert(b==B.RlEnsure or b==B.X5ColdInit or b==B.MenuResolveCharacter,'Dedicated outline ownership byte is not overwritten by another native subsystem')end
end,emu.callbackType.write,L.RlOutlineBypass)
emu.addMemoryCallback(function()
 if not entered or bank(0xa000)~=B.RlFrameReady then return end
 for _,p in ipairs(pending)do emu.write(p[1],p[2],emu.memType.nesDebug)end;pending={}
end,emu.callbackType.exec,L.RlFrameReady)
local function arena()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for i=176,207 do w('Block_Buffer_1',0x54,i);w('Block_Buffer_1',0x54,208+i)end
 for i=0,5 do
  w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i)
  -- A reused object is a new contact, as in native enemy initialization.
  w('Enemy_CollisionBits',0,i)
 end
 for i=0,3 do w('MmBulletType',0,i);w('InvDropKind',0,i)end
 for _,n in ipairs({'TimerControl','GamePauseStatus','InjuryTimer','StarInvincibleTimer','GuestHurtTicks','GuestHurtKind','MmDeathFlag','AreaParserTaskNum','ScrollThirtyTwo','EnemyFrenzyBuffer','EnemyFrenzyQueue','BlockBounceTimer'})do w(n,0)end
 w('ScrollLock',1);w('CheatInvincible',0);w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_X_Position',72);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
 w('Player_X_Speed',0);w('Player_Y_Speed',0);w('MmVX',0);w('MmVX',0,1);w('MmVX',0,2);w('MmVY',0);w('MmVY',0,1);w('MmVY',0,2)
 w('RlCharge',0);w('RlPrevious',0);w('RlHurt',0);w('RlInvul',0);w('GameEngineSubroutine',8);w('OperMode',1)
end
emu.addEventCallback(function()
 local b={}
 if not entered then
  b=menu(wall)
 else
  b.b=(t>=20 and t<23)or(t>=28 and t<31)or(t>=36 and t<39)or(t>=44 and t<47)or(t>=100 and t<195)or(t>=230 and t<325)
  b.a=(t>=505 and t<509)or(t>=522 and t<526)
  b.down=t>=505 and t<509
  b.select=t>=555 and t<559
  b.left=t>=580 and t<583
  if t>=585 and t<588 then b.b=true end
  b.right=respawnAt and not headAt and t>respawnAt
  if headAt then b.a=t>=headAt+10 and t<headAt+40 end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1
 if not entered then
  if r('OperMode')==1 and r('GameEngineSubroutine')==8 then entered=true;t=0 end
  assert(wall<1100,'Roll cold menu entry');return
 end
 t=t+1
 if t>=600 then
  trace:write(table.concat({t,r('RlHealth'),r('RlInvul'),r('InjuryTimer'),r('MmDeathFlag'),r('GameEngineSubroutine'),r('NumberofLives'),r('Player_X_Position'),r('Player_Y_Position'),r('Player_State'),r('Enemy_Flag'),r('Enemy_State'),r('Enemy_X_Position'),r('Enemy_Y_Position'),r('Enemy_CollisionBits')},',')..'\n');trace:flush()
 end
 assert(r('MmSliding')==0 and r('XgDash')==0 and r('XgJumpUsed')==0,'Roll inherits no Bass slide/dash/double-jump state')
 if t==1 then arena()end
 if t>=20 and t<80 then local n=0;for i=0,3 do if r('MmBulletType',i)==1 then n=n+1 end end;peak=math.max(peak,n);assert(n<=3,'Three ordinary buster shots maximum')end
 if t==82 then assert(peak==3,'Three ordinary shots actually coexist')end
 if t==90 then arena();w('RlEnergy',28);w('RlHealth',28)end
 if t>=100 and t<=200 then
  for i=0,3 do if r('MmBulletType',i)==3 then charged=true end end
 end
 if t==180 then
  assert(r('RlChargeFired')>=1 and r('RlEnergy')==24,'Full charge automatically fires and spends4energy')
  assert(charged,'Charge projectile enters the actual world')
  assert(emu.read(0x3f11,emu.memType.nesPpuDebug)==0x1a and emu.read(0x3f12,emu.memType.nesPpuDebug)==0x28 and emu.read(0x3f13,emu.memType.nesPpuDebug)==0x24,'Roll bow, gold and charge palette survives gameplay and charged fire')
  shot('charge')
 end
 if t==220 then
  arena();w('Player_Y_Position',112);w('Block_Buffer_1',0x54,116);w('Block_Buffer_1',0x54,117);w('Block_Buffer_1',0xc1,103);w('Block_Buffer_1',0x54,104)
  blockCamera=r('ScreenLeft_X_Pos');blockPlayer=72
 end
 if t==335 then
  assert(r('Block_Buffer_1',103)==0xc4,'Actual buster activates a native question block')
  assert(r('Block_Buffer_1',104)==0x54,'Question block attack preserves adjacent ground')
  assert(r('ScreenLeft_X_Pos')==blockCamera and r('Player_X_Position')==blockPlayer,'Block hit does not displace player or camera')
  for i=0,5 do if r('Enemy_Flag',i)~=0 and r('Enemy_ID',i)==0x2e then pickupSeen=true end end
  assert(pickupSeen,'Question-block reward actually emerges')
  shot('block-reward')
 end
 if t==345 then
  -- Relocate the actor/player only after native emergence. Collision and
  -- pickup delivery remain real; this is explicitly an authored arena.
  for i=0,5 do if r('Enemy_Flag',i)~=0 and r('Enemy_ID',i)==0x2e then
   w('Player_X_Position',r('Enemy_X_Position',i));w('Player_PageLoc',r('Enemy_PageLoc',i));w('Player_Y_Position',r('Enemy_Y_Position',i)-8)
  end end
  w('RlHealth',12);w('RlEnergy',8)
 end
 if t==370 then assert(r('RlHealth')==28 and r('RlEnergy')==28,'Physical native block reward restores health and charge energy');shot('restored')end
 if t==390 then
  arena();w('InvDropKind',1);w('InvDropX',80);w('InvDropPage',0);w('InvDropY',192);w('InvDropVY',0);w('InvDropVYMid',0);w('InvDropVYHi',0);w('AvDropItem',0);w('RlEnergy',12)
 end
 if t==415 then assert(r('RlEnergy')==14,'Physical small energy capsule restores2')end
 if t==430 then
  w('InvDropKind',2);w('InvDropX',80);w('InvDropPage',0);w('InvDropY',192);w('InvDropVY',0);w('InvDropVYMid',0);w('InvDropVYHi',0);w('AvDropItem',128);w('RlHealth',12)
 end
 if t==455 then assert(r('RlHealth')==22,'Physical large health capsule restores10')end
 if t==500 then arena()end
 if t==520 then lifeBefore=r('MmVY',2)end
 if t==529 then assert(r('MmVY',2)>=lifeBefore,'A second airborne A press does not restart a jump')end
 if t==575 then assert(r('RlVariant')==1 and r('InvSelected',9)==0,'Gameplay Select does not equip Bass weapons or change her identity')end
 if t==595 then
  local left=false;for i=0,3 do if r('MmBulletType',i)==1 and r('MmBulletDir',i)==2 then left=true end end
  assert(left,'Turning left fires a real left-facing buster projectile');shot('left-buster')
 end
 if t==610 or t==690 then
  arena();w('RlHealth',t==610 and 28 or 4)
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
  w('Enemy_X_Position',72);w('Enemy_PageLoc',0);w('Enemy_Y_Position',184);w('Enemy_Y_HighPos',1);w('Enemy_X_Speed',0)
  if t==690 then startLives=r('NumberofLives')end
 end
 if t==635 then assert(r('RlHealth')==24 and r('RlInvul')>0,'A real Goomba body contact removes4HP and starts protection');shot('hurt')end
 if t==640 then w('Enemy_Flag',0)end
 if t==715 then assert(r('MmDeathFlag')~=0,'Lethal real contact enters native death');deathSeen=true end
 if t==750 then shot('death')end
 if deathSeen and not respawnAt and r('MmDeathFlag')==0 and r('GameEngineSubroutine')==8 and r('NumberofLives')==startLives-1 then respawnAt=t;respawnX=r('Player_X_Position')end
 if respawnAt and t>=respawnAt+25 and r('Player_X_Position')>respawnX+8 then
  assert(r('MmDeathFlag')==0,'Component arenas remain playable')
  assert(r('RlHealth')==28 and r('RlEnergy')==28 and r('RlVariant')==1,'Real life-loss restores health/energy and retains Roll')
  if not headAt then
   headAt=t;arena()
   w('Player_X_Position',79);w('Player_PageLoc',1);w('Player_Y_Position',176)
   w('ScreenLeft_X_Pos',220);w('ScreenRight_X_Pos',219);w('ScreenRight_PageLoc',1)
   w('Block_Buffer_1',0x51,324);w('Block_Buffer_1',0xc1,325);w('Block_Buffer_1',0x51,326)
   w('MmXFraction',0);w('MmXFraction',0,1)
  end
 end
 if headAt and t==headAt+70 then
  assert(r('Player_X_Position')==79 and r('Player_PageLoc')==1,'A real head bump between adjacent blocks never shifts Roll sideways')
  assert(r('Block_Buffer_1',325)==0xc4,'Real head bump activates the correct native question block')
  assert(r('Block_Buffer_1',324)==0x51 and r('Block_Buffer_1',326)==0x51,'Head bump preserves both adjacent bricks')
  shot('head-bump')
  local f=assert(io.open(OUTPUT..'roll-proof.json','w'));f:write('{"passed":true,"peakNormalShots":'..peak..',"charged":true,"physicalBlockReward":true,"physicalHealthAndEnergy":true,"realInjuryAndLifeLoss":true,"headBumpNoShift":true,"adjacentBricksPreserved":true,"respawnFrame":'..respawnAt..',"scope":"Cold menu, controller buster/autocharge, authored native block/reward arena, physical restore capsules, real damage/death/respawn and real head bump. No all-powerup/campaign/mobile-timing/audio-parity claim."}');f:close()
  if performance then performance.finish()end
  bodyObserver.finish();trace:close();print('PASS Roll physical ability components');emu.stop(0)
 end
 assert(wall<3000,'Bounded Roll components')
end,emu.eventType.endFrame)
