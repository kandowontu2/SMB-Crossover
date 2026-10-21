-- Explicit collision fixture: Bass is already standing on the parent block.
-- The emerging item must be collectable before its full 48-update rise ends.
local frame,age=0,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140,start=frame==200},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if frame==550 then
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
  w('Block_Buffer_1',0xc4,128+7)
  for i=0,5 do w('Enemy_Flag',0,i)end
  w('Player_X_Position',112);w('Player_PageLoc',0);w('Player_Y_Position',128);w('Player_Y_HighPos',1);w('Player_State',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  w('PlayerStatus',1);w('InvOwnedLo',1,9);w('InvOwnedHi',0,9);w('InvSelected',0,9)
  w('Enemy_Flag',1);w('Enemy_ID',0x2e);w('Enemy_State',1);w('Enemy_BoundBoxCtrl',3)
  w('Enemy_X_Position',112);w('Enemy_PageLoc',0);w('Enemy_Y_Position',152);w('Enemy_Y_HighPos',1);w('Enemy_SprAttrib',32)
  w('InvPickup',3);w('InvPickupOwner',9);w('InvRisePhase',0);w('PowerUpType',1)
  return
 end
 age=age+1
 if age==10 then
  assert(r('Enemy_Flag')==0 and r('InvOwnedLo',9)==9,'Exposed pixels can be collected from above before the full rise finishes')
  print('PASS Bass can collect the exposed part of a rising upgrade from above; no blanket emergence delay');emu.stop(0)
 end
end,emu.eventType.endFrame)
