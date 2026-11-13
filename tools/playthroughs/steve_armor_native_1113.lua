-- Read-only controller for a declared six-question-block native level fixture.
local F={STEVE_FIELDS}
local cookie=STEVE_COOKIE
local mode=STEVE_MODE
local points={STEVE_POINTS}
local rom=assert(os.getenv('SMB_STDOUT_ROM_SHA'))
local frame,pad,updates,last=0,0,0,-1
local done=false
local phase='menu'
local since,block,prepared,collected,births,dma=0,1,0,0,0,0
local tokenLast=0
local armorSeen,entrySeen,exitSeen=false,false,false
local waveFacings={}
local expected,pending={},{}

local function read(at)return emu.read(at,emu.memType.nesDebug)end
local function field(name)return read(F[name])end
local function work(bank,at)return emu.read(bank*8192+(at&8191),emu.memType.nesWorkRam)end
local function x()return field('Player_PageLoc')*256+field('Player_X_Position')end
local function active()
  return field('SelectedCharacter')==16 and read(0x730b)&0x60==0x40
    and field('OperMode')==1 and field('OperMode_Task')==3 and field('GameEngineSubroutine')==8
end
local function header(bank)
  local result={}
  for at=0x1fe0,0x1fef do result[#result+1]=string.format('%02x',work(bank,at))end
  return table.concat(result)
end
local function finish(ok,reason)
  if done then return end
  done=true
  print(string.format('SMB_NATIVE_RECEIPT {"passed":%s,"reason":%q,"ROM_SHA256":%q,'..
    '"mode":%q,"private_level_fixture":%s,"controller_only":true,"runtime_state_writes":0,'..
    '"physical_frames":%d,"updates":%d,"phase":%q,"prepared":%d,"collected":%d,'..
    '"births":%d,"wave_DMA_matches":%d,"armor_seen":%s,"entry_seen":%s,"exit_seen":%s,'..
    '"x":%d,"y":%d,"health":%d,"lives":%d}',
    tostring(ok),reason,rom,mode,tostring(mode=='armor_fixture'),frame,updates,phase,prepared,collected,
    births,dma,tostring(armorSeen),tostring(entrySeen),tostring(exitSeen),x(),field('Player_Y_Position'),
    field('JnHealth'),field('NumberofLives')))
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
    local mapped=emu.convertAddress(at)
    if active() and mapped and mapped.memType==emu.memType.nesWorkRam
      and mapped.address==bank*8192+(at&8191)then callback()end
  end),emu.callbackType.exec,at)
end
observe(0xca00,2,function()
  updates=updates+1
  for bank=1,3 do assert(header(bank)==cookie,'Complete Steve owner identity')end
end)
observe(0xb586,3,function()
  if work(2,0xc1f2)>0 then births=births+1 end
end)
observe(STEVE_WAVE_RENDER,2,function()
  local px=read(0x5c88)+256*read(0x5c89)-field('ScreenLeft_X_Pos')-256*field('ScreenLeft_PageLoc')
  local py=read(0x5c8a)
  local count=work(2,0xc8e0)
  assert(count==8 or count==16,'Original armor wave record')
  expected={}
  for at=1,count,4 do
    local tile,attr,dy,dx=work(2,0xc8e0+at),work(2,0xc8e1+at),work(2,0xc8e2+at),work(2,0xc8e3+at)
    if dy>=128 then dy=dy-256 end
    if dx>=128 then dx=dx-256 end
    local sx=px+dx
    if sx>=0 and sx<=255 then expected[#expected+1]={py+dy,tile,attr,sx}end
  end
  waveFacings[work(2,0xc97b)]=true
end)
emu.addMemoryCallback(guard(function(_,value)
  if not active() or value~=2 or #expected==0 then return end
  pending={}
  for _,cell in ipairs(expected)do
    for at=0,252,4 do
      if read(0x200+at)==cell[1] and read(0x201+at)==cell[2]
        and read(0x202+at)==cell[3] and read(0x203+at)==cell[4]then
        pending[#pending+1]={at,cell}
        break
      end
    end
  end
  assert(#pending==#expected,'Native armor wave reaches OAM DMA')
  expected={}
end),emu.callbackType.write,0x4014)

local function transition(name,bits)
  phase=name;since=updates;pad=bits or 0
end
local function approach(target,nextPhase)
  local gap=target-x()
  if math.abs(gap)<=1 then transition(nextPhase,0)
  else pad=gap>0 and 1 or 2 end
end
local function tick()
  if updates==last then return end
  last=updates
  assert(active() and field('NumberofLives')==2 and field('JnHealth')==6,'Healthy active Steve')
  local age=updates-since
  local tag=read(F.InvPickup+5)
  if tag==0x8c and tokenLast==0 then prepared=prepared+1 end
  tokenLast=tag
  local state=work(2,0xc1f4)
  if state==13 then entrySeen=true end
  if state==16 then exitSeen=true end
  if work(2,0xc1f2)>0 then armorSeen=true end
  if phase=='ingress' then
    pad=age<36 and 1 or 0
    if age>=60 then assert(x()>40,'Ordinary native movement');finish(true,'Unmodified Steve ingress and60updates')end
  elseif phase=='approach' then approach(points[block]-7,'settle')
  elseif phase=='settle' and age>=7 then transition('bump',128)
  elseif phase=='bump' then
    if age>=9 then pad=0 end
    if age>=62 and tag==0x8c and read(F.Enemy_State+5)==128 then transition('back',2)end
    assert(age<120,'Native fixture question block reveals a mature token')
  elseif phase=='back' then approach(points[block]-34,'launch')
  elseif phase=='launch' and age>=9 then transition('collect',129)
  elseif phase=='collect' then
    pad=(age<9 and 128 or 0)|1
    if work(2,0xc3fd)>0 then
      assert(read(F.Enemy_Flag+5)==0 and tag==0,'Native token collection erases actor')
      collected=collected+1;transition('flight',0)
    end
    assert(age<90,'Native fixture token collection')
  elseif phase=='flight' and work(2,0xc3fd)==0 then
    if block==3 then transition('robot',0)
    elseif block==6 then transition('armor',0)
    else block=block+1;transition('approach',1)end
  elseif phase=='robot' then
    if work(2,0xc1f6)==1 and work(2,0xc1f3)==0 and state==0 then block=4;transition('approach',1)end
    assert(age<300,'Original first robot grant')
  elseif phase=='armor' then
    if work(2,0xc1f2)>0 and state==0 then transition('attack-right',64)end
    assert(age<300,'Matching original token pattern activates armor')
  elseif phase=='attack-right' then
    if age>=3 then pad=0 end
    if age>=50 then transition('turn-left',2)end
  elseif phase=='turn-left' and age>=6 then
    assert(field('PlayerFacingDir')==2,'Controller turns Steve left');transition('attack-left',64)
  elseif phase=='attack-left' then
    if age>=3 then pad=0 end
    if age>=50 then
      assert(births==2 and waveFacings[1] and waveFacings[2] and dma>=4,'Both original moving waves survive physical DMA')
      transition('clock',0)
    end
  elseif phase=='clock' then
    if work(2,0xc1f2)==0 and state==0 then
      assert(prepared==6 and collected==6 and entrySeen and exitSeen and work(2,0xc1f6)==1,'Complete original token armor lifecycle')
      finish(true,'Private native six-question fixture, armor waves and natural clock exit')
    end
    assert(age<2300,'Original natural armor clock and exit')
  end
end
local function wait(predicate)
  for _=1,1800 do if predicate()then return end;coroutine.yield()end
  error('Native menu transition timed out')
end
local function press(bits)
  pad=bits;for _=1,4 do coroutine.yield()end
  pad=0;for _=1,8 do coroutine.yield()end
end
local route=coroutine.create(function()
  wait(function()return frame>=70 and read(0x6004)==1 and read(0x775)==0 end)
  press(16);wait(function()return read(0x7307)==2 and read(0x775)==0 end)
  press(4);for _=1,7 do press(1)end
  assert(read(0x7309)==15 and field('SelectedCharacter')==16,'Mike menu position')
  press(32);press(32);press(16);wait(active)
  transition(mode=='ingress' and 'ingress' or 'approach',0)
  while not done do tick();coroutine.yield()end
end)
emu.addEventCallback(guard(function()
  emu.setInput({right=pad&1~=0,left=pad&2~=0,down=pad&4~=0,start=pad&16~=0,
    select=pad&32~=0,b=pad&64~=0,a=pad&128~=0},0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guard(function()
  frame=frame+1;assert(frame<=10000,'Bounded native armor fixture replay')
  for _,entry in ipairs(pending)do
    for at=1,4 do assert(emu.read(entry[1]+at-1,emu.memType.nesSpriteRam)==entry[2][at],'Physical armor wave sprite cell')end
    dma=dma+1
  end
  pending={}
  local ok,message=coroutine.resume(route);assert(ok,message)
end),emu.eventType.endFrame)
