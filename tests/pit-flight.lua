-- Flight is a new port ability, tested in explicit flat-ground/roof fixtures.
local frame=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function vy()local v=r('MmVY')+256*r('MmVY',1)+65536*r('MmVY',2);return (v>=0x800000 and v-0x1000000 or v)/65536 end
local minFuel=60;local wing,shot=false,false
local function fixture(power)
 for i=0,415 do w('Block_Buffer_1',0,i) end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col) end end
 for i=0,5 do w('Enemy_Flag',0,i) end
 for i=0,9 do w('RgShotType',0,i) end
 w('Player_X_Position',120);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('Player_Y_Speed',0);w('Player_X_Speed',0);w('PlayerStatus',power);w('PlayerFacingDir',1)
 w('SwimmingFlag',0);w('XgPitFlight',0);w('XgPitFuel',60);w('RgPreviousButtons',0);w('PreviousA_B_Buttons',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i) end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i) end
end
emu.addEventCallback(function()
 local n=math.floor((frame-550)/180);local t=(frame-550)%180
 emu.setInput({down=frame==80,start=frame==240,a=n>=0 and ((t>=2 and t<10) or (t>=16 and t<100)),b=n==2 and (t==22 or t==40)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 local n=math.floor((frame-550)/180);local t=(frame-550)%180
 if t==0 and n<4 then
  fixture(math.min(n,2));minFuel=60
  if n==3 then
   w('XgPitFuel',0)
   for col=0,15 do w('Block_Buffer_1',0x54,64+col) end
  end
 end
 if n==3 and t==3 then assert(r('Player_State')~=0 and r('XgPitFuel')==60,'Immediate ground jump retains the landing recharge') end
 if t==20 then
  if n<2 then assert(r('XgPitFlight')==0,'Only the third power level flies')
  elseif n==2 then assert(r('XgPitFlight')==1 and math.abs(vy()+1.5)<.001,'Second A press gives controlled winged lift') end
 end
 if n==2 then
  minFuel=math.min(minFuel,r('XgPitFuel'))
  if r('RgPose')==L.XG_POSE_FLAP1 or r('RgPose')==L.XG_POSE_FLAP2 then wing=true end
  if r('RgPose')==L.XG_POSE_FLAPSHOT1 or r('RgPose')==L.XG_POSE_FLAPSHOT2 then shot=true end
  if t==30 or t==42 then local f=assert(io.open(OUTPUT..ROM_NAME..'-pit-flight-'..t..'.png','wb'));f:write(emu.takeScreenshot());f:close() end
  if t>=18 and t<=80 and t%2==0 then local f=assert(io.open(OUTPUT..ROM_NAME..'-pit-flap-'..t..'.png','wb'));f:write(emu.takeScreenshot());f:close() end
  if t==100 then assert(minFuel==0 and r('XgPitFlight')==0,'Flight exhausts its 60-update budget while A is held') end
  if t==165 then assert(r('Player_State')==0 and r('XgPitFuel')==60,'Landing recharges flight');assert(wing and shot,'Flapping body and shooting art displayed') end
 end
 if n==3 and t>=16 and t<100 then assert(r('Player_Y_Position')>=104,'Flight cannot pass through the solid roof: t='..t..' y='..r('Player_Y_Position')) end
 if n==4 then print('PASS Pit third-level flight activation, power gating, flapping/shooting art, one-second budget, exhaustion, solid roof and immediate-jump landing recharge');emu.stop(0) end
end,emu.eventType.endFrame)
