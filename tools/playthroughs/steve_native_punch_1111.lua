-- Cold menu selection, one held punch, and a punch against the first live Goomba.
local rom=assert(os.getenv('SMB_STDOUT_ROM_SHA'))
local cookie=assert(os.getenv('SMB_STEVE_COOKIE'))
local punchBirth=assert(tonumber(os.getenv('SMB_STEVE_BIRTH')))
local drawEmit=assert(tonumber(os.getenv('SMB_STEVE_DRAW')))
local frame,pad,updates,edges,births,dmaMatches=0,0,0,0,0,0
local done=false
local phase='menu'
local heldStart,approachStart,shotStart,victim
local expected,pending={},{}

local function read(at)return emu.read(at,emu.memType.nesDebug)end
local function work(bank,at)return emu.read(bank*8192+(at&8191),emu.memType.nesWorkRam)end
local function x()return read(0x5c)*256+read(0x75)end
local function active()
  return read(0x6002)==16 and read(0x730b)&0x60==0x40 and read(0x771)==1
    and read(0x773)==3 and read(0x0f)==8
end
local function header(bank)
  local bytes={}
  for at=0x1fe0,0x1fef do bytes[#bytes+1]=string.format('%02x',work(bank,at)) end
  return table.concat(bytes)
end
local function finish(ok,reason)
  if done then return end
  done=true
  local slot=victim or 0
  print(string.format('SMB_NATIVE_RECEIPT {"passed":%s,"reason":%q,"ROM_SHA256":%q,'..
    '"controller_only":true,"physical_frames":%d,"phase":%q,"cookie":%q,'..
    '"updates":%d,"edges":%d,"births":%d,"x":%d,"y":%d,"lives":%d,'..
    '"enemy_slot":%d,"enemy_state":%d,"score":%d,"dma_matches":%d}',
    tostring(ok),reason,rom,frame,phase,cookie,updates,edges,births,x(),read(0xbd),read(0x75f),
    slot,read(0x1f+slot),read(0x10d+slot),dmaMatches))
  emu.stop(ok and 0 or 1)
end
local function guard(fn)
  return function(...)
    if done then return end
    local ok,message=pcall(fn,...)
    if not ok then finish(false,tostring(message))end
  end
end
local function observe(at,bank,callback)
  emu.addMemoryCallback(guard(function()
    local m=emu.convertAddress(at)
    if active() and m and m.memType==emu.memType.nesWorkRam
        and m.address==bank*8192+(at&8191) then callback() end
  end),emu.callbackType.exec,at)
end

observe(0xda80,2,function()
  assert(header(2)==cookie and header(3)==cookie,'Authenticated Steve transport')
  updates=updates+1
  if read(0x5c02)&64~=0 then edges=edges+1 end
end)
observe(punchBirth,3,function()births=births+1 end)
observe(drawEmit,2,function()
  local relative=x()-(read(0x71d)*256+read(0x71f))
  local right=read(0x53e)&1~=0
  for i,tile in ipairs({32,34}) do
    local px=relative+(right and 8+8*i or -8*i)
    if px>=0 and px<=255 then expected[tile]={read(0xbd),tile,right and 0 or 64,px} end
  end
end)
emu.addMemoryCallback(guard(function(_,value)
  if not active() or value~=2 then return end
  pending={}
  for at=0,252,4 do
    local cell=expected[read(0x201+at)]
    if cell and read(0x200+at)==cell[1] and read(0x202+at)==cell[3] and read(0x203+at)==cell[4] then
      pending[#pending+1]={at,cell}
    end
  end
  expected={}
end),emu.callbackType.write,0x4014)

local function wait(predicate)
  for _=1,1300 do if predicate() then return end;coroutine.yield() end
  error('Controller transition timed out')
end
local function press(bits)
  pad=bits
  for _=1,4 do coroutine.yield() end
  pad=0
  for _=1,8 do coroutine.yield() end
end
local function approachingGoomba()
  local player=x()
  for slot=0,5 do
    local target=read(0x5d+slot)*256+read(0x76+slot)
    if read(0x10+slot)==1 and read(0x17+slot)==6 and read(0x1f+slot)&32==0
      and read(0xbe+slot)==184 and target>player and target<=player+32 then return slot end
  end
end
local function tick()
  if phase=='settle' and updates>=6 then
    phase='hold';heldStart=updates;pad=64
  elseif phase=='hold' and updates>=heldStart+12 then
    assert(edges==1 and births==1,'A held B creates one donor punch')
    phase='release';approachStart=updates;pad=0
  elseif phase=='release' and updates>=approachStart+6 then
    phase='approach';pad=1
  elseif phase=='approach' then
    if x()>=216 then
      pad=0
      local slot=approachingGoomba()
      if slot then victim=slot;phase='hit';shotStart=updates;pad=64 end
    end
  elseif phase=='hit' then
    if edges==2 then pad=0 end
    if read(0x1f+victim)&32~=0 then
      assert(edges==2 and births==2 and read(0x75f)==2 and read(0x10d+victim)==1,
        'Fresh punch defeats the natural Goomba and awards the native score')
      assert(dmaMatches>=2,'Donor punch cells survive physical OAM DMA')
      finish(true,'Steve held B and naturally defeated the first Goomba')
    elseif updates>shotStart+18 then
      error('The donor punch missed the approaching Goomba')
    end
  end
end

local route=coroutine.create(function()
  assert(#rom==64 and #cookie==32,'Exact ROM and transport cookie required')
  wait(function()return frame>=70 and read(0x6004)==1 and read(0x775)==0 end)
  press(16)
  wait(function()return read(0x7307)==2 and read(0x775)==0 end)
  press(4)
  for _=1,7 do press(1) end
  assert(read(0x7309)==15 and read(0x6002)==16,'Mike Jones menu position')
  press(32);press(32)
  assert(read(0x730b)&0x60==0x40,'Steve alternate')
  press(16);wait(active)
  phase='settle'
  while not done do tick();coroutine.yield() end
end)
emu.addEventCallback(guard(function()
  emu.setInput({right=pad&1~=0,down=pad&4~=0,start=pad&16~=0,
    select=pad&32~=0,b=pad&64~=0},0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guard(function()
  frame=frame+1
  assert(frame<=4200,'Bounded physical Steve replay')
  for _,item in ipairs(pending) do
    for i=1,4 do
      assert(emu.read(item[1]+i-1,emu.memType.nesSpriteRam)==item[2][i],'Physical Steve sprite cell')
    end
    dmaMatches=dmaMatches+1
  end
  pending={}
  local ok,message=coroutine.resume(route)
  assert(ok,message)
end),emu.eventType.endFrame)
