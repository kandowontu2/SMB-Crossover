-- Pinned2.02 Enemy.confirmedHitProj/checkAttackProps: first FREEZE returns
-- before takeDamage. Native health0 is a lazy75HP sentinel; an actual second
-- Ice hit must thaw and initialize/subtract40, leaving35HP. No outcome is seeded.
-- Explicit native-enemy fixtures; a real Ice Beam shot creates the freeze.
-- Then native actor collision exercises the ice platform and Screw protection.
local frame=0
local frozenX,frozenY,freezeAt
local screwHit=false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function enemy(x,y)
 for i=0,5 do w('Enemy_Flag',0,i)end
 w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
 w('Enemy_X_Position',x);w('Enemy_PageLoc',0);w('Enemy_Y_Position',y);w('Enemy_Y_HighPos',1);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
 w('MmEnemyFlash',0);w('MmEnemyHealthLo',0);w('MmEnemyHealthHi',0);w('EnemyOffscrBitsMasked',0)
end
emu.addEventCallback(function()emu.setInput({right=frame==80 or frame==100 or(frame>=700 and frame<704),start=frame==200,down=frame==555,b=(frame>=560 and frame<565)or(frame>=670 and frame<675)},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
  w('PlayerStatus',1);w('InvOwnedLo',0x89,2);w('InvSelected',0,2);w('Player_X_Position',48);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
  enemy(140,176)
 end
 if frame>550 and frame<650 then
  local timer=r('AvFrozen')+256*r('AvFrozenHi')
  if timer>0 and not freezeAt then
   freezeAt=frame;frozenX=r('Enemy_X_Position');frozenY=r('Enemy_Y_Position')
   assert(timer>=350 and timer<=360 and r('MmEnemyHealthLo')==0 and r('MmEnemyHealthHi')==0,'Source first freeze preserves the native lazy-health sentinel without damage')
  end
  if freezeAt then assert(r('Enemy_X_Position')==frozenX and r('Enemy_Y_Position')==frozenY,'Frozen enemy stops moving')end
 end
 if frame==650 then
  assert(freezeAt,'Controller Ice Beam hits and freezes the target')
  w('Player_X_Position',frozenX);w('Player_Y_Position',frozenY-25);w('Player_State',2);w('Player_Y_Speed',1)
  w('MmVY',0);w('MmVY',0,1);w('MmVY',1,2)
 end
 if frame==660 then
  assert(r('Player_Y_Position')==frozenY-24 and r('Player_State')==0,'Samus lands on the frozen enemy at its native top')
  assert(r('PlayerStatus')==1 and r('MmDeathFlag')==0,'Standing on ice does not hurt Samus')
 end
 -- Authored player placement, not an enemy HP/timer outcome write. The
 -- second real Ice shot must remove freeze and deal40 to default75HP.
 if frame==665 then
  w('Player_X_Position',48);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('Player_Y_Speed',0)
  w('PlayerFacingDir',1);w('SmBall',0);w('SmCrouch',1);w('CrouchingFlag',4)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 end
 if frame==690 then
  assert(r('AvFrozen')==0 and r('AvFrozenHi')==0,'Second actual Ice hit removes existing freeze')
  assert(r('MmEnemyHealthLo')==35 and r('MmEnemyHealthHi')==0 and r('Enemy_Flag')~=0 and r('Enemy_State')&32==0,'Thaw hit initializes default75HP then deals40, leaving live35HP')
  local f=assert(io.open(OUTPUT..ROM_NAME..'-samus-thaw-result.json','w'));f:write('{"frame":690,"hp":'..r('MmEnemyHealthLo')..',"timer":'..r('AvFrozen')..',"flag":'..r('Enemy_Flag')..',"state":'..r('Enemy_State')..'}\n');f:close()
 end
 if frame==699 then
  for i=0,5 do w('AvFrozen',0,i);w('AvFrozenHi',0,i)end
  for i=0,9 do w('RgShotType',0,i)end
  w('InvOwnedLo',0x41,2);w('PlayerStatus',1);w('Player_X_Position',128);w('Player_Y_Position',144);w('Player_State',1);w('Player_Y_Speed',0);w('SmFlip',1);w('SmJumpStartY',176);w('InjuryTimer',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  enemy(140,144);w('MmEnemyFlash',2) -- Screw Attack also defeats an enemy flashing from a prior beam.
 end
 if frame>=700 and frame<715 and(r('Enemy_State')&32~=0 or r('Enemy_Flag')==0)then screwHit=true end
 if frame==715 then
  assert(screwHit and r('PlayerStatus')==1 and r('MmDeathFlag')==0,'Screw Attack defeats a touching enemy before native contact can hurt Samus')
  print('PASS first-freeze no damage, actual thaw hit75-to35, native frozen platform, and acquired Screw Attack contact protection/defeat');emu.stop(0)
 end
end,emu.eventType.endFrame)
