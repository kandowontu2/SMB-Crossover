-- Real menu/input, legal staged pickup/shot actors, production dispatch only.
local C=assert(RYU_SOPHIA_NATIVE_CONFIG)
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
local log=assert(io.open(OUTPUT..'updates.csv','w'));log:write('wall,case,age,phase,playerY,state,slash,attack,selected,ammo,shots,paused\n')
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

local function countShots(typ)
 local count=0;for i=0,9 do if r('RgShotType',i)~=0 and(not typ or r('RgShotType',i)==typ)then count=count+1 end end;return count
end
local function seed(q)
 assert(r('SelectedCharacter')==C.character,'Real selected character')
 w('CrossoverBehaviorVersion',1)
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i);w('InvPickup',252,i)end
 for i=0,9 do
  for _,n in ipairs({'RgShotType','RgShotAge','RgShotImpact','RgShotFracX','RgShotFracY','RgShotVXLo','RgShotVXHi','RgShotVYLo','RgShotVYHi','RgShotHits','SsMode','SsAngleLo','SsAngleHi','SsHidden','SsHitTimer'})do w(n,0,i)end
 end
 for i=0,3 do w('Block_State',0,i);w('BlockMetasprite',0,i);w('InvDropKind',0,i)end
 for i=0,8 do w('Misc_State',0,i);w('MiscMetasprite',0,i)end
 for _,n in ipairs({'GamePauseStatus','GamePauseTimer','TimerControl','InvPrevious','InvFresh','InvRefill','RgPreviousButtons','RgAttack','RgAttackAge','RgAttackKind','RgShootPose','RgCooldown','AvSlash','AvFlip','AvFlipClock','AvPending','XgWall','RyWallSide','RyWallResolved','RyWallBlocked','RyPlatformSlot','GuestHurtTicks','CrouchingFlag','Player_X_Speed','Player_Y_Speed','Player_X_Scroll','Player_X_MoveForce','Player_Y_MoveForce','SmCeilingHit','DisableCollisionDet','StarInvincibleTimer','ScrollThirtyTwo','AreaParserTaskNum'})do w(n,0)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i);w('XgGravity',0,i)end
 local x=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')+100
 w('Player_X_Position',x%256);w('Player_PageLoc',x//256);w('Player_Y_Position',C.character==10 and 80 or 176);w('Player_Y_HighPos',1)
 w('Player_State',C.character==10 and 1 or 0);w('PlayerFacingDir',1);w('Player_MovingDir',1);w('PlayerSize',0);w('PlayerStatus',1);w('ScrollLock',1);w('Player_CollisionBits',255)
 w('InvOwnedHi',0,C.character);w('InvSelected',q.kind=='ryu'and 5 or q.kind=='primary'and 0 or 1,C.character)
 w('InvOwnedLo',C.character==10 and 33 or 7,C.character);w('InvAmmo',C.character==10 and 99 or 15,C.character*16+(C.character==10 and 0 or 1))
 current={name=q.name,kind=q.kind,attempts=0,grants=0,pickup_collisions=0,slash_inputs=0,cleanup=0,graphics=0,first_bad_write=false,actor_updates=0}
 age=0
 if C.character==11 then
  for i=0,9-q.free do
   local typ=q.active==1 and 44 or(i<4 and 45 or 6)
   w('RgShotType',typ,i);w('RgShotDir',1,i);w('RgShotX',(x+20+i*2)%256,i);w('RgShotPage',(x+20+i*2)//256,i);w('RgShotY',96+i*3,i);w('RgShotYHigh',1,i)
   w('RgShotImpact',i>=7 and 10 or 0,i);w('RgShotVXHi',1,i)
  end
  phase='fire'
 else phase=q.kind=='ryu'and 'slash' or 'primary' end
 print('RYU_SOPHIA_SEED '..json({case=index,name=q.name,wall=wall,phase=phase}))
end
local function pickup(q)
 local s=5;w('Enemy_Flag',1,s);w('Enemy_ID',C.power_id,s);w('Enemy_State',128,s);w('PowerUpType',1,s)
 w('Enemy_X_Position',r('Player_X_Position')+3,s);w('Enemy_PageLoc',r('Player_PageLoc'),s)
 w('Enemy_Y_Position',r('Player_Y_Position')+8,s);w('Enemy_Y_HighPos',1,s);w('Enemy_BoundBoxCtrl',3,s)
 w('Enemy_X_Speed',0,s);w('Enemy_Y_Speed',0,s);w('Enemy_X_MoveForce',0,s);w('Enemy_Y_MoveForce',0,s);w('Enemy_MovingDir',1,s);w('Enemy_SprAttrib',0,s)
 w('InvPickup',q.item,s);w('InvPickupOwner',10,s);w('InvRisePhase',0,s)
 phase='pickup'
end
for _,name in ipairs({'PowerUpObjHandler','HandlePowerUpCollision'})do emu.addMemoryCallback(function()
 if not entered or done or not valid(name)then return end;bind(name)
 if name=='HandlePowerUpCollision'then current.pickup_collisions=current.pickup_collisions+1 end
end,emu.callbackType.exec,C.hooks[name].address)end
emu.addMemoryCallback(function()
 if not entered or done or not valid('AvRyuSpecial')or phase~='slash'then return end
 onReturn('slash',function()
  if r('AvSlash')==1 then current.slash_inputs=current.slash_inputs+1;phase='grantseed';current.slash_wall=wall;capture('case-'..index..'-slash')end
 end)
end,emu.callbackType.exec,C.hooks.AvRyuSpecial.address)
emu.addMemoryCallback(function()
 if not entered or done or not valid('InventoryGrant')then return end
 local item=emu.getState()['cpu.a'];assert(phase=='pickup'and item==C.cases[index].item and r('AvSlash')==1,'Actual live Slash pickup grant')
 current.grants=current.grants+1
 onReturn('grant',function()
  assert(r('InvSelected',10)==item and r('AvSlash')==1,'Actual grant auto-equips without clearing Slash')
  current.granted_item=item;current.grant_wall=wall;phase='releaseB';current.release_age=age
 end)
end,emu.callbackType.exec,C.hooks.InventoryGrant.address)
emu.addMemoryCallback(function(address,value)
 if not entered or done or value==0 then return end
 local st=emu.getState();writes:write(table.concat({wall,index,age,phase,st['cpu.pc'],bank(st['cpu.pc']),address,r('RgAttack'),value},',')..'\n');writes:flush()
 if current.kind~='ryu'or phase~='attempt'or r('AvSlash')==0 then return end
 if not current.first_bad_write then current.first_bad_write=true;problem('Primary timer written while source Jump Slash remains live',{before=r('RgAttack'),after=value,slash=r('AvSlash'),selected=r('InvSelected',10)},true)end
end,emu.callbackType.write,L.RgAttack)
emu.addMemoryCallback(function(address,value)
 if not entered or done or current.kind~='sophia'or phase~='fire'or value>=r('InvAmmo',177)then return end
 local st=emu.getState();writes:write(table.concat({wall,index,age,phase,st['cpu.pc'],bank(st['cpu.pc']),address,r('InvAmmo',177),value},',')..'\n');writes:flush()
 if current.entry_free and current.entry_free<3 and not current.first_bad_write then current.first_bad_write=true;problem('Ammo spent before a complete three-slot volley can be reserved',{before=r('InvAmmo',177),after=value,entry_free=current.entry_free},true)end
end,emu.callbackType.write,L.InvAmmo+177)
emu.addMemoryCallback(function()
 if not entered or done or not valid('ExpandedWeapons')then return end
 if phase=='attempt'and(r('SavedJoypadBits')&64)~=0 and(r('RgPreviousButtons')&64)==0 then
  current.attempts=current.attempts+1;assert(r('AvSlash')==1 and r('InvSelected',10)==C.cases[index].item,'Fresh primary attempt after actual pickup')
  onReturn('primary',function()
   print('PRIMARY_RETURN '..json({kind=current.kind,attack=r('RgAttack'),slash=r('AvSlash'),bad=current.first_bad_write,phase=phase}))
   if r('RgAttack')~=0 and not current.first_bad_write then problem('Live Slash primary must be refused',{attack=r('RgAttack')},true)end
   current.primary_timer=r('RgAttack');phase='observe';current.observe_age=age
  end)
 elseif phase=='primary'and(r('SavedJoypadBits')&64)~=0 and(r('RgPreviousButtons')&64)==0 then
  current.attempts=current.attempts+1
  onReturn('primary-control',function()assert(r('RgAttack')==14 and r('AvSlash')==0,'Ordinary fresh primary retained');current.primary_timer=r('RgAttack');phase='observe';current.observe_age=age end)
 end
end,emu.callbackType.exec,C.hooks.ExpandedWeapons.address)
emu.addMemoryCallback(function()
 if not entered or done or not valid('RemainingWeapons::SophiaInput')or phase~='fire'or(r('InvFresh')&32)==0 then return end
 current.attempts=current.attempts+1;current.entry_free=10-countShots();local before=r('InvAmmo',177);local existing=countShots(44)
 onReturn('sophia-fire',function()
  local created=countShots(44)-existing;local spent=before-r('InvAmmo',177)
  print('SOPHIA_RETURN '..json({free=current.entry_free,created=created,spent=spent,existing=existing,bad=current.first_bad_write,phase=phase,kind=current.kind}))
  local allowed=current.entry_free>=3 and existing==0
  local want=allowed and 3 or 0
  if created~=want or spent~=want then
   if not current.first_bad_write then problem('Missile volley requires exactly three free slots before spending',{created=created,spent=spent,free=current.entry_free,existing=existing},true)end
  end
  current.created=created;current.spent=spent;current.existing=existing;phase='observe';current.observe_age=age
 end)
end,emu.callbackType.exec,C.hooks['RemainingWeapons::SophiaInput'].address)
emu.addMemoryCallback(function()
 if not entered or done or not valid('InventoryClearActive')then return end
 onReturn('cleanup',function()
  assert(r('AvSlash')==0 and r('RgAttack')==0 and countShots()==0,'Real paused selection cleanup clears attacks and shared pool')
  current.cleanup=current.cleanup+1;phase='complete'
 end)
end,emu.callbackType.exec,C.hooks.InventoryClearActive.address)
emu.addMemoryCallback(function()
 if not valid('PauseSkip')or not native()or r('SelectedCharacter')~=C.character then return end
 if not entered then
  entered=true;index=1;seed(C.cases[index]);return
 end
 if done then return end
 age=age+1;current.actor_updates=current.actor_updates+1
 log:write(table.concat({wall,index,age,phase,r('Player_Y_Position'),r('Player_State'),r('AvSlash'),r('RgAttack'),r('InvSelected',C.character),r('InvAmmo',C.character*16+(C.character==10 and 0 or 1)),countShots(),r('GamePauseStatus')},',')..'\n');log:flush()
 assert(age<110,'Each native case is bounded: '..phase)
 if phase=='grantseed'then pickup(C.cases[index])end
 if phase=='releaseB'and age-current.release_age>=2 then phase='attempt'end
 if phase=='observe'and age-current.observe_age>=6 and current.graphics>=2 then phase='pause';current.cleanup_selected=r('InvSelected',C.character)end
 if phase=='pause'and(r('GamePauseStatus')&1)~=0 then phase='cycle'end
 if phase=='complete'then
  assert(current.attempts==1 and current.cleanup>=1 and current.graphics>=2,'Every attempt, cleanup and displayed publication executed')
  if current.kind=='ryu'then assert(current.grants==1 and current.pickup_collisions==1 and current.slash_inputs==1,'Real activation and pickup owner executed')end
  results[#results+1]=current;index=index+1
  if index>#C.cases then done=true else seed(C.cases[index])end
 end
end,emu.callbackType.exec,C.hooks.PauseSkip.address)
local dma=nil
emu.addMemoryCallback(function(address,value)
 if not entered or done then return end
 dma={case=index,wall=wall,age=age,bytes={}}
 for i=0,255 do dma.bytes[i+1]=emu.read(value*256+i,emu.memType.nesDebug)end
end,emu.callbackType.write,0x4014)
emu.addEventCallback(function()
 local b={}
 if not entered then
  if native()then b.right=true
  elseif wall>=120 and wall%12==0 then
   if r('CrossoverMenuState')~=2 then b.start=true
   elseif r('CrossoverMenuIndex')//6~=C.character//6 then b.down=true
   elseif r('CrossoverMenuIndex')~=C.character then b.right=true else b.a=true end
  end
 elseif not done then
  if phase=='slash'or phase=='primary'or phase=='attempt'then b.b=true
  elseif phase=='fire'then b.select=true
  elseif phase=='pause'then b.start=true
  elseif phase=='cycle'then b.right=true end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1
 if wall==2399 then capture('bounded-timeout');print('TIMEOUT '..json({menu=r('CrossoverMenuState'),index=r('CrossoverMenuIndex'),selected=r('SelectedCharacter'),mode=r('OperMode'),task=r('OperMode_Task'),engine=r('GameEngineSubroutine'),world=world(),phase=phase}))end
 assert(wall<2400,'Bounded native audit')
 if entered and not done and dma and dma.case==index and dma.age>=2 and phase=='observe'and age-current.observe_age>=2 then
  for i=0,255 do assert(emu.read(i,emu.memType.nesSpriteRam)==dma.bytes[i+1],'Exact committed DMA reaches hardware OAM')end
  local body=0
  local rx=world()-(r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'));local py=r('Player_Y_Position')
  for i=0,63 do local a=i*4;local y=dma.bytes[a+1];local x=dma.bytes[a+4];if y>=32 and y<240 and y>=py-16 and y<=py+40 and x>=rx-8 and x<=rx+12 then body=body+1 end end
  if body<2 then
   local parts={};for i=0,63 do local a=i*4;if dma.bytes[a+1]<240 then parts[#parts+1]={y=dma.bytes[a+1],tile=dma.bytes[a+2],attr=dma.bytes[a+3],x=dma.bytes[a+4]}end end
   problem('Native player remains visible in hardware OAM',{oam=parts,dma_age=dma.age,age=age,x=r('Player_X_Position'),scroll=r('ScreenLeft_X_Pos')},false)
  end
  assert(emu.read(0x3f00,emu.memType.nesPpuDebug)==0x22,'Native sky palette preserved')
  current.graphics=current.graphics+1
  if current.graphics<=3 then capture(string.format('case-%02d-observe-%02d-wall-%04d',index,current.graphics,wall))end
 end
 if done then
  assert(nmis>math.min(20,#C.cases*6)and minSP>=128,'Native interrupts and guarded stack exercised')
  local p={passed=#violations==0,cases=results,violations=violations,nmis=nmis,min_sp=minSP,stack_writes=stackWrites,nmi_mapper_store_windows=nmiWindows,staged=true,
   scope='Real selection and controller inputs; explicit legal airborne/equipment/pickup or shared-pool staging at native boundaries. Actual pickup collision/InventoryGrant, source Slash activation, production weapons and paused-selection cleanup. Exact DMA/hardware OAM, sky palette and PPU frames; fiveSMC/NMI/actualbanks/SP guards. No natural pickup emergence, naturally crowded scene, route, full roster, campaign or audio fidelity proof.'}
  local f=assert(io.open(OUTPUT..'proof.json','w'));f:write(json(p));f:close();log:close();writes:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
