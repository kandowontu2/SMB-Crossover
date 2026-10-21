-- Explicit isolated kinematic arenas, never a controller-only stage clear.
-- Pinned 2.02 Link.as movePlayer(): +/-175 immediately; neutral/both zero;
-- grounded attack zero, airborne attack retains normal direction control.
-- Character.as update() applies only the underwater-ground +/-90 cap later.
local character=SOURCE_MOVEMENT_CHARACTER or 4
local name=character==4 and 'Link' or 'Simon'
local walk=character==4 and 175 or 150
local frame,index,started,calls=0,1,false,0
local depth=0
local cases={}
for power=0,2 do
 for _,environment in ipairs({{water=false,state=0},{water=false,state=1},
                              {water=true,state=0},{water=true,state=1}})do
  for _,control in ipairs({
   {name='start-right',mask=1,seed=0},
   {name='reverse-left',mask=2,seed=walk/120},
   {name='reverse-right',mask=1,seed=-walk/120},
   {name='release',mask=0,seed=walk/120},
   {name='both',mask=3,seed=-walk/120},
   {name='sword-right',mask=1,seed=-walk/120,attack=true},
   {name='sword-release',mask=0,seed=walk/120,attack=true},
  })do
   cases[#cases+1]={name=control.name,power=power,water=environment.water,
    state=environment.state,mask=control.mask,seed=control.seed,attack=control.attack}
  end
 end
end
-- The existing real-enemy injury fixture checks native injury and recovery.
-- These four isolated dispatch cases check that the new Link controls cannot
-- overwrite an already active hurt velocity; they do not certify its trajectory.
for _,side in ipairs({-1,1})do for _,mask in ipairs({0,side<0 and 1 or 2})do
 cases[#cases+1]={name='hurt-retention',hurt=true,state=1,power=1,
  water=false,mask=mask,seed=side*(character==4 and 500 or 150)/120}
end end
if SOURCE_KINEMATICS then
 assert(character==4,'Pinned Link kinematic profile')
 cases={}
 for power=0,2 do
  for _,spec in ipairs({
   {name='dry-launch',state=0,water=false,y=176,vy=0,mask=128,launch=true},
   {name='water-launch',state=0,water=true,y=176,vy=0,mask=128,launch=true},
   {name='surface-water-room-launch',state=0,water=true,surface=true,y=0,vy=0,mask=128,launch=true},
   {name='dry-release',state=1,water=false,y=96,vy=-3,mask=0,release=true},
   {name='water-release',state=1,water=true,y=96,vy=-3,mask=0,release=true},
   {name='dry-fall-cap',state=1,water=false,y=96,vy=8,mask=0},
   {name='submerged-fall-order',state=1,water=true,y=96,vy=8,mask=0},
   {name='surface-water-room-fall-cap',state=1,water=true,surface=true,y=0,vy=8,mask=0},
   {name='no-air-rejump',state=1,water=false,y=96,vy=1.25,mask=128},
  })do
   local c={power=power,seed=0,kinematics=true}
   for k,v in pairs(spec)do c[k]=v end
   cases[#cases+1]=c
  end
 end
end
if SOURCE_SIMON_JUMPS then
 assert(character==5,'Pinned default2.02 Simon jump states')
 cases={}
 for power=0,2 do for _,water in ipairs({false,true})do
  for _,spec in ipairs({
   {name='ground-whip-jump',state=0,vy=0,mask=129,seed=-150/120,attack=true,launch=true,cancelAttack=true},
   {name='crouch-jump',state=0,vy=0,mask=132,seed=0,crouch=true,launch=true},
   {name='air-throw-double',state=1,vy=1,mask=130,seed=150/120,attack=true,kind=1,double=true,launch=true,cancelAttack=true},
   {name='no-double-keeps-attack',state=1,vy=1.25,mask=129,seed=150/120,attack=true},
  })do
   local c={power=power,water=water,kinematics=true}
   for k,v in pairs(spec)do c[k]=v end
   c.y=c.state==0 and 176 or 96
   cases[#cases+1]=c
  end
 end end
end
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function quantize(v)return math.floor(math.abs(v)*65536+.5)*(v<0 and-1 or 1)end
local function raw(n)
 local q=r(n)+r(n,1)*256+r(n,2)*65536
 return q>=0x800000 and q-0x1000000 or q
end
local function vset(n,v)
 local q=quantize(v)%0x1000000
 for i=0,2 do w(n,(q>>(8*i))&255,i)end
end
local function label(c)return c.name..' power'..c.power..' water'..tostring(c.water)..' state'..c.state end
local function fixture(c)
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,page*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 w('SelectedCharacter',character);w('PlayerStatus',c.power);w('PlayerSize',0)
 w('Player_X_Position',128);w('Player_PageLoc',0)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0)
 w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0);w('HorizontalScroll',0)
 w('Player_Y_Position',c.y or(c.state==0 and 176 or 96));w('Player_Y_HighPos',1)
 w('Player_State',c.state);w('Player_X_Speed',0);w('Player_X_Scroll',0);w('Player_Y_Speed',math.floor(c.vy or 0))
 w('MmXFraction',0);w('MmXFraction',0x40,1);vset('MmVX',c.seed);vset('MmVY',c.vy or 0)
 w('MmYFraction',0);w('MmYFraction',0,1);w('MmFrictionYActive',0)
 w('PlayerFacingDir',c.seed<0 and 2 or 1);w('Player_CollisionBits',255)
 w('AreaType',c.water and 0 or 1);w('SwimmingFlag',c.water and 1 or 0)
 w('RgAttack',c.attack and 24 or 0);w('RgAttackAge',0);w('RgAttackKind',c.kind or 0);w('RgCooldown',0)
 w('RgCrouch',c.crouch and 1 or 0);w('CrouchingFlag',c.crouch and 4 or 0);w('GuestPowerupActive',0)
 w('RgDoubleJump',c.double and 1 or 0)
 w('GameEngineSubroutine',c.hurt and 10 or 8);w('TimerControl',c.hurt and 0xef or 0)
 w('PlayerChangeSizeFlag',0);w('InjuryTimer',c.hurt and 24 or 0)
 -- Isolated button-history state specifies a fresh real A press/release;
 -- the actual controller input must already match before this setup occurs.
 if c.kinematics then w('PreviousA_B_Buttons',c.release and 128 or 0);w('MmJumpReleased',0)end
 calls=0;started=true
end
for _,pc in ipairs({assert(L.NonMaskableInterrupt),assert(L.IrqScrollSplit)})do
 emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,pc)
end
for _,pc in ipairs({assert(L.NonMaskableInterrupt_RTI),assert(L.IrqScrollSplit_RTI)})do
 emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Balanced Link-source fixture interrupt scope')end,emu.callbackType.exec,pc)
end
emu.addEventCallback(function()
 local c=frame>=550 and cases[index]or nil
 local mask=c and c.mask or 0
 emu.setInput({start=frame==200,right=(frame>=80 and frame<80+20*character and(frame-80)%20==0)or(mask&1)~=0,
  left=(mask&2)~=0,a=(mask&128)~=0,down=(mask&4)~=0},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if frame<560 or depth~=0 or r('CurrentBank')%128~=22 then return end
 assert(emu.read(L.RosterMovement,emu.memType.nesDebug)==0xad and
  emu.read(L.RosterMovement+1,emu.memType.nesDebug)==L.SelectedCharacter%256 and
  emu.read(L.RosterMovement+2,emu.memType.nesDebug)==math.floor(L.SelectedCharacter/256),'Actual ROSTER movement entry opcode')
 local c=cases[index]
 if not c then return end
 if not started and not c.hurt and(r('SavedJoypadBits')&0x87)==c.mask and
  (not c.kinematics or(r('A_B_Buttons')&128)==(c.mask&128))then fixture(c)end
 if started then calls=calls+1 end
end,emu.callbackType.exec,L.RosterMovement)
emu.addMemoryCallback(function()
 if frame<560 or depth~=0 then return end
 assert(emu.read(L.NoDecTimers,emu.memType.nesDebug)==0xe6 and
  emu.read(L.NoDecTimers+1,emu.memType.nesDebug)==L.FrameCounter,'Actual completed-foreground update boundary')
 local c=cases[index]
 if started then
  local expected=0
  if c.hurt then
   expected=c.seed
   assert(calls==0,'Hurt state bypasses normal Link controls: '..label(c))
  else
   assert(calls==1,'Exactly one actual Link movement update: '..label(c))
   local state=c.launch and 1 or c.state
   local speed=c.water and state==0 and 90 or walk
   local direction=c.mask&3
   if not(c.attack and state==0)then
    expected=direction==1 and speed/120 or direction==2 and-speed/120 or 0
   end
  end
  assert(raw('MmVX')==quantize(expected),'2.02 direct horizontal velocity '..label(c)..': '..(raw('MmVX')/65536)..' / '..expected)
  if not c.hurt then
   local facing=c.seed<0 and 2 or 1
   local state=c.launch and 1 or c.state
   local direction=c.mask&3
   if not(c.attack and state==0)and(character==4 or state==0 or c.launch)and(direction==1 or direction==2)then facing=direction end
   assert(r('PlayerFacingDir')==facing,'Source direction changes only with permitted directional movement: '..label(c))
   local position=(r('Player_X_Position')+256*r('Player_PageLoc'))*65536+r('MmXFraction')+256*r('MmXFraction',1)
   assert(position==128*65536+0x4000+quantize(expected),'Source equation integrates exactly one update: '..label(c))
   if c.kinematics then
    local jump=character==4 and(c.water and 500 or 600)or 550
    local vy=c.launch and-jump/120 or c.vy
    if c.release and character==4 then vy=vy*(0.0001)^(1/60)end
    if c.water and not c.surface and vy>250/120 then vy=250/120 end
    local gravity=character==4 and(c.water and not c.surface and 500 or 1300)or(c.water and 750 or 1500)
    vy=vy+gravity/7200
    if vy>0 and character==4 then vy=math.min(vy,(c.water and 500 or 800)/120)end
    assert(math.abs(raw('MmVY')/65536-vy)<0.0002,name..'2.02 source vertical equation '..label(c)..': '..(raw('MmVY')/65536)..' / '..vy)
    local py=(r('Player_Y_Position')+256*(r('Player_Y_HighPos')-1))*65536+r('MmYFraction')+256*r('MmYFraction',1)
    assert(math.abs(py/65536-c.y-vy)<0.0002,'Link2.02 vertical trajectory '..label(c))
    if c.launch then assert(r('Player_State')~=0,'Real fresh A launches the isolated grounded actor')end
    if c.release then assert(r('MmFrictionYActive')~=0,'Fresh A release enables source upward friction')end
    if SOURCE_SIMON_JUMPS then
     assert((r('RgAttack')==0)==(not c.attack or c.cancelAttack==true),'A valid Simon jump cancels whip/throw; rejected jump retains it: '..label(c))
     if c.double then assert(r('RgDoubleJump')==0,'A real second A consumes the one double jump')end
    end
   end
  end
  index=index+1;started=false;w('GameEngineSubroutine',8);w('TimerControl',0);w('InjuryTimer',0)
  if index>#cases then
   print('PASS '..name..'2.02 '..(SOURCE_KINEMATICS and 'source vertical equations' or SOURCE_SIMON_JUMPS and 'jump, double-jump and attack cancellation states' or 'source horizontal equations and hurt retention')..': '..#cases..' cases');emu.stop(0);return
  end
  c=cases[index]
 end
 if c and c.hurt and not started and(r('SavedJoypadBits')&3)==c.mask then fixture(c)end
end,emu.callbackType.exec,L.NoDecTimers)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then assert(r('SelectedCharacter')==character and r('GameEngineSubroutine')==8,'Real menu launches '..name..' before isolated movement arenas')end
 if frame>1800 then assert(false,'Link source movement fixture watchdog, case'..index)end
end,emu.eventType.endFrame)
