local routeGroups={STEVE_ROUTE_GROUPS}
local group,remaining=1,routeGroups[1][1]
local firstUpdate
local companionUpdates,bodyPairs,shotPairs=0,0,0
local seenPatterns,seenPoses,seenTiles={},{},{}
local pendingCompanion={}
local bodySet={[0x6f]=true,[0x71]=true,[0x73]=true,[0x75]=true}
local shotSet={[0x77]=true,[0x79]=true}

observe(STEVE_COMPANION_TICK,2,function()
  companionUpdates=companionUpdates+1
end)

emu.addMemoryCallback(guard(function(_,value)
  if value~=2 or phase~='companion-route' then return end
  pendingCompanion={}
  for at=0,252,4 do
    local py,tile=read(0x200+at),read(0x201+at)
    if py<240 and (bodySet[tile] or shotSet[tile]) then
      pendingCompanion[#pendingCompanion+1]={at,py,tile,read(0x202+at),read(0x203+at)}
    end
  end
end),emu.callbackType.write,0x4014)

local function verifyCompanionDma()
  local body,shot=0,0
  for _,cell in ipairs(pendingCompanion) do
    for i=1,4 do
      assert(emu.read(cell[1]+i-1,emu.memType.nesSpriteRam)==cell[i+1],
        'Companion cells reach hardware OAM')
    end
    if bodySet[cell[3]] then body=body+1
    else shot=shot+1;seenTiles[cell[3]]=true end
  end
  if body>=2 then bodyPairs=bodyPairs+1 end
  if shot>=2 then shotPairs=shotPairs+1 end
  pendingCompanion={}
end

local function playCompanionRoute()
  assert(active() and read(0x75f)==2,string.format('Steve lost the active stage at group %d X%d',group,x()))
  local pattern=work(2,0xc1f1)
  if pattern>0 then seenPatterns[pattern]=true end
  if work(2,STEVE_COMPANION_ACTOR)==1 then
    local pose=work(2,STEVE_COMPANION_POSE)
    seenPoses[pose]=true
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
  if work(2,STEVE_COMPANION_SHOT)~=0 then return end
  assert(seenPatterns[1] and seenPatterns[5] and seenPatterns[0x15],
    string.format('All three tokens must be earned, X%d pattern%02x',x(),pattern))
  local actor=work(2,STEVE_COMPANION_ACTOR)
  assert(actor==1 and math.abs(x()-1740)<=4 and read(0xbd)==48,
    string.format('The first companion must spawn above the third block, actor %d X%d Y%d',actor,x(),read(0xbd)))
  assert(seenPoses[0xbc] and seenPoses[0xbe] and seenPoses[0xc0],'All three donor attack poses')
  assert(bodyPairs>=2 and shotPairs>=2 and seenTiles[0x77] and seenTiles[0x79],
    string.format('Physical DMA body %d shot %d tiles 77=%s 79=%s',
      bodyPairs,shotPairs,tostring(seenTiles[0x77]),tostring(seenTiles[0x79])))
  finish(true,string.format('Earned first companion, body pairs %d, shot pairs %d',bodyPairs,shotPairs))
end
