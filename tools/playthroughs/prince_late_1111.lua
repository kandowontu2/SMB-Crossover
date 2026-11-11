-- Continuation of the cold four-pipe replay. Uses the same read-only state and input helpers.
local koopaBrake=tonumber(os.getenv('SMB_PRINCE_KOOPA_BRAKE') or '1540')
local koopaMode=os.getenv('SMB_PRINCE_KOOPA_MODE') or 'standing'
local koopaJumpX=tonumber(os.getenv('SMB_PRINCE_KOOPA_JUMP_X') or '1501')

for _,address in ipairs({0x75,0x5c,0xc60f,0xc610}) do
  emu.addMemoryCallback(guarded(function(_,value)
    if not late.koopa or (progress~='late-ledge-run' and progress~='late-ledge-step'
      and progress~='late-ledge-settle') then return end
    local writes=late.koopa.writes or {}
    late.koopa.writes=writes
    if #writes>=18 then return end
    local cpu=emu.getState()
    local pc=cpu['cpu.pc']
    local mapping=emu.convertAddress(pc)
    local write={target=address,value=value,pc=pc,mapping=mapping and mapping.address,
      memory=mapping and mapping.memType,source_x=source(0x60f)+256*source(0x610),state=state()}
    if pc==0xc42a then
      local sp=cpu['cpu.sp']
      write.caller=(1+read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255)))&65535
      write.raw_x=source(0x78)+256*source(0x79)
      write.cell_x=source(0x7d)+256*source(0x7e)
      write.surface=source(0x7f)+256*source(0x80)
      write.align_x=source(0xa1)
      write.index=source(0x4b1)
      write.material=source(0x9f)
    end
    writes[#writes+1]=write
  end),emu.callbackType.write,address)
end

local function lateActor(slot)
  return {slot=slot,flag=read(0x10+slot),id=read(0x17+slot),state=read(0x1f+slot),
    x=read(0x76+slot)+256*read(0x5d+slot),y=read(0xbe+slot),direction=read(0x53f+slot)}
end

local function lateWalkers(s,kind)
  local result={}
  for slot=0,5 do
    local a=lateActor(slot)
    if a.flag==1 and a.id<=6 and a.state&32==0 and a.y>=160 and a.x>=s.x-16
        and (kind==nil or a.id==kind) then
      result[#result+1]=a
    end
  end
  table.sort(result,function(a,b)return a.x<b.x end)
  return result
end

local function afterSecondGap(s)
  local onFloor=support(s)
  local stood=onFloor and idle(s)
  local x=s.x
  if progress=='late-second-approach' and x>=1320 then
    switch('late-second-brake',0)
  elseif progress=='late-second-brake' and stood then
    switch('late-second-left',2)
  elseif progress=='late-second-left' and x<=1312 and s.facing==0 then
    switch('late-second-park',0)
  elseif progress=='late-second-park' and stood then
    switch('late-second-run',1)
  elseif progress=='late-second-run' then
    assert(x<1361,'Original second-gap running jump has a supported takeoff')
    if x>=1328 and x<=1356 and s.phase&3<=1 and running(s) then
      assert(tile(1360,208)==0x54 and tile(1376,208)==0 and tile(1392,208)==0
        and tile(1408,208)==0 and tile(1424,208)==0x54,'Actual three-column second gap')
      late.second_request=s
      switch('late-second-jump',129)
    end
  elseif progress=='late-second-jump' and s.action==4 then
    late.second_admission=s
    switch('late-second-flight',1)
  elseif progress=='late-second-flight' and x>=1440 and s.y==176 and onFloor then
    late.second_gap=s
    local pair=lateWalkers(s,6)
    assert(#pair==2 and pair[1].direction==2 and pair[2].direction==2,'Actual leftward Goomba pair')
    late.reverse={pair=pair,falls={}}
    switch('late-brake',0)
  elseif progress=='late-brake' and stood then
    switch('late-face-left',2)
  elseif progress=='late-face-left' and s.facing==0 then
    switch('late-settle-left',0)
  elseif progress=='late-settle-left' and stood then
    assert(s.facing==0 and x+2>=1424,'Supported original left-facing standing jump')
    late.reverse.request=s
    switch('late-reverse-jump',128)
  elseif progress=='late-reverse-jump' and s.action==3 then
    late.reverse.admission=s
    switch('late-reverse-flight',2)
  elseif progress=='late-reverse-flight' and x+2<1376 and s.y==176 and onFloor then
    late.reverse.landing=s
    switch('late-wait-walkers',0)
  elseif progress=='late-wait-walkers' then
    local cleared=0
    for _,a in ipairs(late.reverse.pair) do
      local now=lateActor(a.slot)
      local key=tostring(a.slot)
      if now.flag==1 and now.id==6 and now.x>=1376 and now.x<1424 and now.y>=204 then
        late.reverse.falls[key]=late.reverse.falls[key] or now
      elseif now.flag==0 and late.reverse.falls[key] then
        cleared=cleared+1
      end
    end
    if cleared==2 and stood then switch('late-return-backup',2) end
  elseif progress=='late-return-backup' and x<=s.scroll+4 then
    switch('late-return-settle',0)
  elseif progress=='late-return-settle' and stood then
    assert(s.facing==0 and x+13<1376,'Backed away from the actual lip')
    switch('late-return-face',1)
  elseif progress=='late-return-face' and s.facing==255 then
    switch('late-return-park',0)
  elseif progress=='late-return-park' and stood then
    assert(x+13<1376 and tile(x+13,208)==0x54,'Original return takeoff stays on the near bank')
    late.reverse.return_request=s
    switch('late-forward-jump',128)
  elseif progress=='late-forward-jump' and (s.action==3 or s.action==4) then
    late.reverse.return_admission=s
    switch('late-forward-flight',1)
  elseif progress=='late-forward-flight' and x>=1440 and s.y==176 and onFloor then
    late.reverse.return_landing=s
    switch('late-koopa-approach',1)
  elseif progress=='late-koopa-approach' and x>=koopaBrake then
    assert(x<=1559,'Brake before the first green Koopa')
    late.koopa={brake=s,minimum_y=s.y}
    switch('late-koopa-settle',0)
  elseif progress=='late-koopa-settle' and stood then
    local koopa=lateWalkers(s,0)[1]
    assert(x<1600 and s.facing==255,'Supported standing A before the Koopa')
    late.koopa.request={state=s,actor=koopa}
    if koopaMode~='standing' then
      late.koopa.tiles={}
      for col=1488,1648,16 do
        local cells={}
        for y=112,176,16 do cells[#cells+1]=tile(col,y) end
        late.koopa.tiles[#late.koopa.tiles+1]={x=col,rows_112_to_176=cells}
      end
      switch('late-koopa-climb',8)
    else
      switch('late-koopa-jump',128)
    end
  elseif progress=='late-koopa-climb' then
    if s.mode==2 or s.mode==6 then late.koopa.ledge=late.koopa.ledge or s end
    if s.y<=114 and onFloor and solid(x+13,144) then
      late.koopa.top=s
      if koopaMode=='climb' then
        final=s
        finish(true,'Original climb reaches the authored brick above the Koopa route')
      elseif koopaMode=='step' then
        switch('late-ledge-step',65)
      else
        switch('late-ledge-run',1)
      end
    elseif commits-changedAt>=120 then
      error('Original Up does not reach the authored brick from this stance')
    end
  elseif progress=='late-ledge-step' and s.action==42 then
    late.koopa.step=s
    switch('late-ledge-settle',0)
  elseif progress=='late-ledge-settle' then
    if s.y>116 then error('Original careful step did not retain the single brick')end
    if stood and solid(x+2,144) then
      late.koopa.ledge_stance=s
      switch('late-ledge-run',1)
    end
  elseif progress=='late-ledge-run' then
    local samples=late.koopa.run or {}
    late.koopa.run=samples
    if #samples<12 and (not samples[#samples] or x~=samples[#samples].x) then
      samples[#samples+1]=s
    end
    if x>=koopaJumpX and s.y<=114 and running(s) then
      late.koopa.ledge_request=s
      switch('late-ledge-jump',129)
    elseif x>=1521 or s.y>116 then
      error('Lost native brick support before original jump admission')
    end
  elseif progress=='late-ledge-jump' and s.action==4 then
    late.koopa.ledge_admission=s
    switch('late-ledge-flight',1)
  elseif progress=='late-ledge-flight' then
    if x+13>=1600 and s.y<=114 and onFloor then
      late.koopa.ledge_landing=s
      final=s
      finish(true,'Original running jump lands on the next authored brick above the Koopa')
    elseif s.y>144 or x>1648 then
      error('Original jump fell short of the next brick')
    end
  elseif progress=='late-koopa-jump' and s.action==3 then
    late.koopa.admission=s
    switch('late-koopa-flight',1)
  elseif progress=='late-koopa-flight' then
    late.koopa.minimum_y=math.min(late.koopa.minimum_y,s.y)
    late.koopa.actor=late.koopa.actor or lateWalkers(s,0)[1]
    if x>=1705 and onFloor and s.action~=3 then
      local seen=late.koopa.request.actor or late.koopa.actor
      assert(seen,'Observed the authored green Koopa')
      local actor=lateActor(seen.slot)
      assert((actor.flag==0 or actor.id~=0 or actor.state&32~=0 or actor.x+12<x+2)
        and late.koopa.minimum_y<176,'Native support beyond the Koopa and actual airborne interval')
      late.koopa.clear=s
      switch('late-enemy-probe',1)
    end
  elseif progress=='late-enemy-probe' then
    local samples=late.enemies or {}
    late.enemies=samples
    local walkers=lateWalkers(s)
    if #walkers>0 and #samples<20 and (not samples[#samples] or commits-samples[#samples].state.commit>=4) then
      samples[#samples+1]={state=s,actors=walkers}
    end
    if x>=1760 and #walkers>0 then
      final=s
      finish(true,'Natural supported ground after the first Koopa; captured the next native group')
    end
  end
end
