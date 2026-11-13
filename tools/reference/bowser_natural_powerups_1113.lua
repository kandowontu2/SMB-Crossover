-- Readonly ordinary-input acquisition on the unmodified authored stage.
local function work3(at)return emu.read(3*8192+(at&8191),emu.memType.nesWorkRam)end
local function item(slot)
 return{slot=slot,flag=read(F.Enemy_Flag+slot),id=read(F.Enemy_ID+slot),state=read(F.Enemy_State+slot),
  x=read(F.Enemy_X_Position+slot)+256*read(F.Enemy_PageLoc+slot),y=read(F.Enemy_Y_Position+slot),kind=read(F.PowerUpType+slot)}
end
local function sourceState()
 return{tier=work3(0xbe28),health=work3(0xbe29),active=r('GuestPowerupActive'),age=r('GuestPowerupAge'),status=r('PlayerStatus'),engine=r('GameEngineSubroutine')}
end
local function isWork3(pc)
 local q=emu.convertAddress(pc)
 return q and q.memType==emu.memType.nesWorkRam and q.address//8192==3
end
local pendingPickup=nil
emu.addMemoryCallback(guard(function()
 if not game or not isWork3(F.BwPickup)then return end
 assert(read(F.BwPickup)==0xbd and read(F.BwPickup+1)==F.PowerUpType%256 and read(F.BwPickup+2)==F.PowerUpType//256 and read(F.BwPickup+3)==0xc9 and read(F.BwPickup+4)==2,'Actual source mature pickup leaf')
 local c=emu.getState();local a=item(c['cpu.x'])
 if a.kind>1 or a.state<128 then return end
 assert(not pendingPickup,'One actual mature Bowser collector at a time')
 local sp=c['cpu.sp'];local pc=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535
 local q={item=a,before=sourceState(),player=state(),return_pc=pc,return_sp=(sp+2)&255}
 pendingPickup=q
 emu.addMemoryCallback(guard(function()
  if pendingPickup~=q then return end
  local c=emu.getState();if c['cpu.sp']~=q.return_sp then return end
  q.after=sourceState();q.erased=read(F.Enemy_Flag+a.slot)==0
  q.sound=r('Square2SoundQueue');q.popup=read(F.FloateyNum_Control+a.slot)
  local expected=#natural.pickups+1
  assert(expected<=2 and a.kind==expected-1 and q.after.tier==expected,'Natural mushroom then flower tiers')
  assert(q.erased and q.sound==32 and q.popup==6,'Native erasure, score and pickup sound')
  assert(q.after.health==(identity==0 and 34 or 5),'Source-specific health refill')
  assert(q.after.active==1 and q.after.engine==9,'Actual source upgrade freeze begins')
  natural.pickups[#natural.pickups+1]=q;natural.freeze={q=q,ticks=0}
  pendingPickup=nil;pad=0
 end),emu.callbackType.exec,pc)
end),emu.callbackType.exec,F.BwPickup)
emu.addMemoryCallback(guard(function()
 if game and natural.freeze and r('GuestPowerupActive')~=0 and isWork3(F.BwPowerupTick)then
  natural.freeze.ticks=natural.freeze.ticks+1
 end
end),emu.callbackType.exec,F.BwPowerupTick)
emu.addMemoryCallback(guard(function()
 if not game then return end
 local at=emu.convertAddress(F.NativeRarePlayerHeadCollisionCore)
 if not at or at.memType~=emu.memType.nesPrgRom or at.address~=BOWSER_HEAD_OFFSET then return end
 local c=emu.getState();local s=state()
 if s.x>=312 and s.x<=344 or s.x>=1224 and s.x<=1264 then
  natural.heads[#natural.heads+1]={a=c['cpu.a'],s=s,tier=work3(0xbe28)}
  assert(#natural.heads<=30,'Finite actual native head observations')
 end
end),emu.callbackType.exec,F.NativeRarePlayerHeadCollisionCore)
local function phaseTo(name)
 natural.phase=name;natural.since=updates;natural.events[#natural.events+1]={phase=name,s=state()}
end
local function directional(target)
 local at=x();if at<target then return 1 elseif at>target+1 then return 2 end;return 0
end
local function drive()
 local s=state()
 assert(r('SelectedCharacter')==27 and r('FmAlts')&8==identity*8,'Actual selected Bowser identity retained')
 assert(s.lives==2 and s.health>0 and s.engine~=6 and s.engine~=11 and s.ready==183,'Live original Bowser with both lives')
 assert(updates<5000,'Bounded natural two-item route')
 if natural.freeze then
  pad=0
  if s.engine==8 and r('GuestPowerupActive')==0 then
   assert(natural.freeze.ticks==60,'All60 actual source upgrade ticks')
   natural.freeze.q.ticks=natural.freeze.ticks;natural.freeze.q.resumed=state();natural.freeze=nil
   phaseTo(#natural.pickups==1 and 'flower-travel'or 'resumed-play')
  end
  return
 end
 if not active()then pad=0;return end
 assert(s.world==0 and s.level==0,'Authored1-1 item route')
 if natural.phase=='mushroom-approach'then
  pad=directional(328)|(updates%32==0 and 64 or 0)
  if s.x>=328 and s.x<=329 and s.native_state==0 then phaseTo('mushroom-head');pad=128 end
 elseif natural.phase=='mushroom-head'then
  local age=updates-natural.since;pad=age<12 and 128 or 0
  for slot=0,5 do local a=item(slot)
   if a.flag==1 and a.id==46 and a.kind==0 then natural.mushroom_birth=natural.mushroom_birth or{item=a,s=s};phaseTo('mushroom-collect');pad=1;break end
  end
  assert(age<120,'Actual first question must produce its mushroom')
 elseif natural.phase=='mushroom-collect'then
  pad=(s.x<395 and 1 or 0)|(updates%32==0 and 64 or 0)
  assert(updates-natural.since<500,'Mature mushroom returns from authored first pipe')
 elseif natural.phase=='flower-travel'then
  if s.x<1184 then traversalDrive()else
   assert(solid(s.x+8,208),'Settle on authored floor beyond the first gap')
   phaseTo('flower-approach');pad=0
  end
 elseif natural.phase=='flower-approach'then
  if not natural.approach_grounded then
   pad=0;if s.native_state==0 and s.y==176 then natural.approach_grounded=true end;return
  end
  pad=directional(1240)|(updates%32==0 and 64 or 0)
  if s.x>=1240 and s.x<=1241 and s.native_state==0 then phaseTo('flower-head');pad=128 end
  assert(updates-natural.since<400,'Ordinary approach below authored flower question')
 elseif natural.phase=='flower-head'then
  local age=updates-natural.since;pad=age<12 and 128 or 0
  for slot=0,5 do local a=item(slot)
   if a.flag==1 and a.id==46 and a.kind==1 then natural.flower_birth=natural.flower_birth or{item=a,s=s};phaseTo('flower-collect');natural.pulse=0;break end
  end
  assert(age<120,'Actual flower question head hit')
 elseif natural.phase=='flower-collect'then
  local age=updates-natural.since;pad=directional(1258)
  if natural.pulse>0 then natural.pulse=natural.pulse-1;pad=pad|128
  elseif s.native_state==0 and age-(natural.last_pulse or -100)>40 then natural.last_pulse=age;natural.pulse=17;pad=pad|128 end
  assert(age<500,'Mature authored flower ordinary east-side jump collection')
 elseif natural.phase=='resumed-play'then
  pad=1|(updates%32==0 and 64 or 0)
  if updates-natural.since>=60 then
   assert(s.x-natural.events[#natural.events].s.x>=16 and work3(0xbe28)==2,'Retain flower tier through resumed movement')
   finish(true,'Natural authored mushroom and flower, two60-tick upgrades, resumed original Bowser play')
  end
 else error('Unknown natural Bowser phase '..natural.phase)end
end
