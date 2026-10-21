-- Explicit posture/terrain arenas, not a level-clear proof. Only each arena's
-- initial RAM is authored; all crouch release, movement, attacks and jumps use
-- ordinary controller input. The retained-state implementation is not an oracle.
local frame,index,current,finished=0,0,nil,false
local cases={}
for _,blocked in ipairs({true,false})do
 for _,air in ipairs({true,false})do
  for _,dir in ipairs({1,2})do
   for _,x in ipairs({0x4ef,0x4ff,0x500})do
    for _,stationary in ipairs({true,false})do
     cases[#cases+1]={blocked=blocked,air=air,dir=dir,x=x,stationary=stationary}
    end
   end
  end
 end
end
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function worldX()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function worldY()return r('Player_Y_Position')+256*(r('Player_Y_HighPos')-1)end
local function cell(x,y)return (x//256)%2*208+((y-32)//16)*16+(x%256)//16 end
local function solidBand(c,x,y)
 if not c.blocked then return false end
 -- Independent AABB overlap for the standing-only band (short top19/full8).
 -- This deliberately does not duplicate the helper's four point samples.
 return x+1<c.roofRight and x+15>c.roofLeft and y+8<c.roofY+16 and y+19>c.roofY
end
local function setup(c)
 c.age=0;c.lastX=c.x;c.blockedUpdates=0;c.shortUpdates=0;c.fullUpdates=0
 c.fired=false;c.moved=false;c.stood=false;c.jumped=false;c.updates=0
 local tileX=((c.x+(c.dir==1 and 1 or 14))//16)*16
 c.roofLeft=tileX-(c.dir==1 and 16 or 0);c.roofRight=c.roofLeft+32
 c.roofY=c.air and 64 or 176
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('RgMeleeBlocks',0,i)end
 for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x61,page*208+176+col)end end
 if c.blocked then for x=c.roofLeft,c.roofRight-1,16 do w('Block_Buffer_1',0x62,cell(x,c.roofY))end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('MmBulletType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('SelectedCharacter',6);w('PlayerStatus',0);w('PlayerSize',0)
 w('InvOwnedLo',1,6);w('InvOwnedHi',0,6);w('InvSelected',0,6)
 w('Player_X_Position',c.x%256);w('Player_PageLoc',c.x//256)
 w('Player_Y_Position',c.air and 65 or 176);w('Player_Y_HighPos',1)
 w('Player_State',c.air and 1 or 0);w('Player_X_Speed',0);w('Player_Y_Speed',0)
 w('PlayerFacingDir',c.dir);w('Player_MovingDir',c.dir)
 w('ScreenLeft_X_Pos',(c.x-96)%256);w('ScreenLeft_PageLoc',(c.x-96)//256)
 w('ScreenRight_X_Pos',(c.x+159)%256);w('ScreenRight_PageLoc',(c.x+159)//256)
 w('ScrollLock',1);w('ScrollThirtyTwo',0);w('AreaParserTaskNum',0)
 w('TimerControl',0);w('InjuryTimer',0);w('GuestPowerupActive',0)
 w('GameEngineSubroutine',8);w('DisableCollisionDet',0);w('SwimmingFlag',0);w('AreaType',1)
 w('RgCrouch',1);w('CrouchingFlag',4);w('Player_BoundBoxCtrl',17)
 w('RgPreviousButtons',0);w('RgAttack',0);w('RgCooldown',0);w('RgShootPose',0)
 w('MmSliding',0);w('SmBall',0);w('SmCrouch',0)
 w('XgJumpUsed',0);w('XgDash',0);w('XgRise',0);w('XgWall',0);w('XgWallContact',0)
 w('XgCeiling',0);w('XgHoverActive',0);w('XgPitFlight',0)
 if L.XgPitCrouchHeld then w('XgPitCrouchHeld',0)end
end
local log=assert(io.open(OUTPUT..ROM_NAME..'-pit-crouch-clearance.csv','w'))
log:write('case,blocked,air,direction,startX,stationary,age,x,y,crouch,box,blockedVolume,updates,shots\n')
local interruptDepth=0
emu.addMemoryCallback(function()interruptDepth=interruptDepth+1 end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()interruptDepth=interruptDepth-1 end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
if L.IrqScrollSplit and L.IrqScrollSplit_RTI then
 emu.addMemoryCallback(function()interruptDepth=interruptDepth+1 end,emu.callbackType.exec,L.IrqScrollSplit)
 emu.addMemoryCallback(function()interruptDepth=interruptDepth-1 end,emu.callbackType.exec,L.IrqScrollSplit_RTI)
end
emu.addMemoryCallback(function()
 if current and interruptDepth==0 and r('CurrentBank')%128==1 then current.updates=current.updates+1 end
end,emu.callbackType.exec,L.PlayerBGCollision)
emu.addEventCallback(function()
 if frame<600 then emu.setInput({down=frame==80,start=frame==240},0);return end
 if not current and not finished then
  index=index+1
  if not cases[index]then
   finished=true;log:close()
   print('PASS Pit crouch clearance:48 blocked/open stationary/moving ground/air cases, mirrored row/page seams, real short/full bounds, shots and post-clear jumps')
   emu.stop(0);return
  end
  current=cases[index];setup(current)
 end
 if not current then return end
 local c=current
 -- Moving cases also hold the direction during deliberate Down. That must
 -- still stop; only the later clearance-retained pose may move out.
 local move=c.age>=(c.stationary and 12 or 0)
 local jumping=c.jumpAt and c.age>=c.jumpAt and c.age<c.jumpAt+16
 emu.setInput({down=c.age<4,right=move and c.dir==1,left=move and c.dir==2,
  b=c.age>=4 and c.age%12<5,a=jumping},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if not current then assert(frame<14000,'Bounded posture matrix completes');return end
 local c=current;local x,y=worldX(),worldY()
 local blocked=solidBand(c,x,y)
 local short=r('RgCrouch')~=0
 local count=0;for i=0,9 do if r('RgShotType',i)~=0 then count=count+1 end end
 c.fired=c.fired or count>0
 if not c.air and c.age>=1 and c.age<4 then
  assert(x==c.x,'Deliberate Down retains Pit native crouch stop even with a direction held')
 end
 if c.age>=4 and c.updates>1 then
  log:write(table.concat({index,tostring(c.blocked),tostring(c.air),c.dir,c.x,tostring(c.stationary),c.age,x,y,r('RgCrouch'),r('Player_BoundBoxCtrl'),tostring(blocked),c.updates,count},',')..'\n');log:flush()
  assert(math.abs(x-c.lastX)<=4,'Pit cannot traverse a tile row during uncrouch:case '..index..' age '..c.age..' dx '..(x-c.lastX))
  if blocked then
   c.blockedUpdates=c.blockedUpdates+1
   assert(short and r('CrouchingFlag')~=0 and r('Player_BoundBoxCtrl')==17,'Pit must retain the actual short body while the standing volume overlaps a roof:case '..index..' age '..c.age..' X '..x..' Y '..y)
   assert(r('BoundingBox_UL_Corner',1)==(r('Player_Y_Position')+19)%256,'Actual retained body top remains canonicalY+19 under the roof')
   assert(r('BoundingBox_UL_Corner',3)==(r('Player_Y_Position')+32)%256,'Actual retained body bottom remains canonicalY+32 under the roof')
  end
  if not c.blocked and c.age>=8 and c.updates>=6 then
   assert(not short and r('Player_BoundBoxCtrl')==12,'Open-space release promptly restores the full body')
  end
  if short then
   c.shortUpdates=c.shortUpdates+1
   assert(r('Player_BoundBoxCtrl')==17,'Retained crouch uses the short body, not only a pose flag')
  elseif not blocked then
   c.fullUpdates=c.fullUpdates+1;c.stood=true
   assert(r('Player_BoundBoxCtrl')==12,'Clear uncrouch restores the full Pit body')
   -- Actual enemy-collision rectangle agrees with the selected short/full body.
   assert(r('BoundingBox_UL_Corner',1)==(r('Player_Y_Position')+8)%256,'Standing body top is canonicalY+8')
   assert(r('BoundingBox_UL_Corner',3)==(r('Player_Y_Position')+32)%256,'Standing body bottom remains canonicalY+32')
  end
  c.moved=c.moved or math.abs(x-c.x)>=8
  if c.stood and not c.air and not c.jumpAt and not blocked and c.age>=24 and r('Player_State')==0 then c.jumpAt=c.age+8 end
  if c.jumpAt and c.age>=c.jumpAt+4 and y<170 and r('Player_State')~=0 then c.jumped=true end
  local done=c.stood and c.moved and c.fired and(c.air or c.jumped)
  if done and c.age>=40 then
   if c.blocked then assert(c.blockedUpdates>0 and c.shortUpdates>0,'Blocked fixture actually exercised retained short-body updates')end
   assert(c.fullUpdates>0,'Each arena eventually restores full body in clear space')
   print('PASS Pit clearance case '..index..' blocked='..tostring(c.blocked)..' air='..tostring(c.air)..' dir='..c.dir..' seam='..c.x..' updates='..c.updates)
   current=nil
  end
 end
 if current then
  c.lastX=x;c.age=c.age+1
  assert(c.age<180,'Pit retains required movement/attacks and eventually stands and jumps after clearance:case '..index)
 end
 assert(frame<14000,'Bounded posture matrix completes')
end,emu.eventType.endFrame)
