-- Isolated source-geometry fixture, not traversal evidence. Actual Select
-- creates each weapon. Its creation pose is explicitly injected at the origin
-- entry; the independent oracle is RyuProjectile.setDirection's Flash pads.
local cases={}
for weapon=1,4 do for dir=1,2 do for _,pose in ipairs({'stand','crouch','air','wall','wall-back'})do
 cases[#cases+1]={weapon=weapon,dir=dir,pose=pose}
end end end
local frame,index,age=0,0,-1
local active,pending
local seen={}
local kinds={[1]=5,[2]=39,[3]=8,[4]=40}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local interruptDepth=0
for _,pc in ipairs({assert(L.NonMaskableInterrupt),assert(L.IrqScrollSplit)})do
 emu.addMemoryCallback(function()interruptDepth=interruptDepth+1 end,emu.callbackType.exec,pc)
end
for _,pc in ipairs({assert(L.NonMaskableInterrupt_RTI),assert(L.IrqScrollSplit_RTI)})do
 emu.addMemoryCallback(function()interruptDepth=interruptDepth-1;assert(interruptDepth>=0,'Balanced origin-fixture interrupt scope')end,emu.callbackType.exec,pc)
end
-- ROSTER is PRG bank22 at $a000 on both mappers. An exec address alone also
-- fires while an unrelated bank occupies that window; never inject a pose
-- or inspect a return there. The v17 negative hit this address in bank61.
local function inOriginBank()return interruptDepth==0 and r('CurrentBank')%128==22 end
local function reset()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 w('Player_X_Position',128);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('PlayerStatus',1);w('PlayerFacingDir',active.dir)
 w('InvOwnedLo',0x1f,10);w('InvSelected',active.weapon,10);w('InvAmmo',50,160)
 w('RgAttack',0);w('RgAttackAge',0);w('RgAttackKind',0);w('RgCooldown',0);w('RgPreviousButtons',0)
 w('RgCrouch',0);w('XgWall',0);w('XgWallContact',0);w('XgWallLock',0);w('AvSlash',0)
 w('TimerControl',0);w('PlayerChangeSizeFlag',0);w('GameEngineSubroutine',8)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 pending=nil
end
emu.addMemoryCallback(function()
 if not active or not inOriginBank()then return end
 local pose,dir=active.pose,active.dir
 local wall=pose=='wall'or pose=='wall-back'
 local back=pose=='wall-back'
 if back then assert((r('SavedJoypadBits')&(dir==1 and 2 or 1))~=0,string.format('Real opposite direction requests a backward wall throw: case=%d weapon=%d dir=%d frame=%d age=%d saved=%02x live=%02x engine=%d pending=%d',index,active.weapon,dir,frame,age,r('SavedJoypadBits'),r('SavedJoypad1Bits'),r('GameEngineSubroutine'),r('AvPending')))end
 -- Only the actor pose is injected; the actual projectile is never written.
 w('Player_X_Position',128);w('Player_PageLoc',1);w('Player_Y_Position',96);w('Player_Y_HighPos',1)
 w('PlayerFacingDir',dir);w('RgCrouch',pose=='crouch'and 1 or 0)
 w('Player_State',pose=='air'and 1 or wall and 2 or 0);w('XgWall',wall and dir or 0)
 local horizontal=wall and(back and 20 or 10)or pose=='stand'and 15 or 13
 local vertical=wall and 9.5 or pose=='crouch'and 16 or 11
 local shotDir=back and 3-dir or dir
 pending={slot=r('RgSlot'),x=384+8+(shotDir==1 and horizontal or-horizontal),y=96+vertical,dir=shotDir}
end,emu.callbackType.exec,L.RyuProjectileOrigin)
emu.addMemoryCallback(function()
 if not pending or not inOriginBank()then return end
 local i=pending.slot
 assert(r('RgShotType',i)==kinds[active.weapon],string.format('Actual selected weapon reaches common source origin: case=%d pose=%s weapon=%d type=%d expected=%d frame=%d age=%d selected=%d pending=%d engine=%d bank=%d',index,active.pose,active.weapon,r('RgShotType',i),kinds[active.weapon],frame,age,r('InvSelected',10),r('AvPending'),r('GameEngineSubroutine'),r('CurrentBank')%128))
 assert(r('RgShotX',i)+256*r('RgShotPage',i)==pending.x,'Source horizontal pad, '..active.pose..'/'..active.weapon..'/'..active.dir)
 assert(r('RgShotY',i)+r('RgShotFracY',i)/256==pending.y,'Source vertical pad, '..active.pose..'/'..active.weapon..'/'..active.dir)
 assert(r('RgShotDir',i)==pending.dir,'Source forward/backward launch direction')
 seen[index]=(seen[index]or 0)+1;pending=nil
end,emu.callbackType.exec,L.RyuProjectileOriginDone)
emu.addEventCallback(function()
 local t=age%80
 local back=active and active.pose=='wall-back'and t>=5 and t<45
 emu.setInput({down=frame==80,right=frame>=100 and frame<180 and(frame-100)%20==0 or(back and active.dir==2),
  left=back and active.dir==1,start=frame==240,select=active and t>=10 and t<15},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<600 then return end
 age=age+1
 if age%80==0 then
  index=index+1;active=cases[index]
  if not active then print('PASS all four Ryu projectiles use source standing/crouched/air/wall/backward-wall origins, both directions: 40 actual Select launches');emu.stop(0);return end
  assert(r('SelectedCharacter')==10,'Real menu selected Ryu');reset()
 end
 if age%80==65 then assert(seen[index]==1,'Exactly one actual source origin observed for case '..index..': '..tostring(seen[index]))end
end,emu.eventType.endFrame)
