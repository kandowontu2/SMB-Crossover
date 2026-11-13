local C={STEVE_COMBAT_FIELDS}
local pendingContact
local function combatActor(slot)
  return {slot=slot,x=read(C.Enemy_X_Position+slot)+256*read(C.Enemy_PageLoc+slot),
    y=read(C.Enemy_Y_Position+slot)}
end
local function nativeObserve(at,bank,callback)
  emu.addMemoryCallback(guard(function()
    local mapped=emu.convertAddress(at)
    if active() and mapped and mapped.memType==emu.memType.nesPrgRom
      and mapped.address==bank*8192+(at&8191)then callback()end
  end),emu.callbackType.exec,at)
end
nativeObserve(C.InitEnemyObject,C.InitEnemyObjectBank,function()
  local slot=emu.getState()['cpu.x']
  if read(C.Enemy_ID+slot)~=6 then return end
  local actor=combatActor(slot)
  assert(actor.x==1120 or actor.x==1152,'Native parser Goomba world position')
  assert(actor.y==176,'Native parser Goomba initial Y')
  combat.spawns[#combat.spawns+1]=actor
end)
nativeObserve(C.JnInjury,C.JnInjuryBank,function()
  if work(2,0xc1f2)>0 then combat.injuryCalls=combat.injuryCalls+1 end
end)
observe(C.ArmorDamage,1,function()
  local timer,age=work(2,0xc1f2),work(2,0xc97e)
  if timer>0 and age>=32 then pendingContact={timer=timer,hp=field('JnHealth'),slot=read(C.JnSavedX)}end
end)
observe(C.ArmorDamageProtected,1,function()
  if not pendingContact then return end
  local hit=pendingContact;pendingContact=nil
  local expected=hit.timer<8 and 2 or ((hit.timer-8)|7)
  assert(work(2,0xc1f2)==expected and work(2,0xc97e)==0,'Original eight-unit armor contact arithmetic')
  assert(field('JnHealth')==hit.hp and hit.hp==6 and read(C.Enemy_ID+hit.slot)==6,'Actual Goomba contact preserves native health')
  hit.after=expected;combat.contacts[#combat.contacts+1]=hit
end)
nativeObserve(C.JnDefeat,C.JnDefeatBank,function()
  local slot=emu.getState()['cpu.x']
  if read(C.Enemy_ID+slot)~=6 or combat.defeated[slot]then return end
  combat.defeated[slot]=true;combat.defeats[#combat.defeats+1]=combatActor(slot)
end)
local function combatTick()
  local age=updates-since
  assert(active() and field('JnHealth')==6 and field('NumberofLives')==2,'Healthy armored combat')
  if #combat.defeats>0 and read(0x5c87)>0 then combat.retained=true end
  if phase=='combat-approach'then
    approach(1040,'combat-contact');assert(age<600,'Grounded combat approach')
  elseif phase=='combat-contact'then
    pad=0
    if #combat.contacts>0 then
      assert(#combat.spawns==2 and combat.injuryCalls>0,'Two actual parsed enemies and native injury call')
      assert(field('PlayerFacingDir')==1 and read(0x1e)==0,'Grounded right-facing attack')
      transition('combat-wave',64)
    end
    assert(age<400,'Actual Goomba armor contact')
  elseif phase=='combat-wave'then
    pad=age<3 and 64 or 0
    if #combat.defeats==2 and read(0x5c87)==0 and age>=30 then
      assert(births==1 and combat.retained and waveFacings[1],'One retained wave defeats both actual Goombas')
      transition('combat-turn',2)
    end
    assert(age<90,'Native piercing Goomba defeats')
  elseif phase=='combat-turn'then
    if age>=6 then
      assert(field('PlayerFacingDir')==2,'Native left-facing controller turn')
      transition('combat-left',64)
    end
  elseif phase=='combat-left'then
    pad=age<3 and 64 or 0
    if age>=50 then
      assert(births==2 and waveFacings[2] and dma>=4,'Both wave facings and physical sprite DMA')
      transition('clock',0)
    end
  end
end
