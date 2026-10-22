-- Numeric reference fixtures in the actual 2-2 water room. These use explicit
-- state setup and are not presented as controller-only level clears.
local character=assert(WATER_CHARACTER)
local frame=0
local gravity=({350,500,400,500,500,750})[character+1]/7200
local dryGravity=({700,1500,700,1000,1300,1500})[character+1]/7200
local jump=({200,560,500,550,500,550})[character+1]/120
-- Bill's fixtures are placed airborne without a jump, so the source keeps his
-- upright main HRect (31.5); only an actual jump publishes the16.25 form.
local surface=({15.75,27.5,25,31.5,15,25})[character+1]
local beforeRelease
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
local function velocity(n) local a=r(n)+r(n,1)*256+r(n,2)*65536;if a>=0x800000 then a=a-0x1000000 end;return a/65536 end
local function vset(n,v) local a=math.floor(v*65536+.5)%0x1000000;for i=0,2 do w(n,(a>>(i*8))&255,i) end end
local function fixture(y,state,vy)
 w('Player_X_Position',40);w('Player_PageLoc',0);w('Player_Y_Position',math.floor(y));w('Player_Y_HighPos',1)
 local fraction=math.floor((y%1)*65536+.5);w('MmYFraction',fraction&255);w('MmYFraction',(fraction>>8)&255,1)
 w('MmXFraction',0);w('MmXFraction',0,1);vset('MmVX',0);vset('MmVY',vy or 0)
 w('Player_X_Speed',0);w('MmLastXSpeed',0);w('Player_Y_Speed',math.floor(vy or 0)%256);w('Player_State',state)
 w('MmFrictionYActive',0);w('MmJumpReleased',0);w('MmSliding',0);w('SmBall',0);w('SmCrouch',0);w('RgDoubleJump',0);w('RgAttack',0);w('RgCrouch',0)
 w('A_B_Buttons',0);w('PreviousA_B_Buttons',0)
 if character==1 then w('MmStepTimer',0);w('MmPreviousDir',0) end
end
emu.addEventCallback(function()
 emu.setInput({start=frame==200,
  a=frame==610 or (frame>=640 and frame<660) or frame==670 or (character==1 and frame==820),down=frame>=820 and frame<850 and(character~=2 or frame~=821),
  b=frame==825 or (frame>=1040 and frame<1070),right=(frame>=80 and frame<80+20*character and (frame-80)%20==0) or (frame>=560 and frame<580) or (frame>=1040 and frame<1070)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==199 then w('WorldNumber',1);w('LevelNumber',1);w('AreaNumber',2) end
 if frame>=540 then for i=0,5 do w('Enemy_Flag',0,i);w('Whirlpool_PageLoc',0,i) end end
 if frame==550 then
  assert(r('SelectedCharacter')==character and r('AreaType')==0 and r('SwimmingFlag')==1 and r('GameEngineSubroutine')==8,'Real 2-2 water room initialized')
  if character==1 then assert(r('MmAudioCurrentSong')==3,'Water uses Bubble Man music')
  elseif character==2 then assert(r('SmAudioCurrent')==16,'Water uses the native Metroid water track')
  elseif character>=3 then assert(r('RgAudioSong')==({[3]=0x36,[4]=0x80,[5]=0x30})[character],'Character-specific water music') end
  fixture(176,0,0)
 end
 if frame==560 then fixture(176,0,0) end
 if frame>=561 and frame<=580 then
  local n=frame-560
  -- HARD (2.02) Mario: unpulled source acceleration350; EASY keeps400.
  local acceleration=character==0 and 350/7200 or 600/7200
  local expected=character==0 and math.min(.75,n*acceleration) or .75
  if character==1 then expected=n<=6 and 0 or .75 end
  assert(math.abs(velocity('MmVX')-expected)<.002,'Water ground speed/acceleration at '..frame..': '..velocity('MmVX')..' / '..expected)
 end
 if frame==590 then print('PASS water '..character..' ground speed and source acceleration') end
 if frame==610 then fixture(100,1,0) end
 if frame==611 then
  local expected=character==0 and -jump+gravity or gravity
  assert(math.abs(velocity('MmVY')-expected)<.002,'Only Mario paddles in mid-water: '..velocity('MmVY')..' / '..expected)
 end
 if frame==640 then fixture(176,0,0) end
 if frame>=641 and frame<=650 then
  local expected=-jump+(frame-640)*gravity
  assert(math.abs(velocity('MmVY')-expected)<.002,'Source underwater launch and gravity at '..frame..': '..velocity('MmVY')..' / '..expected)
 end
 if frame==655 then print('PASS water '..character..' character-specific jump and mid-water input rules') end
 if frame==650 and character==0 then assert(r('PlayerAnimTimerSet')==4 or r('PlayerAnimTimerSet')==5,'Mario uses the source moderate swim animation timing') end
 if frame==660 then beforeRelease=velocity('MmVY') end
 if frame==661 then
  local friction=1
  -- HARD (2.02) Mario releases with FY=.000001; EASY Mario keeps .0001.
  if character==0 or character==1 then friction=(.000001)^(1/60)
  elseif character==2 or character==4 then friction=(.0001)^(1/60) end
  local expected=beforeRelease<0 and beforeRelease*friction+gravity or beforeRelease+gravity
  assert(math.abs(velocity('MmVY')-expected)<.002,'Source jump-release friction underwater: '..velocity('MmVY')..' / '..expected..' from '..beforeRelease)
 end
 if frame==671 then
  if character==0 or character==5 then assert(math.abs(velocity('MmVY')+jump-gravity)<.002,'Mario re-paddles; Simon uses his single second jump')
  else assert(math.abs(velocity('MmVY')+jump-gravity)>.2,'Guest cannot re-jump while suspended in water') end
 end
 if frame==700 then fixture(100,1,3) end
 -- Mario's source updateLoc instead caps400 after gravity.
 if frame==701 then
  local fall=character==0 and math.min(3+gravity,400/120) or 250/120+gravity
  assert(math.abs(velocity('MmVY')-fall)<.002,'Shared water fall cap precedes gravity: '..velocity('MmVY')) end
 if frame==730 then fixture(surface,1,0) end
 if frame==731 then
  assert(r('MmUnderwater')==0,'Exact hitbox surface equality is above water')
  assert(math.abs(velocity('MmVY')-dryGravity)<.002,'Above-water gravity')
 end
 if frame==740 then fixture(surface+1/65536,1,0) end
 if frame==741 then
  assert(r('MmUnderwater')==1,'A fractional pixel below the pose-specific waterline is submerged')
  assert(math.abs(velocity('MmVY')-gravity)<.002,'Submerged gravity at the surface')
 end
 if frame==760 then fixture(240,1,0);w('Player_Y_HighPos',0) end
 if frame==761 then assert(r('MmUnderwater')==0,'Offscreen upward Y wrap cannot become underwater') end
 if frame==780 then if character==2 then w('InvOwnedLo',2,2);w('PlayerStatus',1);end;
  print('PASS water '..character..' hitbox/fraction surface boundary and fall cap')
  fixture(176,0,0);w('PlayerStatus',2)
 end
 if frame==820 then fixture(176,0,0) end
 if frame==831 then
  if character==1 then assert(r('MmSliding')==1 and math.abs(velocity('MmVX'))==1.875,'Underwater slide retains its 225 Flash px/s override')
  elseif character==2 then
   assert(r('SmBall')==1,'Morph Ball remains available underwater')
   local bombs=0;for i=0,2 do if r('SmBombAge',i)>0 then bombs=bombs+1 end end
   assert(bombs==1,'Morph Ball plants a bomb underwater')
  elseif character==3 then
   local shots=0;for i=0,9 do if r('RgShotType',i)>0 then shots=shots+1 end end
   assert(shots>=5,'Water crouch spread shot is available')
  elseif character>=4 then assert(r('RgAttack')>0,'Melee remains available underwater') end
  local f=assert(io.open(OUTPUT..ROM_NAME..'-water-'..character..'.png','wb'));f:write(emu.takeScreenshot());f:close()
 end
 if frame==870 then
  fixture(120,1,0);w('Player_PageLoc',1);w('ScreenLeft_PageLoc',1)
  w('Whirlpool_PageLoc',1);w('Whirlpool_LeftExtent',0);w('Whirlpool_Length',128)
 end
 if frame==871 then
  if character==0 then assert(r('MarioWaterPulled')==1 and velocity('MmVY')>gravity+.08,'Mario receives source whirlpool acceleration')
  else assert(r('Whirlpool_Flag')==0 and math.abs(velocity('MmVY')-gravity)<.002,'Guests are immune to Mario-only PitVacuum') end
  print('PASS water '..character..' weapons, poses and source whirlpool eligibility')
 end
 for power=0,2 do
  local base=900+power*40
  local boundary=character==0 and (power==0 and 15.75 or 31) or surface
  if frame==base then
   w('PlayerStatus',power);if character==0 then w('PlayerSize',power==0 and 1 or 0) end
   fixture(boundary,1,0)
  end
  if frame==base+1 then assert(r('MmUnderwater')==0,'Waterline equality in power form '..power) end
  if frame==base+5 then fixture(boundary+1/65536,1,0) end
  if frame==base+6 then assert(r('MmUnderwater')==1,'Fractional waterline in power form '..power) end
 end
 if frame==1020 then
  if character==1 then
   fixture(20,0,0);w('MmSliding',1);w('MmSlideStop',0);w('MmSlideTravel',0);w('MmSlideTravel',0,1)
  elseif character==2 then fixture(15,1,0);w('SmBall',1)
  elseif character==5 then fixture(27,1,0);w('RgAttack',10) end
 end
 if frame==1021 then
  if character==1 or character==2 then assert(r('MmUnderwater')==1,'Short form uses its actual waterline')
  elseif character==5 then assert(r('MmUnderwater')==0,'Airborne whip uses its tall hit rectangle at the surface') end
 end
 if frame==1040 then fixture(100,1,0) end
 if frame==1070 then
  -- HARD (2.02) Mario walks at175/120; EASY keeps150/120.
  local expected=({175/120,165/120,1.25,1.25,175/120,150/120})[character+1]
  assert(math.abs(velocity('MmVX')-expected)<.002,'Air speed and B/run eligibility underwater: '..velocity('MmVX')..' / '..expected)
 end
 if frame==1071 then
   local expected=({175/120,0,0,1.25,0,0})[character+1]
  assert(math.abs(velocity('MmVX')-expected)<.003,'Character-specific underwater air momentum on release')
  print('PASS water '..character..' all power forms, short/attack hitboxes, air steering and momentum');emu.stop(0)
 end
end,emu.eventType.endFrame)
