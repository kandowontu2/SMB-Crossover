-- Real menu/input, legal staged pickup/shot actors, production dispatch only.
local C=assert(MAC_TMNT_NATIVE_CONFIG)
for n,a in pairs(C.ram)do L[n]=a end
local wall,index,age,nmis=0,0,0,0
local entered,done=false,false
local current=nil
local results,violations={},{}
local minSP,stackWrites=255,0
local phase='menu'
local r=function(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local w=function(n,v,i)emu.write(assert(L[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
local function json(v)
 if type(v)=='table'then local o={};if #v>0 then for _,x in ipairs(v)do o[#o+1]=json(x)end;return'['..table.concat(o,',')..']'end
  for k,x in pairs(v)do o[#o+1]=string.format('%q',k)..':'..json(x)end;return'{'..table.concat(o,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)else return tostring(v)end
end
local function native()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function world()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function bank(a)local p=emu.convertAddress(a);return p and p.address//8192 or -1 end
local function valid(n)return bank(C.hooks[n].address)==C.hooks[n].physical_bank end
local function bind(n)local h=C.hooks[n];for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Bound '..n)end end
local function capture(name)
 local f=assert(io.open(OUTPUT..name..'.argb','wb'));for _,v in ipairs(emu.getScreenBuffer())do f:write(string.pack('<I4',v))end;f:close()
end
local function problem(message,data,known)
 local st=emu.getState();local q={wall=wall,case=index,age=age,phase=phase,message=message,data=data,pc=st['cpu.pc'],bank=bank(st['cpu.pc']),sp=st['cpu.sp']}
 violations[#violations+1]=q
 local f=assert(io.open(OUTPUT..'violations.json','w'));f:write(json(violations));f:close()
 capture('failure-'..index..'-'..age..'-'..#violations)
 if C.diagnostic~=1 or not known then assert(false,message)end
end
local log=assert(io.open(OUTPUT..'updates.csv','w'));log:write('wall,case,age,phase,playerY,state,lives,marker,hp,equipment,ammo\n')
local writes=assert(io.open(OUTPUT..'first-writes.csv','w'));writes:write('wall,case,age,phase,pc,bank,address,old,new\n')
local returns,installed={},{}
local function onReturn(name,fn)
 local st=emu.getState();local sp=st['cpu.sp'];minSP=math.min(minSP,sp)
 local ret=(emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 local key=name..':'..ret
 returns[key]={sp=(sp+2)%256,bank=bank(ret),fn=fn}
 if not installed[key]then installed[key]=true;emu.addMemoryCallback(function()
  local q=returns[key];if not q or emu.getState()['cpu.sp']~=q.sp or bank(ret)~=q.bank then return end
  returns[key]=nil;q.fn()
 end,emu.callbackType.exec,ret)end
end
local savedNmi=nil
local nmiWindows={}
local function storeAt(pc,target)
 return emu.read(pc,emu.memType.nesDebug)==0x8d and emu.read(pc+1,emu.memType.nesDebug)==target%256 and emu.read(pc+2,emu.memType.nesDebug)==target//256
end
local function bankWindow(pc,target,shadow)
 if storeAt(pc,target)then
  return storeAt(pc-3,shadow)or(emu.read(pc-2,emu.memType.nesDebug)==0xa9 and storeAt(pc-5,shadow))
 end
 return emu.read(pc,emu.memType.nesDebug)==0xa9 and storeAt(pc+2,target)and storeAt(pc-3,shadow)
end
emu.addMemoryCallback(function(address,value)
 if entered and not done then assert(false,'Native stack crosses the end of copied SMC code')end
end,emu.callbackType.write,C.stack_guard)
emu.addMemoryCallback(function()
 if not entered then return end
 bind('NonMaskableInterrupt')
 savedNmi={a=bank(0xa000),c=bank(0xc000),fields={},sp=emu.getState()['cpu.sp']}
 savedNmi.cpu_a=emu.getState()['cpu.a']
 savedNmi.shadow_a=r('CurrentBank')&127;savedNmi.shadow_c=r('CurrentBankC')&127
 local sp=savedNmi.sp
 savedNmi.resume=emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+3)%256,emu.memType.nesDebug)
 savedNmi.resume_bank=bank(savedNmi.resume);savedNmi.code={}
 for i=-8,8 do savedNmi.code[#savedNmi.code+1]=emu.read(savedNmi.resume+i,emu.memType.nesDebug)end
 savedNmi.a_window=savedNmi.a~=savedNmi.shadow_a and bankWindow(savedNmi.resume,0x5115,L.CurrentBank)
 savedNmi.c_window=savedNmi.c~=savedNmi.shadow_c and bankWindow(savedNmi.resume,0x5116,L.CurrentBankC)
 for _,a in ipairs(C.smc_fields)do savedNmi.fields[#savedNmi.fields+1]=emu.read(a,emu.memType.nesDebug)end
 nmis=nmis+1;minSP=math.min(minSP,savedNmi.sp)
end,emu.callbackType.exec,C.hooks.NonMaskableInterrupt.address)
emu.addMemoryCallback(function()
 if not savedNmi then return end
 local wantA=savedNmi.a_window and savedNmi.shadow_a or savedNmi.a
 local wantC=savedNmi.c_window and savedNmi.shadow_c or savedNmi.c
 if bank(0xa000)~=wantA or bank(0xc000)~=wantC then
  local q=savedNmi;q.after_a=bank(0xa000);q.after_c=bank(0xc000)
  problem('NMI restores foreground A/C banks',q)
 end
 assert((r('CurrentBank')&127)==savedNmi.shadow_a and(r('CurrentBankC')&127)==savedNmi.shadow_c,'NMI restores foreground bank shadows')
 assert(emu.getState()['cpu.a']==savedNmi.cpu_a,'NMI restores foreground A before resumed mapper store')
 if savedNmi.a_window or savedNmi.c_window then nmiWindows[#nmiWindows+1]={wall=wall,case=index,age=age,resume=savedNmi.resume,
  a=savedNmi.a,shadow_a=savedNmi.shadow_a,c=savedNmi.c,shadow_c=savedNmi.shadow_c,code=savedNmi.code}end
 for i,a in ipairs(C.smc_fields)do assert(emu.read(a,emu.memType.nesDebug)==savedNmi.fields[i],'NMI preserves five SMC operands')end
 assert(emu.getState()['cpu.sp']==savedNmi.sp,'NMI stack balanced before RTI');savedNmi=nil
end,emu.callbackType.exec,C.hooks.NmiReturn.address)


local snapshots,lifeAwards,ensureCalls,reveals,rises,collects={},{},0,0,0,0
local dma=nil
local function snap()
 local t={};for _,n in ipairs({'LmHealth','LmStars','LmHearts','LmAttack','LmSuper','LmWalk','LmPrevious','LmLife','NumberofLives'})do t[n]=r(n)end;return t
end
local function clearActors()
 for i=0,5 do
  for _,n in ipairs({'Enemy_Flag','EnemyMetasprite','Enemy_State','FloateyNum_Control','FloateyNum_Timer','TnPickupStamp','InvRisePhase'})do w(n,0,i)end
  w('InvPickup',252,i)
 end
 for i=0,3 do w('Block_State',0,i);w('BlockMetasprite',0,i);w('InvDropKind',0,i)end
 for i=0,8 do w('Misc_State',0,i);w('MiscMetasprite',0,i)end
end
local function anchor(x,y,air)
 w('Player_X_Position',x%256);w('Player_PageLoc',x//256);w('Player_Y_Position',y);w('Player_Y_HighPos',1)
 w('Player_State',air or 0);w('PlayerFacingDir',1);w('Player_MovingDir',1);w('PlayerSize',0);w('PlayerStatus',1);w('Player_CollisionBits',255)
 for _,n in ipairs({'CrouchingFlag','Player_X_Speed','Player_Y_Speed','Player_X_Scroll','Player_X_MoveForce','Player_Y_MoveForce'})do w(n,0)end
end
local function camera(x)
 w('ScreenLeft_X_Pos',x%256);w('ScreenLeft_PageLoc',x//256);w('ScreenRight_X_Pos',(x+255)%256);w('ScreenRight_PageLoc',(x+255)//256)
 w('ScrollLock',1);w('ScrollThirtyTwo',0);w('AreaParserTaskNum',0)
end
local function actor(slot,x,y,typ,state)
 w('Enemy_Flag',1,slot);w('Enemy_ID',C.power_id,slot);w('Enemy_State',state,slot);w('PowerUpType',typ,slot)
 w('Enemy_X_Position',x%256,slot);w('Enemy_PageLoc',x//256,slot);w('Enemy_Y_Position',y,slot);w('Enemy_Y_HighPos',1,slot);w('Enemy_BoundBoxCtrl',3,slot)
 for _,n in ipairs({'Enemy_X_Speed','Enemy_Y_Speed','Enemy_X_MoveForce','Enemy_Y_MoveForce','Enemy_SprAttrib'})do w(n,0,slot)end
 w('Enemy_MovingDir',1,slot)
end
local function common()
 clearActors()
 for _,n in ipairs({'GamePauseStatus','GamePauseTimer','TimerControl','InvPrevious','InvFresh','InvRefill','GuestHurtTicks','DisableCollisionDet','StarInvincibleTimer','PlayerChangeSizeFlag','BlockBounceTimer','CheatInvincible'})do w(n,0)end
 w('CrossoverBehaviorVersion',1)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
end
local function seed(q)
 current={name=q.name,kind=q.kind,checks=0,rises=0,contacts=0,frames=0};age=0
 if q.kind=='newgame'then assert(r('OperMode')==3 and r('NumberofLives')==255,'Canonical Game Over precedes new game');phase='newgame';return end
 common()
 if C.character==15 then
  camera(0);anchor(100,176,0)
  w('LmReady',77);w('LmLife',q.life);w('NumberofLives',q.life);w('LmArea',r('AreaPointer'));w('LmWorld',r('WorldNumber'))
  w('LmHealth',37);w('LmStars',3);w('LmHearts',9);w('LmAttack',24);w('LmSuper',1);w('LmWalk',17);w('LmPrevious',0);w('LmInvul',0);w('LmHurt',0);w('LmRest',0);w('CoinTally',0)
  if q.kind=='coin'or q.kind=='death'then
   -- An explicit ordinary coin cell at the actual native head probe. The
   -- player must collect it through terrain collision/GiveOneCoin.
   local at=L.Block_Buffer_1+6+0x90
   emu.write(at,0xc2,emu.memType.nesDebug);w('CoinTally',99);phase='award'
  elseif q.kind=='score'then
   w('FloateyNum_Control',11,5);w('FloateyNum_Timer',43,5);w('FloateyNum_X_Pos',108,5);w('FloateyNum_Y_Pos',176,5);phase='award'
  elseif q.kind=='oneup'then
   actor(5,104,176,3,128);w('InvPickup',252,5);phase='award'
  elseif q.kind=='area'then current.area_before=r('AreaPointer');w('AreaPointer',r('AreaPointer')~1);phase='area'
  else phase='deathseed'end
 else
  w('TnVariant',q.variant);w('TnMarker',0xc9);w('TnLife',r('NumberofLives'));w('TnFood',1)
  for i=0,3 do w('TnHealth',128,i);w('TnEquipment',0,i);w('TnAmmo',0,i)end
  for _,n in ipairs({'TnVYHi','TnVYLo','TnVXHi','TnVXLo','TnLastVx','TnLastVy','TnXFraction','TnYFraction','TnHurt','TnHurtMove','TnPrevious','TnPendingFresh','TnAttack','TnNativeState'})do w(n,0)end
  w('TnJumpStage',8);w('TnSeq',128);w('TnTimer',6);w('TnPose',9)
  if q.kind=='real'then
   -- Original first mushroom block (world336,Y144), after real navigation.
   anchor(332,176,0);phase='jump'
  else
   local sc=768+q.scroll;camera(sc);anchor(sc+64,176,0)
   actor(q.slot,sc+q.relative,136,1,1);w('InvPickup',180,q.slot);w('InvPickupOwner',19,q.slot);w('InvRisePhase',0,q.slot);w('TnPickupStamp',4,q.slot);phase='rise'
  end
 end
 print('MAC_TMNT_SEED '..json({case=index,name=q.name,wall=wall,phase=phase}))
end
local function finishCase()
 current.frames=age;results[#results+1]=current;index=index+1
 if index>#C.cases then done=true else seed(C.cases[index])end
end
emu.addMemoryCallback(function(address,value)
 if not entered or done or C.character~=15 then return end
 local st=emu.getState();local old=r('NumberofLives')
 writes:write(table.concat({wall,index,age,phase,st['cpu.pc'],bank(st['cpu.pc']),address,old,value},',')..'\n');writes:flush()
 if phase=='newgame'then return end
 if value==(old+1)%256 then
  assert(phase=='award','Only native award phase increments lives')
  assert(emu.read(st['cpu.pc']-3,emu.memType.nesDebug)==0xee and emu.read(st['cpu.pc']-2,emu.memType.nesDebug)==L.NumberofLives%256 and emu.read(st['cpu.pc']-1,emu.memType.nesDebug)==L.NumberofLives//256,'Award is the actual assembled INC life instruction')
  current.award_pc=st['cpu.pc'];current.award_bank=bank(st['cpu.pc']);current.old_lives=old;current.new_lives=value;current.awards=(current.awards or 0)+1
  lifeAwards[#lifeAwards+1]={case=index,pc=st['cpu.pc'],bank=bank(st['cpu.pc']),old=old,new=value}
  phase='ensure';current.award_wall=wall
 elseif value==(old-1)%256 and phase=='dying'then current.decrements=(current.decrements or 0)+1;current.after_death_lives=value end
end,emu.callbackType.write,L.NumberofLives)
emu.addMemoryCallback(function()
 if not entered or done or C.character~=15 or not valid('LmEnsure')then return end
 local before=snap();ensureCalls=ensureCalls+1
 if phase=='area'then
  onReturn('area-control',function()
   assert(r('LmHealth')==37 and r('LmStars')==3 and r('LmHearts')==9 and r('LmAttack')==0 and r('LmLife')==r('NumberofLives')and r('LmArea')==r('AreaPointer'),'Staged area marker retains persistent resources and clears transient moves')
   current.checks=1;current.staged_area_marker_only=true;w('AreaPointer',current.area_before);w('LmArea',current.area_before);phase='observe';current.observe_age=age
  end)
 elseif phase=='ensure' then
  assert(before.LmLife==current.old_lives and before.NumberofLives==current.new_lives,'Actual gain before ensure')
  onReturn('ensure-gain',function()
   local after=snap();local bad=false
   for _,n in ipairs({'LmHealth','LmStars','LmHearts','LmAttack','LmSuper','LmWalk','LmPrevious'})do if after[n]~=before[n]then bad=true end end
   if bad then problem('Native life gain resets live boxing state',{before=before,after=after},true)end
   assert(after.LmLife==current.new_lives,'Gain marker advances')
   current.before=before;current.after=after;current.checks=current.checks+1
   if current.kind=='death'then phase='deathseed'else phase='observe';current.observe_age=age end
  end)
 end
end,emu.callbackType.exec,C.hooks.LmEnsure.address)
emu.addMemoryCallback(function(address,value)
 if not entered or done or C.character~=15 or phase~='ensure' or value==r('LmHealth')then return end
 if current.first_wrong_write then return end
 local st=emu.getState();current.first_wrong_write={pc=st['cpu.pc'],bank=bank(st['cpu.pc']),address=address,old=r('LmHealth'),new=value}
end,emu.callbackType.write,L.LmHealth)
for _,n in ipairs({'GiveOneCoin','FloateyNumbersCore','HandlePowerUpCollision','KillPlayer','LmDeathStartGate','PlayerLoseLife','LmResetGate','X5InventoryInit','X5ProfilesNewGame'})do
 emu.addMemoryCallback(function()
  if not entered or done or not valid(n)then return end
  current[n]=(current[n]or 0)+1
  if n=='X5ProfilesNewGame'and phase=='newgame'then onReturn('newgame-clear',function()
   assert(r('LmReady')==0 and r('LmHealth')==0 and r('LmStars')==0 and r('LmHearts')==0,'Real new-game initializer clears persistent boxing record');current.newgame_cleared=true
  end)end
  if n=='PlayerLoseLife'then onReturn('lose-life',function()
   current.death_return={mode=r('OperMode'),lives=r('NumberofLives'),health=r('LmHealth'),marker=r('LmLife')}
   if current.kind=='gameover'then assert(r('OperMode')==3 and r('NumberofLives')==255,'Actual DEC0->255 is Game Over');phase='complete'
   else assert(r('NumberofLives')==2,'Gain then actual death restores zero-based count2');phase='respawn'end
  end)end
 end,emu.callbackType.exec,C.hooks[n].address)
end
emu.addMemoryCallback(function()
 if not entered or done or C.character~=19 or not valid('TnPreparePickupDispatch')then return end
 local s=emu.getState()['cpu.x'];onReturn('prepare',function()
  if r('InvPickup',s)==180 and r('TnPickupStamp',s)==4 then
   assert(phase=='jump'and s==5,'First Kiai is a real question-block reveal')
   current.reveal={x=r('Enemy_X_Position',s)+256*r('Enemy_PageLoc',s),y=r('Enemy_Y_Position',s),state=r('Enemy_State',s),slot=s,type=r('PowerUpType',s),stamp=r('TnPickupStamp',s),owner=r('InvPickupOwner',s)}
   reveals=reveals+1;phase='rise';current.rises=0;current.slot=s
  end
 end)
end,emu.callbackType.exec,C.hooks.TnPreparePickupDispatch.address)
emu.addMemoryCallback(function()
 if not entered or done or C.character~=19 or not valid('TnRisePickupDispatch')or phase~='rise'then return end
 local q=C.cases[index];local s=current.slot or q.slot
 if emu.getState()['cpu.x']~=s then return end
 local before=r('Enemy_State',s);onReturn('rise',function()
  if r('InvPickup',s)~=180 then return end
  current.rises=current.rises+1;rises=rises+1
  local count=current.rises;local y=r('Enemy_Y_Position',s);local state=r('Enemy_State',s)
  assert(y==136-count//3,'Native Kiai rises one pixel per three actor calls')
  assert(state==(count==48 and 128 or 1+count//3),'Exact native Kiai emergence state')
  assert(r('TnEquipment',q.variant)==0 and r('TnAmmo',q.variant)==0,'Cannot collect rising Kiai')
  if count==48 then assert(y==120,'48-call rise complete');phase='contactseed';current.mature_age=age;capture('case-'..index..'-mature')end
 end)
end,emu.callbackType.exec,C.hooks.TnRisePickupDispatch.address)
emu.addMemoryCallback(function()
 if not entered or done or C.character~=19 or not valid('TnCollectEquipment')then return end
 local q=C.cases[index];local s=emu.getState()['cpu.x'];onReturn('collect',function()
  if r('TnEquipment',q.variant)==4 then
   current.contacts=current.contacts+1;collects=collects+1
   if q.kind=='miss'or q.kind=='edge'then problem('Kiai collected at false wrapped screen coordinate',{slot=s,scroll=q.scroll,relative=q.relative,player=world()},true)
   else assert(phase=='contact'and current.rises==48,'Mature Kiai collection occurs only at real contact');assert(r('TnAmmo',q.variant)==20,'Native Kiai ammo grant20');phase='observe';current.observe_age=age end
  end
 end)
end,emu.callbackType.exec,C.hooks.TnCollectEquipment.address)
emu.addMemoryCallback(function()
 if not valid('PauseSkip')then return end
 if not entered then
  if not native()or r('SelectedCharacter')~=C.character then return end
  if C.character==19 and world()<404 then return end
  entered=true;index=1;seed(C.cases[index]);return
 end
 if done then return end
 age=age+1
 if age==30 and C.character==19 and phase=='jump'then capture('jump-30')end
 log:write(table.concat({wall,index,age,phase,r('Player_Y_Position'),r('Player_State'),r('NumberofLives'),C.character==15 and r('LmLife')or r('TnLife'),C.character==15 and r('LmHealth')or r('TnHealth',C.cases[index].variant),C.character==19 and r('TnEquipment',C.cases[index].variant)or r('LmStars'),C.character==19 and r('TnAmmo',C.cases[index].variant)or r('LmHearts')},',')..'\n');log:flush()
 assert(age<650,'Each case is bounded: '..phase)
 if phase=='newgame'and native()then
  assert(current.newgame_cleared and(current.X5InventoryInit or 0)>0,'Actual new-game initializer executed')
  assert(r('SelectedCharacter')==15 and r('NumberofLives')==2 and r('LmHealth')==96 and r('LmStars')==0 and r('LmHearts')==20 and r('LmReady')==77 and r('LmLife')==2,'Fresh real game defaults');phase='complete'
 end
 if phase=='deathseed'then
  clearActors();anchor(100,176,0);w('LmHealth',8);w('LmAttack',0);w('LmInvul',0);w('LmHurt',0);w('LmStars',3);w('LmHearts',9)
  w('Enemy_Flag',1,0);w('Enemy_ID',6,0);w('Enemy_State',0,0);w('Enemy_X_Position',108,0);w('Enemy_PageLoc',0,0);w('Enemy_Y_Position',184,0);w('Enemy_Y_HighPos',1,0);w('Enemy_BoundBoxCtrl',9,0);w('Enemy_MovingDir',2,0);w('Enemy_X_Speed',0,0);phase='dying'
 end
 if phase=='respawn'and native()then
  assert(r('LmHealth')==96 and r('LmStars')==0 and r('LmHearts')==20 and r('LmAttack')==0 and r('LmLife')==2,'Real gain then death resets boxing resources')
  assert((current.KillPlayer or 0)>0 and(current.LmDeathStartGate or 0)>0 and(current.PlayerLoseLife or 0)>0,'Actual injury/death and canonical life decrement ran');phase='complete'
 end
 if phase=='contactseed'then
  local q=C.cases[index];local s=current.slot or q.slot;local item=r('Enemy_X_Position',s)+256*r('Enemy_PageLoc',s)
  local x=item
  if q.kind=='miss'then local ghost=(item%256)+4;x=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')+ghost-4
  elseif q.kind=='edge'then x=(r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'))+(q.relative<0 and 240 or 4)end
  anchor(x,128,1);w('TnSeq',135);w('TnPose',21);w('TnTimer',20);w('TnVYHi',1);w('Player_Y_Speed',1);w('TnLastVy',1);w('TnVYLo',0);w('TnJumpStage',8)
  phase='contact';current.contact_age=age
 end
 if phase=='contact'and age-current.contact_age>=5 then
  local q=C.cases[index]
  if q.kind=='miss'or q.kind=='edge'then
   if current.contacts==0 then assert(r('TnEquipment',q.variant)==0 and r('TnAmmo',q.variant)==0,'False distant contact cannot equip');current.checks=current.checks+1 end
   phase='observe';current.observe_age=age
  else problem('Visible mature Kiai must collect at actual contact',{rises=current.rises,x=world(),y=r('Player_Y_Position'),state=r('Enemy_State',q.slot),box={r('EnemyBoundingBoxCoord',q.slot*4),r('EnemyBoundingBoxCoord',q.slot*4+1),r('EnemyBoundingBoxCoord',q.slot*4+2),r('EnemyBoundingBoxCoord',q.slot*4+3)}},true);phase='observe';current.observe_age=age end
 end
 if phase=='observe'and age-current.observe_age>=3 then capture('case-'..index..'-result');phase='complete'end
 if phase=='complete'then
  if C.character==15 and current.kind~='gameover'and current.kind~='newgame'and current.kind~='area'then
   assert(current.awards==1 and current.checks==1,'Exactly one real award and preserved boxing-state check')
   if current.kind=='coin'or current.kind=='death'then assert(current.GiveOneCoin==1,'Coin collector invokes native award')end
   if current.kind=='oneup'then assert(current.HandlePowerUpCollision==1,'Actual 1Up actor collision before delayed award')end
  end
  finishCase()
 end
end,emu.callbackType.exec,C.hooks.PauseSkip.address)
emu.addMemoryCallback(function(address,value)
 if not entered or done then return end
 dma={case=index,age=age,bytes={}};for i=0,255 do dma.bytes[i+1]=emu.read(value*256+i,emu.memType.nesDebug)end
end,emu.callbackType.write,0x4014)
emu.addEventCallback(function()
 local b={}
 if not entered then
  if native()then b.right=true;if C.character==19 then w('CheatInvincible',1)end
  elseif wall>=120 and wall%12==0 then
   if r('CrossoverMenuState')~=2 then b.start=true
   elseif r('CrossoverMenuIndex')~=C.menu_target then b[C.menu_moves[r('CrossoverMenuIndex')+1]]=true else b.a=true end
  end
 elseif not done then
  if phase=='jump'then b.a=true
  elseif phase=='newgame'and wall%12==0 then
   if r('CrossoverMenuState')==2 then
    if r('CrossoverMenuIndex')~=C.menu_target then b[C.menu_moves[r('CrossoverMenuIndex')+1]]=true else b.a=true end
   else b.start=true end
  end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1
 if wall%300==0 then print('PROGRESS '..json({wall=wall,phase=phase,index=index,age=age,world=world()}))end
 assert(wall<7000,'Bounded whole native audit')
 if entered and not done and native()and dma and dma.case==index then
  for i=0,255 do assert(emu.read(i,emu.memType.nesSpriteRam)==dma.bytes[i+1],'Exact DMA reaches hardware OAM')end
  current.dma=(current.dma or 0)+1
 end
 if done then
  assert(nmis>=math.min(20,#C.cases*2),'Native interrupts exercised')
  local p={passed=#violations==0,cases=results,violations=violations,nmis=nmis,min_sp_sampled_at_native_entries=minSP,nmi_mapper_store_windows=nmiWindows,life_awards=lifeAwards,ensure_calls=ensureCalls,real_block_reveals=reveals,native_rise_calls=rises,native_collections=collects,wall_frames=wall,staged=true,
   scope='Cold real menu and controller input; explicit legal native actor/terrain/life component staging at PauseSkip. Actual native coin/Floatey/1Up awards, LmEnsure, injury/death/life loss, Kiai emergence/collision/grant. Exact hardware DMA, real PPU frames, fiveSMC/NMI/banks/SP. No campaign, audio fidelity or performance claim.'}
  local f=assert(io.open(OUTPUT..'proof.json','w'));f:write(json(p));f:close();log:close();writes:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
