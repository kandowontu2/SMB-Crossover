-- Real Select-created homing missiles, with isolated vector inputs at the
-- steering boundary. Oracle uses the source's direct cos(atan2)/sin formula.
local updates=0;local slot
local frame=0
local seen={}
local returns,pending={}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function phase()return math.floor((frame-550)/70),(frame-550)%70 end
local function fixture()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1)
 w('PlayerStatus',1);w('InvOwnedLo',0x85,11);w('InvSelected',2,11);w('InvAmmo',20,178);w('InvPrevious',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_X_Position',160);w('Enemy_PageLoc',0);w('Enemy_Y_Position',112);w('Enemy_Y_HighPos',1)
 w('Enemy_BoundBoxCtrl',9);w('EnemyOffscrBitsMasked',0);w('MmEnemyHealthLo',255);w('MmEnemyHealthHi',127);w('AvStopwatch',200)
end
emu.addMemoryCallback(function()
 if frame<550 or (r('CurrentBank')%128~=36 or r('CurrentBankC')%128~=36) then return end
 updates=updates+1;slot=r('AvSlot')
 w('RgShotX',244,slot);w('RgShotPage',4,slot);w('RgShotY',64,slot);w('RgShotYHigh',3,slot)
 local sp=emu.getState()['cpu.sp']
 local pc=emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1
 pending={slot=slot,sp=sp,n=updates}
 if returns[pc]then return end
 returns[pc]=true
 emu.addMemoryCallback(function()
  if not pending or (r('CurrentBank')%128~=36 or r('CurrentBankC')%128~=36) or emu.getState()['cpu.sp']~=pending.sp+2 then return end
  local p=pending;pending=nil
  local force=r('SsHidden',p.slot)+256*r('SsAngleHi',p.slot)
  assert(force==math.floor((p.n*16+4)/9),'Source force continues growing: update '..p.n..' got '..force)
 end,emu.callbackType.exec,pc)
end,emu.callbackType.exec,assert(L.SophiaHomingVector))
emu.addEventCallback(function()
 emu.setInput({start=frame==240,down=frame==80,right=frame>=100 and frame<200 and(frame-100)%20==0,select=frame>=562 and frame<566},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<550 then return end
 if frame==550 then fixture()end
 w('AvStopwatch',200)
 if frame==1300 then
  assert(updates>150,'Actual missile remains active beyond two seconds')
  assert(slot and r('RgShotType',slot)==45 and r('SsMode',slot)<6,'Tracked missile survives offscreen world position')
  print('PASS source homing force grows past two seconds and active missile persists offscreen: '..updates..' updates');emu.stop(0)
 end
end,emu.eventType.endFrame)
