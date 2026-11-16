-- Ordinary post-MF progression to the observed actual1-2 C1 block160/144.
local function bombShot(i)return {slot=i,action=r('RdWAction',i),x=r('RdWX',i)+256*r('RdWHi',i),y=r('RdWY',i),age=r('RdWAge',i),frame=r('RdWFrame',i)}end
local function bombEvent(name)
 assert(#gear.events<16,'Bounded Bomb phase witnesses')
 gear.events[#gear.events+1]={name=name,player=state(),phase=gear.phase,held=r('RdHeld'),fresh=r('RdFresh')}
end
local function bombReady(c)
 local a,v,g=r('RdAction'),r('RdVY'),r('RdGravity')
 return c.grounded and(a==0 or a==4 or(a==1 and v<128 and g==0))
end
local function bombDrive()
 local c=context();assert(identity()and r('NumberofLives')==2 and r('RdHealthLo')+r('RdHealthHi')>0,'Genuine earned progression alive')
 assert(r('RdTanks')==1 and r('RdMissiles')==5 and r('RdMaxMissiles')==5,'Tank/missiles preserved before Bomb')
 if r('WorldNumber')==0 and r('LevelNumber')==0 then return gearTravel(c)end
 assert(r('WorldNumber')==0 and r('LevelNumber')==1,'Ordinary1-1 to1-2 only')
 if not active()then return{}end
 if gear.phase=='travel'then
  if not(c.yHigh==1 and bombReady(c)and c.y>=176)then return{}end
  assert(r('AreaPointer')==192 and c.block(160,144)==0xc1,'Actual parsed1-2 authored power block160/144')
  gear.cache={area=r('AreaPointer'),x=160,y=144,tile=c.block(160,144),near={}}
  for x=96,208,16 do gear.cache.near[#gear.cache.near+1]={x=x,y144=c.block(x,144),y160=c.block(x,160),y192=c.block(x,192)}end
  gear.phase='align';bombEvent('actual-authored-block')
 end
 if stock=='bomb-credit'then return{}end
 if gear.phase=='morph'then
  if r('RdAction')==3 then gear.morph=state();gear.phase='release';bombEvent('real-morph');return{}end
  return{down=true}
 elseif gear.phase=='release'then
  if(r('RdHeld')&64)~=0 then return{}end
  for _,i in ipairs({0xd0,0xe0,0xf0})do if r('RdWAction',i)~=0 then return{}end end
  gear.phase='request';gear.request=state();bombEvent('fresh-B-request');return{b=true}
 elseif gear.phase=='request'then
  assert(updates-gear.request.Main<12,'Actual fresh Bomb admission')
  if gear.bomb then gear.phase='fuse';return{}end
  return{b=true}
 elseif gear.phase=='fuse'then
  if gear.expiry then
   local er,rr=snapshot('_entered'),snapshot('_returned');local enough=true
   for n,v in pairs(er)do if v-gear.expiry.entered[n]<25 or rr[n]-gear.expiry.returned[n]<25 then enough=false end end
   if enough then
    assert(#pending==0 and gear.bomb and gear.states[8]and gear.states[9]and gear.states[10]and gear.states[0]and gear.place_request and gear.explode_request,'Actual Bomb fuse/explosion/removal/requests')
    for i=1,5 do assert(gear.terrain[i],'Actual original Bomb terrain phase '..i)end
    gear.postexpiry_entered={};gear.postexpiry_returned={}
    for n,v in pairs(er)do gear.postexpiry_entered[n]=v-gear.expiry.entered[n];gear.postexpiry_returned[n]=rr[n]-gear.expiry.returned[n]end
    gear.complete=true;finish('natural-Bomb-and-lifecycle25');return{}
   end
  end
  assert(updates-gear.request.Main<180,'Bounded natural Bomb lifecycle');return{}
 end
 if born and gear.phase~='mount-back'and gear.phase~='mount-rise'and gear.phase~='mount-cross'then gear.phase='mount-back';gear.hold=0;bombEvent('real-D0-birth-mount')end
 if gear.phase=='align'then
  if c.x>=160 and c.x<=162 and c.y>=176 and bombReady(c)and(r('RdHeld')&128)==0 then gear.phase='bump';gear.hold=48;bombEvent('ordinary-block-bump')end
  return{right=c.x<160,left=c.x>162,b=updates%7<3}
 elseif gear.phase=='bump'then
  gear.hold=math.max(gear.hold-1,0)
  if gear.hold==0 and bombReady(c)and(r('RdHeld')&128)==0 then gear.hold=48 end
  return{right=c.x<160,left=c.x>162,a=gear.hold>0 or r('RdVY')>=128,b=updates%7<3}
 elseif gear.phase=='mount-back'then
  if c.x>=107 and c.x<=109 and c.y>=176 and bombReady(c)and(r('RdHeld')&128)==0 then gear.phase='mount-rise';gear.hold=48;bombEvent('ordinary-clear-head-takeoff');return{a=true,b=updates%7<3}end
  return{right=c.x<107,left=c.x>109,b=updates%7<3}
 elseif gear.phase=='mount-rise'then
  if c.y<=112 and c.yHigh==1 then gear.phase='mount-cross';bombEvent('actual-height-before-cross')end
  gear.hold=math.max(gear.hold-1,0);return{a=gear.hold>0 or r('RdVY')>=128,b=updates%7<3}
 elseif gear.phase=='mount-cross'then
  if c.y>=176 and bombReady(c)then gear.phase='mount-back';gear.hold=0 end
  return{right=c.x<156,left=c.x>164,a=r('RdVY')>=128,b=updates%7<3}
 end
 return{}
end
local function bombReturned(n,p)
 if not gear.started then return end
 if n=='RdBombAllocate'then
  for _,i in ipairs({0xd0,0xe0,0xf0})do
   if r('RdWAction',i)==8 and p.bombs[i]==0 then
    assert(not gear.bomb and r('RdGear')==1 and r('RdAction')==3,'Single genuinely earned Bomb allocation')
    gear.slot=i;gear.bomb={before=p.before,after=state(),shot=bombShot(i),held=r('RdHeld'),fresh=r('RdFresh')};gear.states[8]=true
   end
  end
 elseif(n=='RdBombStepBegin'or n=='RdBombStepFinish')and gear.bomb and p.weapon_slot==gear.slot then
  local a=r('RdWAction',gear.slot);gear.states[a]=true
  if a==0 and not gear.expiry then gear.expiry={player=state(),shot=bombShot(gear.slot),entered=snapshot('_entered'),returned=snapshot('_returned')}end
 end
end
