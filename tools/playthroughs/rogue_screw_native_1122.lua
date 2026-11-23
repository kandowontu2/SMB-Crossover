-- Continue the retained earned Wall Jump route into ordinary 1-3.
local function screwPhase(name)
 local f=gear.screw;f.phase=name;f.entered=updates
 assert(#f.steps<32,'Bounded natural Screw milestones')
 f.steps[#f.steps+1]={phase=name,player=state(),level=r('LevelNumber')}
end
local function screwCounts(suffix)
 local q=snapshot(suffix);q.RdControlDispatch=counts['RdControlDispatch'..suffix]or 0;return q
end
local function screwDrive(c)
 local f=gear.screw
 assert(identity()and r('NumberofLives')==2 and r('RdHealthLo')+r('RdHealthHi')>0,
        'Natural earned route retains life and positive source health')
 assert(c.world==0 and (c.level==1 or c.level==2) and updates-f.started<5000,
        'Bounded ordinary 1-2 exit and next stock upgrade')
 if not active()then return{}end
 if updates%24==0 then
  if #f.tail==20 then table.remove(f.tail,1)end
  local actors={};for i=0,5 do local a=actor(i);if a.flag>0 then actors[#actors+1]=a end end
  f.tail[#f.tail+1]={player=state(),level=c.level,area=c.area,actors=actors}
 end
 local grounded=c.yHigh==1 and bombReady(c)
 if c.level==1 then
  assert(r('RdGear')==7 and r('RdTanks')==1 and r('RdMissiles')==5,'All preceding earned upgrades preserved')
  return gearTravel(setmetatable({area=gear.high.areaOffset},{__index=c}))
 end
 if not f.arrival then
  f.arrival={player=state(),area=c.area,areaOffset=r('AreaAddrsLOffset')}
  screwPhase('travel')
 end
 assert(c.areaType==1 and r('AreaAddrsLOffset')==f.arrival.areaOffset,'Actual next native tree stage')
 if stock=='screw-credit'then return{}end
 if f.phase=='travel'then
  if c.x>=886 then screwPhase('approach-block')
  else return gearTravel(c)end
 end
 if f.phase=='approach-block'then
  if born then screwPhase('mount')
  else
   if grounded and c.y<=129 and c.x>=944 and c.x<=947 then
    assert(c.block(944,160)==0xc1,'Land on the real unspent power block')
    screwPhase('morph-on-block');return{down=true}
   end
   local b={right=c.x<944,left=c.x>947}
   if not b.left and not b.right and grounded and r('RdHeld')&128==0 then
    assert(c.block(944,160)==0xc1,'Real unspent 1-3 raw1 question block')
    f.blockBefore=c.block(944,160);b.a=true
   end
   b.a=b.a or r('RdVY')>=128
   return b
  end
 end
 if f.phase=='morph-on-block'then
  if r('RdAction')~=3 then return{down=true}end
  if r('RdHeld')&64~=0 then return{}end
  for _,i in ipairs({0xd0,0xe0,0xf0})do if r('RdWAction',i)~=0 then return{}end end
  screwPhase('place-bomb');return{b=true}
 end
 if f.phase=='place-bomb'then
  for _,i in ipairs({0xd0,0xe0,0xf0})do
   if r('RdWAction',i)==8 then
    assert(r('RdGear')==7 and r('RdAction')==3,'Ordinary fresh B places the earned Bomb')
    f.bomb=bombShot(i);screwPhase('open-block');return{}
   end
  end
  assert(updates-f.entered<12,'Fresh B allocates the original Bomb');return{b=true}
 end
 if f.phase=='open-block'then
  if born then screwPhase('collect')end
  assert(updates-f.entered<180,'Original Bomb reveals the authored next upgrade');return{}
 end
 if f.phase=='collect'then
  if r('RdAction')==3 then return{up=true}end
  return{}
 end
 if f.phase=='mount'then
  if r('RdAction')==3 then return{up=true}end
  if grounded and c.y<=129 and c.x>=936 and c.x<=956 then return{}end
  if grounded and c.y>=160 and r('RdHeld')&128==0 then
   if c.x>915 then return{left=true}end
   f.mountLaunch=state();screwPhase('rise');return{a=true}
  end
  return{left=c.x>915,right=c.x<912}
 end
 if f.phase=='rise'then
  if c.y<=112 then screwPhase('cross')end
  assert(updates-f.entered<100,'Earned High Jump reaches the actual Screw carrier')
  return{a=true}
 end
 if f.phase=='cross'then
  if grounded and c.y>=160 then screwPhase('mount');return{}end
  return{right=c.x<942,left=c.x>948,a=r('RdVY')>=128}
 end
 if f.phase=='use'then
  assert(r('RdGear')==15 and r('RdTanks')==1 and r('RdMissiles')==5,'Naturally earned Screw and resources')
  if r('RdAction')==3 then return{up=true}end
  if not f.baseline then f.baseline=state()end
  assert(r('RdHealthLo')==f.baseline.health_raw[1]and r('RdHealthHi')==f.baseline.health_raw[2],
         'Captured health protected through actual Screw encounter')
  if f.hit then
   if grounded then
    f.landing=f.landing or{player=state(),entered=screwCounts('_entered'),returned=screwCounts('_returned')}
    local er,rr=screwCounts('_entered'),screwCounts('_returned');local enough=true
    f.postlanding_returned={}
    for n,v in pairs(er)do
     f.postlanding_returned[n]=rr[n]-f.landing.returned[n]
     if v-f.landing.entered[n]<25 or f.postlanding_returned[n]<25 then enough=false end
    end
    if enough then
     assert(f.admitted and f.groundRejected and #pending==0 and(not f.bomb or r('RdWAction',f.bomb.slot)==0),
            'Original spin admission, grounded refusal and completed workers')
     f.complete=true;finish('natural-Screw-body-defeat-and-landing');return{}
    end
    return{}
   end
   local b=gearTravel(c);b.b=false;return b
  end
  local e=c.enemy()
  if grounded and e and e.dx>8 and e.dx<=26 and math.abs(e.y-c.y)<32
     and (e.id==6 or e.id==0 or e.id==3) and r('RdHeld')&128==0 then
   f.takeoff=f.takeoff or{player=state(),target=actor(e.slot)}
   return{right=true,a=true}
  end
  local b=gearTravel(c);b.b=false
  if grounded and e and e.dx>26 and e.dx<80 and math.abs(e.y-c.y)<32 then b.a=false end
  assert(c.x<2000,'Find a real ordinary enemy after the earned Screw')
  return b
 end
 return{}
end
