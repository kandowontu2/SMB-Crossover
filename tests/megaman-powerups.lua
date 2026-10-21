local frame=0
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
local function pickup(kind)
  for i=0,5 do w('Enemy_Flag',0,i) end
  w('Enemy_Flag',1,5);w('Enemy_ID',0x2e,5);w('Enemy_State',0x80,5)
  w('PowerUpType',kind,5);w('Enemy_BoundBoxCtrl',3,5)
  w('Enemy_X_Position',r('Player_X_Position'),5);w('Enemy_PageLoc',r('Player_PageLoc'),5)
  w('Enemy_Y_Position',184,5);w('Enemy_Y_HighPos',1,5)
  w('Enemy_X_Speed',0,5);w('Enemy_Y_Speed',0,5)
end
emu.addEventCallback(function()
  emu.setInput({right=frame==80,start=frame==120,
    b=frame==700 or frame==740 or frame==760 or frame==780 or (frame>=810 and frame<900)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
  frame=frame+1
  if frame==480 then
    assert(r('PlayerStatus')==0,'Mega Man starts helmetless')
    assert(r('ObjectMetasprite')==L.METASPRITE_MM_HAIR_STAND,'Helmetless standing art')
  end
  if frame==500 then pickup(0) end
  if frame==580 then
    assert(r('PlayerStatus')==1,'Collecting a mushroom enables the helmet state')
    assert(r('ObjectMetasprite')==L.METASPRITE_MM_HELMET_STAND,'Mushroom displays the hosted helmet art')
    print('PASS actual mushroom pickup enables helmet and charge power state')
  end
  if frame==600 then pickup(1) end
  if frame==690 then
    assert(r('PlayerStatus')==2,'Collecting a flower enables fire shots')
    assert(r('ObjectMetasprite')==L.METASPRITE_MM_FIRE_STAND,'Flower displays the hosted red/yellow form')
    assert(emu.read(0x3f12,emu.memType.nesPpuDebug)==0x16,'Fire suit uses NES red')
    assert(emu.read(0x3f13,emu.memType.nesPpuDebug)==0x28,'Fire suit uses NES yellow')
    assert(emu.read(0x3f1e,emu.memType.nesPpuDebug)==0x37,'Face uses the hosted skin color')
    assert(emu.read(0x3f1a,emu.memType.nesPpuDebug)==0x30,'White shares the existing enemy palette')
    assert(emu.read(0x3f1f,emu.memType.nesPpuDebug)==0x17,'Goomba brown remains available')
    print('PASS actual flower pickup, fire art and shared NES palettes')
  end
  if frame==704 then assert(r('MmBulletType',3)==4,'Flower produces fire-type buster shots') end
  if frame==710 then w('Block_Buffer_1',0x51,167) end
  if frame==735 then
    assert(r('Block_Buffer_1',167)~=0x51,'One 34-damage fire shot breaks a 34-health brick')
    for i=0,5 do w('Enemy_Flag',0,i) end
    w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0)
    w('Enemy_X_Position',112);w('Enemy_PageLoc',0);w('Enemy_Y_Position',184);w('Enemy_Y_HighPos',1)
    w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('Enemy_BoundBoxCtrl',9)
    w('MmEnemyHealthLo',100);w('MmEnemyHealthHi',0)
  end
  if frame>735 and frame<800 and r('Enemy_State')<32 then w('Enemy_X_Position',112);w('Enemy_X_Speed',0) end
  if frame==755 then assert(r('MmEnemyHealthLo')==66,'First fire hit deals 34 damage') end
  if frame==775 then assert(r('MmEnemyHealthLo')==32,'Second fire hit leaves 32 health') end
  if frame==800 then
    assert(r('Enemy_State')>=32 or r('Enemy_Flag')==0,'Third fire shot defeats the Goomba')
    for i=0,3 do w('MmBulletType',0,i) end
    print('PASS fire-shot damage, one-hit bricks and three-hit Goombas')
  end
  if frame==899 then
    assert(r('MmChargeFrames')==87,'Fire state reaches full charge')
    assert(emu.read(0x3f11,emu.memType.nesPpuDebug)~=0x0f,'Full charge cycles the hosted suit colors')
  end
  if frame==904 then
    local full=false
    for i=0,3 do if r('MmBulletType',i)==6 then full=true end end
    assert(full,'Flower full charge emits the stronger fire charge')
    assert(emu.read(0x3f11,emu.memType.nesPpuDebug)==0x0f,'Release restores the normal suit palette')
    local f=assert(io.open(OUTPUT..ROM_NAME..'-fire-charge.png','wb'));f:write(emu.takeScreenshot());f:close()
    print('PASS charge palette cycling and fire full-charge graphics')
    emu.stop(0)
  end
end,emu.eventType.endFrame)
