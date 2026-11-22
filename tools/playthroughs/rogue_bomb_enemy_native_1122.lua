-- Continue from the earned Bomb and coin-block pass into the next 1-2 encounter.
local function bombEnemyDrive(c)
 local fight=gear.enemy
 assert(c.level==1 and c.areaType==2 and r('AreaAddrsLOffset')==fight.areaOffset
        and updates-fight.started<1100,'Bounded live Bomb encounter in ordinary 1-2')
 fight.farthest=math.max(fight.farthest or 0,c.x)
 if updates%24==0 then
  local nearest=c.enemy()
  if #fight.approach==14 then table.remove(fight.approach,1)end
  fight.approach[#fight.approach+1]={player=state(),enemy=nearest}
 end
 if fight.phase=='unmorph' then
  if r('RdAction')==3 then return {up=true}end
  fight.phase='travel'
 end
 if fight.phase=='travel' then
  local target=c.enemy()
  if target and target.id==6 and target.state<2 and target.slot<5
     and target.dx>=24 and target.dx<=43 and math.abs(target.y-(c.y+7))<=6 and bombReady(c) then
   fight.target={actor=actor(target.slot),player=state()}
   fight.phase='morph'
  elseif c.x>=415 and c.x<446 and c.y<145 then
   fight.phase='pocket-top'
  else
   local b=gearTravel(setmetatable({area=fight.areaOffset},{__index=c}))
   if c.x>=350 then b.b=false end
   assert(c.x<512,'Passed the next authored Goomba pocket without a ground placement')
   return b
  end
 end
 if fight.phase=='pocket-top' then
  -- Land on the left lip before morphing, without the usual next travel jump.
  if c.x>=432 and c.x<=436 and c.y>=120 and c.y<=138 and bombReady(c) then
   fight.phase='pocket-morph'
  else
   return {right=c.x<432,left=c.x>436}
  end
 end
 if fight.phase=='pocket-morph' then
  if r('RdAction')~=3 then return {down=true}end
  fight.phase='pocket-roll'
 end
 if fight.phase=='pocket-roll' then
  local target=c.enemy()
  if c.x>=448 and c.y>=176 and target and target.id==6 and target.slot<5
     and target.x>=448 and target.x<496 then
   fight.target={actor=actor(target.slot),player=state()}
   fight.phase='morph'
  else
   return {right=c.x<457,left=c.x>462}
  end
 end
 if fight.phase=='morph' then
  if r('RdAction')~=3 then return {down=true}end
  if r('RdHeld')&64~=0 then return {}end
  fight.phase='place';fight.request=state()
  return {b=true}
 end
 if fight.phase=='place' then
  if not fight.bomb then
   assert(updates-fight.request.Main<16,'Fresh B allocates the earned terrain Bomb')
   return {b=true}
  end
  fight.phase='retreat'
 end
 if fight.expiry then
  assert(fight.hit,'Bomb exploded without an admitted Goomba damage event')
  local er,rr=snapshot('_entered'),snapshot('_returned')
  for name,value in pairs(er)do
   if value-fight.expiry.entered[name]<25 or rr[name]-fight.expiry.returned[name]<25 then
    return {}
   end
  end
  assert(#pending==0 and r('RdGear')==1 and r('RdTanks')==1 and r('RdMissiles')==5,
         'Earned gear and live stage survive the Bomb and 25 more updates')
  fight.postexpiry_returned={}
  for name,value in pairs(rr)do fight.postexpiry_returned[name]=value-fight.expiry.returned[name]end
  fight.complete=true;finish('natural-Bomb-damages-Goomba');return {}
 end
 local leftGoal=fight.request.x-36
 if c.x>leftGoal then
  local behind=c.block(c.x-2,c.y+16)
  if behind~=0 and behind<0xc0 and updates-fight.request.Main>12 then
   if r('RdAction')==3 then return {up=true}end
   return {left=true,a=true}
  end
  return {left=true}
 end
 return {}
end
