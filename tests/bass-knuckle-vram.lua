-- Dense masonry/coin fixture; all impacts come from controller-fired Knuckle.
local frame,age=0,0
local maxBuffer=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
emu.addMemoryCallback(function(addr,value)
 if frame>=550 then
  maxBuffer=math.max(maxBuffer,value)
  assert(value<84,'Native VRAM queue must fit its allocation: offset '..value..' age '..age)
 end
end,emu.callbackType.write,L.VRAM_Buffer1_Offset)
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140,start=frame==200,
  b=frame>=550 and age%18>=10 and age%18<16},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if frame==550 then
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
  for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
  for x=4,13 do w('Block_Buffer_1',0x51,160+x);w('Block_Buffer_1',0x51,144+x);w('Block_Buffer_1',0xc2,128+x)end
  for i=0,5 do w('Enemy_Flag',0,i)end
  w('Player_X_Position',32);w('Player_PageLoc',0);w('Player_Y_Position',162);w('Player_Y_HighPos',1);w('Player_State',1);w('PlayerFacingDir',1)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  w('PlayerStatus',1);w('InvOwnedLo',255,9);w('InvOwnedHi',1,9);w('InvSelected',3,9);w('InvAmmo',255,147);w('InvDirty',1)
  return
 end
 age=age+1
 assert(emu.read(0x3f00,emu.memType.nesPpuDebug)==0x22,'Dense Knuckle destruction preserves sky')
 if age==250 then print('PASS dense Knuckle masonry and coin impacts keep native VRAM queue in bounds: max '..maxBuffer);emu.stop(0)end
end,emu.eventType.endFrame)
