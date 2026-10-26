-- Real MarioEasy mushroom -> later authored flower -> native fireball contact.
local C=assert(MARIO_FLOWER_CONFIG)
local wall,entered,finished=0,false,false
local revealed,collected=0,0
local updates,freezePos={0,0},{}
local revealRequests,pickupRequests,fireRequests,shots,contacts=0,0,0,0,0
local enemyContacts=0
local log=assert(io.open(ROSTER_CONFIG.out..'flower-owner.jsonl','w'))
local trace=assert(io.open(ROSTER_CONFIG.out..'flower-state.csv','w'))
trace:write('frame,phase,x,y,power,size,engine,growing,age,revealed,collected,shot0,shot1,actors\n')
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function pos()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function json(v)
 if type(v)=='table'then local t={};for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..json(x)end;table.sort(t);return'{'..table.concat(t,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif type(v)=='boolean'then return tostring(v)else return tostring(v)end
end
local function event(k,z)
 z.kind=k;z.frame=wall;z.x=pos();z.y=r('Player_Y_Position');log:write(json(z)..'\n');log:flush()
end
local function active()return r('OperMode')==1 and r('OperMode_Task')==3 and r('SelectedCharacter')==C.character end
local function hook(n,fn)
 local h=assert(C.hooks[n]);emu.addMemoryCallback(function()
  if not active()then return end
  local p=emu.convertAddress(h.address);if not p or p.address//8192~=h.bank then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Actual source owner '..n)end
  fn(emu.getState())
 end,emu.callbackType.exec,h.address)
end
hook('PwrUpJmp',function(s)
 local x=s['cpu.x'];local wx=r('Enemy_X_Position',x)+256*r('Enemy_PageLoc',x)
 if wx~=336 and wx~=1248 then event('other-real-delivery',{slot=x,worldX=wx,type=r('PowerUpType',x)});return end
 assert(x==5 and r('Enemy_ID',x)==0x2e,'Actual authored powerup delivery slot')
 local next=revealed+1;assert(next<=2 and wx==C.blocks[next],'Real first and later powerup block order')
 assert(r('PlayerStatus')==next-1,'Retained unpowered/Super state at physical block reveal')
 revealed=next;event('real-block-reveal',{itemIndex=next,blockX=wx,initialType=r('PowerUpType',x),playerPower=r('PlayerStatus')})
end)
hook('MarioSourcePowerupCollision',function(s)
 local x=s['cpu.x'];local kind=r('PowerUpType',x)
 if kind>=2 then event('other-real-native-pickup',{type=kind,slot=x});return end
 local next=collected+1;assert(next<=2 and revealed==next,'Native pickup follows its actual block delivery')
 assert(r('Enemy_ID',x)==0x2e and r('Enemy_Flag',x)>0 and r('Enemy_State',x)>=128,'Fully emerged real reward')
 assert(kind==next-1 and r('PlayerStatus')==next-1,'Physical mushroom then retained-Super flower')
 if next==2 then assert(r('Enemy_X_Position',x)+256*r('Enemy_PageLoc',x)==1248,'Genuine later stationary flower')end
 collected=next;event('real-native-collection',{itemIndex=next,type=kind,slot=x,playerPower=r('PlayerStatus')})
end)
hook(C.growthOwner,function()
 if not entered or collected==0 or r('GuestPowerupActive')==0 then return end
 assert(r('GuestLegacyHurt')==0,'Retain power; no injury masquerading as progression')
 local n=collected;updates[n]=updates[n]+1
 assert(r('GuestPowerupAge')==updates[n]-1 and updates[n]<=60,'Actual sequential source transform')
 assert(r('GuestPowerupTarget')==n,'Original Easy source target tier')
 local p={x=pos(),y=r('Player_Y_Position')}
 if freezePos[n]then assert(p.x==freezePos[n].x and p.y==freezePos[n].y,'Source transform holds position')else freezePos[n]=p end
end)
local function shotActive()
 local i=r('ObjectOffset');return i<2 and r('Fireball_State',i)>0 and r('Fireball_State',i)<128
end
hook('MarioSourceFireballBrick',function(s)
 if collected<2 or r('PlayerStatus')~=2 or not shotActive()then return end
 local t=s['cpu.a'];local brick=t==0x22 or t==0x51 or t==0x52 or t==0x88 or t>=0x55 and t<0x5f
 if brick then contacts=contacts+1;event('actual-fireball-brick-contact',{tile=t,slot=r('ObjectOffset'),shotX=r('Fireball_X_Position',r('ObjectOffset'))+256*r('Fireball_PageLoc',r('ObjectOffset')),shotY=r('Fireball_Y_Position',r('ObjectOffset'))})end
end)
hook('HandleEnemyFBallCol',function(s)
 if collected<2 or r('PlayerStatus')~=2 then return end
 local x=s['cpu.x'];local id=r('Enemy_ID',x)
 if x<6 and(id==0 or id==1 or id==6)and r('Enemy_Flag',x)>0 then
  contacts=contacts+1;enemyContacts=enemyContacts+1;event('actual-fireball-enemy-contact',{enemySlot=x,enemyID=id,state=r('Enemy_State',x)})
 end
end)
emu.addMemoryCallback(function(_,v)
 if not active()then return end
 if v&C.sfx.reveal~=0 then revealRequests=revealRequests+1 end
 if v&C.sfx.pickup~=0 then pickupRequests=pickupRequests+1 end
end,emu.callbackType.write,C.ram.Square2SoundQueue)
emu.addMemoryCallback(function(_,v)
 if active()and collected==2 and r('PlayerStatus')==2 and v&C.sfx.fire~=0 then fireRequests=fireRequests+1 end
end,emu.callbackType.write,C.ram.Square1SoundQueue)
emu.addMemoryCallback(function(at,v)
 if active()and collected==2 and r('PlayerStatus')==2 and v==2 then shots=shots+1;event('actual-fireball-allocation',{slot=at-C.ram.Fireball_State})end
end,emu.callbackType.write,C.ram.Fireball_State,C.ram.Fireball_State+1)
local phase,age,mount='first-travel',0,'back'
local function aim(c,target)
 local v=c.vx>=128 and c.vx-256 or c.vx
 if c.x>target+4 then return{left=true}elseif c.x<target-4 then return{right=true}
 elseif v>1 then return{left=true}elseif v< -1 then return{right=true}else return{}end
end
local function actor(c)
 for i=0,5 do if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e and c.r('PowerUpType',i)<2 then return c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)end end
end
-- Right-side controller only. Both earlier failed native attempts stay frozen.
local rightPhase,rightAge,arcAge,quiet,escapeX='align',0,0,0,1312
local function precise(c,target)
 local v=c.vx>=128 and c.vx-256 or c.vx
 if c.x<target-2 then return{right=true}elseif c.x>target+2 then return{left=true}
 elseif v>0 then return{left=true}elseif v<0 then return{right=true}else return{}end
end
function MARIO_FLOWER_RIGHT_CONTROL(c)
 rightAge=rightAge+1;assert(rightAge<=360,'Bounded right-side alignment, wait and retreat')
 local nearest=c.enemy();local owners={};local clear=true;local danger=false
 if nearest then
  local i=nearest.slot
  assert(i%1==0 and i>=0 and i<6,'Actual bounded nearest-enemy slot')
  assert(c.r('Enemy_Flag',i)>0 and c.r('Enemy_Flag',i)<128 and nearest.id==c.r('Enemy_ID',i)and nearest.state==c.r('Enemy_State',i),'Actual nearest-enemy owner')
  assert(nearest.x==c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)and nearest.y==c.r('Enemy_Y_Position',i)and nearest.dx==nearest.x-c.x,'Actual nearest-enemy position')
  assert(nearest.state<0x20 and(nearest.id<0x15 or nearest.id==0x2d or nearest.id==0x33)and not(nearest.id==6 and nearest.state>=2),'Actual nearest-enemy filter')
 end
 local flowerReady=false
 for i=0,5 do
  local flag,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
  if flag>0 and flag<128 then
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   local y,h=c.r('Enemy_Y_Position',i),c.r('Enemy_Y_HighPos',i)
   if id==0x2e and x==1248 and c.r('PowerUpType',i)==1 and st>=128 then flowerReady=true end
   if st<0x20 and not(id==6 and st>=2)and(id<0x15 or id==0x2d or id==0x33)and h==1 then
    if x>=1208 and x<=1320 and y>=64 and y<=208 then
     owners[#owners+1]=table.concat({i,id,flag,st,x,y,h},':')
     if id~=6 or x>1236 then clear=false end
    end
    -- Escape only a genuine nearby body behind us; a new actor ahead fails
    -- closed instead of requesting inputs toward an unproved hazard.
    if id==6 and x+13>=c.x-8 and x+3<=c.x+22 and y+20>=c.y+4 and y+14<=c.y+36 then
     assert(x<c.x,'Unexpected right-side body threat ahead')
     danger=true
    end
   end
  end
 end
 if rightAge==1 or rightAge%16==0 then event('right-side-owner-gate',{phase=rightPhase,owners=table.concat(owners,';'),clear=clear,flowerReady=flowerReady})end
 if rightPhase=='arc'then
  arcAge=arcAge+1;assert(arcAge<180,'Bounded guided right-side jump')
  assert(not(c.grounded and arcAge>2 and c.y>128),'Right-side physical mount fell short')
  local b=aim(c,1248);b.a=arcAge<32;b.b=true;return b
 end
 if danger then
  rightPhase='escape';quiet=0;escapeX=math.min(1320,math.max(1312,c.x+24))
  event('right-side-physical-retreat',{target=escapeX,owners=table.concat(owners,';')})
 end
 if rightPhase=='escape'then
  if c.x>=escapeX-2 and c.grounded and c.vx==0 then rightPhase='align'else
   local b=precise(c,escapeX);b.b=true;return b
  end
 end
 if c.grounded and c.y==176 and c.x>=1288 and c.x<=1292 and c.vx==0 then
  quiet=quiet+1
  -- Neutral settles the visible speed; Luigi may retain native fractional speed.
  if quiet>=2 and clear and flowerReady and not c.lastA then
   rightPhase='arc';arcAge=0
   event('right-side-real-launch',{owners=table.concat(owners,';'),flowerReady=flowerReady})
   return{a=true,left=true,b=true}
  end
  return{}
 end
 quiet=0;local b=precise(c,1290)
 if b.right and c.x<1276 then b.b=true end
 return b
end
function MARIO_FLOWER_CONTROL(c,base)
 if collected==0 then
  if phase=='first-travel'then if c.x<404 then return base(c)end;phase='first-drop';age=0 end
  age=age+1;assert(age<1500,'Bounded first physical mushroom pursuit')
  if phase=='first-drop'then if c.grounded and c.y>=160 then phase='first-under'end;return aim(c,420)
  elseif phase=='first-under'then
   if c.grounded and c.x>=328 and c.x<=343 and c.vx==0 then phase='first-bump';age=0;return{a=true}end
   return aim(c,336)
  elseif phase=='first-bump'then
   if actor(c)then phase='first-chase';age=0;return{}end
   if c.grounded and age>45 then age=0 end;return{a=age<24}
  else local x=actor(c);assert(x,'Real mushroom remains active before collection');return aim(c,math.min(430,math.max(328,x)))end
 end
 if r('GuestPowerupActive')~=0 then return{}end
 assert(c.status==collected,'Retain actual acquired tier through the named component')
 if collected==1 then
  if phase:sub(1,5)=='first'then phase='flower-travel';age=0 end
  age=age+1;assert(age<3500,'Bounded physical later flower pursuit')
  if phase=='flower-travel'then
   if c.x<1190 then return base(c)end
   phase='flower-under';age=0
  end
  if phase=='flower-under'then
   if c.y<=128 then phase='flower-drop';return{right=true}end
   if c.grounded and c.x>=1244 and c.x<=1252 and c.vx==0 then phase='flower-bump';age=0;return{a=true}end
   return aim(c,1248)
  elseif phase=='flower-drop'then
   if c.grounded and c.y>=160 then phase='flower-under'end
   return{right=c.x<1296,left=c.x>1300}
  elseif phase=='flower-bump'then
   if revealed==2 then phase='flower-mount';mount='back';age=0;return{}end
   if c.grounded and age>45 then age=0 end;return{a=age<24}
  else
   assert(actor(c),'Real flower stays in the world before collection')
   return MARIO_FLOWER_RIGHT_CONTROL(c)
  end
 end
 if phase:sub(1,6)=='flower'then phase='fire-aim';age=0 end
 age=age+1;assert(age<500,'Bounded actual fireball use and release')
 if phase=='fire-aim'then
  if c.grounded and math.abs(c.x-1244)<=4 and c.vx==0 then
   if c.r('PlayerFacingDir')~=2 then return{left=true}end
   phase='fire';age=0;return{}
  end
  return aim(c,1244)
 elseif phase=='fire'then
  if enemyContacts>0 then phase='drain';age=0;return{}end
  local b=base(c);b.b=age%16<4;return b
 else
  if age>=45 and r('Fireball_State')==0 and r('Fireball_State',1)==0 then MARIO_FLOWER_DONE=true end
  return{}
 end
end
emu.addEventCallback(function()
 wall=wall+1;if finished or not active()then return end
 if not entered and r('GameEngineSubroutine')~=8 then return end
 if not entered then
  entered=true;assert(r('CrossoverBehaviorVersion')==0 and r('MarioVariant')==C.variant,'Real cold selected LuigiEasy')
  assert(r('PlayerStatus')==0,'Cold unpowered source start')
 end
 local actors={};for i=0,5 do if r('Enemy_Flag',i)>0 and r('Enemy_ID',i)==0x2e then actors[#actors+1]=table.concat({i,r('Enemy_State',i),r('PowerUpType',i),r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),r('Enemy_Y_Position',i)},':')end end
 trace:write(table.concat({wall,phase,pos(),r('Player_Y_Position'),r('PlayerStatus'),r('PlayerSize'),r('GameEngineSubroutine'),r('GuestPowerupActive'),r('GuestPowerupAge'),revealed,collected,r('Fireball_State'),r('Fireball_State',1),table.concat(actors,';')},',')..'\n')
 if r('GuestPowerupActive')~=0 then local f=assert(io.open(ROSTER_CONFIG.out..'growth-'..collected..'-'..wall..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
end,emu.eventType.endFrame)
function MARIO_FLOWER_FINISH()
 if finished then return end;finished=true
 local ok=MARIO_FLOWER_DONE==true
 if ok then
  assert(enemyContacts>0,'Actual live Goomba/Koopa fireball contact before release')
  assert(revealed==2 and collected==2 and updates[1]==60 and updates[2]==60,'Actual two physical tiers and source transforms')
  assert(shots>0 and contacts>0 and fireRequests>0,'Actual B allocation, source target contact and fire request')
  assert(revealRequests>0 and pickupRequests>0 and r('PlayerStatus')==2,'Actual pickup cues and retained Fire')
 end
 local f=assert(io.open(ROSTER_CONFIG.out..'flower-component.json','w'));f:write(json({passed=ok,native_executed=true,ROM_sha256=C.ROM_sha256,actual_mode=r('CrossoverBehaviorVersion'),character=C.character,variant=r('MarioVariant'),reveals=revealed,collections=collected,first_transform_updates=updates[1],second_transform_updates=updates[2],shots=shots,target_contacts=contacts,enemy_contacts=enemyContacts,fire_request_stores=fireRequests,reveal_request_stores=revealRequests,pickup_request_stores=pickupRequests,final_power=r('PlayerStatus'),no_fixture_game_state_writes=true,scope='One genuine LuigiEasy mushroom then later flower and actual fireball enemy/brick contact; no fullroute/Hard/sourcewaveform/allitems claim'})..'\n');f:close();trace:close();log:close()
end
