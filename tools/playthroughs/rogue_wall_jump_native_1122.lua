-- Continue from the verified High Jump landing on the 1-2 floor.
local function wallJumpPhase(name)
 local wall=gear.wall
 wall.phase=name
 wall.entered=updates
 assert(#wall.steps<42,'Bounded Wall Jump route milestones')
 wall.steps[#wall.steps+1]={phase=name,player=state()}
end

local function descendingLift()
 for slot=0,5 do
  local a=actor(slot)
  if a.id==0x27 and a.flag>0 and a.flag<128 and a.x==2236
     and r('Enemy_Y_HighPos',slot)==1 and a.y>=128 and a.y<=156 then
   return a
  end
 end
end

local function wallJumpLift(c,wall,grounded)
 if not wall.liftTakeoff then
  local aim={left=c.x>2199,right=c.x<2196}
  if aim.left or aim.right or not grounded or r('RdHeld')&128~=0 then return aim end
  assert(c.y<=115,'Reach the top of the native staircase')
  local lift=descendingLift()
  if not lift then return {} end
  wall.liftTarget=lift
  wall.liftTakeoff=state()
  return {right=true,a=true}
 end
 if not wall.liftLanding then
  if not wall.liftApex or c.y<wall.liftApex.y then wall.liftApex=state() end
  local lift=actor(wall.liftTarget.slot)
  if c.x>=2240 and c.x<=2276 and grounded and r('RdFrozenSupport')~=0
     and lift.id==0x27 and lift.flag>0 and math.abs(c.y+32-lift.y)<=1 then
   wall.liftLanding=state()
   return {}
  end
  local inRange=c.x>=2252 and c.x<=2255
  return {left=c.x>2255,right=c.x<2252,a=not inRange and r('RdVY')>=128}
 end
 if not wall.liftExit then
  if grounded and c.x>=2262 and r('RdHeld')&128==0 then
   wall.liftExit=state()
   return {right=true,a=true}
  end
  return {right=true}
 end
 if c.x<2320 then return {right=true,a=r('RdVY')>=128} end
 wall.crossedLiftGap=state()
end

local function wallJumpTravel(c, wall, grounded)
 if not wall.firstGap and c.x>=1198 then
  if not wall.firstTakeoff then
   if c.x<1274 then return {right=true,b=updates%8==0} end
   if not grounded then return {} end
   wall.firstTakeoff=state()
   return {right=true,a=true}
  end
  if not wall.firstApex or c.y<wall.firstApex.y then wall.firstApex=state() end
  if c.x<1328 then return {right=true,a=r('RdVY')>=128} end
  wall.firstGap=state()
 end
 if wall.firstGap and c.x<1440 then return {right=true,b=updates%8==0} end
 if c.x>=1890 and not wall.pairedGaps then
  if not wall.islandTakeoff then
   if c.x<1908 then return {right=true,b=updates%8==0} end
   if not grounded then return {} end
   wall.islandTakeoff=state()
   return {right=true,a=true}
  elseif not wall.islandLanding then
   if grounded and c.x>=1952 and c.x<1980 and c.y<=132 then
    wall.islandLanding=state()
    return {}
   end
   return {left=c.x>1961,right=c.x<1958,a=r('RdVY')>=128}
  elseif not wall.bankTakeoff then
   if r('RdHeld')&128~=0 or not grounded then return {} end
   wall.bankTakeoff=state()
   return {right=true,a=true}
  elseif c.x<2016 then
   return {right=true,a=r('RdVY')>=128}
  end
  wall.pairedGaps=state()
 end
 if c.x>=2184 and not wall.crossedLiftGap then
  local input=wallJumpLift(c,wall,grounded)
  if input then return input end
 end
 return gearTravel(setmetatable({area=gear.high.areaOffset},{__index=c}))
end

local function wallJumpDrive(c)
 local wall=gear.wall
 assert(c.level==1 and c.areaType==2 and r('AreaAddrsLOffset')==gear.high.areaOffset
        and updates-wall.started<4600,'Bounded ordinary route to 1-2 Wall Jump')
 wall.farthest=math.max(wall.farthest or 0,c.x)
 local function aim(low,top)
  return {left=c.x>top,right=c.x<low}
 end
 local grounded=c.yHigh==1 and bombReady(c)
 local releasedA=r('RdHeld')&128==0

 if wall.phase=='travel' then
  if c.x<2330 then return wallJumpTravel(c,wall,grounded) end
  wall.tile=c.block(2400,128)
  assert(wall.tile==0x5a,'Actual authored Wall Jump brick')
  wallJumpPhase('mount')
 end
 if stock=='wall-jump-credit' then return {} end
 if wall.phase=='mount' then
  if grounded and c.y<=98 and c.x>=2404 and c.x<=2407 then
   wallJumpPhase('morph-on-brick')
   return {}
  end
  if grounded and c.y<=98 and c.x<2404 then return {right=true} end
  local b=aim(2423,2426)
  if not b.left and not b.right and grounded and c.y>=160 and releasedA then
   wallJumpPhase('rise')
   b.a=true
  end
  return b
 end
 if wall.phase=='rise' then
  if c.y<=96 then
   wallJumpPhase('cross')
   return {left=true,a=true}
  end
  assert(updates-wall.entered<90,'Reach the top of the authored Wall Jump brick')
  return {a=true}
 end
 if wall.phase=='cross' then
  local b=aim(2404,2407)
  b.a=r('RdVY')>=128
  if grounded and c.y<=98 and not b.left and not b.right then
   wallJumpPhase('morph-on-brick')
   return {}
  end
  if grounded and c.y>=160 then wallJumpPhase('mount') end
  return b
 end
 if wall.phase=='morph-on-brick' then
  if r('RdAction')~=3 then return {down=true} end
  if r('RdHeld')&64~=0 then return {} end
  wallJumpPhase('place-bomb')
  return {b=true}
 end
 if wall.phase=='place-bomb' then
  if not wall.bomb then
   assert(updates-wall.entered<12,'Fresh B places the Wall Jump Bomb')
   return {b=true}
  end
  wallJumpPhase('open-brick')
  return {}
 end
 if wall.phase=='open-brick' then
  assert(updates-wall.entered<180,'Bomb reveals the actual Wall Jump item')
  if wall.hit and born then wallJumpPhase('collect') end
  return {}
 end
 if wall.phase=='collect' then
  if r('RdAction')==3 then return {up=true} end
  return {}
 end
 if wall.phase=='prepare' and not wall.gapRemoved then
  local b=aim(2384,2387)
  if not b.left and not b.right and grounded and c.y<=98 then
   assert(c.block(2384,128)==0x52,'Actual ordinary brick beside the used upgrade brick')
   wallJumpPhase('morph-for-gap')
   return {}
  end
  return b
 end
 if wall.phase=='morph-for-gap' then
  if r('RdAction')~=3 then return {down=true} end
  if r('RdHeld')&64~=0 then return {} end
  wallJumpPhase('place-gap-bomb')
  return {b=true}
 end
 if wall.phase=='place-gap-bomb' then
  if not wall.gapBomb then
   assert(updates-wall.entered<12,'Fresh B places the ordinary-brick Bomb')
   return {b=true}
  end
  wallJumpPhase('wait-gap')
  return {}
 end
 if wall.phase=='wait-gap' then
  assert(updates-wall.entered<180,'Bomb removes the actual adjacent brick')
  if wall.gapHit and r('RdWAction',wall.gapBomb.slot)==0 and c.block(2384,128)==0 then
   wall.gapRemoved=state()
   wallJumpPhase('prepare')
  end
  return {}
 end
 if wall.phase=='prepare' then
  if r('RdAction')==3 then return {up=true} end
  local b=aim(2382,2384)
  if not b.left and not b.right and grounded and c.y>=174 and releasedA then
   assert(c.block(2400,128)==0xc4,'The used upgrade brick provides the actual wall')
   wall.start=state()
   wallJumpPhase('run')
  end
  return b
 end
 local toward={right=true}
 if wall.phase=='run' then
  if grounded and r('RdAction')==1 and releasedA and c.x>=2384 then
   wallJumpPhase('rise-at-wall')
   toward.a=true
  end
  return toward
 end
 if wall.phase=='rise-at-wall' then
  if not grounded then
   -- Rise in the opening before leaning toward the elevated wall.
   -- Neutral horizontal input in the air keeps the running jump action.
   if c.y<=140 then
    wallJumpPhase('release')
    return toward
   end
   return {a=true}
  end
  assert(updates-wall.entered<10,'Running jump leaves the floor')
  toward.a=true
  return toward
 end
 if wall.phase=='release' then
  if grounded then
   wallJumpPhase('prepare')
   return {}
  end
  if c.y<=140 and releasedA and r('RdHeld')&3==1 then
   wallJumpPhase('press')
   toward.a=true
  end
  return toward
 end
 if wall.phase=='press' then
  if wall.launches.right then
   assert(r('RdMaxSpeed')==0x12,'Native wall jump publishes the dry maximum speed')
   wall.launches.right.maxSpeed=r('RdMaxSpeed')
   wallJumpPhase('land')
   return {a=true}
  end
  if grounded then
   wallJumpPhase('prepare')
   return {}
  end
  if updates-wall.entered>=3 then
   wallJumpPhase('release')
   return toward
  end
  toward.a=true
  return toward
 end
 if wall.phase=='land' then
  if grounded and updates-wall.entered>=10 then
   wall.landings.right=state()
   wallJumpPhase('settled')
   return {}
  end
  return {a=r('RdVY')>=128}
 end
 if wall.phase=='settled' and updates-wall.entered>=25 then
  assert(wall.launches.right and wall.landings.right
         and r('RdGear')==7 and r('RdTanks')==1 and r('RdMissiles')==5,
         'Earned Wall Jump and earlier resources survive landing')
  wall.complete=true
  finish('natural-wall-jump-and-landing')
 end
 return {}
end
