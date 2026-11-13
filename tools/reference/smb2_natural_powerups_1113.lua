-- Ordinary current-stage item evidence. No gameplay/actor writes or grants.
local function sourceState()
 local s={};for _,name in ipairs({'S2Health','S2MaxHealth','S2Vegetables','S2Size','S2Air','S2VX','S2VY','S2Held','S2Fresh','S2Holding','S2State','S2Timer','S2Hurt','PlayerStatus'})do s[name]=r(name)end
 return s
end
local function actor(slot)
 return{slot=slot,flag=read(F.Enemy_Flag+slot),id=read(F.Enemy_ID+slot),kind=read(F.PowerUpType+slot),state=read(F.Enemy_State+slot),x=read(F.Enemy_X_Position+slot)+256*read(F.Enemy_PageLoc+slot),y=read(F.Enemy_Y_Position+slot)}
end
local function currentHook(name)
 local q=emu.convertAddress(F[name]);return q and q.memType==emu.memType.nesPrgRom and q.address==itemHooks[name].offset
end
local function newPhase(name)natural.phase=name;natural.since=updates;natural.events[#natural.events+1]={phase=name,s=state(),source=sourceState()}end
local function settle(target)
 local at=x();local vx=r('S2VX');if vx>=128 then vx=vx-256 end
 if at>target+1 then return 2 elseif at<target then return 1 elseif vx>0 then return 2 elseif vx<0 then return 1 end
 return 0
end
local pendingItem=nil
emu.addMemoryCallback(guard(function()
 if not game or not currentHook('NativeRarePlayerHeadCollisionCore')then return end
 natural.heads[#natural.heads+1]={a=emu.getState()['cpu.a'],s=state(),source=sourceState()}
 assert(#natural.heads<=30,'Finite actual native head attempts')
end),emu.callbackType.exec,F.NativeRarePlayerHeadCollisionCore)
emu.addMemoryCallback(guard(function()
 if not game or not currentHook('S2MainPrepare')then return end
 local a=actor(emu.getState()['cpu.x']);natural.prepares[#natural.prepares+1]={item=a,s=state(),source=sourceState()}
end),emu.callbackType.exec,F.S2MainPrepare)
emu.addMemoryCallback(guard(function()
 if not game or not currentHook('S2MainPickup')then return end
 assert(not pendingItem,'One actual SMB2 native collector at a time')
 local c=emu.getState();local sp=c['cpu.sp'];local a=actor(c['cpu.x'])
 local pc=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535
 local q={item=a,before=sourceState(),s=state(),return_pc=pc,return_sp=(sp+2)&255};pendingItem=q
 emu.addMemoryCallback(guard(function()
  if pendingItem~=q or emu.getState()['cpu.sp']~=q.return_sp then return end
  q.after=sourceState();q.erased=read(F.Enemy_Flag+a.slot)==0;q.sound=r('Square2SoundQueue');q.popup=read(F.FloateyNum_Control+a.slot)
  assert(a.kind==0 and a.state>=128,'Actual mature natural Mushroom collector')
  assert(q.before.S2Health==15 and q.before.S2MaxHealth==0,'Naturally injured initial health at collection')
  assert(q.after.S2Health==47 and q.after.S2MaxHealth==1 and q.after.S2Vegetables==0,'Original max-heart increment/full heal')
  assert(q.erased and q.sound==32 and q.popup==6,'Native erasure/pickup SFX/popup')
  natural.pickups[#natural.pickups+1]=q;pendingItem=nil;newPhase('resume');pad=0
 end),emu.callbackType.exec,pc)
end),emu.callbackType.exec,F.S2MainPickup)
local function drive()
 local s=state();local own=sourceState()
 assert(r('SelectedCharacter')==25 and r('S2Variant')==identity and s.ready==178,'Actual SMB2/Doki identity and owner')
 assert(s.lives==2 and own.S2Health>0 and s.engine~=6 and s.engine~=11,'Both lives and live source health')
 assert(updates<1200,'Finite ordinary first-item route')
 if not active()then pad=0;return end
 assert(s.world==0 and s.level==0,'Unmodified authored1-1')
 if not natural.opening then natural.opening={s=s,source=own}end
 if own.S2Health<natural.previousHealth then natural.injuries[#natural.injuries+1]={before=natural.previousHealth,s=s,source=own}end
 natural.previousHealth=own.S2Health
 if natural.phase=='approach'then
  pad=1
  if natural.hold>0 then natural.hold=natural.hold-1;pad=129
  elseif itemMode=='healthy-flower-birth'and own.S2Air==0 and own.S2Held&128==0 then
   for slot=0,5 do local a=actor(slot)
    if a.flag==1 and a.id<21 and a.state<32 and a.x-s.x>0 and a.x-s.x<48 then natural.hold=23;pad=129;break end
   end
  end
  if s.x>=326 then newPhase('settle')end
 elseif natural.phase=='settle'then
  pad=settle(328)
  if own.S2Air==0 and s.x>=328 and s.x<=329 and own.S2VX==0 and own.S2Held&128==0 then newPhase('head');natural.hold=23;pad=128 end
 elseif natural.phase=='head'then
  pad=0
  if natural.hold>0 then natural.hold=natural.hold-1;pad=128
  elseif own.S2Air==0 and own.S2Held&128==0 then natural.hold=23;pad=128 end
 elseif natural.phase=='collect'then
  pad=s.x<395 and 1 or s.x>397 and 2 or 0
 elseif natural.phase=='resume'then
  pad=0
  if updates-natural.since>=60 then
   assert(own.S2Health==47 and own.S2MaxHealth==1 and own.S2Size==0,'Retained original large full-health source form')
   finish(true,'Natural injured Mushroom, original max-heart/full-heal, native pickup effects and60resumed updates');return
  end
 else error('Unknown natural phase '..natural.phase)end
 if not natural.birth then
  for slot=0,5 do local a=actor(slot)
   if a.flag==1 and a.id==46 then
    natural.birth={item=a,s=s,source=own}
    if itemMode=='healthy-flower-birth'then
     assert(a.kind==1 and own.S2Health==31 and own.S2MaxHealth==0 and own.S2Size==0 and #natural.injuries==0,'Documented healthy initial Flower choice')
     finish(true,'Healthy first authored question naturally produces Flower, confirming existing adaptation');return
    end
    assert(a.kind==0 and own.S2Health==15 and own.S2MaxHealth==0 and #natural.injuries==1,'One real injury produces natural Mushroom')
    newPhase('collect');pad=1;break
   end
  end
 end
end
