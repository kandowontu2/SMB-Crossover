-- Land and rearm on the actual bank before committing to the two short pits.
screwPairedGap=function(c,wall,grounded)
 wall.pairedApproach=wall.pairedApproach or{started=updates,tail={}}
 local p=wall.pairedApproach
 if updates%8==0 then
  if #p.tail==12 then table.remove(p.tail,1)end
  p.tail[#p.tail+1]={phase=wall.pairedPhase or'land-bank',player=state()}
 end
 local function aim(low,high)return{left=c.x>high,right=c.x<low}end
 local released=r('RdHeld')&128==0
 if not wall.pairedSetup then
  local b=aim(1880,1883)
  if not b.left and not b.right and grounded and c.y>=175 and c.y<=177 and released then
   wall.pairedSetup=state();wall.pairedPhase='run-bank'
  else
   assert(updates-p.started<220,'Actually land on the safe left bank before the paired pits')
   return b
  end
 end
 assert(updates-wall.pairedSetup.Main<500,'Bounded two genuine bank-to-bank jumps')
 if wall.pairedPhase=='run-bank'then
  if c.x<1907 then return{right=true}end
  if not grounded or not released then return aim(1906,1909)end
  assert(c.y>=175 and c.y<=177 and c.x<=1911,'Fresh A request while the real left bank still supports the player')
  wall.islandRequest=state();wall.pairedPhase='launch-island'
  return{right=true,a=true}
 end
 if wall.pairedPhase=='launch-island'then
  if not grounded and r('RdVY')>=128 and c.y<wall.islandRequest.y then
   wall.islandTakeoff=state();wall.pairedPhase='fly-island'
  else
   assert(updates-wall.islandRequest.Main<12,'Observe actual negative-VY island launch before committing across')
   if updates-wall.islandRequest.Main>=2 and not released then return aim(1906,1909)end
   return{right=true,a=true}
  end
 end
 if wall.pairedPhase=='fly-island'then
  if grounded and c.x>=1952 and c.x<1980 and c.y<=132 then
   wall.islandLanding=state();wall.pairedPhase='release-island';return{}
  end
  local b=aim(1958,1961);b.a=r('RdVY')>=128;return b
 end
 if wall.pairedPhase=='release-island'then
  local b=aim(1958,1961)
  if b.left or b.right or not grounded or not released then return b end
  wall.bankRequest=state();wall.pairedPhase='launch-bank';return{right=true,a=true}
 end
 if wall.pairedPhase=='launch-bank'then
  if not grounded and r('RdVY')>=128 and c.y<wall.bankRequest.y then
   wall.bankTakeoff=state();wall.pairedPhase='fly-bank'
  else
   assert(updates-wall.bankRequest.Main<12,'Observe actual negative-VY far-bank launch')
   if updates-wall.bankRequest.Main>=2 and not released then return aim(1958,1961)end
   return{right=true,a=true}
  end
 end
 if wall.pairedPhase=='fly-bank'then
  if c.x>=2016 then wall.pairedGaps=state();wall.pairedPhase='complete';return{right=true}end
  return{right=true,a=r('RdVY')>=128}
 end
 return{right=true}
end

screwLift=function(c,wall,grounded)
 local function aim(low,high)return{left=c.x>high,right=c.x<low}end
 local released=r('RdHeld')&128==0
 local lift=wall.liftTarget and actor(wall.liftTarget.slot)or nil
 wall.liftTrace=wall.liftTrace or{}
 if updates%2==0 then
  if #wall.liftTrace==28 then table.remove(wall.liftTrace,1)end
  wall.liftTrace[#wall.liftTrace+1]={phase=wall.liftPhase or'settle',player=state(),lift=lift}
 end
 if not wall.liftTakeoff then
  local b=aim(2196,2199)
  if wall.liftPhase=='request'or wall.liftPhase=='armed'then
   local p=wall.liftRequest
   if not grounded and not released and r('RdVY')>=128 and not p.armed then
    p.armed=state();wall.liftArmed=p.armed;wall.liftPhase='armed'
   end
   if p.armed and not grounded and not released and r('RdVY')>=128 and c.y<p.player.y then
    wall.liftTakeoff=state();wall.liftPhase='fly'
   elseif updates-p.player.Main>=10 or(not p.armed and not released and updates-p.player.Main>=2)then
    wall.liftPhase='release';return b
   else
    assert(c.x<=2205 and(grounded or p.armed),'Lift request stays on the staircase or in its genuinely armed launch')
    return{right=c.x<2203,a=true}
   end
  else
   if b.left or b.right or not grounded or not released or r('RdAction')~=0 then return b end
   assert(c.y<=115,'Settle on the real staircase before requesting the lift jump')
   lift=descendingLift()
   if not lift then wall.liftPhase='wait';return{}end
   wall.liftAttempts=wall.liftAttempts or{}
   assert(#wall.liftAttempts<8,'Bounded genuine lift launch attempts')
   wall.liftTarget=lift
   wall.liftRequest={player=state(),lift=lift}
   wall.liftAttempts[#wall.liftAttempts+1]=wall.liftRequest
   wall.liftPhase='request';return{right=true,a=true}
  end
 end
 lift=actor(wall.liftTarget.slot)
 if not wall.liftLanding then
  if not wall.liftApex or c.y<wall.liftApex.y then wall.liftApex=state()end
  if c.x>=2240 and c.x<=2276 and grounded and r('RdFrozenSupport')~=0
     and lift.id==0x27 and lift.flag>0 and math.abs(c.y+32-lift.y)<=1 then
   wall.liftLanding=state();wall.liftPhase='landed';return{}
  end
  local inRange=c.x>=2252 and c.x<=2255
  return{left=c.x>2255,right=c.x<2252,a=not inRange and r('RdVY')>=128}
 end
 if not wall.liftExit then
  if wall.liftExitRequest then
   if not grounded and not released and r('RdVY')>=128 and c.y<wall.liftExitRequest.y then
    wall.liftExit=state();wall.liftPhase='exit-flight'
   else
    assert(updates-wall.liftExitRequest.Main<10 and c.x<=2277,
           'Confirm negative-VY launch while the native lift still supports the player')
    if not released and updates-wall.liftExitRequest.Main>=2 then return aim(2262,2265)end
    return{right=c.x<2270,a=true}
   end
  else
   if grounded and c.x>=2262 and released then
    wall.liftExitRequest=state();wall.liftPhase='exit-request';return{right=true,a=true}
   end
   return{right=true}
  end
 end
 if c.x<2320 then return{right=true,a=r('RdVY')>=128}end
 wall.crossedLiftGap=state();wall.liftPhase='complete'
end

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
  if c.x>=2580 then
   f.exit=f.exit or{phase='back',started=updates,farthest=c.x,lastProgress=updates}
   if c.x>f.exit.farthest then f.exit.farthest=c.x;f.exit.lastProgress=updates end
   if not f.exit.tiles then
    f.exit.tiles={}
    for y=96,192,16 do local row={y=y,tiles={}}
     for x=2640,2720,16 do row.tiles[#row.tiles+1]=c.block(x,y)end
     f.exit.tiles[#f.exit.tiles+1]=row
    end
   end
   -- The retained opening route drops to this mouth before holding Right.
   -- The later generic travel wrapper omitted that exit-specific policy.
   if f.exit.phase=='back'then
    local target=math.max(2616,c.camera+1)
    assert(updates-f.exit.started<300,'Drop below the upper path before the ordinary side entrance')
    if c.x>=target and c.x<=target+3 and grounded and c.y>=128 then
     f.exit.phase='enter';f.exit.landing=state();f.exit.lastProgress=updates
    end
    return{right=c.x<target,left=c.x>target+3}
   end
   assert(updates-f.exit.lastProgress<160,'Bounded normal-input side-pipe approach; retain exact obstruction')
   return{right=true}
  end
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
   if r('RdAction')~=1 or r('RdHeld')&3~=1 then return{right=true}end
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
