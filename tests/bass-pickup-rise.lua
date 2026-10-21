-- One real controller buster hit reveals an upgrade. Measure native pickup
-- updates, not hardware frames: lag must neither speed nor skip emergence.
local frame,age,slot,startY,updates=0,0,nil,nil,0
local sawFreeze=false
local freezeRequested=false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
emu.addMemoryCallback(function()
 if frame<550 or r('SelectedCharacter')~=9 then return end
 local s=emu.getState()['cpu.x']
 if r('InvPickup',s)>0 and r('InvPickup',s)<252 then
  if not slot then slot=s;startY=r('Enemy_Y_Position',s)end
  if r('TimerControl')==0 then updates=updates+1 else sawFreeze=true end
 end
end,emu.callbackType.exec,L.InventoryRisePickup)
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140,start=frame==200,b=frame>=550 and age>=10 and age<16},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if frame==550 then
  for i=0,415 do w('Block_Buffer_1',0,i)end
  for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
  w('Block_Buffer_1',0xc1,160+7)
  for i=0,5 do w('Enemy_Flag',0,i)end
  w('Player_X_Position',32);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  w('PlayerStatus',1);w('InvOwnedLo',1,9);w('InvOwnedHi',0,9);w('InvSelected',0,9)
  return
 end
 age=age+1
 if slot then
  assert(r('Enemy_Y_Position',slot)==startY-math.floor(math.min(updates,48)/3),'Native upgrade emergence follows source 40px/s rise speed')
  if updates==18 and not freezeRequested then w('TimerControl',10);freezeRequested=true end
  if r('Enemy_State',slot)==128 then
   assert(updates==48 and sawFreeze,'Exactly 48 active updates, with a real timer freeze, complete emergence: '..updates)
   assert(r('Enemy_X_Position',slot)==112 and r('Enemy_PageLoc',slot)==0,'Pickup remains aligned to its native question block')
   assert(r('Enemy_SprAttrib',slot)&32==0 and r('Enemy_X_Speed',slot)==0,'Exiting the block clears behind-ground priority and leaves the icon stationary')
   print('PASS native Bass upgrade emergence: exact source rise speed, 48 active updates, frozen interval, block alignment and stationary exit');emu.stop(0)
  end
 end
 assert(age<230,'A native question-block upgrade completes emergence')
end,emu.eventType.endFrame)
