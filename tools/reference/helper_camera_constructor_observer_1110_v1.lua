-- Read-only construction and boarding observations shared by the three routes.
local function helperCameraObserver(config)
 local rows={}
 local function peek(address)return emu.read(address,emu.memType.nesDebug)end
 local function stage()
  return peek(0x6002)==config.owner and peek(0x0771)==1 and
   peek(0x0764)==0 and peek(0x0761)==0 and peek(0x0754)==5
 end
 local function actorAt(slot,left)
  return peek(0x10+slot)==1 and peek(0x17+slot)==0x25 and
   peek(0x76+slot)+256*peek(0x5d+slot)==left
 end
 local function world()
  return peek(0x75)+256*peek(0x5c)
 end
 emu.addMemoryCallback(function()
  if not stage()or peek(0x0145)~=config.tag then return end
  assert(peek(config.pc)==0x20 and peek(config.pc+1)==0x5a and
   peek(config.pc+2)==0x01,'Expected constructor farcall')
  local s=emu.getState()
  local slot=s['cpu.x']
  local left=peek(0x76+slot)+256*peek(0x5d+slot)
  local y=peek(0xbe+slot)
  local camera=peek(0x071f)+256*peek(0x071d)
  local relative=left-camera
  local i=#rows+1
  assert(slot<6 and actorAt(slot,left),'Native platform flag and ID')
  assert(left==config.lefts[i] and y==config.y,'Source placement and initial Y')
  assert(relative>=256 and relative<=287,'Constructor must be offscreen')
  if config.tag==154 then
   assert(peek(0x73ab+i-1)==slot+1 and peek(0x73ae+slot)==0x82+i,
    'Independent reciprocal ownership')
   if i==2 then
    assert(slot~=rows[1].slot and actorAt(rows[1].slot,rows[1].left),
     'Second constructor retains visible first actor')
   end
  end
  local row={left=left,y=y,camera=camera,relative=relative,slot=slot,player=world(),
   supportX=-1,supportY=-1,crossed=false}
  rows[i]=row
 end,emu.callbackType.exec,config.pc)
 emu.addEventCallback(function()
  if not stage()then return end
  local x=world()
  for i,row in ipairs(rows)do
   if row.supportX<0 and actorAt(row.slot,row.left)and peek(0x0566+row.slot)==row.slot and
      math.abs(peek(0xbd)+32-peek(0xbe+row.slot))<=4 and
      x>=row.left-16 and x<=row.left+32 then
    row.supportX=x;row.supportY=peek(0xbd)
   end
   if row.supportX>=0 and x>=config.pipes[i]+32 then row.crossed=true end
  end
 end,emu.eventType.endFrame)
 return function(ok,reason)
  if ok then
   if #rows~=#config.lefts then ok=false;reason='Missing offscreen constructor' end
   for _,row in ipairs(rows)do
    if not row.crossed then ok=false;reason='Missing assisted crossing' end
   end
  end
  local out=assert(io.open(OUTPUT..'helper-camera.json','w'))
  out:write(string.format('{"passed":%s,"ROM_sha256":"%s","reason":%q,"owner":%d,"placements":[',
   tostring(ok),config.sha,reason,config.owner))
  for i,row in ipairs(rows)do
   if i>1 then out:write(',')end
   out:write(string.format('{"left_x":%d,"center_x":%d,"initial_y":%d,"camera_left":%d,"relative_left":%d,'..
    '"slot":%d,"player_x_at_constructor":%d,"board_x":%d,"board_y":%d,"crossed":%s}',
    row.left,row.left+16,row.y,row.camera,row.relative,row.slot,row.player,row.supportX,row.supportY,
    tostring(row.crossed)))
  end
  out:write(']}\n');out:close()
  return ok,reason
 end
end
