-- Source2.02 body rules. Every case is an explicit flat arena with initial
-- actor health/positions; real Down+A pays for the attack. No outcome or
-- program-flow writes, no ordinary-controller progression claim.
local char=BODY_CHARACTER or 1
local cases={
 {name='ordinary-fall-small',fall=true,power=0,hurt=true},
 {name='ordinary-fall-mushroom',fall=true,power=1,hurt=true},
 {name='ordinary-fall-full',fall=true,power=2,hurt=true},
 {name='ordinary-fall-invulnerable',fall=true,power=1,invul=true},
 {name='selected-standing',selected=5,power=1,hurt=true,injuryHP=100},
 {name='empty-energy-slide',kick=true,ammo=0,power=1,hurt=true,injuryHP=100},
 {name='paid-last-energy',kick=true,ammo=4,power=1,expectedHP=25,continuous=true},
 {name='paid-full-power',kick=true,ammo=4,power=2,expectedHP=25},
 {name='paid-beetle-armor',kick=true,ammo=4,power=1,enemy=2,expectedHP=100,graphic=true},
 {name='paid-bullet-armor',kick=true,ammo=4,power=1,enemy=8,expectedHP=100,graphic=true},
 {name='paid-spiny-body',kick=true,ammo=4,power=1,enemy=18,expectedHP=25},
 {name='paid-lava-projectile',kick=true,ammo=4,power=1,enemy=12,hp=255,hurt=true},
 {name='paid-bowser-projectile',kick=true,ammo=4,power=1,enemy=21,hp=255,hurt=true},
 {name='switch-away-back',kick=true,ammo=8,power=1,switch=true,hurt=true,expectedAmmo=4,injuryHP=100},
 {name='protection-ends-with-slide',kick=true,ammo=4,power=1,late=true,hurt=true},
 {name='contact-gap-rearms',kick=true,ammo=4,power=1,reenter=true,expectedHP=0},
 {name='bowser-rear-only',kick=true,ammo=4,power=1,boss='rear',enemy=45,hp=600,expectedHP=525},
 {name='bowser-both-halves',kick=true,ammo=4,power=1,boss='both',enemy=45,hp=600,expectedHP=525},
 {name='ordinary-stationary-shell',power=1,shell=true,expectedKickHP=100},
 {name='paid-stationary-shell',kick=true,ammo=4,power=1,shell=true,expectedKickHP=25},
 {name='paid-armored-shell',kick=true,ammo=4,power=1,shell=true,enemy=2,expectedKickHP=100},
 {name='paid-wounded-shell-defeat',kick=true,ammo=4,power=1,shell=true,hp=25,expectedHP=0,forbidKick=true},
}
local frame,age,index,completed=0,0,0,0
local c,body,stomps,injury,graphic,paid,seenAmmo,seenSlide,injuryHP,deflected,contactSlots,kickHP
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function active()return r('MmSliding')~=0 or r('XgDash')~=0 end
local function target(on,far)
 if not on then w('Enemy_Flag',0);return end
 local x=r('Player_X_Position')+256*r('Player_PageLoc')+(c.dir==1 and(far and 90 or 8)or-(far and 90 or 8))
 w('Enemy_X_Position',x);w('Enemy_PageLoc',math.floor(x/256));w('Enemy_Y_Position',184);w('Enemy_Y_Speed',0);w('Enemy_X_Speed',0)
end
local function setup()
 age=0;body=0;stomps=0;injury=false;graphic=false;paid=false;seenSlide=false;seenAmmo=nil;injuryHP=nil;deflected=false;contactSlots=0;kickHP=nil
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_State',0,i);w('MmEnemyHealthLo',0,i);w('MmEnemyHealthHi',0,i);w('Enemy_CollisionBits',0,i);w('AvFrozen',0,i);w('AvFrozenHi',0,i);w('RgEnemyStun',0,i)end
 for i=0,9 do w('RgShotType',0,i);w('SsHidden',0,i)end
 for i=0,3 do w('MmBulletType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i);w('MmSlideTravel',0,i)end
 w('Player_X_Position',c.dir==1 and 64 or 192);w('Player_PageLoc',1);w('Player_Y_Position',c.fall and 158 or 176);w('Player_Y_HighPos',1)
 w('Player_State',c.fall and 2 or 0);w('Player_Y_Speed',c.fall and 2 or 0);w('Player_X_Speed',0);w('PlayerFacingDir',c.dir);w('Player_CollisionBits',3)
 w('PlayerStatus',c.power);w('PlayerSize',0);w('InvOwnedLo',255,char);w('InvSelected',c.kick and 5 or c.selected or 0,char);w('InvAmmo',c.ammo or 112,char*16+5);w('InvDirty',1)
 w('InjuryTimer',c.invul and 20 or 0);w('StompTimer',c.fall and 3 or 0);w('GameEngineSubroutine',8);w('TimerControl',0);w('MmDeathFlag',0);w('MmDeathAge',0);w('GuestPowerupActive',0);w('StarInvincibleTimer',0)
 w('EnemyFrenzyBuffer',0);w('EnemyFrenzyQueue',0)
 if L.GuestHurtKind then
  w('GuestHurtKind',0);w('GuestHurtTicks',0);w('GuestInvulTicks',0)
 end
 w('MmSliding',0);w('XgDash',0);w('XgBassDashJump',0);w('SsKick',0);w('SsFreeze',0);w('SsBodyStop',0);w('PreviousA_B_Buttons',0);w('A_B_Buttons',0);w('RgPreviousButtons',0);w('MmJumpReleased',0);w('MmSlideStop',0);w('RgCooldown',0)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',1);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',1)
 -- The arena's two authored pages stay fixed; ordinary camera streaming would
 -- otherwise replace the flat floor with the real level's next pipe mid-case.
 w('ScrollLock',1);w('AreaParserTaskNum',0)
 if c.fall then w('MmVY',2,2);w('MmFrictionYActive',0)end
end
local function spawn()
 w('Enemy_Flag',1);w('Enemy_ID',c.enemy or(c.fall and 6 or 0));w('Enemy_State',c.shell and 4 or 0);w('EnemyIntervalTimer',255);w('Enemy_Y_HighPos',1);w('Enemy_Y_MoveForce',0);w('Enemy_X_MoveForce',0);w('BowserFlamePRandomOfs',0);w('Enemy_BoundBoxCtrl',9);w('Enemy_MovingDir',c.dir==1 and 2 or 1)
 local hp=c.hp or(c.fall and 75 or 100);w('MmEnemyHealthLo',hp);w('MmEnemyHealthHi',math.floor(hp/256));target(true,false)
 if c.boss then
  w('Enemy_Flag',0x80,1);w('Enemy_ID',45,1);w('Enemy_State',0,1);w('Enemy_Y_HighPos',1,1);w('Enemy_PageLoc',1,1);w('Enemy_BoundBoxCtrl',10,1)
  w('BowserFront_Offset',0);w('DuplicateObj_Offset',1);w('BowserHitPoints',5);w('BowserBodyControls',0);w('BowserFeetCounter',255);w('BowserMovementSpeed',0);w('BowserOrigXPos',r('Enemy_X_Position'));w('MaxRangeFromOrigin',32);w('EnemyFrameTimer',255);w('BowserFireBreathTimer',255)
 end
end
-- Pin only boss AI placement/facing. Native front/rear body boxes, duplicate
-- dispatch, canonical health and contact decisions still execute normally.
emu.addMemoryCallback(function()
 if not c or not c.boss or age<18 or r('CurrentBank')%128~=0 or r('Enemy_State')~=0 then return end
 local offset=c.boss=='rear'and(c.dir==1 and-24 or 24)or(c.dir==1 and-4 or 12)
 if age>=26 then offset=c.dir==1 and 90 or-90 end
 local x=r('Player_X_Position')+256*r('Player_PageLoc')+offset
 w('Enemy_X_Position',x);w('Enemy_PageLoc',math.floor(x/256));w('Enemy_Y_Position',176);w('Enemy_Y_HighPos',1);w('Enemy_MovingDir',c.dir==1 and 2 or 1)
end,emu.callbackType.exec,L.BowserGfxHandler)
emu.addMemoryCallback(function()if c then body=body+1;contactSlots=contactSlots|(1<<r('ObjectOffset'))end end,emu.callbackType.exec,L.HandlePECollisions)
emu.addMemoryCallback(function()if c then stomps=stomps+1 end end,emu.callbackType.exec,L.EnemyStomped)
emu.addMemoryCallback(function()if c and not injuryHP then injuryHP=r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi');if BODY_TRACE then print('BODY_INJURY case'..index..' slot'..r('ObjectOffset')..' age'..age..' kick'..r('SsKick')..' slide'..r('MmSliding')..' dash'..r('XgDash')..' type'..r('Enemy_ID',r('ObjectOffset'))..' enemyState'..r('Enemy_State',r('ObjectOffset'))..' enemyX'..r('Enemy_X_Position',r('ObjectOffset'))..' frenzy'..r('EnemyFrenzyBuffer')..' hp'..injuryHP..' x'..r('Player_X_Position'))end end end,emu.callbackType.exec,L.InjurePlayer)
emu.addMemoryCallback(function(_,v)if c and v==26 then deflected=true end end,emu.callbackType.write,L.SsAudioRequest)
emu.addEventCallback(function()
 emu.setInput({down=(char==9 and frame==80)or(c and c.kick and age>=10 and age<14),right=(char==1 and frame==80)or(char==9 and(frame==100 or frame==120 or frame==140)),start=frame==200,a=c and c.kick and age>=10 and age<14},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<550 then return end
 if frame==550 then assert(r('SelectedCharacter')==char,'Actual character menu');index=BODY_FIRST or 1;c=cases[index];c.dir=1;setup();return end
 age=age+1
 if BODY_TRACE and index>=19 and age%2==0 and age<75 then print('BODY_STATE case'..index..' age'..age..' hp'..r('MmEnemyHealthLo')..' state'..r('Enemy_State')..' kick'..r('SsKick')..' slide'..r('MmSliding')..' dash'..r('XgDash')..' x'..r('Player_X_Position')..' y'..r('Player_Y_Position')..' enemyx'..r('Enemy_X_Position')..' engine'..r('GameEngineSubroutine')..' prev'..r('GuestBodyPrev')..' now'..r('GuestBodyNow'))end
 if r('PlayerStatus')~=c.power or r('GameEngineSubroutine')==10 or r('GameEngineSubroutine')==11 then injury=true end
 if c.shell and r('Enemy_Flag')~=0 and r('Enemy_State')&128~=0 and not kickHP then kickHP=r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')end
 if active()then
  seenSlide=true
  if c.kick and c.ammo and c.ammo>=4 and age>=14 and age<40 and r('InvAmmo',char*16+5)==c.ammo-4 then paid=true end
  for i=0,9 do if r('RgShotType',i)==19 then graphic=true end end
 end
 if c.switch then if age==14 then w('InvSelected',0,char)elseif age==16 then w('InvSelected',5,char)end end
 local born=c.late and 80 or c.kick and 18 or 1
 if c.graphic and body>0 and age>=born and age<born+24 and active()then
  local visible=false;for i=0,9 do if r('RgShotType',i)==19 then visible=true end end
  assert(visible,'The paid kick graphic persists after every armored body contact')
 end
 if age==born then spawn()end
 if age>=born and r('Enemy_Flag')~=0 then
  if c.continuous or c.reenter or c.graphic or c.enemy==12 or c.enemy==21 then
   -- Keep contact inside the real62.5NES-pixel source slide lifetime.
   -- A separate late-contact case verifies that protection ends with it.
   local far=age>=29 or(c.reenter and age>=22 and age<25)
   if not c.reenter then far=age>=26 end
   target(true,far)
  end
 end
 if age==100 then
  assert(body>0,'Actual native body overlap exercised: '..c.name..' direction'..c.dir)
  assert(stomps==0,'Source canStomp=false: '..c.name..' direction'..c.dir..' native stomps='..stomps)
  assert(injury==not not c.hurt,'Source body injury/protection: '..c.name..' direction'..c.dir..' injury='..tostring(injury))
  if not c.hurt then assert(r('PlayerStatus')==c.power,'Protected contact retains power')end
  if c.invul then assert(r('MmEnemyHealthLo')==75 and r('Enemy_State')&32==0,'Hurt invulnerability never turns into an ordinary stomp')end
  if c.kick then
   assert(seenSlide,'Real Down+A started slide/dash: '..c.name)
   if c.ammo>=4 then assert(paid,'Exactly4 energy funded this real ChargeKick: '..c.name)end
  end
  if c.boss then assert(contactSlots==(c.boss=='rear'and 2 or 3),'Actual intended Bowser body halves touched: '..c.name..' slots'..contactSlots)end
  if c.forbidKick then assert(kickHP==nil,'A shell defeated by the attack is not kicked or passed to native injury')end
  if c.expectedKickHP then assert(kickHP==c.expectedKickHP,'Stationary shell still kicks after source body attack: '..c.name..' kickHP'..tostring(kickHP))end
  if c.injuryHP then assert(injuryHP==c.injuryHP,'Unpaid body contact never deals virtualkick damage: '..c.name..' injuryHP'..tostring(injuryHP))end
  if c.expectedAmmo then assert(r('InvAmmo',char*16+5)==c.expectedAmmo,'Weapon switch does not repurchase old slide')end
  if c.expectedHP then
   local hp=r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')
   if c.expectedHP==0 then assert(r('Enemy_Flag')==0 or r('Enemy_State')&32~=0,'The source body attack defeats this target without ordinary stomp handling: '..c.name)
   else assert(hp==c.expectedHP,'Source damage/continuous-contact/armor: '..c.name..' hp'..hp..' expected'..c.expectedHP)end
  end
  if c.graphic then assert(graphic and not deflected,'Armored body contact keeps kick visual without projectile deflection cue')end
  completed=completed+1
  print('PASS MM/Bass source bodycontact char'..char..' '..c.name..' direction'..c.dir)
  if c.dir==1 then c.dir=2 else index=index+1;c=index<=(BODY_LAST or #cases)and cases[index]or nil;if c then c.dir=1 end end
  if not c then print('PASS MM/Bass '..completed..' source contact cases, ordinary injury, paidlastenergy, armor, hostileprojectiles, contactcadence and weaponexit');emu.stop(0)else setup()end
 end
end,emu.eventType.endFrame)
