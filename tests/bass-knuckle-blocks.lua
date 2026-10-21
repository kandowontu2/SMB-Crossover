-- Native Knuckle impacts at several world pages, heights and scroll offsets.
local frame,age,phase=0,0,0
local cases={}
for page=0,1 do for _,y in ipairs({96,128,160,192})do for _,tile in ipairs({0xc1,0x51,0x55,0xc0})do cases[#cases+1]={page=page,y=y,tile=tile}end end end
local current,slot
local reveals,hits=0,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140,start=frame==200,b=frame>=550 and age>=10 and age<16},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if age==0 then
  phase=phase+1;current=cases[phase];slot=nil
  if not current then print('PASS '..hits..' native Knuckle block impacts and '..reveals..' uncollected world pickups preserve inventory and background');emu.stop(0);return end
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  local row=current.y-32
  for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+row+16+x)end end
  w('Block_Buffer_1',current.tile,current.page*208+row+7)
  for i=0,5 do w('Enemy_Flag',0,i)end
  for i=0,9 do w('RgShotType',0,i);w('SsMode',0,i)end
  for i=0,3 do w('MmBulletType',0,i);w('Block_State',0,i);w('BlockMetasprite',0,i)end
  for i=0,1 do w('Block_RepFlag',0,i)end
  w('BlockBounceTimer',0);w('RgCooldown',0);w('SsFreeze',0);w('SsBodyStop',0)
  w('Player_X_Position',32);w('Player_PageLoc',current.page);w('Player_Y_Position',current.y-12);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',current.page);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',current.page)
  w('PlayerStatus',1);w('InvOwnedLo',9,9);w('InvOwnedHi',0,9);w('InvViewedLo',8,9);w('InvViewedHi',0,9);w('InvSelected',3,9);w('InvAmmo',112,147);w('InvDirty',1)
 end
 age=age+1
 assert(emu.read(0x3f00,emu.memType.nesPpuDebug)==0x22,'Knuckle impact preserves universal background, case '..phase)
 assert(r('BackgroundColorCtrl')==0 and r('AreaType')==1,'Knuckle impact preserves area palette selectors')
 assert(r('InvOwnedLo',9)==9 and r('InvOwnedHi',9)==0,'Distant upgrade cannot auto-collect, case '..phase)
 for i=0,5 do
  if r('Enemy_Flag',i)~=0 and r('Enemy_ID',i)==0x2e then
   if not slot then slot=i;reveals=reveals+1 end
  end
 end
 if age==150 then
  local tile=r('Block_Buffer_1',current.page*208+current.y-32+7)
  assert(tile~=current.tile,'Controller Knuckle strikes the native target cell, case '..phase)
  hits=hits+1
  if current.tile==0xc1 or current.tile==0x55 then assert(slot and r('Enemy_Flag',slot)~=0,'Upgrade emerges and remains collectable in the world')end
  age=0
 end
end,emu.eventType.endFrame)
