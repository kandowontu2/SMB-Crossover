-- Explicit flat-ground fixture; walking/stopping/reversal use controller input.
local c=assert(WALK_CHARACTER)
local frame=0
local groups,last,count={},nil,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function fixture()
 for i=0,415 do w('Block_Buffer_1',0,i) end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col) end end
 for i=0,5 do w('Enemy_Flag',0,i) end
 for i=0,9 do w('RgShotType',0,i) end
 w('Player_X_Position',80);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('Player_Y_Speed',0);w('Player_X_Speed',0);w('PlayerStatus',0);w('PlayerFacingDir',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('RgClock',147);w('RgShootPose',0);w('RgAttack',0);w('XgBassStep',0);w('XgDash',0);w('RgPreviousButtons',0)
 w('XgWalkTick',0);w('XgWalkPhase',0);w('XgWalkDirection',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i) end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i) end
 groups={};last=nil;count=0
end
local function verify()
 if last then groups[#groups+1]={last,count} end
 local seq=c==9 and {L.XG_POSE_WALK1,L.XG_POSE_WALK2,L.XG_POSE_WALK3,L.XG_POSE_WALK2} or {L.XG_POSE_WALK1,L.XG_POSE_WALK2,L.XG_POSE_WALK3}
 assert(#groups>=7,'At least two full walk cycles')
 for i=1,#groups-1 do
  assert(groups[i][1]==seq[(i-1)%#seq+1],'Source walk frame order at '..i..': '..groups[i][1])
  assert(groups[i][2]==(c==9 and 6 or 7),'Source walk frame duration at '..i..': '..groups[i][2])
 end
end
emu.addMemoryCallback(function()
 if frame<550 or frame>=790 or r('CurrentBank')%128~=0x1e then return end
 local t=(frame-550)%120
 if t<8 or t>=83 then return end
 local pose=r('RgPose')
 if pose<L.XG_POSE_WALK1 or pose>L.XG_POSE_WALK3 then return end
 if pose~=last then if last then groups[#groups+1]={last,count} end;last=pose;count=0 end
 count=count+1
end,emu.callbackType.exec,L.ExpandedPose)
emu.addEventCallback(function()
 local n=math.floor((frame-550)/120);local t=(frame-550)%120
 emu.setInput({down=frame==80,right=(frame>=100 and frame<100+20*(c-6) and (frame-100)%20==0) or (n==0 and t>=8 and t<83),
 left=n==1 and t>=8 and t<83,start=frame==240},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 local n=math.floor((frame-550)/120);local t=(frame-550)%120
 if t==0 and n<2 then fixture() end
 if t==15 and c==9 then assert(r('RgPose')==L.XG_POSE_WALKSTEP or r('RgPose')==L.XG_POSE_WALK1,'Initial step uses dedicated art before the walk loop') end
 if t==90 then verify();assert(r('RgPose')==L.XG_POSE_STAND and r('XgWalkTick')==0,'Release returns to idle and resets the walk timer') end
 if t>=8 and t<85 and t%3==0 then
  local f=assert(io.open(OUTPUT..ROM_NAME..'-walk-'..c..'-'..n..'-'..t..'.png','wb'));f:write(emu.takeScreenshot());f:close()
 end
 if n==2 then print('PASS character '..c..' source walking art order/cadence, dedicated Bass step, left/right start and idle reset');emu.stop(0) end
end,emu.eventType.endFrame)
