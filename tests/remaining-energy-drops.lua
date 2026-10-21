-- Controller attacks defeat a native Goomba, then walking collects its ammo.
-- Only the initial map/inventory and the independent random draw are fixtures.
local c=assert(CHARACTER)
local spec=assert(({[2]={auto=0x85,item=2,ammo=2,value=2},[4]={auto=0x45,item=2,ammo=2,value=2},
 [5]={auto=5,item=2,ammo=0,value=1,hi=2},[10]={auto=3,item=1,ammo=0,value=5},
 [11]={auto=0x83,item=1,ammo=1,value=6}})[c])
if BIG_DROP then spec.value=c==5 and 5 or 10 end
local frame,age,drop,stock,seen=0,0,nil,nil,false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
emu.addMemoryCallback(function()
 if frame>=550 and(r('CurrentBank')&127)==0x3b then w('PseudoRandomBitReg',0,1);w('PseudoRandomBitReg',BIG_DROP and 255 or 0,2)end
end,emu.callbackType.exec,assert(L.InventoryEnemyDrop))
-- This fixture isolates Enemy.die()'s immediate roll. Sophia's independent
-- explosion-expiry roll is covered by sophia-enemy-explosion.lua.
if c==11 then emu.addMemoryCallback(function()
 if frame>=550 and(r('CurrentBank')&127)==0x3b then w('PseudoRandomBitReg',1,1)end
end,emu.callbackType.exec,assert(L.InventoryDropPoint))end
emu.addEventCallback(function()
 local choosing=c<6 and frame>=80 and frame<80+c*20 and frame%20==0 or c>=6 and frame>=100 and frame<100+(c-6)*20 and frame%20==0
 -- Samus's standing muzzle is above a Goomba. Tap Down to stay crouched,
 -- then release it before Select (Down+Select changes beam mode).
 emu.setInput({start=frame==200,right=choosing or drop~=nil,down=(c>=6 and frame==80)
  or(c==2 and frame>=550 and frame<555)or(c==10 and frame>=550 and not drop),
  select=frame>=560 and not drop and age%28<5},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 age=age+1
 if frame==550 then
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
  for i=0,5 do w('Enemy_Flag',0,i)end
  w('PlayerStatus',1);w('InvOwnedLo',spec.auto,c);w('InvOwnedHi',spec.hi or 0,c);w('InvSelected',spec.item,c);w('InvDirty',1)
  w('InvAmmo',10,c*16+spec.ammo);w('Player_X_Position',48);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_State',0)
  w('Enemy_Flag',1);w('Enemy_BoundBoxCtrl',9);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_X_Position',140);w('Enemy_PageLoc',0);w('Enemy_Y_Position',176);w('Enemy_Y_HighPos',1)
  w('Enemy_MovingDir',2);w('Enemy_X_Speed',0);w('EnemyOffscrBitsMasked',0);w('MmEnemyHealthLo',0);w('MmEnemyHealthHi',0)
  return
 end
 w('InjuryTimer',255)
 local active=false
 for i=0,3 do if r('InvDropKind',i)~=0 then
  active=true
  if not drop then
   drop=age;stock=r('InvAmmo',c*16+spec.ammo);seen=true
   assert(r('AvDropItem',i)==spec.ammo,'Ammo type is pinned at spawn, '..c..' slot '..i..' actual '..r('AvDropItem',i)..' selected '..r('SelectedCharacter'))
   -- A later selection must not retarget an existing world collectible.
   w('InvSelected',0,c);w('InvDirty',1)
  end
 end end
 if drop and not active then
  assert(r('InvAmmo',c*16+spec.ammo)==stock+spec.value,'Native ammo contact restores '..spec.value..' to the original pool for '..c..': '..r('InvAmmo',c*16+spec.ammo)..' vs '..stock)
  print('PASS character '..c..' controller kill, 25% enemy drop, distinct ammo type, selection-independent world pickup and source refill '..spec.value);emu.stop(0)
 end
 assert(age<500,'Native attack defeats Goomba and its world ammo is collected: '..c..' drop '..tostring(drop)..' ammo '..r('InvAmmo',c*16+spec.ammo)..' enemy '..r('MmEnemyHealthLo'))
end,emu.eventType.endFrame)
