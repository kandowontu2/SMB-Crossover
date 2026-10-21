-- Flat-ground and mature-pickup fixtures; firing/morphing use controller input.
local frame,case,age=0,0,0
local current
local cases={}
for _,power in ipairs({0,1,2})do for _,dir in ipairs({1,2})do cases[#cases+1]={power=power,dir=dir}end end
local checked=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
emu.addMemoryCallback(function()
 if not current or r('CurrentBank')%128~=4 then return end
 local ptr=r('R0')+256*r('R1')
 for i=0,2 do
  local kind=r('SmShotType',i)
  if kind~=0 and r('R4')==(r('SmShotX',i)-r('ScreenLeft_X_Pos'))%256 and r('R6')==r('SmShotY',i)then
   local pose=1+(kind-1)*2+(r('SmShotImpact',i)>0 and 1 or 0)
   -- Long Beam reuses the normal beam's pixel data. ca65 does not emit
   -- these alias constants in the VICE label file; resolve the source alias.
   pose=({[3]=1,[4]=2})[pose]or pose
   local up=r('SmShotDir',i)==3 and pose~=5
   local name='SmSAMUS_BEAM_'..pose..(up and '_UP' or '')..(r('SmShotDir',i)==2 and 'Left' or 'Right')
   assert(ptr==assert(L[name],name),'Samus beam renderer reads its native weapon pointer, not a table in another PRG bank: '..string.format('%04x / %04x',ptr,L[name]))
   checked=checked+1
  end
 end
end,emu.callbackType.exec,L.MetaspriteRenderLoop)
emu.addEventCallback(function()
 emu.setInput({right=frame==80 or frame==100,start=frame==200,b=current and(age>=10 and age<14 or age>=30 and age<34),
  up=current and age>=30 and age<34,down=frame==1000 or(frame>=1003 and frame<1005)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 for i=0,5 do if frame<990 or r('Enemy_ID',i)~=0x2e then w('Enemy_Flag',0,i)end end
 if case<6 and(not current or age==60)then
  case=case+1;current=cases[case];age=0
  for i=0,415 do w('Block_Buffer_1',0,i)end
  for x=0,15 do w('Block_Buffer_1',0x54,176+x)end
  for i=0,2 do w('SmShotType',0,i);w('MmVX',0,i);w('MmVY',0,i)end
  w('Player_X_Position',128);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',current.dir)
  w('PlayerStatus',current.power>0 and 1 or 0);w('InvOwnedLo',({0,129,145})[current.power+1],2);w('InvSelected',0,2)
 end
 age=age+1
 if current and(age==15 or age==35)then
  local f=assert(io.open(OUTPUT..ROM_NAME..'-samus-beam-fixed-'..case..'-'..age..'.png','wb'));f:write(emu.takeScreenshot());f:close()
 end
 if frame==985 then current=nil;w('InvOwnedLo',129,2);w('SmBall',0)end
 if frame==990 then
  -- Collect Morph Ball through the real private-pickup collision path.
  w('Player_X_Position',64);w('Player_Y_Position',176);w('Player_State',0)
  w('Enemy_Flag',1,5);w('Enemy_ID',0x2e,5);w('Enemy_State',0x80,5)
  w('Enemy_X_Position',64,5);w('Enemy_PageLoc',0,5);w('Enemy_Y_Position',184,5);w('Enemy_Y_HighPos',1,5)
  w('InvPickupOwner',2,5);w('InvPickup',1,5);w('PowerUpType',1,5)
 end
 if frame==1010 then
  assert(r('InvOwnedLo',2)&2~=0 and r('SmBall')==1,'A collected Morph Ball upgrade enables Down transformation')
  assert(checked>100,'Ground/air-facing and upward native beam pointers exercised repeatedly')
  print('PASS short/long/wave beam graphics pointers in both directions and upward, plus real Morph Ball collection and Down input');emu.stop(0)
 end
end,emu.eventType.endFrame)
