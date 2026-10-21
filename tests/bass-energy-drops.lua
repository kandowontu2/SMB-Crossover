-- Explicit flat-world fixtures; real controller shots defeat native Goombas.
-- Only the random draws are pinned, to test both sizes and the no-drop path.
local frame,age,phase=0,0,0
local spawned,dead,collected=false,false,false
local before,expected,draws
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function setup()
 for i=0,415 do w('Block_Buffer_1',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('MmEnemyHealthLo',0,i);w('MmEnemyHealthHi',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('InvDropKind',0,i)end
 w('Player_X_Position',32);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('Player_Y_Speed',0);w('PlayerFacingDir',1);w('PlayerStatus',1)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('InvOwnedLo',5,9);w('InvOwnedHi',phase==3 and 1 or 0,9)
 w('InvSelected',phase==3 and 0 or 2,9);w('InvAmmo',32,146);w('InvDirty',1)
 w('InvRefill',0);w('SsFreeze',0);w('SsBodyStop',0);w('TimerControl',0)
 w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
 w('Enemy_X_Position',140);w('Enemy_PageLoc',0);w('Enemy_Y_Position',176);w('Enemy_Y_HighPos',1)
 w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
 age=0;spawned=false;dead=false;collected=false;draws=0
end
emu.addMemoryCallback(function()
 if frame>=550 then w('PseudoRandomBitReg',phase==2 and 1 or 0,1);w('PseudoRandomBitReg',phase==1 and 255 or 0,2)end
end,emu.callbackType.exec,L.InventoryEnemyDrop)
emu.addMemoryCallback(function()
 if frame>=550 then
  local art=emu.getState()['cpu.a']
  if art==L.SS_ART_PICKUP14 or art==L.SS_ART_PICKUP15 or art==L.SS_ART_PICKUP16 or art==L.SS_ART_PICKUP17 then draws=draws+1 end
 end
end,emu.callbackType.exec,L.SpecialPickupArt)
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140,start=frame==200,
  b=frame>=550 and ((age>=10 and age<16)or(age>=40 and age<46)or(age>=70 and age<76))},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if frame==550 then setup();return end
 age=age+1
 if r('Enemy_State')&0x20~=0 then dead=true end
 for i=0,3 do
  if r('InvDropKind',i)>0 then
   spawned=true
   assert(r('InvDropKind',i)==(phase==1 and 2 or 1),'Pinned random roll selects the source drop size')
   if age>=100 and not collected then
    assert(draws>0,'Energy has its own animated pickup art')
    before=r('InvAmmo',146);expected=before+(phase==1 and 40 or 8)
    w('Player_X_Position',(r('InvDropX',i)-8)%256);w('Player_PageLoc',r('InvDropPage',i))
    w('Player_Y_Position',176);w('Player_State',0);w('Player_Y_Speed',0)
    for j=0,2 do w('MmVY',0,j)end
    collected=true
   end
  end
 end
 if age==160 then
  assert(dead,'Controller-created shots actually defeat the native Goomba')
  if phase==2 then assert(not spawned,'A non-dropping roll creates no collectible')
  else
   assert(spawned and collected,'An enemy creates a collectible that Bass touches')
   assert(r('InvAmmo',146)==expected,'Refill restores exactly '..(phase==1 and 40 or 8)..' units: '..r('InvAmmo',146)..' expected '..tostring(expected))
   assert(r('InvRefill')==0 and r('TimerControl')==0,'The refill completes and unfreezes gameplay: index '..r('InvRefill')..' timer '..r('TimerControl')..' remain '..r('InvRefillRemain')..' tick '..r('InvRefillTick')..' engine '..r('GameEngineSubroutine'))
  end
  phase=phase+1
  if phase==4 then print('PASS Bass native enemy deaths, source drop chance/size, animated small/large collectibles, exact 8/40 refills, Energy Balancer and unfreeze');emu.stop(0)
  else setup()end
 end
end,emu.eventType.endFrame)
