-- A single actual button press against two native enemy fixtures checks
-- piercing and per-enemy hit suppression; no projectile RAM is injected.
local frame=0
local c=assert(EXPANDED_CHARACTER)
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
local returning=false
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame>=100 and frame<100+20*(c-6) and (frame-100)%20==0,start=frame==200,
  -- One Select press spans skipped controller-read frames during lag. Its
  -- duration changes no weapon state or the original damage/return oracles.
  b=c==9 and frame>=560 and frame<563,select=c==10 and frame>=560 and frame<564},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=540 and frame<550 then for i=0,5 do w('Enemy_Flag',0,i) end end
 if frame==550 then
  w('PlayerStatus',2);if c==10 then w('InvOwnedLo',9,10);w('InvSelected',3,10);w('InvAmmo',50,160)end;w('Player_X_Position',40);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_State',0);w('PlayerFacingDir',1)
  for i=0,1 do
   w('Enemy_Flag',1,i);w('Enemy_ID',6,i);w('Enemy_State',0,i);w('Enemy_BoundBoxCtrl',9,i);w('Enemy_PageLoc',0,i);w('Enemy_Y_HighPos',1,i)
   w('MmEnemyHealthLo',0,i);w('MmEnemyHealthHi',0,i)
  end
 end
 if frame>=550 and frame<630 then
  for i=0,1 do w('Enemy_X_Position',92+40*i,i);w('Enemy_Y_Position',176,i);w('Enemy_X_Speed',0,i);w('Enemy_Y_Speed',0,i) end
 end
 if c==10 and frame>592 then for i=0,9 do if r('RgShotType',i)==8 and r('RgShotVXHi',i)>=128 then returning=true end end end
 if frame==(c==10 and 640 or 610)then
  if c==9 then
   assert(r('MmEnemyHealthLo')==58 and r('MmEnemyHealthLo',1)==0,'Bass deals 17 damage against the 2.02 Goomba health of 75, consumed by the first enemy')
   print('PASS Bass buster deals 17 damage without invented flower piercing')
  else
   assert(r('Enemy_State')&0x20~=0 and r('MmEnemyHealthLo',1)==25,'Windmill can hit again after leaving an enemy, while continuous overlap hits once: states '..r('Enemy_State')..'/'..r('Enemy_State',1)..', HP '..r('MmEnemyHealthLo')..'/'..r('MmEnemyHealthLo',1))
   print('PASS Ryu windmill hits on outbound and re-entry without continuous-contact damage')
  end
 end
 if frame==650 then
  if c==10 then
   assert(returning,'Windmill reverses and tracks its owner')
   for i=0,9 do assert(r('RgShotType',i)==0,'Windmill is caught by Ryu') end
  end
  print('PASS upgraded weapon collision, hit masks and stable gameplay');emu.stop(0)
 end
end,emu.eventType.endFrame)
