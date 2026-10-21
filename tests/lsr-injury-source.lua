-- Independent source-injury entry check, explicit actual Spiny body arena.
-- The pinned2.02 source never uses SMB's world-freezing engine10 for these.
local character=assert(HURT_CHARACTER)
local frame,ready=0,false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function q(n)local v=r(n)+256*r(n,1)+65536*r(n,2);return(v>=0x800000 and v-0x1000000 or v)/65536 end
emu.addEventCallback(function()
 local choosing=character<6 and frame>=80 and frame<80+20*character and frame%20==0 or character==10 and frame>=100 and frame<180 and frame%20==0
 emu.setInput({right=choosing,down=character==10 and frame==80,start=frame==240},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then
  assert(r('SelectedCharacter')==character,'Real menu launches injury character'..character)
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
  for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_State',0,i);w('RgEnemyStun',0,i)end
  for i=0,9 do w('RgShotType',0,i)end
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  w('Player_X_Position',96);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
  w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0);w('ScrollLock',1)
  w('Player_State',0);w('PlayerStatus',1);w('PlayerSize',0);w('PlayerFacingDir',2);w('Player_X_Speed',0);w('Player_Y_Speed',0)
  w('InvOwnedLo',1,character);w('InvOwnedHi',0,character);w('RgAttack',0);w('RgThrust',0);w('AvSlash',0)
  w('GameEngineSubroutine',8);w('TimerControl',0);w('InjuryTimer',0);w('StarInvincibleTimer',0);w('GuestHurtKind',0);w('GuestHurtTicks',0);w('GuestInvulTicks',0);w('GuestPowerupActive',0)
  w('Enemy_Flag',1);w('Enemy_ID',18);w('Enemy_BoundBoxCtrl',9);w('Enemy_X_Position',104);w('Enemy_PageLoc',0);w('Enemy_Y_Position',176);w('Enemy_Y_HighPos',1);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('EnemyOffscrBitsMasked',0)
  ready=true
 elseif ready and r('PlayerStatus')==0 and r('InjuryTimer')>0 then
  print('Actual injury c'..character..' engine'..r('GameEngineSubroutine')..' timer'..r('TimerControl')..' kind'..r('GuestHurtKind')..' vx'..q('MmVX')..' vy'..q('MmVY'))
  assert(r('GameEngineSubroutine')==8 and r('TimerControl')==0 and r('GuestHurtKind')==character,'Source injury preserves the live world instead of native engine10: c'..character)
  local expectedVX=-(character==4 and 500 or 150)/120
  local expectedVY=character==4 and 0 or-(character==5 and 300 or 385)/120
  assert(math.abs(q('MmVX')-expectedVX)<.00003,'Source attacker-relative horizontal recoil')
  assert(math.abs(q('MmVY')-expectedVY)<.00003,'Source initial vertical recoil or retained Link VY')
  assert(r('PlayerFacingDir')==1,'Recoil faces the attacker independent of old facing')
  print('PASS independent source injury entry c'..character);emu.stop(0)
 end
 assert(frame<650,'Actual Spiny contact starts source injury')
end,emu.eventType.endFrame)
