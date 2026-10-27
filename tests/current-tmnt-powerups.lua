-- Current TMNT earned components. Typed scenes, never owned-resource seeds.
local C=assert(CURRENT_TMNT_POWERUPS)
local wall,updates,age,index=0,0,0,1
local entered,done,writing=false,false,false
local phase,menuPhase='menu',C.mode==1 and'options-focus'or'start'
local rec,records=nil,{}
local nmi,irq=nil,false
local minSP,dmas,enables,late,irqCount,nmis,images=255,0,0,0,0,0,0
local mask,pending,upper,physical,chrChecks=0,nil,0,{},0
local screenshot
local csv=assert(io.open(OUTPUT..'tmnt-components.csv','w'))
csv:write('event,wall,update,case,age,health,food,gear,ammo,selected,x,y,state,hurt,injury,shots,value\n')
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(at)local p=emu.convertAddress(at);return p and p.address//8192 or-1 end
local function pool()local n=0;for i=0,2 do if r('TnShotKind',i)~=0 then n=n+1 end end;return n end
local function health()return r('TnHealth',C.variant)end
local function ammo()return r('TnAmmo',C.variant)end
local function gear()return r('TnEquipment',C.variant)end
local function event(kind,value)
 csv:write(table.concat({kind,wall,updates,index,age,health(),r('TnFood'),gear(),ammo(),r('TnGearSelected'),r('Player_X_Position'),r('Player_Y_Position'),r('Player_State'),r('TnHurt'),r('InjuryTimer'),pool(),value or 0},',')..'\n')
end
local function json(v)
 if type(v)=='table'then local out={};if #v>0 then for _,x in ipairs(v)do out[#out+1]=json(x)end;return'['..table.concat(out,',')..']'end
  for k,x in pairs(v)do out[#out+1]=string.format('%q',tostring(k))..':'..json(x)end;table.sort(out);return'{'..table.concat(out,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local function hook(name,fn)
 local h=assert(C.hooks[name],name)
 emu.addMemoryCallback(function()
  local actual=bank(h.pc);local allowed=false;for _,b in ipairs(h.banks)do if actual==b then allowed=true end end
  if not allowed then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Actual hook '..name)end
  fn(emu.getState())
 end,emu.callbackType.exec,h.pc)
end
local forbidden={PlayerStatus=true,PlayerSize=true,GuestPowerupActive=true,GuestPowerupTarget=true,InvOwnedLo=true,InvOwnedHi=true,InvAmmo=true,InvSelected=true,TnHealth=true,TnEquipment=true,TnAmmo=true,TnFood=true,TnMarker=true,TnLife=true,TnVariant=true,TnDropCounter=true,TnGearSelected=true,TnAttack=true,TnThrow=true,TnHurt=true,TnHurtMove=true,TnShotKind=true,TnEnemyHP=true,TnEnemyType=true,TnEnemyHurt=true,TnDropReceipt=true,InjuryTimer=true,GuestHurtTicks=true,MmDeathFlag=true,CheatInvincible=true,PseudoRandomBitReg=true}
local function w(n,v,i)
 assert(writing and not nmi and not irq and r('NmiDisable')==255,'Only private native GameLoop boundary')
 assert(C.setup_allowed[n]and not forbidden[n],'No ownership/resource/attack/hurt/RNG/result seeds: '..n)
 emu.write(assert(C.ram[n],n)+(i or 0),v&255,emu.memType.nesDebug)
end
local function transaction(fn)
 assert(not writing and not nmi and not irq and r('NmiDisable')==255,'Synchronous scene owner')
 writing=true;fn();writing=false;event('disclosed-scene-setup')
end
local function tile(page,col,row,id)
 assert(writing and not nmi and not irq,'Same native setup owner')
 local function source(n)local p=C.metatiles[n];return emu.read(p.bank*8192+p.offset+id,emu.memType.nesPrgRom)end
 local function put(a,v)emu.write(a,v,emu.memType.nesPpuDebug)end
 local at=0x2000+page*1024+row*64+col*2
 put(at,source('MTileTopLeft'));put(at+1,source('MTileTopRight'));put(at+32,source('MTileBotLeft'));put(at+33,source('MTileBotRight'))
 local a=0x23c0+page*1024+(row//2)*8+col//2;local shift=row%2*4+col%2*2
 put(a,(emu.read(a,emu.memType.nesPpuDebug)&(~(3<<shift)))|((source('MTileAttribute')>>6)<<shift))
end
local function quiet()return pool()==0 and r('TnAttack')==0 and r('TnThrow')==0 and r('TnHurt')==0 and r('InjuryTimer')==0 and r('Player_State')==0 end
local function arena(face)
 assert(quiet(),'Prior native actors/hurt really finished before new scene')
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do for row=2,14 do for col=0,15 do tile(p,col,row,row>=13 and 0x54 or 0)end end end
 for p=0,1 do for row=11,12 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+row*16+col)end end end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_CollisionBits',0,i)end
 for _,n in ipairs({'Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','TnVXHi','TnVXLo','TnVYHi','TnVYLo','TnXFraction','TnYFraction','ScrollThirtyTwo','AreaParserTaskNum'})do w(n,0)end
 w('ScrollLock',1);w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_X_Position',112);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',face);w('Player_MovingDir',face);w('Player_CollisionBits',255)
end
local function actor(x,y,kind,slot)
 for _,a in ipairs({{'Enemy_Flag',1},{'Enemy_ID',kind},{'Enemy_State',kind==0x2e and 128 or 0},{'Enemy_BoundBoxCtrl',kind==0x2e and 3 or 9},{'Enemy_X_Position',x},{'Enemy_PageLoc',0},{'Enemy_Y_Position',y},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_Y_MoveForce',0},{'Enemy_MovingDir',1},{'Enemy_SprAttrib',0},{'EnemyOffscrBitsMasked',0},{'Enemy_CollisionBits',0}})do w(a[1],a[2],slot)end
end
local function target(face,contact)
 local x,y=contact and 112 or(face==1 and 140 or 88),contact and 184 or 168
 if not contact then for col=x//16,(x+16)//16 do w('Block_Buffer_1',0x54,160+col);tile(0,col,12,0x54)end end
 actor(x,y,6,0)
end
local function pickup(task)
 actor(112,184,0x2e,5);w('PowerUpType',task.pickup,5);w('InvPickupOwner',19,5)
 w('InvPickup',task.kind=='kiai'and 0xb4 or 0xfc,5);w('TnPickupStamp',task.kind=='kiai'and 4 or 0,5)
end
local function drop(kind)
 assert(r('TnDropKind',0)==0,'Previous native private pickup consumed')
 w('TnDropKind',kind,0);w('TnDropX',120,0);w('TnDropPage',0,0);w('TnDropY',184,0);w('TnDropTimer',120,0)
end
local function beginCase()
 local task=assert(C.plan[index]);assert(health()==task.health,'Earned health carried between components')
 rec={name=task.name,kind=task.kind,started=wall,health=health(),food=r('TnFood'),gear=gear(),ammo=ammo(),collisions=0,grants=0,hits=0,contacts=0,spawns=0,debits=0,refunds=0,toggles=0}
 records[#records+1]=rec;phase=task.kind;age=0
 transaction(function()arena(task.face or 1);if phase=='primary'or phase=='weapon'then target(task.face or 1,false)elseif phase=='contact'then target(1,true)elseif phase=='food'or phase=='kiai'then pickup(task)elseif phase=='gear'then drop(task.gear)end end)
 event('case-start')
end
local function finishCase()
 rec.completed=wall;rec.updates=age;event('case-complete');index=index+1
 if index>#C.plan then done=true;phase='complete'else phase='setup'end
end
local function menu()
 if wall<90 or wall%12~=0 then return{}end
 if menuPhase=='options-focus'then menuPhase='options-open';return{down=true}end
 if menuPhase=='options-open'then menuPhase='mode';return{a=true}end
 if menuPhase=='mode'then if r('CrossoverMenuState')~=4 then return{}end;if r('CrossoverOptionsFocus')~=1 then return{down=true}end;if r('CrossoverBehaviorVersion')~=C.mode then menuPhase='back';return{a=true}end;menuPhase='back'end
 if menuPhase=='back'then menuPhase='start';return{b=true}end
 if menuPhase=='start'then if r('CrossoverMenuState')==2 then menuPhase='select'else return{start=true}end end
 if r('CrossoverMenuState')~=2 then return{}end
 local i=r('CrossoverMenuIndex');if i~=18 then return{down=true}end
 if r('TnVariant')~=C.variant then return{select=true}end
 return{a=true}
end
hook('GameLoopOwned',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then
  if r('GameEngineSubroutine')~=8 then return end
  assert(r('SelectedCharacter')==19 and r('TnVariant')==C.variant and r('CrossoverBehaviorVersion')==C.mode and r('CheatInvincible')==0,'Real cold menu owner/alternate/mode/cheats')
  entered=true;phase='settle';age=0
 end
 updates=updates+1;age=age+1;assert(updates<=3500,'At most3500 real updates')
 assert(r('SelectedCharacter')==19 and r('TnVariant')==C.variant and r('CrossoverBehaviorVersion')==C.mode and r('CheatInvincible')==0,'Native identity/mode retained')
 if phase=='settle'and age>=30 then
  for i=0,3 do assert(r('TnHealth',i)==128 and r('TnEquipment',i)==0 and r('TnAmmo',i)==0,'Real source cold initializer all4 independent turtles')end
  assert(r('TnFood')==0 and quiet(),'Cold actor ready');beginCase()
 elseif phase=='setup'and quiet()then beginCase()
 elseif rec and phase=='contact'then
  if rec.remove then transaction(function()w('Enemy_Flag',0,0);w('Enemy_CollisionBits',0,0)end);rec.remove=false;rec.separated=updates end
  if rec.rearm and quiet()and updates>rec.separated then transaction(function()arena(1);target(1,true)end);rec.rearm=false end
 elseif rec and phase=='gear'and rec.nextDrop then transaction(function()drop(C.plan[index].gear)end);rec.nextDrop=false end
end)
hook('PhysicalPickup',function(s)
 if entered and(phase=='food'or phase=='kiai')then
  assert(s['cpu.x']==5 and r('Enemy_Flag',5)~=0 and r('Enemy_ID',5)==0x2e and r('Enemy_State',5)>=128,'Actual mature actor collision before native erase')
  assert(r('PowerUpType',5)==C.plan[index].pickup,'Actual food/flower kind');rec.collisions=rec.collisions+1;rec.collisionUpdate=updates;event('physical-mature-collision')
 end
end)
hook('GiveEquipment',function(s)
 if not entered or not rec then return end
 assert(phase=='gear'or phase=='kiai','No unexpected earned gear grant')
 local task=C.plan[index];local kind=phase=='kiai'and 4 or task.gear
 assert(s['cpu.a']==kind and r('TnVariant')==C.variant,'Actual native gear kind/index')
 if phase=='gear'then assert(r('TnDropKind',0)==kind and r('TnDropTimer',0)>0,'Live private physical drop before source collection')else assert(rec.collisionUpdate==updates and r('InvPickup',5)==0xb4 and r('TnPickupStamp',5)==4,'Classified Kiai flower at actual source collection')end
 rec.pendingGrant={gear=kind,ammo=gear()==kind and math.min(ammo()+20,99)or 20};rec.grants=rec.grants+1;event('actual-source-grant',kind)
end)
hook('InjuryStart',function()
 if entered and rec and r('TnHurt')==0 then
  assert(phase=='contact'and not rec.pendingHit and rec.hits<C.plan[index].hits,'Only real planned body contacts hurt')
  assert(r('Enemy_Flag',0)~=0 and r('Enemy_ID',0)==6,'Actual live Goomba contact actor')
  rec.pendingHit=health()-16;event('actual-injury-entry')
 end
end)
for _,name in ipairs({'PrimaryDefeat','ShotDefeat'})do hook(name,function(s)
 if entered and rec then assert((phase=='primary'or phase=='weapon')and s['cpu.x']==0 and r('TnEnemyHP',0)>0,'Real native weapon contact before source defeat');rec.contacts=rec.contacts+1;event('actual-native-weapon-contact',r('TnDamageNow'))end
end)end
hook('BoomRefund',function()
 if entered and rec then assert(phase=='weapon'and C.plan[index].gear==3,'Actual returning boomerang source');rec.refunds=rec.refunds+1;event('actual-catch-refund')end
end)
emu.addMemoryCallback(function(_,v)
 if entered and rec and not writing and v~=0 then assert(phase=='weapon'and v==C.plan[index].gear,'Only native tested secondary actor births');rec.spawns=rec.spawns+1;rec.shotDMA=rec.shotDMA or dmas;event('actual-secondary-birth',v)end
end,emu.callbackType.write,C.ram.TnShotKind,C.ram.TnShotKind+2)
emu.addMemoryCallback(function(a,v)
 if entered and rec and not writing and a==C.ram.TnAmmo+C.variant and phase=='weapon'and v==ammo()-1 then rec.debits=rec.debits+1;event('actual-one-ammo-debit',v)end
end,emu.callbackType.write,C.ram.TnAmmo,C.ram.TnAmmo+3)
hook('GameLoopFinish',function()
 if not entered or done then return end
 for i=0,3 do if i~=C.variant then assert(r('TnHealth',i)==128 and r('TnEquipment',i)==0 and r('TnAmmo',i)==0,'Other turtles retain independent cold resources')end end
 if not rec or phase=='setup'or phase=='settle'then return end
 assert(r('MmDeathFlag')==0 and r('GameEngineSubroutine')==8,'No native death/hidden transition')
 local task=C.plan[index]
 if rec.contacts>0 and r('Enemy_State',0)&0x20~=0 then rec.defeatSeen=true end
 if rec.pendingHit then assert(health()==rec.pendingHit and r('TnHurt')>0 and r('InjuryTimer')>0,'Native contact exact16HP loss plus real hurt timers');rec.hits=rec.hits+1;rec.pendingHit=nil;rec.remove=true;rec.rearm=rec.hits<task.hits end
 if rec.pendingGrant then assert(gear()==rec.pendingGrant.gear and ammo()==rec.pendingGrant.ammo and r('TnGearSelected')==1,'Native same-kind+20/cap99 or replacement20/autoselect');rec.pendingGrant=nil;if phase=='gear'and rec.grants<task.count then rec.nextDrop=true end end
 if phase=='food'then
  if rec.collisions>0 then assert(rec.collisions==1 and r('Enemy_Flag',5)==0 and health()==math.min(rec.health+task.heal,128)and r('TnFood')==1-rec.food and r('GuestPowerupActive')==0,'Physical food heals/caps/toggles food without invented tier transform');if age>=8 then if task.picture then screenshot=task.picture end;finishCase()end end
 elseif phase=='kiai'then if rec.grants==1 then assert(rec.collisions==1 and r('Enemy_Flag',5)==0 and gear()==4 and ammo()==20 and health()==128,'Full-health classified flower grants native Kiai');if age>=8 then screenshot=task.picture;finishCase()end end
 elseif phase=='gear'then if rec.grants==task.count and r('TnDropKind',0)==0 then assert(gear()==task.gear and ammo()==task.stock,'Actual physical pickup stock result');finishCase()end
 elseif phase=='contact'then if rec.hits==task.hits and not rec.remove and quiet()then assert(health()==rec.health-16*task.hits and rec.separated<updates,'Actual separated contacts/restoration deficit');finishCase()end
 elseif phase=='select'then
  if r('TnGearSelected')~=rec.previousSelect then if rec.previousSelect~=nil then rec.toggles=rec.toggles+1;event('actual-select-toggle',r('TnGearSelected'))end;rec.previousSelect=r('TnGearSelected')end
  if age>=26 then assert(rec.toggles==2 and r('TnGearSelected')==1 and gear()==rec.gear and ammo()==rec.ammo,'Select switches primary/gear without stock cost');finishCase()end
 elseif phase=='primary'or phase=='weapon'then
  if task.picture and not rec.pictured and(phase=='primary'and r('TnPose',1)~=0 or phase=='weapon'and pool()>0 and dmas>(rec.shotDMA or dmas))then screenshot=task.picture;rec.pictured=true end
  if age>=35 and quiet()then
   assert(rec.contacts==1 and rec.defeatSeen,'Actual recorded target defeat and later cleanup')
   if phase=='primary'then assert(rec.spawns==0 and gear()==0 and ammo()==0,'Native primary uses no owned projectile ammo')
   else assert(rec.spawns==(task.gear==2 and 3 or 1)and rec.debits==1 and rec.refunds==(task.gear==3 and 1 or 0),'One native volley/cost and actual catch only for boomerang');assert(ammo()==rec.ammo-1+rec.refunds and gear()==task.gear,'Exact earned stock conservation');if task.gear==3 then screenshot=task.catch_picture end end
   finishCase()
  end
 end
 event('update');assert(age<task.limit,'Finite component deadline')
end)
-- All callback registration is startup-static. No callback adds/removes callbacks.
local function bytes(at,kind)local t={};for i=0,255 do t[i+1]=emu.read(at+i,kind or emu.memType.nesDebug)end;return t end
local function equal(a,b)for i=1,256 do if a[i]~=b[i]then return false end end;return true end
local function smc()local t={};for i,a in ipairs(C.smc)do t[i]=emu.read(a,emu.memType.nesDebug)end;return t end
local function store(pc,target)return emu.read(pc,emu.memType.nesDebug)==0x8d and emu.read(pc+1,emu.memType.nesDebug)==target%256 and emu.read(pc+2,emu.memType.nesDebug)==target//256 end
local function publicationWindow(pc,target,shadow)
 if store(pc,target)then return store(pc-3,shadow)or(emu.read(pc-2,emu.memType.nesDebug)==0xa9 and store(pc-5,shadow))end
 return emu.read(pc,emu.memType.nesDebug)==0xa9 and store(pc+2,target)and store(pc-3,shadow)
end
hook('NmiEntry',function(s)
 assert(not nmi,'No recursive NMI')
 local sp=s['cpu.sp'];local pc=emu.read(256+(sp+2)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+3)%256,emu.memType.nesDebug)
 nmi={a=s['cpu.a'],x=s['cpu.x'],y=s['cpu.y'],sp=sp,fields=smc(),ba=r('CurrentBank'),bc=r('CurrentBankC'),pa=bank(0xa000),pc=bank(0xc000)}
 nmi.wa=nmi.pa~=(nmi.ba&127)and publicationWindow(pc,0x5115,C.ram.CurrentBank)
 nmi.wc=nmi.pc~=(nmi.bc&127)and publicationWindow(pc,0x5116,C.ram.CurrentBankC);nmis=nmis+1
end)
hook('NmiReturn',function(s)
 assert(nmi and s['cpu.a']==nmi.a and s['cpu.x']==nmi.x and s['cpu.y']==nmi.y and s['cpu.sp']==nmi.sp,'NMI AXY/SP restored')
 for i,v in ipairs(smc())do assert(v==nmi.fields[i],'NMI five SMC operands restored')end
 assert(r('CurrentBank')==nmi.ba and r('CurrentBankC')==nmi.bc,'NMI bank shadows restored')
 assert(bank(0xa000)==(nmi.wa and(nmi.ba&127)or nmi.pa)and bank(0xc000)==(nmi.wc and(nmi.bc&127)or nmi.pc),'Actual foreground banks restored, including verified publication window');nmi=nil
end)
hook('IrqEntry',function()assert(not irq,'No nested IRQ');irq=true;if entered and r('Sprite0HitDetectFlag')~=0 then assert(emu.getState()['ppu.scanline']==31,'Actual HUD IRQ31');irqCount=irqCount+1 end end)
hook('IrqReturn',function()irq=false end)
emu.addMemoryCallback(function(_,v)mask=v end,emu.callbackType.write,0x2001)
emu.addMemoryCallback(function(_,v)
 assert(not pending and mask&24==0,'Rendering disabled at actual DMA start')
 local s=emu.getState();assert(v==2 and s['cpu.pc']==C.dma_store_return,'Actual native page2 DMA owner')
 assert(s['ppu.spriteRamAddr']==0,'Actual native DMA begins at OAM address zero')
 pending={source=bytes(v*256),writes=0}
end,emu.callbackType.write,0x4014)
emu.addMemoryCallback(function(_,v)
 assert(pending and mask&24==0,'Actual DMA byte while rendering disabled')
 local i=pending.writes+1
 assert(i<=256 and v==pending.source[i]and emu.getState()['ppu.spriteRamAddr']==i-1,'All256 raw DMA source/value/destination bytes match')
 pending.writes=i
end,emu.callbackType.write,0x2004)
hook('DmaComplete',function()
 if not pending then return end
 local hw=bytes(0,emu.memType.nesSpriteRam);local same=true
 for i=1,256 do local want=pending.source[i];if(i-1)%4==2 then want=want&0xe3 end;if hw[i]~=want then same=false end end
 assert(pending.writes==256 and mask&24==0 and emu.getState()['ppu.spriteRamAddr']==0 and same,'All256 physical OAM bytes match hardware attribute E3 semantics')
 pending=nil;dmas=dmas+1
end)
emu.addMemoryCallback(function(_,v)
 if entered and nmi and v&24~=0 then
  local s=emu.getState();local line,dot=s['ppu.scanline'],s['ppu.cycle'];enables=enables+1
  local safe=line>=241 and line<=260 or line==-1 and dot<=274
  if not safe then late=late+1 end;assert(safe,'Actual NMI render enable deadline')
 end
end,emu.callbackType.write,0x2001)
emu.addMemoryCallback(function()if entered then assert(emu.getState()['cpu.sp']>=128,'Actual lower stack guard')end end,emu.callbackType.write,0x17f)
emu.addMemoryCallback(function(_,v)upper=v&3 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(a,v)physical[a-0x5120]=v+256*upper end,emu.callbackType.write,0x5120,0x512b)
emu.addEventCallback(function()
 if not entered then emu.setInput(menu(),0);return end
 local input={}
 if phase=='primary'or phase=='weapon'then input.b=age>=8 and age<12
 elseif phase=='select'then input.select=age>=5 and age<9 or age>=16 and age<20 end
 emu.setInput(input,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1;minSP=math.min(minSP,emu.getState()['cpu.sp'])
 if entered then local s=emu.getState();for i=0,11 do assert(s['mapper.chrBanks'..i]==physical[i],'Actual CHR hardware agrees with write-time latch model');chrChecks=chrChecks+1 end end
 if screenshot then assert(images<8,'At most8 meaningful whole-frame PNGs');local f=assert(io.open(OUTPUT..screenshot,'wb'));f:write(emu.takeScreenshot());f:close();images=images+1;screenshot=nil end
 assert(wall<8000,'At most8000 physical frames')
 if done then
  assert(not pending and dmas>100 and irqCount>100 and nmis>100 and enables>100 and late==0,'Native hardware/source guards really exercised')
  local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=true,native_run=true,ROM_sha256=C.ROM_sha256,identity=C.identity,variant=C.variant,actual_mode=C.mode,records=records,wall=wall,updates=updates,complete256_DMAs=dmas,NMI_checks=nmis,IRQ31_checks=irqCount,NMI_safe_enables=enables,CHR_checks=chrChecks,minSP=minSP,screenshots=images,goal_complete=false,scope=C.scope}));f:close();csv:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
