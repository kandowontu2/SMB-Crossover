local beta=os.getenv('SMB_STEVE_TOKEN_BETA')=='1'
local tokenSince,tokenLast=0,-1
local tokenBefore
local tokenCells,expectedTokens={},{}
local lastTag=0
local slot=5

local function tokenWork(at) return work(2,at) end
local function transition(name,bits)
  phase=name
  tokenSince=updates
  pad=bits
end

local function approach(target,ready)
  local gap=target-x()
  if math.abs(gap)<=1 then transition(ready,0)
  else pad=gap>0 and 1 or 2 end
end

local function tokenTick()
  assert(active() and read(0x75f)==2,'Active Steve keeps both lives')
  if updates==tokenLast then return end
  tokenLast=updates
  local age=updates-tokenSince
  local tag=read(0x7d62+slot)
  if lastTag==0x8c and tag==0x8d then tokenSwitches=tokenSwitches+1 end
  lastTag=tag
  if phase=='token-approach' then approach(329,'token-settle')
  elseif phase=='token-settle' and age>=7 then
    tokenBefore={read(0x5f30),read(0x5f31),read(0x5f32)}
    transition('token-bump',128)
  elseif phase=='token-bump' then
    if age>=9 then pad=0 end
    if age>=62 and tag==0x8c and read(0x1f+slot)==0x80 then
      tokenStarts=tokenStarts+1
      transition('token-back',2)
    end
  elseif phase=='token-back' then approach(302,'token-launch')
  elseif phase=='token-launch' and age>=9 then transition('token-collect',129)
  elseif phase=='token-collect' then
    if tokenWork(0xc3fd)~=0 then
      assert(not (read(0x10+slot)~=0 or tag~=0),'Native collector erases the token actor')
      assert(tokenWork(0xc3fd)==(beta and 2 or 1),'Correct pending token symbol')
      transition('token-flight',0)
    else
      pad=1|(age<9 and 128 or 0)|(beta and age>=17 and age<24 and 64 or 0)
    end
  elseif phase=='token-flight' and tokenWork(0xc1f1)==(beta and 2 or 1) and tokenHud>0 then
    assert(tokenStarts==1 and tokenSwitches==(beta and 1 or 0),'One authored item and the expected punch switch')
    assert(tokenFlights>0 and tokenWorld>0,'Physical world and flight sprites reached DMA')
    for i=1,3 do
      assert(read(0x5f2f+i)==tokenBefore[i],'Pickup leaves borrowed heart and tier state unchanged')
    end
    finish(true,'Original Alpha/Beta glyphs render in the world, flight and HUD')
  end
  assert(age<=180,'Bounded Steve token movement')
end

observe(assert(tonumber(os.getenv('SMB_STEVE_TOKEN_PAIR'))),2,function()
  if phase:sub(1,6)~='token-' then return end
  local symbol=1+emu.getState()['cpu.a']
  local px,py=read(0x07),read(0x09)
  if px>247 then return end
  local state
  if px==96 and py==34 and tokenWork(0xc1f1)==symbol then state='hud'
  elseif px==tokenWork(0xc3fe) and py==tokenWork(0xc3ff) and tokenWork(0xc3fd)==symbol then state='flight'
  elseif py>=80 and py<=152 and read(0x7d62+slot)==0x8b+symbol then state='world' end
  if state then
    assert(#expectedTokens<16,'Bounded token sprite expectations')
    expectedTokens[#expectedTokens+1]={py,0x31+4*(symbol-1),px,state}
  end
end)

emu.addMemoryCallback(guard(function(_,value)
  if not active() or value~=2 or phase:sub(1,6)~='token-' then return end
  tokenCells={}
  for _,expected in ipairs(expectedTokens) do
    local py,tile,px,state=table.unpack(expected)
    local left,right
    for at=0,252,4 do
      if read(0x200+at)==py and read(0x202+at)==2 then
        local itemTile,itemX=read(0x201+at),read(0x203+at)
        if itemTile==tile and itemX==px then left=at end
        if itemTile==tile+2 and itemX==px+8 then right=at end
      end
    end
    if left and right then tokenCells[#tokenCells+1]={left,right,py,tile,px,state} end
  end
  expectedTokens={}
end),emu.callbackType.write,0x4014)

local function verifyTokenDma()
  for _,item in ipairs(tokenCells) do
    local at,other,py,tile,px,state=table.unpack(item)
    local left,right={py,tile,2,px},{py,tile+2,2,px+8}
    for i=1,4 do
      assert(emu.read(at+i-1,emu.memType.nesSpriteRam)==left[i]
          and emu.read(other+i-1,emu.memType.nesSpriteRam)==right[i],
          'Authentic token sprite cells reach hardware OAM')
    end
    if state=='hud' then tokenHud=tokenHud+1
    elseif state=='flight' then tokenFlights=tokenFlights+1
    else tokenWorld=tokenWorld+1 end
  end
  tokenCells={}
end
