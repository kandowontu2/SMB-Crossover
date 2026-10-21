-- Controller weapon selection and repeated Knuckle fire must preserve sky.
local frame,age=0,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function pal()return emu.read(0x3f00,emu.memType.nesPpuDebug)end
emu.addEventCallback(function()
 local step=age%100
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140,start=frame==200,
  select=frame>=550 and step>=10 and step<16,
  b=frame>=550 and ((step>=35 and step<41)or(step>=65 and step<71)),
  a=frame>=550 and step>=50 and step<56},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if frame==550 then
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
  for i=0,5 do w('Enemy_Flag',0,i)end
  w('Player_X_Position',32);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  w('PlayerStatus',1);w('InvOwnedLo',255,9);w('InvOwnedHi',1,9);w('InvSelected',0,9);w('InvDirty',1)
  return
 end
 age=age+1
 if pal()~=0x22 then
  print('BAD PALETTE '..pal()..' age '..age..' selected '..r('InvSelected',9)..' bgctrl '..r('BackgroundColorCtrl')..' area '..r('AreaType'))
 end
 assert(pal()==0x22,'Weapon selection/firing preserves the overworld universal background color')
 if age==1800 then print('PASS Bass repeated selection, grounded/airborne shots and Knuckle preserve background palette');emu.stop(0)end
end,emu.eventType.endFrame)
