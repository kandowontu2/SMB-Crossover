local pendingHits, verifiedHits={},{}
local healthChanges,lateApproach={},{}
local stageUpdates,stageFirstUpdate,previousHp=0,nil,nil
local jumpedLateEnemies,lastBand=false,nil

observe(STEVE_LASER_NATIVE_HIT,2,function()
  if phase~='laser-stage' then return end
  local slot=emu.getState()['cpu.x']
  assert(slot<6 and read(0x10+slot)>0 and read(0x1f+slot)&32==0,'Beam contacts an active native enemy')
  pendingHits[slot]={kind=read(0x17+slot),hp=read(STEVE_LASER_ENEMY_HP+slot),
    x=read(0x5d+slot)*256+read(0x76+slot),y=read(0xbe+slot)}
end)

local function laserStageTick()
  for slot,hit in pairs(pendingHits) do
    local hp,state=read(STEVE_LASER_ENEMY_HP+slot),read(0x1f+slot)
    if (hit.hp>=2 and hp==hit.hp-1) or (hit.hp<2 and state&32~=0) then
      hit.defeated=state&32~=0
      verifiedHits[#verifiedHits+1]=hit
    end
  end
  pendingHits={}
  local hp=read(0x5f30)
  if previousHp and hp~=previousHp then
    healthChanges[#healthChanges+1]=string.format('X%d %d>%d',x(),previousHp,hp)
  end
  previousHp=hp
  if not stageFirstUpdate then stageFirstUpdate=companionUpdates end
  if active() then stageUpdates=stageUpdates+1 end
  if hp==0 then
    local hit=verifiedHits[1]
    finish(false,string.format('Steve ran out of HP with %d beam hits, first hit X%d, %s, approach %s',
      #verifiedHits,hit and hit.x or -1,table.concat(healthChanges,','),table.concat(lateApproach,',')))
    return
  end
  fullTick()
  if not active() then return end
  local wx=x()
  if wx<2060 and #verifiedHits==0 and pad&128==0 then pad=pad|64 end
  local grounded=read(0x1e)==0 and read(0x5c92)==0
  if wx>=2656 and wx<2744 then
    local band=wx//8
    if band~=lastBand and #lateApproach<14 then
      lateApproach[#lateApproach+1]=string.format('%d/%d/%d/%d:%02x',wx,read(0xbd),read(0x1e),read(0x5c92),pad)
      lastBand=band
    end
  end
  if not jumpedLateEnemies and wx>=2729 and wx<2737 and grounded then
    -- Clear the enemy approach after the exit pipe while preserving the two lives.
    jumpedLateEnemies=true
    full.lastJump,full.hold=companionUpdates,companionUpdates+9
    pad=129
  end
end

finishLaserStage=function()
  local hit=verifiedHits[1]
  local detail=hit and string.format('first beam hit enemy %02x at X%d Y%d, HP %d, defeated %s',
    hit.kind,hit.x,hit.y,hit.hp,tostring(hit.defeated)) or 'no beam contact'
  finish(hit~=nil,string.format('Earned Laserbot and cleared 1-1, %d verified hits, %s, %d physical/%d native active frames, actor %d, HP %d',
    #verifiedHits,detail,stageUpdates,companionUpdates-stageFirstUpdate,work(2,STEVE_COMPANION_ACTOR),read(0x5f30)))
end
