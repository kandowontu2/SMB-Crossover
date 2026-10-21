-- Controller discovery using Scrooge's native stronger pogo; no state grants.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local normal=assert(dofile(root..'/tools/playthroughs/mario_luigi_scrooge_policy.lua'))
local airborne=0
local drillStart
local lastCap='edge'
local lastCapArm
local secondWorldCap='land'
local secondWorldArm
local lateGap='land'
local lateGapLaunch
local springPhase='approach'
local springJumpAt
local waterFirst='land'
local waterFirstLaunch
local waterBridge='land'
local waterBridgeJump
local waterBridgeRise
local waterExitPhase='land'
local waterExitJump
local undergroundExit='land'
local undergroundExitLaunch
local firstHighCap='land'
local firstHighCapArm
local bonusPhase='back'
local undergroundGaps='edge'
local gapLaunch,gapArm
local castleFireJump
return function(c)
 local b=normal(c)
 if c.char~=12 then return b end
 if c.areaType==2 and c.area==64 then
  -- The exit's raised brick tread sits above its low side entrance. Settle
  -- in the entrance well left of that tread, then walk along the lower floor.
  if bonusPhase=='back' then
   local target=c.camera+24
   if c.x>=target and c.x<=target+3 and c.grounded and c.y>=176 then bonusPhase='exit'
   else return {right=c.x<target,left=c.x>target+3}end
  end
  return {right=true}
 end
 bonusPhase='back'
 if c.world==0 and c.level==1 and c.areaType==2 and c.x>=1840 and c.x<2064 then
  if undergroundGaps=='edge' then
   if c.grounded and c.x>=1908 and c.y>=176 then undergroundGaps='first';gapLaunch=c.poll
   else return {right=c.x<1908}end
  end
  if undergroundGaps=='first' then
   if c.grounded and c.x>=1940 then undergroundGaps='island'
   else return {right=c.x<1960,left=c.x>1964,a=c.poll-gapLaunch<32}end
  end
  if undergroundGaps=='island' then
   if c.grounded and c.x>=1970 and c.x<=1974 then undergroundGaps='arm';gapArm=c.poll
   else return {right=c.x<1972,left=c.x>1974}end
  end
  if undergroundGaps=='arm' then
   if c.r('ScPogo')~=0 and c.r('MmVY',2)==250 then undergroundGaps='cross'
   else return {a=c.poll-gapArm<16,down=c.poll-gapArm>=3,b=c.poll-gapArm>=3}end
  end
  return {right=true,down=true,b=true}
 end
 if c.areaType==0 then
  if c.world==1 and c.level==1 and c.x>=2960 then
   if waterExitPhase=='land' then
    if c.grounded and c.y<=112 and c.x>=3004 and c.x<=3012 then waterExitPhase='enter'
    else
     if c.grounded and c.y>112 and(not waterExitJump or c.poll-waterExitJump>60)then waterExitJump=c.poll end
     return {right=c.x<3008,left=c.x>3012,a=waterExitJump and c.poll-waterExitJump<16,b=c.poll%16<4}
    end
   end
   return {right=true}
  end
  if c.world==1 and c.level==1 and c.x>=2020 and c.x<2256 then
   if waterBridge=='land' then
    if c.grounded and c.y<=112 and c.x>=2062 and c.x<=2068 then waterBridge='rise';waterBridgeRise=c.poll
    else
     if c.grounded and c.y>112 and(not waterBridgeJump or c.poll-waterBridgeJump>60)then waterBridgeJump=c.poll end
     return {right=c.x<2064,left=c.x>2068,a=waterBridgeJump and c.poll-waterBridgeJump<16,b=c.poll%16<4}
    end
   end
   if waterBridge=='rise' then
    -- Water controls are disabled outside YHigh=1. Reach the stem's left
    -- edge before the brief top wrap so rightward control resumes on landing.
    if c.yHigh==0 or c.y<=64 then waterBridge='cross'
    else return {a=c.poll-waterBridgeRise<34,b=c.poll%16<4}end
   end
   return {right=true,b=c.poll%16<4}
  end
  if c.world==1 and c.level==1 and c.x>=980 and c.x<1160 then
   if waterFirst=='land' then
    if c.grounded and c.y<=96 and c.x>=1022 and c.x<=1028 then waterFirst='edge'
    else return {right=c.x<1024,left=c.x>1028,b=c.poll%16<4}end
   end
   if waterFirst=='edge' then
    if c.grounded and c.x>=1030 then waterFirst='cross';waterFirstLaunch=c.poll
    else return {right=true,b=c.poll%16<4}end
   end
   return {right=true,a=c.poll-waterFirstLaunch<34,b=c.poll%16<4}
  end
  return b
 end
 if c.areaType==3 then
  -- Bowser flames are native actor $15, outside the generic nearest-enemy
  -- helper's ordinary-enemy filter. Respond with real jump inputs.
  if c.grounded and not c.lastA then
   for slot=0,5 do
    if c.r('Enemy_Flag',slot)>0 and c.r('Enemy_Flag',slot)<128 and c.r('Enemy_ID',slot)==0x15 then
     local fx=c.r('Enemy_X_Position',slot)+256*c.r('Enemy_PageLoc',slot)
     local fy=c.r('Enemy_Y_Position',slot)
     if fx>c.x and fx<c.x+64 and math.abs(fy-c.y)<56 then castleFireJump=c.poll end
    end
   end
  end
  if castleFireJump and c.poll-castleFireJump<32 then return {right=true,a=true}end
  return b -- Release pogo to descend below castle overhangs.
 end
 if c.world==0 and c.level==2 and c.x>=580 and c.x<656 then
  -- The first tall cap rises64px, beyond the ordinary58px jump. Use the
  -- actual84px pogo rebound rather than entering its lower side corner.
  if firstHighCap=='land' then
   if c.grounded and c.y==96 and c.x>=598 and c.x<=604 then firstHighCap='arm';firstHighCapArm=c.poll
   else return {right=c.x<600,left=c.x>604}end
  end
  if firstHighCap=='arm' then
   if c.r('ScPogo')~=0 and c.r('MmVY',2)==250 then firstHighCap='cross'
   else return {a=c.poll-firstHighCapArm<16,down=c.poll-firstHighCapArm>=3,b=c.poll-firstHighCapArm>=3}end
  end
  return {right=true,down=true,b=true}
 end
 if c.world==1 and c.level==0 and c.x>=2944 and c.x<3070 then
  local animation=c.r('JumpspringAnimCtrl')
  if springPhase=='approach' then
   if animation>0 then springPhase='compress';return {}end
   if c.grounded and c.x>=2990 and(not springJumpAt or c.poll-springJumpAt>40)then springJumpAt=c.poll end
   return {right=c.x<3008,left=c.x>3012,a=springJumpAt and c.poll-springJumpAt<16}
  elseif springPhase=='compress' then
   if animation==0 and c.vy>=128 then springPhase='cross';return {right=true}end
   return {a=animation>=2 and animation<=4}
  end
  return {right=true}
 end
 if c.world==1 and c.level==0 and c.x>=2080 and c.x<2280 then
  if lateGap=='land' then
   if c.grounded and c.y>=176 and c.x>=2172 and c.x<=2180 then lateGap='approach'
   else return {right=c.x<2176,left=c.x>2180}end
  end
  if lateGap=='approach' then
   if c.x>=2208 and c.grounded then lateGap='cross';lateGapLaunch=c.poll
   else return {right=true}end
  end
  return {right=true,a=c.poll-lateGapLaunch<32}
 end
 if c.world==1 and c.level==0 and c.x>=1352 and c.x<1440 then
  if secondWorldCap=='land' then
   if c.grounded and c.y<=112 and c.x>=1394 and c.x<=1400 then secondWorldCap='arm';secondWorldArm=c.poll
   else return {right=c.x<1396,left=c.x>1400}end
  end
  if secondWorldCap=='arm' then
   if c.r('ScPogo')~=0 and c.r('MmVY',2)==250 then secondWorldCap='cross'
   else return {a=c.poll-secondWorldArm<16,down=c.poll-secondWorldArm>=3,b=c.poll-secondWorldArm>=3}end
  end
  return {right=true,down=true,b=true}
 end
 if c.world==1 and c.level==0 and c.x>=1312 and c.x<1552 then
  b.b=false;b.down=false -- Climb the brick stairs without smashing their treads.
  return b
 end
 -- The last 1-3 cap rises64px. Engage pogo on the preceding safe ledge,
 -- then cross on its real84px rebound rather than the ordinary58px jump.
 if c.world==0 and c.level==2 and c.x>=1576 and c.x<1648 then
  if lastCap=='edge' then
   if c.grounded and c.x>=1590 and c.x<=1596 then lastCap='arm';lastCapArm=c.poll
   else return {right=c.x<1592,left=c.x>1596}end
  end
  if lastCap=='arm' then
   if c.r('ScPogo')~=0 and c.r('MmVY',2)==250 then lastCap='cross'
   else return {a=c.poll-lastCapArm<16,down=c.poll-lastCapArm>=3,b=c.poll-lastCapArm>=3}end
  end
  return {right=true,down=true,b=true}
 end
 if c.world==0 and c.level==1 and c.areaType==2 and c.x>=2420 and c.x<2580 then
  -- Release pogo and use the second real lift below the exit roof.
  if undergroundExit=='land' then
   if c.grounded and c.yHigh==1 and c.y>=112 and c.y<=128 and c.x>=2514 and c.x<=2520 then
    undergroundExit='cross';undergroundExitLaunch=c.poll
   else return {right=c.x<2516,left=c.x>2520}end
  end
  return {right=true,a=c.poll-undergroundExitLaunch<32}
 end
 if c.world==0 and c.level==1 and c.areaType==2 and c.x>=2580 then return b end
 if c.world==0 and c.level==1 and c.areaType==2 and c.x>=820 and c.x<928 then
  drillStart=drillStart or c.poll
  local age=(c.poll-drillStart)%80
  return {right=true,a=age<20,b=c.poll%16<4}
 end
 if c.grounded then airborne=0 else airborne=airborne+1 end
 if not c.grounded and airborne>=3 then
  b.down=true;b.b=true
 elseif c.r('ScPogo')~=0 then
  local function solid(x,y)
   local t=c.block(x,y)
   return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3
  end
  local wall=solid(c.x+40,c.y+8)or solid(c.x+40,c.y+24)
  local mount=solid(c.x+40,c.y-24)or solid(c.x+40,c.y-8)
  local gap=not solid(c.x+32,math.min(c.y+40,232))
  if wall or mount or gap then b.down=true;b.b=true;b.a=false end
 end
 return b
end
