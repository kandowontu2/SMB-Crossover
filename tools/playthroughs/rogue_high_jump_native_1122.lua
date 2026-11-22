-- Continue after the real 1-2 Bomb coin transaction using pad input only.
local function highJumpPhase(high, name)
 high.phase = name
 high.entered = updates
 assert(#high.steps < 24, 'Bounded High Jump route milestones')
 high.steps[#high.steps + 1] = {phase=name, player=state()}
end

local function highJumpDrive(c)
 local high = gear.high
 -- The enemy stream can publish a pipe destination while this room is live.
 assert(c.level == 1 and c.areaType == 2 and r('AreaAddrsLOffset') == high.areaOffset
        and updates - high.started < 2200,
        'Bounded ordinary route to 1-2 High Jump')
 if not high.destination and c.area ~= high.initialLink then
  high.destination = {x=c.x, pointer=c.area, loadedOffset=high.areaOffset}
 end
 local travel = setmetatable({area=high.areaOffset}, {__index=c})
 high.farthest = math.max(high.farthest or 0, c.x)
 local function aim(low, top)
  return {left=c.x > top, right=c.x < low}
 end
 local function releasedA()
  return r('RdHeld') & 128 == 0
 end
 local grounded = c.yHigh == 1 and bombReady(c)

 if high.phase == 'unmorph' then
  if r('RdAction') == 3 then return {up=true} end
  highJumpPhase(high, 'travel')
 end
 if high.phase == 'travel' then
  if c.x >= 832 and not high.passedLowCeiling then
   highJumpPhase(high, 'low-ceiling')
  elseif c.x >= 1052 and grounded and c.y >= 160 then
   high.tiles = {lower=c.block(1104,144), upper=c.block(1104,128)}
   assert(high.tiles.lower == 0x52 and high.tiles.upper == 0x5a, 'Actual stacked 1-2 bricks')
   highJumpPhase(high, 'mount')
  else
   return gearTravel(travel)
  end
 end
 if high.phase == 'low-ceiling' then
  if r('RdAction') ~= 3 then return {down=grounded} end
  if c.x < 900 then return {right=true} end
  highJumpPhase(high, 'stand-after-ceiling')
 end
 if high.phase == 'stand-after-ceiling' then
  if r('RdAction') == 3 then return {up=true} end
  high.passedLowCeiling = true
  highJumpPhase(high, 'walk-under')
 end
 if high.phase == 'walk-under' then
  -- The next bricks hang above the floor. A jump traps the player at
  -- their right edge, so regain the floor and walk underneath.
  if not grounded or c.y < 170 then return {} end
  if c.x < 1052 then return {right=true, b=updates%8==0} end
  highJumpPhase(high, 'travel')
 end
 if stock == 'high-jump-credit' then return {} end

 if high.phase == 'mount' then
  local b = aim(1123,1126)
  if not b.left and not b.right and grounded and c.y >= 160 and releasedA() then
   highJumpPhase(high, 'rise')
   b.a = true
  end
  return b
 end
 if high.phase == 'rise' then
  if c.y <= 96 then
   highJumpPhase(high, 'cross')
   return {left=true, a=true}
  end
  assert(updates - high.entered < 65, 'Reach the top of the authored High Jump brick')
  return {a=true}
 end
 if high.phase == 'cross' then
  local b = aim(1104,1107)
  b.a = r('RdVY') >= 128
  if grounded and c.y <= 98 and not b.left and not b.right then
   highJumpPhase(high, 'morph-on-brick')
   return {}
  end
  if grounded and c.y >= 160 then highJumpPhase(high, 'mount') end
  return b
 end
 if high.phase == 'morph-on-brick' then
  if r('RdAction') ~= 3 then return {down=true} end
  if r('RdHeld') & 64 ~= 0 then return {} end
  highJumpPhase(high, 'place-bomb')
  return {b=true}
 end
 if high.phase == 'place-bomb' then
  if not high.bomb then
   assert(updates - high.entered < 12, 'Actual fresh B places the second Bomb')
   return {b=true}
  end
  highJumpPhase(high, 'open-brick')
  return {}
 end
 if high.phase == 'open-brick' then
  assert(updates - high.entered < 180, 'Bomb reveals the actual High Jump item')
  if high.hit and born then highJumpPhase(high, 'collect') end
  return {}
 end
 if high.phase == 'collect' then
  if r('RdAction') == 3 then return {up=true} end
  return {}
 end
 if high.phase == 'clear' then
  local b = aim(1123,1126)
  if grounded and c.y >= 175 and c.y <= 177 and not b.left and not b.right and releasedA() then
   highJumpPhase(high, 'test-arc')
   high.takeoffY = c.y
   b.a = true
  end
  return b
 end
 if high.phase == 'test-arc' then
  if not high.launch then
   assert(updates - high.entered < 16, 'Actual fresh A calls the source jump routine')
   return {a=true}
  end
  high.apex = math.min(high.apex or c.y, c.y)
  if grounded and math.abs(c.y - high.takeoffY) <= 1 and updates - high.launch.Main > 10 then
   assert(high.takeoffY - high.apex > 84, 'Earned High Jump exceeds the ordinary dry jump height')
   high.landing = state()
   highJumpPhase(high, 'settled')
   return {}
  end
  return {a=r('RdVY') >= 128}
 end
 if high.phase == 'settled' and updates - high.entered >= 25 then
  assert(high.baseLaunch and high.hit and r('RdWAction',high.bomb.slot) == 0
         and r('RdGear') == 3 and r('RdTanks') == 1 and r('RdMissiles') == 5,
         'High Jump and earned resources survive subsequent gameplay')
  high.complete = true
  finish('natural-high-jump-and-landing')
 end
 return {}
end
