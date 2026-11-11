local full={furthest=0, advanced=0, hold=0, lastJump=-60, lastProjection=-1,
  jumps={}, crossings={}, crossed={}, flag=false, castle=false, cap='approach'}
local routeObstacles={{608,640},{736,768},{912,944},{1104,1136},{1376,1424},
  {2448,2480},{2608,2640},{2864,2896}}
local routeGaps={{1104,1090},{1376,1366},{2448,2435}}

local function fullCamera()
  return read(0x71d)*256+read(0x71f)
end

local function fullEnemy(wx,wy)
  local nearest,kind=53,nil
  for slot=0,5 do
    local flag,id=read(0x10+slot),read(0x17+slot)
    local dx=read(0x5d+slot)*256+read(0x76+slot)-wx
    if flag>0 and flag<128 and id<13 and read(0x1f+slot)&32==0
      and read(0xa5+slot)==1 and dx>0 and dx<nearest
      and math.abs(read(0xbe+slot)-wy)<=25 then
      nearest,kind=dx,id
    end
  end
  return nearest,kind
end

local function beginFull()
  full.furthest=x()
  full.advanced=projections
  full.lastProjection=projections-1
  pad=1
end

local function fullTick()
  local wx,wy=x(),read(0xbd)
  local engine,level=read(0x0f),read(0x761)
  local lives,hp=read(0x75f),read(0x5f30)
  assert(lives==2 and engine~=11 and hp>0,'Steve route lost a life at X'..wx..'/Y'..wy)
  if level==1 and engine==8 and read(0x753)==2 then
    assert(full.flag and full.castle and #full.crossings==#routeObstacles,
      'All stock pipes, gaps, flagpole and castle crossed')
    finish(true,'Steve cleared 1-1 and entered underground 1-2')
    return
  elseif engine~=8 then
    if engine==4 and wx>=3140 then full.flag=true end
    if engine==5 and wx>=3160 then full.castle=true end
    pad=0
    return
  end
  if projections==full.lastProjection then return end
  full.lastProjection=projections
  if wx>full.furthest then full.furthest,full.advanced=wx,projections end
  assert(projections-full.advanced<=200,'Steve stalled at X'..wx..'/Y'..wy)

  local ground=read(0x1e)==0
  if ground and wy<=176 then
    for _,pair in ipairs(routeObstacles) do
      local left,right=pair[1],pair[2]
      if not full.crossed[left] and wx>=right then
        full.crossed[left]=true
        full.crossings[#full.crossings+1]=string.format('[%d,%d,%d,%d,%d,%d,%d]',
          projections,left,right,wx,wy,fullCamera(),hp)
      end
    end
  end

  local gap
  for _,pair in ipairs(routeGaps) do
    if not full.crossed[pair[1]] then gap=pair;break end
  end
  local dx,id=fullEnemy(wx,wy)
  if full.cap=='jump' and wx>=2411 then
    if ground and read(0x5c92)==0 then full.cap='landed'
    else pad=0;return end
  end
  if ground and read(0x5c92)==0 and projections-full.lastJump>=13 then
    local reason,hold=nil,9
    if gap and wx>=gap[2] and wx<gap[1]+8 then
      reason='gap-'..gap[1]
    elseif gap and gap[1]==2448 and wx>=2398 and wx<2416 and wy==128 and full.cap=='approach' then
      reason,hold='third-gap-cap',1
      full.cap='jump'
    elseif read(0x6eba)~=0 or projections-full.advanced>=15 and projections-full.lastJump>=38 then
      reason='wall'
    elseif dx<=28 and (not gap or gap[1]-wx>80) and (read(0x5c80)~=0 or id==12) then
      reason='enemy-hop'
    end
    if reason then
      full.lastJump,full.hold=projections,projections+hold
      full.jumps[#full.jumps+1]=string.format('[%d,%q,%d,%d,%d,%d,%d]',
        projections,reason,wx,wy,fullCamera(),hp,hold)
    end
  end
  local previous=pad
  pad=projections<full.hold and 129 or 1
  if dx<=36 and previous&64==0 and pad&128==0 then pad=pad|64 end
end
