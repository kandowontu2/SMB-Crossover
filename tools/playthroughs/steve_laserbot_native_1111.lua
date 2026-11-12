local sawCooldown=false
local recent,previousTag={},0
observe(STEVE_LASER_TOKEN_HIT,2,function()
  if x()>1680 and read(0x7d67)==0x8c and #recent<12 then
    local hx=read(STEVE_PROBE_SteveHitPage)*256+read(STEVE_PROBE_SteveHitX)
    local ix=read(STEVE_PROBE_Enemy_PageLoc+5)*256+read(STEVE_PROBE_Enemy_X_Position+5)
    recent[#recent+1]=string.format('hit %d/%d item %d/%d',hx,read(STEVE_PROBE_SteveHitY),ix,
      read(STEVE_PROBE_Enemy_Y_Position+5))
  end
end)

local function playCompanionRoute()
  assert(active() and read(0x75f)==2,string.format('Steve lost the active stage at group %d X%d',group,x()))
  local pattern=work(2,0xc1f1)
  if pattern>0 then seenPatterns[pattern]=true end
  local tag=read(0x7d67)
  if x()>1680 and (tag~=previousTag or pad==65) and #recent<12 then
    recent[#recent+1]=string.format('%d:%d/%d=%02x',group,x(),read(0xbd),tag)
  end
  previousTag=tag
  if work(2,STEVE_COMPANION_ACTOR)==3 then
    seenPoses[work(2,STEVE_COMPANION_POSE)]=true
    sawCooldown=sawCooldown or work(2,STEVE_LASER_COOLDOWN)>0
  end
  if not firstUpdate then firstUpdate=companionUpdates end
  if companionUpdates~=firstUpdate then
    assert(companionUpdates==firstUpdate+1,'One controller sample per native companion update')
    firstUpdate=companionUpdates
    remaining=remaining-1
    if remaining==0 then
      group=group+1
      if routeGroups[group] then remaining=routeGroups[group][1] end
    end
  end
  if routeGroups[group] then pad=routeGroups[group][2];return end
  pad=0
  local actor=work(2,STEVE_COMPANION_ACTOR)
  assert(seenPatterns[1] and seenPatterns[5] and seenPatterns[0x25],
    string.format('Alpha Alpha Beta must be earned, actor%d A=%s AA=%s AAA=%s AAB=%s %s',actor,
      tostring(seenPatterns[1]),tostring(seenPatterns[5]),tostring(seenPatterns[0x15]),
      tostring(seenPatterns[0x25]),table.concat(recent,',')))
  assert(actor==3 and seenPoses[0x3c] and seenPoses[0x3e] and sawCooldown,
    string.format('Laserbot must fire and cool down, actor %d X%d Y%d',actor,x(),read(0xbd)))
  assert(bodyPairs>=2 and shotPairs>=2 and seenTiles[0x41] and seenTiles[0x7b] and seenTiles[0x7d]
    and seenTiles[0x7f],string.format('Physical Laserbot DMA body %d shot %d muzzle %s beam %s/%s/%s',
      bodyPairs,shotPairs,tostring(seenTiles[0x41]),tostring(seenTiles[0x7b]),tostring(seenTiles[0x7d]),
      tostring(seenTiles[0x7f])))
  finish(true,string.format('Earned Laserbot, body pairs %d, beam pairs %d',bodyPairs,shotPairs))
end
