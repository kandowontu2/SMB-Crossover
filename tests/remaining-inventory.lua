-- Native pickup collision and controller attacks, with explicit map/ammo fixtures.
-- Expectations are the pinned 2.02 upgrade IDs, shared ammo costs and shot pools.
local c=assert(CHARACTER)
local specs={
 [1]={auto=1,hi=4,n=9,attacks={[2]={10,4},[3]={11,8},[6]={15,4,16},[7]={17,16},[8]={20,0}}},
 [2]={auto=0x81,n=6,attacks={[2]={41,1},[3]={46,0},[4]={-3,0}}},
 [3]={auto=1,n=6,attacks={[1]={1,0},[2]={42,0},[3]={43,0},[4]={2,0},[5]={3,0},[6]={3,0}}},
 [4]={auto=0x41,n=5,attacks={[1]={33,1},[2]={32,1},[3]={5,0}}},
 [5]={auto=1,hi=2,n=8,attacks={[2]={35,1},[3]={36,1,37},[4]={-180,5},[5]={38,1},[6]={6,1}}},
 [10]={auto=1,n=7,attacks={[1]={5,3},[2]={39,5},[3]={8,5},[4]={40,5},[5]={-74,5}}},
 [11]={auto=0x81,n=6,attacks={[1]={44,3},[2]={45,1}}}
}
local spec=assert(specs[c]);local frame,age,case=0,-1,0
local seen={}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function has(item)return((r('InvOwnedLo',c)+256*r('InvOwnedHi',c))&(1<<item))~=0 end
local function reset()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('AvFrozen',0,i);w('AvFrozenHi',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,2 do w('SmShotType',0,i);w('SmBombAge',0,i);w('MmVX',0,i);w('MmVY',0,i)end
 w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('PlayerStatus',1);w('PlayerFacingDir',1);w('SmBall',0);w('SmCrouch',0);w('SmFlip',0)
 w('RgAttack',0);w('RgShootPose',0);w('RgCooldown',0);w('AvSlash',0);w('AvStopwatch',0);w('AvSamusMode',0)
 w('TimerControl',0);w('GameEngineSubroutine',8)
 w('InvAmmo',50,c*16);w('InvAmmo',20,c*16+1);w('InvAmmo',20,c*16+2)
 if c==1 then for i=1,8 do w('InvAmmo',112,16+i)end;w('MmSliding',0);w('SsFreeze',0);w('SsBodyStop',0);w('SsWaterExpand',0)end
 if c==11 and case==2 then
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_X_Position',180);w('Enemy_PageLoc',0)
  w('Enemy_Y_Position',176);w('Enemy_BoundBoxCtrl',9);w('Enemy_Y_HighPos',1);w('EnemyOffscrBitsMasked',0);w('MmEnemyHealthLo',100);w('MmEnemyHealthHi',0)
 end
 -- Mature private pickup is placed in the player's real native hit rectangle.
 w('Enemy_Flag',1,5);w('Enemy_ID',0x2e,5);w('Enemy_State',0x80,5)
 w('Enemy_X_Position',64,5);w('Enemy_PageLoc',0,5);w('Enemy_Y_Position',184,5);w('Enemy_Y_HighPos',1,5)
 w('InvPickupOwner',c,5);w('InvPickup',case,5);w('PowerUpType',1,5)
end
emu.addEventCallback(function()
 local choosing=c<6 and frame>=80 and frame<80+c*20 and frame%20==0 or c>=6 and frame>=100 and frame<100+(c-6)*20 and frame%20==0
 local phase=age%60
 local shot=phase>=20 and phase<25 and spec.attacks[case]
 local basic=c==1 or c==3 or(c==2 and case>=3)
 emu.setInput({right=choosing,down=c>=6 and frame==80 or(c==2 and case==1 and(phase==20 or(phase>=22 and phase<25))),
  start=frame==200,b=shot and basic,select=(shot and not basic)or(c==1 and case<=8 and phase==12),
  a=c==10 and case==5 and phase>=10 and phase<18},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if frame==550 then
  assert(r('SelectedCharacter')==c and r('GameEngineSubroutine')==8,'Real menu launches character '..c..': actual='..r('SelectedCharacter')..' mode='..r('OperMode')..' task='..r('OperMode_Task')..' engine='..r('GameEngineSubroutine'))
  w('InvOwnedLo',spec.auto,c);w('InvOwnedHi',spec.hi or 0,c);w('PlayerStatus',1)
 end
 age=age+1
 if age%60==0 then case=case+1;if case>spec.n then print('PASS 2.02 native inventory for character '..c..': '..spec.n..' separate pickups, source attacks and ammo costs');emu.stop(0);return end;reset()end
 local t=age%60
 if t==8 then assert(has(case),'Native collision collects upgrade '..case..' for '..c)end
 local expected=spec.attacks[case]
 if expected and expected[1]>0 and t>=20 and t<=38 then
  for i=0,9 do if r('RgShotType',i)==expected[1]or r('RgShotType',i)==expected[3]then seen[case]=true end end
 end
 if t==38 then
  local a=spec.attacks[case]
  if a then
   local found=seen[case] or false
   if a[1]>0 then for i=0,9 do if r('RgShotType',i)==a[1]or r('RgShotType',i)==a[3]then found=true end end
   elseif a[1]==-3 then for i=0,2 do if r('SmShotType',i)==3 then found=true end end
   elseif a[1]==-180 then found=r('AvStopwatch')>140
   elseif a[1]==-74 then found=r('AvSlash')~=0 end
   assert(found,'Source weapon '..case..' creates expected attack '..a[1]..' for '..c)
   local index=c*16+((c==5 or c==10)and 0 or case)
   if a[2]>0 then
    local start=c==1 and 112 or(c==5 or c==10)and 50 or 20
    assert(r('InvAmmo',index)==start-a[2],'Source ammunition cost '..a[2]..' for '..c..'/'..case..': '..r('InvAmmo',index))
   end
  end
  local f=assert(io.open(OUTPUT..ROM_NAME..'-inventory-'..c..'-'..case..'.png','wb'));f:write(emu.takeScreenshot());f:close()
 end
end,emu.eventType.endFrame)
