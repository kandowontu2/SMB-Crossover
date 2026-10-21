-- The source equations are the oracle. Only the arena/character state is
-- injected; a real Select press creates each projectile and attack sequence.
local frame,case,updates=0,0,0
local modelvx,side,reverse,pending=0,false,false,nil
local launches,trajectoryUpdates={},{}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
local function signed(v,bits)return v>=2^(bits-1) and v-2^bits or v end
local interruptDepth=0
for _,pc in ipairs({assert(L.NonMaskableInterrupt),assert(L.IrqScrollSplit)})do
 emu.addMemoryCallback(function()interruptDepth=interruptDepth+1 end,emu.callbackType.exec,pc)
end
for _,pc in ipairs({assert(L.NonMaskableInterrupt_RTI),assert(L.IrqScrollSplit_RTI)})do
 emu.addMemoryCallback(function()interruptDepth=interruptDepth-1;assert(interruptDepth>=0,'Balanced Windmill-fixture interrupt scope')end,emu.callbackType.exec,pc)
end
-- Both labels are in ROSTER bank22. The v22 negative also executed the entry
-- address in physical bank61 ($D0 instead of Ryu's $AE), advancing the host
-- oracle without a projectile update. Audio can change physical mappings
-- without the foreground shadow, so exclude NMI/IRQ execution as well.
local function inWindmillBank()return interruptDepth==0 and r('CurrentBank')%128==22 end
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame>=100 and frame<180 and (frame-100)%20==0,start=frame==240,select=frame==560 or frame==760},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if frame<560 or not inWindmillBank()then return end
 local slot=r('RgSlot');local px=r('Player_X_Position')+256*r('Player_PageLoc')+8
 local sx=r('RgShotX',slot)+256*r('RgShotPage',slot)
 if r('RgShotAge',slot)==1 then
  launches[case]=(launches[case]or 0)+1
  assert(math.abs(sx-px)==15,'Source standing muzzle is 30 Flash pixels from center')
  assert(r('RgAttackAge')==3,'Projectile launches on throw-2 after the first 45ms boundary')
  modelvx=(case==1 and 1 or -1)*800/120;side=false;reverse=false
 end
 local newside=sx>px
 if newside~=side then reverse=false end
 side=newside
 if math.abs(sx-px)>=25 then reverse=true end
 modelvx=math.max(-800/120,math.min(800/120,modelvx+(side and 1 or -1)*(reverse and -1 or 1)*2300/7200))
 pending={slot=slot,vx=modelvx}
end,emu.callbackType.exec,L.RyuWindmillMotion)
emu.addMemoryCallback(function()
 if not pending or not inWindmillBank()then return end
 local slot=pending.slot
 if r('RgShotType',slot)~=0 then
  local v=signed(r('RgShotVXHi',slot)*65536+r('RgShotVXLo',slot)*256+r('XgWindmillFraction'),24)/65536
  assert(math.abs(v-pending.vx)<0.001,'Windmill source acceleration, reversal and cap: '..v..' / '..pending.vx)
  updates=updates+1
  trajectoryUpdates[case]=(trajectoryUpdates[case]or 0)+1
 end
 pending=nil
end,emu.callbackType.exec,L.RyuWindmillUpdated)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 or frame==750 then
  case=case+1
  for i=0,415 do w('Block_Buffer_1',0,i) end
  for col=0,15 do w('Block_Buffer_1',0x54,176+col) end
  for i=0,5 do w('Enemy_Flag',0,i) end
  for i=0,9 do w('RgShotType',0,i) end
  w('PlayerStatus',2);if true then w('InvOwnedLo',9,10);w('InvSelected',3,10);w('InvAmmo',50,160)end;w('Player_X_Position',128);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',case)
  w('RgAttack',0);w('RgCooldown',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i) end
 end
 if frame==940 then
  assert(updates>80,'Both mirrored source trajectories were observed: '..updates)
  for i=1,2 do
   assert(launches[i]==1,'One actual Select launch for mirrored trajectory '..i)
   assert((trajectoryUpdates[i]or 0)>0,'Actual motion observed for mirrored trajectory '..i)
  end
  for i=0,9 do assert(r('RgShotType',i)==0,'Windmill catches its owner') end
  print('PASS Ryu source 45ms throw launch and both windmill trajectories: 800 speed, 2300 spring, 50-pixel reversal and catch');emu.stop(0)
 end
end,emu.eventType.endFrame)
