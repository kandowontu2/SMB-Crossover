local pickupFields={FOUR_PICKUP_FIELDS}
local runtimeParts={FOUR_RUNTIME_PARTS}
local pickupPoints={
  {left=336,approach=329,launch=302,pattern=1,kind='alpha'},
  {left=1024,approach=1017,kind='oneup'},
  {left=1248,approach=1239,launch=1214,pattern=5,kind='alpha'},
  {left=1616,approach=1609,kind='star'}
}
local travelTargets={1014,1236,1607}

local function verifyPickupRuntime()
  assert(header(1)==cookie and header(2)==cookie and header(3)==cookie,
    'Complete current Steve owner identities')
  for _,part in ipairs(runtimeParts)do
    for offset=0,#part.hex//2-1 do
      local expected=tonumber(part.hex:sub(2*offset+1,2*offset+2),16)
      assert(work(part.bank,part.at+offset)==expected,'Exact mounted Steve runtime')
    end
  end
  natural.authenticated=true
end

local function pickupNative(name,callback)
  local at,bank=pickupFields[name],pickupFields[name..'Bank']
  emu.addMemoryCallback(guard(function()
    local mapped=emu.convertAddress(at)
    if active() and mapped and mapped.memType==emu.memType.nesPrgRom
      and mapped.address==bank*8192+(at&8191)then callback()end
  end),emu.callbackType.exec,at)
end

pickupNative('JnPreparePickup',function()
  local slot=emu.getState()['cpu.x']
  local point=pickupPoints[natural.index]
  assert(slot>=0 and slot<6 and read(pickupFields.Enemy_ID+slot)==46,
    'Actual native powerup preparation slot')
  local wx=read(pickupFields.Enemy_X_Position+slot)+256*read(pickupFields.Enemy_PageLoc+slot)
  assert(wx==point.left,'Authored powerup birth position')
  natural.slot=slot
  natural.slots[natural.index]=slot
  natural.kinds[natural.index]=read(pickupFields.PowerUpType+slot)
  natural.preparations=natural.preparations+1
end)

pickupNative('JnCollectPickup',function()
  local slot=emu.getState()['cpu.x']
  local point=pickupPoints[natural.index]
  assert(slot==natural.slot and read(pickupFields.Enemy_ID+slot)==46,
    'Actual prepared pickup collector slot')
  assert(read(pickupFields.Enemy_State+slot)&128~=0,'Mature authored pickup at collection')
  local tag=read(pickupFields.InvPickup+slot)
  assert(tag==(point.kind=='alpha' and 0x8c or 0xfc),'Prepared source or native item transport')
  natural.collections=natural.collections+1
  natural.receipts[#natural.receipts+1]=string.format(
    '{"block":%d,"slot":%d,"kind":%d,"actor_x":%d,"actor_y":%d,"player_x":%d,"player_y":%d,"tag":%d}',
    point.left,slot,read(pickupFields.PowerUpType+slot),
    read(pickupFields.Enemy_X_Position+slot)+256*read(pickupFields.Enemy_PageLoc+slot),
    read(pickupFields.Enemy_Y_Position+slot),x(),read(0xbd),tag)
end)

emu.addMemoryCallback(guard(function(_,value)
  if active() and value==64 then natural.lifeSound=true end
end),emu.callbackType.write,pickupFields.Square2SoundQueue)
emu.addMemoryCallback(guard(function(_,value)
  if active() and value==35 then natural.starGranted=true end
end),emu.callbackType.write,pickupFields.StarInvincibleTimer)
emu.addMemoryCallback(guard(function(_,value)
  if active() and value==64 then natural.starMusic=true end
end),emu.callbackType.write,pickupFields.AreaMusicQueue)

local function pickupPhase(nextPhase,bits)
  phase=nextPhase
  natural.since=projections
  pad=bits
end

local function pickupApproach(target,nextPhase)
  local gap=target-x()
  if math.abs(gap)<=1 then pickupPhase(nextPhase,0)
  else pad=gap>0 and 1 or 2 end
end

local function pickupActor()
  local slot=natural.slot
  if slot==nil then return nil end
  local flag=read(pickupFields.Enemy_Flag+slot)
  if flag>0 then assert(read(pickupFields.Enemy_ID+slot)==46,'Tracked native pickup identity')end
  return {flag=flag,state=read(pickupFields.Enemy_State+slot),
    x=read(pickupFields.Enemy_X_Position+slot)+256*read(pickupFields.Enemy_PageLoc+slot),
    y=read(pickupFields.Enemy_Y_Position+slot),tag=read(pickupFields.InvPickup+slot)}
end

local function starFollowPad(actor)
  local gap=actor.x-x()-8
  if gap>4 then return 1 end
  if gap< -4 then return 2 end
  return 0
end

local function pickupTravel(target)
  natural.target=target
  beginFull()
  pickupPhase('natural-traverse',1)
end

local function pickupAdvance()
  natural.items=natural.items+1
  natural.index=natural.index+1
  natural.slot=nil
  pickupTravel(travelTargets[natural.items])
end

local function naturalTick()
  if projections==natural.lastProjection then return end
  natural.lastProjection=projections
  local point=pickupPoints[natural.index]
  local age=projections-natural.since
  assert(natural.authenticated and active() and read(0x5f30)>0,'Living authenticated Steve pickup route')
  if phase=='natural-approach'then
    pickupApproach(point.approach,'natural-settle')
    assert(age<240,'Authored block approach bound')
  elseif phase=='natural-settle'then
    if age>=7 then pickupPhase('natural-reveal',128)end
  elseif phase=='natural-reveal'then
    pad=age<9 and 128 or 0
    local actor=pickupActor()
    if point.kind=='alpha'then
      if age>=62 then
        assert(actor and actor.flag>0 and actor.state==128 and actor.x==point.left
          and actor.y==120 and actor.tag==0x8c,'Actual Alpha emergence and maturity')
        pickupPhase('natural-return',2)
      end
    elseif actor and actor.flag>0 and actor.state&128~=0 then
      assert(actor.tag==0xfc,'Actual native Star or 1UP transport')
      pickupPhase('natural-chase',point.kind=='star' and starFollowPad(actor) or 1)
    end
    assert(age<120,'Native pickup reveal and maturity bound')
  elseif phase=='natural-return'then
    pickupApproach(point.launch,'natural-launch-settle')
    assert(age<240,'Alpha collection approach bound')
  elseif phase=='natural-launch-settle'then
    if age>=9 then pickupPhase('natural-collect',129)end
  elseif phase=='natural-collect'then
    pad=age<9 and 129 or 1
    if work(2,0xc3fd)>0 then
      local actor=pickupActor()
      assert(work(2,0xc3fd)==point.pattern and actor.flag==0 and actor.tag==0,
        'Native Alpha collection and erasure')
      pickupPhase('natural-flight',0)
    end
    assert(age<90,'Actual Alpha collection bound')
  elseif phase=='natural-flight'then
    if work(2,0xc3fd)==0 then
      assert(work(2,0xc1f1)==point.pattern,'Original Alpha HUD pattern commit')
      pickupAdvance()
    end
    assert(age<80,'Original token flight bound')
  elseif phase=='natural-traverse'then
    if x()>=natural.target and read(0xbd)==176 and read(0x1e)==0 then
      pickupPhase('natural-approach',1)
    else fullTick()end
  elseif phase=='natural-chase'then
    local actor=pickupActor()
    if actor.flag==0 then
      if point.kind=='oneup'then
        assert(read(pickupFields.FloateyNum_Control+natural.slot)==11,'Native deferred extra-life award')
        pickupPhase('natural-life-award',0)
      else
        assert(natural.starGranted and natural.starMusic and read(pickupFields.StarInvincibleTimer)>0,
          'Native Star timer and music grant')
        pickupPhase('natural-star-continuation',0)
      end
    else pad=point.kind=='star' and starFollowPad(actor) or 1 end
    assert(age<180,'Native moving-item chase bound')
  elseif phase=='natural-life-award'then
    if age>=12 then
      assert(read(0x75f)==3 and natural.lifeSound,'Native extra-life sound and single life award')
      natural.oneupAwarded=true
      pickupAdvance()
    end
  elseif phase=='natural-star-continuation'then
    if age>=24 then
      natural.items=natural.items+1
      assert(natural.items==4 and natural.preparations==4 and natural.collections==4
        and read(0x75f)==3 and work(2,0xc1f1)==5 and read(pickupFields.StarInvincibleTimer)>0,
        'Four authored stock items and their source/native effects')
      finish(true,'Steve earns both Alphas, hidden1UP and Star in stock1-1')
    end
  end
end
