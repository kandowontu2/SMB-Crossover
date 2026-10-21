-- Explicit collision arena. Each acquired upgrade is collected as a mature
-- native pickup, then one ordinary B press tests damage against a live enemy.
-- These are ability fixtures, not controller-only level clears.
local c=assert(MELEE_CHARACTER)
local frame,age,index=0,-1,0
local cases={}
for tier=0,(c==10 and 1 or 2)do
 for dir=1,2 do
  for crouch=0,(c==4 and 0 or 1)do
   for far=0,(c==10 and 2 or 0)do
    cases[#cases+1]={tier=tier,dir=dir,crouch=crouch,far=far}
   end
  end
 end
end
local active
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function reset()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('RgEnemyStun',0,i);w('AvFrozen',0,i);w('AvFrozenHi',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('Player_X_Position',96);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('PlayerFacingDir',active.dir);w('PlayerStatus',active.tier==0 and c~=10 and 0 or 1)
 w('RgAttack',0);w('RgAttackAge',0);w('RgMeleeHits',0);w('RgThrust',0);w('RgCrouch',0);w('CrouchingFlag',0)
 w('RgPreviousButtons',0);w('RgCooldown',0);w('RgShootPose',0);w('AvSlash',0);w('AvFlip',0)
 w('TimerControl',0);w('GameEngineSubroutine',8);w('InjuryTimer',255)
 w('InvOwnedLo',1,c);w('InvOwnedHi',c==5 and 2 or 0,c);w('InvSelected',0,c)
 if (c~=10 and active.tier==2)or(c==10 and active.tier==1)then
  local item=c==4 and 4 or c==5 and 1 or 6
  w('Enemy_Flag',1,5);w('Enemy_ID',0x2e,5);w('Enemy_State',0x80,5)
  w('Enemy_X_Position',96,5);w('Enemy_PageLoc',0,5);w('Enemy_Y_Position',184,5);w('Enemy_Y_HighPos',1,5)
  w('InvPickupOwner',c,5);w('InvPickup',item,5);w('PowerUpType',1,5)
 end
 local dx=active.far==1 and 45 or 27
 local x=active.dir==1 and 96+dx or 96+16-dx-16
 -- The far target sits beyond the normal sword's tip in either direction.
 if active.far==1 and active.dir==2 then x=96-46 end
 active.enemyX=x
 active.enemyY=active.far==2 and(186+active.crouch*6)or 176
 w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
 w('Enemy_PageLoc',0);w('Enemy_X_Position',x);w('Enemy_Y_Position',active.enemyY);w('Enemy_Y_HighPos',1)
 w('EnemyOffscrBitsMasked',0);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
 w('MmEnemyHealthLo',200);w('MmEnemyHealthHi',0)
end
emu.addEventCallback(function()
 local t=age%90
 local choosing=c<6 and frame>=80 and frame<80+c*20 and frame%20==0 or c>=6 and frame>=100 and frame<100+(c-6)*20 and frame%20==0
 emu.setInput({right=choosing,down=(c>=6 and frame==80)or(active and active.crouch==1 and t>=15),start=frame==240,b=active and t==25},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<600 then return end
 age=age+1
 local t=age%90
 if t==0 then
  index=index+1;active=cases[index]
  if not active then print('PASS 2.02 melee acquired tiers, mirrored reach and crouch damage: character '..c..', '..#cases..' arenas');emu.stop(0);return end
  assert(r('SelectedCharacter')==c,'Real menu launches expected character');reset()
 end
 if t<55 then
  w('Enemy_X_Position',active.enemyX);w('Enemy_Y_Position',active.enemyY);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
 end
 if t==12 and((c~=10 and active.tier==2)or(c==10 and active.tier==1))then
  local item=c==4 and 4 or c==5 and 1 or 6
  assert((r('InvOwnedLo',c)&(1<<item))~=0,'Upgrade collected through native pickup collision')
 end
 if t==(c==4 and 31 or 55)then
  local damage=c==4 and({50,75,100})[active.tier+1]or c==5 and({70,75,100})[active.tier+1]or 75
  if c==10 and active.far~=0 and active.tier==0 then damage=0 end
  assert(r('MmEnemyHealthLo')==200-damage,'Source melee damage/reach c='..c..' tier='..active.tier..' dir='..active.dir..' crouch='..active.crouch..' far='..active.far..': '..r('MmEnemyHealthLo')..' expected '..(200-damage))
 end
 if c==4 and active.tier==2 and t==55 then
  assert(r('MmEnemyHealthLo')==50,'Red ring separately launches its 50-damage sword beam after the 100-damage melee window')
 end
end,emu.eventType.endFrame)
