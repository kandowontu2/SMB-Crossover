-- Continuation of the cold, ordinary Kirby food replay. All writes are pad input.
local itemX = C.stockKind == 3 and 1024 or 1616
local alignX = itemX - 2
local itemY = C.stockKind == 3 and 128 or 144
local function tileAt(wx, wy)
 return r('Block_Buffer_1', (wx // 256) % 2 * 208 + (wy - 32) // 16 * 16 + (wx % 256) // 16)
end
local function velocity()
 local signed = r('MmVX', 1) + r('MmVX', 2) * 256
 return ((signed + 32768) % 65536 - 32768) / 256
end

local function inventory()
 return {hp=r('KbHealth'), copy=r('KbCopy'), mouth=r('KbMouth'), food=r('KbFoodKind')}
end

local function score()
 local total = 0
 for digit=0,5 do total = total * 10 + r('PlayerScoreDisplay', digit) end
 return total
end

hook('stockCollector', function(slot)
 local a = foodActor(slot)
 if a.kind ~= C.stockKind then return end
 assert(stock.birth and stock.mature and a.slot == stock.birth.slot, 'Collector follows real block and maturity')
 assert(a.id == 46 and a.flag == 1 and a.state >= 128, 'Native collector receives mature actor')
 assert(not stock.collector and r('NumberofLives') == 2 and r('StarInvincibleTimer') == 0)
 stock.collector = {actor=a, player=player(), inventory=inventory(), score=score()}
end)

local function returned(slot, popup)
 if not stock.collector or stock.collected then return false end
 assert(slot == stock.collector.actor.slot and r('Enemy_Flag', slot) == 0, 'Stock collector erases actor')
 assert(r('FloateyNum_Control', slot) == popup and r('GuestPowerupActive') == 0, 'Native popup without growth')
 for name, value in pairs(inventory()) do
  assert(value == stock.collector.inventory[name], 'Pickup preserves Kirby '..name)
 end
 stock.collected = {player=player(), popup=popup}
 return true
end

hook('lifeReturn', function(slot)
 if C.stockKind ~= 3 or not returned(slot, 11) then return end
 assert(r('NumberofLives') == 2, 'Life credit follows popup')
end)

hook('lifeCredit', function(slot)
 if C.stockKind ~= 3 or not stock.collected or slot ~= stock.collector.actor.slot then return end
 assert(r('NumberofLives') == 2 and r('FloateyNum_Control', slot) == 11)
 stock.lifePending = player()
end)

hook('lifeCredited', function(slot)
 if not stock.lifePending then return end
 assert(slot == stock.collector.actor.slot and r('NumberofLives') == 3 and r('Square2SoundQueue') == 64)
 stock.life = {before=stock.lifePending, after=player(), cue=64}
 stock.lifePending = nil
end)

hook('starReturn', function(slot)
 if C.stockKind ~= 2 or not returned(slot, 6) then return end
 assert(r('StarInvincibleTimer') == 35 and r('AreaMusicQueue') == 64, 'Star starts native timer and music')
 assert(r('Square2SoundQueue') & 32 ~= 0, 'Star pickup cue')
 stock.star = {timer=35, music=64, cue=r('Square2SoundQueue')}
end)

if C.stockLifecycle then
 hook('starDefeat', function(slot)
  if not stock.star or stock.defeat then return end
  local enemy = actor(slot)
  local timer = r('StarInvincibleTimer')
  if timer == 0 or enemy.id >= 21 or enemy.flag == 0 or enemy.state & 32 ~= 0 then return end
  assert(math.abs(enemy.x - x()) <= 24 and pad & 64 == 0, 'Star defeat uses genuine body contact')
  stock.defeatPending = {enemy=enemy, player=player(), timer=timer}
 end)
 hook('restoreMusic', function()
  if stock.star and r('StarInvincibleTimer') == 4 then
   stock.musicRestored = {timer=4, player=player()}
  end
 end)
 hook('injury', function(slot)
  if not stock.star or stock.injury then return end
  assert(r('StarInvincibleTimer') == 0, 'Star contact must protect Kirby from injury')
  stock.injuryPending = {enemy=actor(slot), player=player()}
 end)
end

local function continueStar()
 local timer = r('StarInvincibleTimer')
 local defeat = stock.defeatPending
 if defeat and not stock.defeat then
  local enemy = actor(defeat.enemy.slot)
  assert(enemy.state & 32 ~= 0 and r('KbHealth') == defeat.player.hp,
         'Protected contact defeats the enemy without costing health')
  stock.defeat = defeat
  stock.defeatPending = nil
 end
 if not stock.defeat then
  assert(timer > 0, 'The Star must defeat an enemy before it expires')
  pad = 1
  return
 end
 if timer > 0 then return end
 if not stock.expiry then
  local atExpiry = stock.injuryPending and stock.injuryPending.player or player()
  assert(stock.musicRestored, 'Area music returns as the Star winds down')
  assert(atExpiry.hp == stock.defeat.player.hp, 'Health remains intact through expiry')
  stock.expiry = {player=atExpiry, step=step}
 end
 local injury = stock.injuryPending
 if injury and not stock.injury then
  assert(r('KbHealth') == injury.player.hp - 1 and r('KbHurt') > 0,
         'Ordinary enemy contact costs one HP once protection expires')
  stock.injury = injury
  stock.injuryStep = step
  stock.injuryPending = nil
 end
 if not stock.injury then
  pad = 1
  return
 end
 stock.resume = step - stock.injuryStep
 if stock.resume >= 25 then finish('natural-star-lifecycle') end
end

local function steer(px, target, speed)
 local stopping = px + speed * math.abs(speed) / 0.25
 if stopping < target - 1 then return 1 end
 if stopping > target + 1 then return 2 end
 return 0
end

local function stockControl(px, y, ground, item)
 if stock.collected then
  pad = 0
  if C.stockLifecycle then
   continueStar()
   return true
  end
  if stock.life or (stock.star and score() >= stock.collector.score + 1000) then
   if not stock.credit then
    stock.credit = {player=player(), score=score(), step=step}
   end
   stock.resume = step - stock.credit.step
   if stock.resume >= 25 then
    assert(stock.life or r('StarInvincibleTimer') > 0)
    finish('natural-stock-credit')
   end
  end
  return true
 end

 if not stock.phase then
  local ready = C.stockKind == 3 and #heals >= 1 and px >= 955
             or C.stockKind == 2 and #heals == 2
  if not ready then return false end
  stock.phase = C.stockKind == 3 and 'align' or 'past-pit'
  stock.start = player()
 end

 if stock.phase == 'past-pit' then
  pad = 1
  if px >= 1308 and px < 1424 then
   if ground and y == 176 and not stock.pitJump then stock.pitJump = step end
   if stock.pitJump and step - stock.pitJump < 23 then pad = pad | 128 end
   if not ground and px >= 1332 then pad = pad | 8 end
  end
  if px >= 1424 and r('KbFloat') ~= 0 then pad = pad | 64 end
  if px >= 1560 then stock.phase = 'align' end
  return true
 end

 if stock.phase == 'align' then
  local speed = velocity()
  pad = steer(px, alignX, speed)
  if r('KbFloat') ~= 0 then pad = pad | 64 end
  if ground and y == 176 and r('Player_Y_HighPos') == 1 and r('KbHurtMove') == 0
     and math.abs(px - alignX) <= 3 and math.abs(speed) < 0.125 then
   pad = 0
   if r('SavedJoypadBits') & 128 == 0 then
    stock.request, stock.requestStep = player(), step
    stock.block = tileAt(itemX, itemY)
    stock.lowestY, stock.risingY = y, y
    stock.phase, pad = 'reveal', 128
   end
  end
  return true
 end

 if not stock.birth then
  pad = 128
  -- Start the lift from the air so the ground check cannot cancel inflation.
  if C.stockKind == 3 and y <= 152 then pad = pad | 8 end
  stock.lowestY = math.min(stock.lowestY, y)
  if r('Player_Y_Speed') >= 128 and y < stock.risingY then
   stock.risingY = y
   stock.headAtApex = {x=px+8,y=y+17,jumpAge=r('KbJumpAge'),
                       hurt=r('GuestHurtTicks'),bounce=r('BlockBounceTimer'),tile=tileAt(px+8,y+17)}
  end
  assert(step - stock.requestStep <= 90, 'Jump and float must reveal the authored item')
  return true
 end

 pad = 0
 if r('KbFloat') ~= 0 then pad = 64 end
 assert(item and item.kind == C.stockKind and item.slot == stock.birth.slot, 'Revealed stock actor stays live')
 if item.state >= 128 then
  stock.mature = stock.mature or item
  stock.phase = 'follow'
  local gap = item.x - (px + 5)
  pad = pad | (gap > 2 and 1 or gap < -5 and 2 or 0)
  if C.stockKind == 2 then
   if ground and math.abs(gap) < 25 and item.y < y + 12 and step - lastJump > 30
       and r('SavedJoypadBits') & 128 == 0 then lastJump = step end
   if step - lastJump < 23 then pad = pad | 128 end
  end
 end
 return true
end
