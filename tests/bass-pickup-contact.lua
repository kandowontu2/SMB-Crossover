-- A head bump must reveal a world upgrade before contact collects it.
-- Explicit flat-world/initial-inventory fixture; controller jump and reveal.
local frame,age=0,0
local slot,spawnY,spawnFrame,item
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
emu.addEventCallback(function()
 emu.setInput({down=frame==80,left=age>=130 and age<150 and r('Player_X_Position')>80,
  right=frame==100 or frame==120 or frame==140 or(age>=154 and age<235 and r('Player_X_Position')<112),
  start=frame==200,a=frame>=550 and ((age>=10 and age<24)or(age>=154 and age<185))},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if frame==550 then
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
  w('Block_Buffer_1',0xc1,128+7)
  for i=0,5 do w('Enemy_Flag',0,i)end
  w('Player_X_Position',112);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  w('PlayerStatus',1);w('InvOwnedLo',1,9);w('InvOwnedHi',0,9);w('InvSelected',0,9)
  return
 end
 age=age+1
 for i=0,5 do
  if r('Enemy_Flag',i)~=0 and r('Enemy_ID',i)==0x2e then
   if not slot then slot=i;spawnY=r('Enemy_Y_Position',i);spawnFrame=frame;item=r('InvPickup',i)end
  end
 end
 if slot and frame<spawnFrame+48 then assert(r('InvOwnedLo',9)==1 and r('InvOwnedHi',9)==0,'Bumping a block does not collect its emerging upgrade through the block')end
 if age==150 then
  assert(slot,'Head bump reveals a native upgrade')
  assert(r('Enemy_Flag',slot)~=0,'Uncollected upgrade remains in the world above its block')
  local aligned=false
  for i=0,63 do
   local ox=emu.read(i*4+3,emu.memType.nesSpriteRam)
   local oy=emu.read(i*4,emu.memType.nesSpriteRam)
   if (ox==112 or ox==120)and oy==144 then aligned=true end
  end
  assert(aligned,'Emerged 16-pixel source icon rests exactly on the block top at Y=160')
  -- A second controller jump approaches from beside the block and collects it.
 end
 if age==300 then
  assert(r('Enemy_Flag',slot)==0,'Controller jump onto the block collects the world upgrade')
  assert((r('InvOwnedLo',9)+256*r('InvOwnedHi',9))&(1<<item)~=0,'Only actual player contact grants the revealed upgrade')
  print('PASS head-bumped Bass upgrade emerges, rests on its block and requires later player contact');emu.stop(0)
 end
end,emu.eventType.endFrame)
