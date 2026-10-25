-- Explicit legal actors/terrain; native input, gravity, cleanup and contacts.
local C=assert(KIRBY_CHIP_NATIVE_CONFIG)
for n,a in pairs(C.ram)do L[n]=a end
local wall,index,age,nmis=0,0,0,0
local entered,done=false,false
local current=nil
local results,violations={},{}
local minSP,stackWrites=255,0
local phase='menu'
local r=function(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)
 if n=='Enemy_Y_HighPos'then assert(v==1,'Fixture never forces an off-page enemy')end
 emu.write(assert(L[n],n)+(i or 0),v&255,emu.memType.nesDebug)
end
local function json(v)
 if type(v)=='table'then local o={};if #v>0 then for _,x in ipairs(v)do o[#o+1]=json(x)end;return'['..table.concat(o,',')..']'end
  for k,x in pairs(v)do o[#o+1]=string.format('%q',k)..':'..json(x)end;return'{'..table.concat(o,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)else return tostring(v)end
end
local function native()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function bank(a)local p=emu.convertAddress(a);return p and p.address//8192 or -1 end
local function valid(n)return bank(C.hooks[n].address)==C.hooks[n].physical_bank end
local function bind(n)local h=C.hooks[n];for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Bound '..n)end end
local function capture(name)
 local f=assert(io.open(OUTPUT..name..'.argb','wb'));for _,v in ipairs(emu.getScreenBuffer())do f:write(string.pack('<I4',v))end;f:close()
end
local function problem(message,data,known)
 local st=emu.getState();violations[#violations+1]={message=message,data=data,case=index,age=age,wall=wall,pc=st['cpu.pc'],bank=bank(st['cpu.pc']),sp=st['cpu.sp']}
 local f=assert(io.open(OUTPUT..'violations.json','w'));f:write(json(violations));f:close();capture('failure-'..index..'-'..age)
 if not known then assert(false,message)end
end
local returns,installed={},{}
local function onReturn(name,fn)
 local st=emu.getState();local sp=st['cpu.sp'];minSP=math.min(minSP,sp)
 local ret=(emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 local key=name..':'..ret;returns[key]={sp=(sp+2)%256,bank=bank(ret),fn=fn}
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
local stackLowest=0x200
emu.addMemoryCallback(function(address,value)
 if not entered or done then return end
 stackWrites=stackWrites+1
 if address<stackLowest then
  local sp=emu.getState()['cpu.sp']
  if address==0x100+sp then stackLowest=address;minSP=math.min(minSP,(sp-1)%256)end
 end
end,emu.callbackType.write,0x180,0x1ff)
emu.addMemoryCallback(function(address,value)
 if entered and not done then assert(emu.getState()['cpu.sp']>=0x80,'Native stack does not cross lower-page guard')end
end,emu.callbackType.write,0x17f)
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


local log=assert(io.open(OUTPUT..'updates.csv','w'));log:write('wall,case,age,phase,playerY,state,enemyFlag,enemyState,enemyHigh,enemyY,enemyVY,shotType,shotY,dropKind,dropY,mouth,health,crateKind,crateMode,crateY,crateVY\n')
local events=assert(io.open(OUTPUT..'events.jsonl','w'))
local function event(name,data)
 local st=emu.getState();events:write(json({event=name,data=data,case=index,age=age,wall=wall,pc=st['cpu.pc'],bank=bank(st['cpu.pc']),sp=st['cpu.sp']})..'\n');events:flush()
end
local function cell(x,y,v)w('Block_Buffer_1',v,(x//16)%32+((y-32)//16)*16)end
local function seed(q)
 phase='seed'
 assert(r('SelectedCharacter')==C.character,'Real selected identity')
 assert(r(C.character==13 and 'KbVariant'or 'CdVariant')==C.variant,'Real selected alternate')
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i);w('Enemy_State',0,i);w('AvFrozen',0,i);w('AvFrozenHi',0,i);w('RgEnemyStun',0,i)end
 for i=0,3 do w('Block_State',0,i);w('BlockMetasprite',0,i)end
 for i=0,8 do w('Misc_State',0,i);w('MiscMetasprite',0,i)end
 for i=0,415 do w('Block_Buffer_1',0,i)end
 for col=0,31 do for y=208,240,16 do cell(col*16,y,0x54)end end
 local falling=q.kind=='fall'or q.kind=='alias'
 if falling then
  for col=4,9 do for y=176,240,16 do cell(col*16,y,0)end end
  -- A legal upper brick platform supports a player atY32, over the pit.
  cell(96,64,0x51);cell(112,64,0x51)
 end
 if q.kind=='top'then cell(96,96,0x51);cell(112,96,0x51)end
 for _,n in ipairs({'GamePauseStatus','GamePauseTimer','TimerControl','MmDeathFlag','MmDeathAge','GuestHurtTicks','CrouchingFlag','Player_X_Speed','Player_Y_Speed','Player_X_Scroll','Player_X_MoveForce','Player_Y_MoveForce','SmCeilingHit','DisableCollisionDet','StarInvincibleTimer','ScrollThirtyTwo','AreaParserTaskNum','GameTimerExpiredFlag'})do w(n,0)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i);w('XgGravity',0,i)end
 w('Player_X_Position',100);w('Player_PageLoc',0);w('Player_Y_Position',falling and 32 or q.kind=='top'and 64 or 176);w('Player_Y_HighPos',1);w('Player_State',0)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0);w('ScrollLock',1)
 w('PlayerFacingDir',q.face or 1);w('Player_MovingDir',q.face or 1);w('Player_CollisionBits',255);w('CrossoverBehaviorVersion',1)
 if C.character==13 then
  for _,n in ipairs({'KbMouth','KbFloat','KbAction','KbActionAge','KbPrevious','KbFresh','KbCooldown','KbDropKind','KbHurt'})do w(n,0)end
  w('KbInputFrame',255);w('KbHealth',6);w('KbCopy',q.copy or(q.kind=='inhale'and 2 or 7))
  for i=0,2 do for _,n in ipairs({'KbShotType','KbShotAge','KbShotX','KbShotPage','KbShotY','KbShotFX','KbShotFY','KbShotVXLo','KbShotVXHi','KbShotVYLo','KbShotVYHi','KbShotHits','KbShotKind'})do w(n,0,i)end end
 else
  for _,n in ipairs({'CdPressed','CdPrevious','CdHurtTimer','CdHide','CdThrowAge','CdThrowUp','CdHeld','CdEntrancePending'})do w(n,0)end
  w('CdReady',0x43);w('CdHealth',3);w('CdVYLo',0xab);w('CdVYHi',255)
  for i=0,5 do for _,n in ipairs({'CdBoxKind','CdBoxMode','CdBoxAge','CdBoxVX','CdBoxVYLo','CdBoxVYHi','CdBoxFrac'})do w(n,0,i)end end
  if q.kind=='alias'or q.kind=='top'then w('CdBoxKind',1);w('CdBoxMode',1);w('CdHeld',1);w('CdBoxX',100);w('CdBoxPage',0);w('CdBoxY',q.kind=='top'and 56 or 24)
  elseif q.kind=='crate'then w('CdBoxKind',1);w('CdBoxMode',0);w('CdBoxX',q.face==2 and 88 or 112);w('CdBoxPage',0);w('CdBoxY',184)end
 end
 if falling or q.kind=='inhale'or q.kind=='crate'or q.kind=='top'then
  w('Enemy_Flag',1);w('Enemy_ID',C.goomba);w('Enemy_State',0);w('Enemy_Y_HighPos',1);w('Enemy_Y_Position',184)
  w('Enemy_X_Position',falling and(q.face==2 and 108 or 92)or q.kind=='top'and 104 or q.kind=='inhale'and 148 or q.face==2 and 24 or 176);w('Enemy_PageLoc',0);w('Enemy_X_Speed',falling and(q.face==2 and 248 or 8)or q.kind=='top'and 0 or q.face==2 and 8 or 248);w('Enemy_MovingDir',falling and(q.face==2 and 2 or 1)or q.face==2 and 1 or 2)
  if q.kind=='top'then w('Enemy_Y_Position',32)end
  w('Enemy_Y_Speed',0);w('Enemy_Y_MoveForce',0);w('Enemy_X_MoveForce',0);w('Enemy_YMoveForceFractional',0);w('Enemy_BoundBoxCtrl',3);w('EnemyIntervalTimer',0);w('EnemyFrameTimer',0);w('Enemy_CollisionBits',0)
 end
 current={name=q.name,kind=q.kind,spawns=0,contacts=0,defeats=0,offpage_contacts=0,offpage_weapon_entries={},crossings={},erasures={},graphics=0,updates=0,origins={},suction=0,aligned_pull=0,box_releases=0}
 age=0;phase=q.kind=='inhale'and 'drop'or q.kind=='crate'and 'pickup'or q.kind=='top'and 'upthrow'or 'watch'
 event('seed',{kind=q.kind,enemy_high=1,enemy_y=184,player_y=r('Player_Y_Position')})
end
emu.addMemoryCallback(function(address,value)
 if not entered or done or phase=='seed'then return end
 local before=r('Enemy_Y_HighPos')
 if value~=before then current.crossings[#current.crossings+1]={before=before,after=value,y=r('Enemy_Y_Position'),age=age,wall=wall};event('native-enemy-page-write',{before=before,after=value,y=r('Enemy_Y_Position')})end
end,emu.callbackType.write,L.Enemy_Y_HighPos)
emu.addMemoryCallback(function()
 if not entered or done or not valid('EraseEnemyObject')or emu.getState()['cpu.x']~=0 then return end
 current.erasures[#current.erasures+1]={high=r('Enemy_Y_HighPos'),y=r('Enemy_Y_Position'),state=r('Enemy_State'),age=age,wall=wall}
 event('erase',{high=r('Enemy_Y_HighPos'),y=r('Enemy_Y_Position'),state=r('Enemy_State')})
end,emu.callbackType.exec,C.hooks.EraseEnemyObject.address)
local inContacts=false
for _,n in ipairs({'KbWeapons::EnemyContacts','CdBoxEnemies'})do emu.addMemoryCallback(function()
 if not entered or done or not valid(n)then return end
 inContacts=true;current.contacts=current.contacts+1
 onReturn(n,function()inContacts=false end)
end,emu.callbackType.exec,C.hooks[n].address)end
emu.addMemoryCallback(function(address,value)
 if not entered or done or not inContacts or value~=0 or r('Enemy_Flag')==0 then return end
 local pc=emu.getState()['cpu.pc']
 if emu.read(pc-2,emu.memType.nesDebug)~=0x86 or emu.read(pc-1,emu.memType.nesDebug)~=L.ObjectOffset then return end
 local targetY=C.character==13 and r('KbShotY',r('KbSavedSlot'))or r('CdRectY')
 local actualY=(r('Enemy_Y_HighPos')-1)*256+r('Enemy_Y_Position')+(C.character==14 and 8 or 0)
 local limit=C.character==13 and 13 or 16
 if actualY-targetY>=-limit and actualY-targetY<limit then return end
 current.offpage_contacts=current.offpage_contacts+1
 if current.offpage_contacts==1 then problem('Weapon selects a native falling enemy across a vertical wrap',{high=r('Enemy_Y_HighPos'),enemyY=r('Enemy_Y_Position'),enemyState=r('Enemy_State'),actualY=actualY,targetY=targetY,gap=actualY-targetY,shotY=C.character==13 and r('KbShotY')or -1,crateY=C.character==14 and r('CdBoxY')or -1},true)end
end,emu.callbackType.write,L.ObjectOffset)
for _,n in ipairs({'ShellOrBlockDefeat','CdDefeatEnemy'})do emu.addMemoryCallback(function()
 if not entered or done or not valid(n)then return end
 current.defeats=current.defeats+1
 event('actual-defeat-entry',{owner=n,high=r('Enemy_Y_HighPos'),y=r('Enemy_Y_Position'),state=r('Enemy_State'),crateY=C.character==14 and r('CdBoxY')or -1})
end,emu.callbackType.exec,C.hooks[n].address)end
for _,n in ipairs({'KbWeapons','CdWeapons'})do emu.addMemoryCallback(function()
 if not entered or done or not valid(n)then return end
 if r('Enemy_Flag')~=0 and r('Enemy_Y_HighPos')~=1 then
  local q={high=r('Enemy_Y_HighPos'),y=r('Enemy_Y_Position'),state=r('Enemy_State'),age=age,wall=wall};current.offpage_weapon_entries[#current.offpage_weapon_entries+1]=q;event('weapons-before-erase',q)
 end
end,emu.callbackType.exec,C.hooks[n].address)end
emu.addMemoryCallback(function()
 if not entered or done or not valid('KbWeapons::Spawn')then return end
 onReturn('spawn',function()
  if(emu.getState()['cpu.ps']or 0)&1~=0 then
   local x=emu.getState()['cpu.x'];current.spawns=current.spawns+1
   current.origins[#current.origins+1]={kind='shot',dy=r('KbShotY',x)-r('Player_Y_Position'),y=r('KbShotY',x),playerY=r('Player_Y_Position'),age=age};event('native-shot-spawn',current.origins[#current.origins])
  end
 end)
end,emu.callbackType.exec,C.hooks['KbWeapons::Spawn'].address)
emu.addMemoryCallback(function()
 if not entered or done or not valid('KbDropCopy')then return end
 onReturn('drop',function()
  if r('KbDropKind')~=0 then current.origins[#current.origins+1]={kind='drop',dy=r('KbDropY')-r('Player_Y_Position'),y=r('KbDropY'),playerY=r('Player_Y_Position')};phase='inhale' end
 end)
end,emu.callbackType.exec,C.hooks.KbDropCopy.address)
emu.addMemoryCallback(function()
 if not entered or done or not valid('KbWeapons::Suction')then return end
 current.suction=current.suction+1;local object=r('ObjectOffset')
 onReturn('suction',function()
  assert(r('ObjectOffset')==object,'Suction restores native actor ownership')
  if r('Enemy_Flag')~=0 and r('Enemy_Y_HighPos')==1 then
   if r('Enemy_Y_Position')==r('Player_Y_Position')+8 and r('Enemy_Y_Speed')==0 and r('Enemy_Y_MoveForce')==0 then current.aligned_pull=current.aligned_pull+1 end
   assert(r('KbMouth')==0 and r('KbDropKind')==2,'Eligible enemy has inhale priority over nearby copy star')
  elseif r('KbMouth')~=0 then
   assert(r('KbMouth')==C.goomba+1 and r('KbMouthCopy')==1 and r('KbDropKind')==2,'Actual Goomba captured before nearby copy star');current.captured=true
  end
 end)
end,emu.callbackType.exec,C.hooks['KbWeapons::Suction'].address)
emu.addMemoryCallback(function()
 if not entered or done or not valid('CdRelease')then return end
 onReturn('crate-release',function()current.box_releases=current.box_releases+1;event('actual-crate-release',{y=r('CdBoxY'),up=r('CdThrowUp'),high=r('Enemy_Y_HighPos'),enemyY=r('Enemy_Y_Position')});phase='released' end)
end,emu.callbackType.exec,C.hooks.CdRelease.address)
emu.addMemoryCallback(function()
 if not valid('PauseSkip')or not native()or r('SelectedCharacter')~=C.character then return end
 if not entered then entered=true;index=1;seed(C.cases[index]);return end
 if done then return end
 age=age+1;current.updates=current.updates+1
 log:write(table.concat({wall,index,age,phase,r('Player_Y_Position'),r('Player_State'),r('Enemy_Flag'),r('Enemy_State'),r('Enemy_Y_HighPos'),r('Enemy_Y_Position'),r('Enemy_Y_Speed'),C.character==13 and r('KbShotType')or -1,C.character==13 and r('KbShotY')or -1,C.character==13 and r('KbDropKind')or -1,C.character==13 and r('KbDropY')or -1,C.character==13 and r('KbMouth')or -1,r(C.character==13 and 'KbHealth'or 'CdHealth'),C.character==14 and r('CdBoxKind')or -1,C.character==14 and r('CdBoxMode')or -1,C.character==14 and r('CdBoxY')or -1,C.character==14 and r('CdBoxVYHi')or -1},',')..'\n');log:flush()
 if current.kind=='alias'and phase=='watch'and r('Enemy_Flag')~=0 and r('Enemy_Y_HighPos')==1 and r('Enemy_Y_Position')>=238 then phase='upthrow'end
 if current.kind=='crate'and phase=='pickup'and r('CdHeld')~=0 then phase='release-input';current.pickup_age=age end
 if phase=='release-input'and age-current.pickup_age>=3 then phase='throw'end
 local duration=current.kind=='inhale'and 65 or 55
 if age>=duration then
  if current.kind=='fall'or current.kind=='alias'then
   assert(#current.crossings>0 and #current.offpage_weapon_entries>0 and #current.erasures>0,'Actual page1 fall crosses and reaches weapons before cleanup')
  elseif current.kind=='copy'then assert(current.spawns>0,'Actual copied shot dispatched');for _,q in ipairs(current.origins)do assert(q.dy==20,'Grounded copied shot starts at source mouthY+20')end
  elseif current.kind=='inhale'then assert(current.captured and current.aligned_pull>0 and current.suction>8 and r('KbHealth')==6,'Actual aligned inhale preserves health and takes enemy first');assert(current.origins[1].dy==20,'Actual discarded star starts at sourceY+20')
  elseif current.kind=='crate'then assert(current.box_releases>0,'Actual pickup and timed throw execute')
  elseif current.kind=='top'then assert(current.box_releases>0 and current.defeats>0,'Valid near-top overlap is retained')end
  assert(current.graphics>=2,'Native displayed frames observed for every case')
  results[#results+1]=current;index=index+1
  if index>#C.cases then done=true else seed(C.cases[index])end
 end
end,emu.callbackType.exec,C.hooks.PauseSkip.address)
local dma=nil
emu.addMemoryCallback(function(address,value)
 if not entered or done then return end;dma={case=index,age=age,bytes={}}
 for i=0,255 do dma.bytes[i+1]=emu.read(value*256+i,emu.memType.nesDebug)end
end,emu.callbackType.write,0x4014)
emu.addEventCallback(function()
 local b={}
 if not entered then
  if wall>=120 and wall%12==0 then
   local at=r('CrossoverMenuIndex');local row=at<12 and at//6 or 2;local wanted=C.menu_slot<12 and C.menu_slot//6 or 2
   if r('CrossoverMenuState')~=2 then b.start=true elseif row~=wanted then b.down=true elseif at~=C.menu_slot then b.right=true
   elseif r(C.character==13 and 'KbVariant'or 'CdVariant')~=C.variant then b.select=true else b.a=true end
  end
 elseif not done then
  if current.kind=='copy'or(current.kind=='fall'and C.character==13)or phase=='inhale'or phase=='pickup'or phase=='throw'then
   b.b=true
   if phase=='throw'and C.cases[index].style=='up'then b.up=true elseif phase=='throw'and C.cases[index].style=='down'then b.down=true end
  elseif phase=='drop'then b.select=true
  elseif phase=='upthrow'then b.up=true;b.b=true end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1;assert(wall<2400,'Bounded native investigation')
 if entered and not done and dma and dma.case==index and dma.age>=3 and(age==8 or age==16 or age==24 or age==32 or age==48)then
  for i=0,255 do assert(emu.read(i,emu.memType.nesSpriteRam)==dma.bytes[i+1],'Hardware OAM matches exact committed DMA')end
  assert(emu.read(0x3f00,emu.memType.nesPpuDebug)==0x22,'Native sky palette preserved')
  current.graphics=current.graphics+1;capture(string.format('case-%02d-age-%02d-wall-%04d',index,age,wall))
 end
 if done then
  local f=assert(io.open(OUTPUT..'proof.json','w'));f:write(json({passed=#violations==0,cases=results,violations=violations,nmis=nmis,min_sp=minSP,stack_writes=stackWrites,nmi_mapper_store_windows=nmiWindows,scope='Actual selected actors, explicitly legal starting page1 enemies and terrain; no manual enemy high-page forcing. Native falls/weapons/cleanup, source copy/drop/inhale controls, PPU frames and NMI/SMC/bank/SP guards. Staged component arenas, not natural routes or full campaign.'}));f:close();log:close();events:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
