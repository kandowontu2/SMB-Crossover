-- Explicit native-room injury arenas, not full-stage clears. Each character
-- actually collides with a Spiny, traverses the native injury timer and then
-- responds to Right. No profile may start the native $f0 shrink; Mario's
-- source profile instead freezes, loses every power and resumes control.
local frame,age,index=0,-1,0
-- Source MM/Bass/Samus/Link/Simon/Ryu recoil and Bill/Lance one-hit deaths
-- have independent fixtures; these six retain native scripted injury.
-- These retained profiles exercise the native scripted-injury integration.
local cases={0,6,7,8,11,12}
local active,hurt,f0,sized,xStart,source
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function reset()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('SelectedCharacter',active);w('BillVariant',0)
 w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('PlayerStatus',1);w('PlayerSize',0);w('PlayerFacingDir',1)
 w('Player_X_Speed',0);w('Player_Y_Speed',0);w('SmBall',0);w('SmCrouch',0);w('RgCrouch',0);w('CrouchingFlag',0)
 w('GameEngineSubroutine',8);w('TimerControl',0);w('InjuryTimer',0);w('StarInvincibleTimer',0);w('PlayerChangeSizeFlag',0);w('GuestPowerupActive',0)
 w('RgAttack',0);w('MmDeathFlag',0);w('AvSlash',0);w('SmFlip',0)
 -- Mario's source invulnerability outlasts its slot; each arena starts unhurt.
 w('GuestHurtTicks',0);w('GuestInvulTicks',0);w('GuestLegacyHurt',0);w('GuestHurtKind',0);w('GuestFlickerPhase',0)
 w('Enemy_Flag',1);w('Enemy_ID',0x12);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9);w('Enemy_CollisionBits',0)
 w('Enemy_X_Position',64);w('Enemy_PageLoc',0);w('Enemy_Y_Position',176);w('Enemy_Y_HighPos',1);w('EnemyOffscrBitsMasked',0)
 w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
 hurt,f0,sized,source=false,false,false,false;xStart=64
end
emu.addEventCallback(function()
 emu.setInput({start=frame==240,right=active~=nil and age%180>=120},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<600 then return end
 age=age+1;local t=age%180
 if t==0 then
  index=index+1;active=cases[index]
  if active==nil then print('PASS Mario source injury and five retained native profiles leave scripted injury without stale size state');emu.stop(0);return end
  reset()
 end
 if r('GameEngineSubroutine')==10 then hurt=true end
 if active==0 and r('GuestHurtKind')==0x80 then hurt,source=true,true end
 if hurt then
  w('Enemy_Flag',0)
  if r('TimerControl')==240 then f0=true end
  if r('PlayerChangeSizeFlag')~=0 then sized=true end
  assert(not sized,'Profile '..active..' must not begin the native shrink at $f0')
 end
 if t==170 then
  if active==0 then
   assert(source and r('PlayerStatus')==0,'Mario source injury loses every power without native shrink')
  else
   assert(hurt and f0,'Native enemy injury crosses the $f0 boundary for '..active)
  end
  assert(r('GameEngineSubroutine')==8 and r('PlayerChangeSizeFlag')==0,'Injury completes without blocking scripted/native movement')
  assert(r('Player_X_Position')+256*r('Player_PageLoc')>xStart+5,'Controller movement resumes after injury for '..active)
 end
end,emu.eventType.endFrame)
