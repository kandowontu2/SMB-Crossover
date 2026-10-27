-- Narrow current Pit components. Actual tiers/fuel/forms remain ROM-owned.
local C=assert(CURRENT_PIT_POWERUPS)
local wall,updates,age,index=0,0,0,1
local entered,done,writing=false,false,false
local phase,menuPhase='menu',C.mode==1 and'options-focus'or'start'
local rec,records=nil,{}
local nmi,irq=nil,false
local minSP,dmas,enables,late,irqCount,nmis,images=255,0,0,0,0,0,0
local mask,pending,upper,physical,chrChecks=0,nil,0,{},0
local flightPending,screenshot=nil,nil
local csv=assert(io.open(OUTPUT..'pit-components.csv','w'))
csv:write('event,wall,update,case,age,tier,x,y,state,fuel,flight,pose,shots,value\n')
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(at)local p=emu.convertAddress(at);return p and p.address//8192 or-1 end
local function pool()local n=0;for i=0,9 do if r('RgShotType',i)~=0 then n=n+1 end end;return n end
local function event(kind,value)
 csv:write(table.concat({kind,wall,updates,rec and rec.case_index or index,age,r('PlayerStatus'),r('Player_X_Position'),r('Player_Y_Position'),r('Player_State'),r('XgPitFuel'),r('XgPitFlight'),r('RgPose'),pool(),value or 0},',')..'\n')
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
local forbidden={PlayerStatus=true,PlayerSize=true,GuestPowerupActive=true,GuestPowerupTarget=true,InvOwnedLo=true,InvOwnedHi=true,InvAmmo=true,InvSelected=true,XgPitFuel=true,XgPitFlight=true,XgPitBlocked=true,RgShotType=true,RgAttack=true,InjuryTimer=true,GuestHurtTicks=true,MmDeathFlag=true,CheatInvincible=true}
local function w(n,v,i)
 assert(writing and not nmi and not irq and r('NmiDisable')==255,'Only private native GameLoop boundary')
 assert(C.setup_allowed[n]and not forbidden[n],'No tested tier/fuel/form/resource/outcome seeds: '..n)
 emu.write(assert(C.ram[n],n)+(i or 0),v&255,emu.memType.nesDebug)
end
local function transaction(fn)
 assert(not writing and not nmi and not irq and r('NmiDisable')==255,'Synchronous scene setup')
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
local function arena()
 assert(pool()==0 and r('RgAttack')==0 and r('RgShootPose')==0,'Prior native shots/attack really cleaned up')
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do for row=2,14 do for col=0,15 do tile(p,col,row,row>=13 and 0x54 or 0)end end end
 for p=0,1 do for row=11,12 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+row*16+col)end end end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_CollisionBits',0,i)end
 for i=0,3 do w('InvDropKind',0,i)end
 for _,n in ipairs({'Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','ScrollThirtyTwo','AreaParserTaskNum'})do w(n,0)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('ScrollLock',1);w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_X_Position',112);w('Player_PageLoc',0);w('MmOldX',112);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1);w('Player_MovingDir',1);w('Player_CollisionBits',255)
end
local function mature(kind)
 for _,a in ipairs({{'Enemy_Flag',1},{'Enemy_ID',0x2e},{'Enemy_State',128},{'Enemy_BoundBoxCtrl',3},{'Enemy_X_Position',112},{'Enemy_PageLoc',0},{'Enemy_Y_Position',184},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_SprAttrib',0},{'PowerUpType',kind},{'InvPickupOwner',6},{'InvPickup',0xfc}})do w(a[1],a[2],5)end
end
local function target(hammer)
 local x,y=hammer and 136 or 160,hammer and 168 or 184
 if hammer then w('Block_Buffer_1',0x54,168);tile(0,8,12,0x54)end
 for _,a in ipairs({{'Enemy_Flag',1},{'Enemy_ID',6},{'Enemy_State',0},{'Enemy_X_Position',x},{'Enemy_PageLoc',0},{'Enemy_Y_Position',y},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_Y_MoveForce',0},{'Enemy_MovingDir',1},{'Enemy_BoundBoxCtrl',9},{'EnemyOffscrBitsMasked',0},{'Enemy_CollisionBits',0},{'MmEnemyHealthLo',0},{'MmEnemyHealthHi',0},{'MmEnemyFlash',0},{'RgEnemyStun',0}})do w(a[1],a[2],0)end
end
local function beginCase()
 local task=assert(C.plan[index]);assert(r('PlayerStatus')==task.tier,'Cold/physically earned tier retained')
 rec={case_index=index,name=task.name,kind=task.kind,tier=task.tier,started=wall,spawns=0,damage=0,hpWrites=0,transforms=0,collisions=0,burn=0,minFuel=60,flapPoses={},sounds={}}
 records[#records+1]=rec;age=0;phase=task.kind
 transaction(function()arena();if phase=='collect'then mature(task.pickup)elseif phase=='bow'or phase=='hammer'then target(phase=='hammer')end end)
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
 if menuPhase=='mode'then
  if r('CrossoverMenuState')~=4 then return{}end
  if r('CrossoverOptionsFocus')~=1 then return{down=true}end
  if r('CrossoverBehaviorVersion')~=C.mode then menuPhase='back';return{a=true}end
  menuPhase='back'
 end
 if menuPhase=='back'then menuPhase='start';return{b=true}end
 if menuPhase=='start'then if r('CrossoverMenuState')==2 then menuPhase='select'else return{start=true}end end
 if r('CrossoverMenuState')~=2 then return{}end
 local i=r('CrossoverMenuIndex');if i//6~=1 then return{down=true}end;if i~=6 then return{right=true}end;return{a=true}
end
hook('GameLoopOwned',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then
  if r('GameEngineSubroutine')~=8 then return end
  assert(r('SelectedCharacter')==6 and r('CrossoverBehaviorVersion')==C.mode and r('PlayerStatus')==0 and r('CheatInvincible')==0,'Real cold Pit/numeric mode/default cheats')
  entered=true;phase='settle';age=0
 end
 updates=updates+1;age=age+1;assert(updates<=3000,'At most3000 actual updates')
 assert(r('SelectedCharacter')==6 and r('CrossoverBehaviorVersion')==C.mode and r('CheatInvincible')==0,'Owner/mode remain native')
 if phase=='settle'and age>=30 or phase=='setup'then beginCase()end
end)
hook('PhysicalPickup',function(s)
 if entered and phase=='collect'then
  assert(s['cpu.x']==5 and r('Enemy_Flag',5)~=0 and r('Enemy_ID',5)==0x2e and r('Enemy_State',5)>=128,'Real mature actor before erase')
  assert(r('PowerUpType',5)==C.plan[index].pickup,'Actual mushroom/flower actor type');rec.collisions=rec.collisions+1;rec.collisionUpdate=updates;event('actual-mature-collision')
 end
end)
hook('GuestBeginPowerup',function()
 if entered and phase=='collect'then assert(rec.collisionUpdate==updates and r('Enemy_Flag',5)==0 and r('PlayerStatus')==rec.tier,'Real erase precedes actual tier animation');rec.beginSeen=true;event('actual-growth-begin')end
end)
hook('GuestPowerupUpdate',function()
 if entered and phase=='collect'and r('GuestPowerupActive')~=0 then rec.transforms=rec.transforms+1 end
end)
hook('DamageEnemy',function(s)
 if entered and(phase=='bow'or phase=='hammer')and s['cpu.x']==0 then
  assert(r('MmBulletType')==(phase=='bow'and(26+C.plan[index].tier)or 38),'Actual bow/hammer source contact type')
  if phase=='hammer'then assert(r('RgAttackAge')>=4 and r('RgAttackAge')<9,'Actual hammer active window')end
  rec.damage=rec.damage+1;event('actual-source-contact',r('MmBulletType'))
 end
end)
emu.addMemoryCallback(function(_,v)if entered and rec and(phase=='bow'or phase=='hammer')and rec.damage>0 and not writing then rec.hpWrites=rec.hpWrites+1;event('actual-target-health-write',v)end end,emu.callbackType.write,C.ram.MmEnemyHealthLo,C.ram.MmEnemyHealthHi)
emu.addMemoryCallback(function(_,v)if entered and rec and v==1 and not writing then rec.spawns=rec.spawns+1;rec.firstShotDMA=rec.firstShotDMA or dmas;event('actual-bow-spawn')end end,emu.callbackType.write,C.ram.RgShotType,C.ram.RgShotType+9)
emu.addMemoryCallback(function(_,v)if entered and rec and not writing and v~=0 then rec.sounds[v]=true end end,emu.callbackType.write,C.ram.Square1SoundQueue)
hook('PitFlightEntry',function(s)
 if not entered or not(phase=='gate'or phase=='fullflight'or phase=='releaseflight')then return end
 assert(not flightPending,'No nested PitFlight owner')
 local sp=s['cpu.sp'];local ret=emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug)
 assert((ret+1)%65536==C.flight_return_PC,'Genuine compiled ExpandedMovement farcall continuation')
 flightPending={sp=sp,ret=ret,owner=rec,state=r('Player_State'),tier=r('PlayerStatus'),fuel=r('XgPitFuel'),flight=r('XgPitFlight'),a=r('A_B_Buttons')&128,down=r('SavedJoypadBits')&4,water=r('MmUnderwater')}
 if r('Player_State')~=0 then rec.airSeen=true end
 if age>=15 and age<30 and r('Player_State')~=0 and r('XgFresh')&128~=0 then rec.secondAirAttempt=true end
end)
local function flightExit(s)
 local before=flightPending;if not before then return end
 assert(s['cpu.sp']==before.sp and before.owner==rec,'Real same-frame leaf return owner/SP')
 local ret=emu.read(256+(before.sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(before.sp+2)%256,emu.memType.nesDebug);assert(ret==before.ret,'Real leaf return word unchanged')
 local active=before.state~=0 and before.state~=3 and before.tier==2 and before.water==0 and before.a~=0 and before.down==0 and before.fuel>0 and before.flight~=0
 if active then
  assert(r('XgPitFuel')==before.fuel-1 and r('XgPitFlight')==1,'Exactly one actual eligible flutter fuel debit')
  assert(r('XgPitBlocked')==0 and r('MmVY')==0 and r('MmVY',1)==128 and r('MmVY',2)==254,'Empty-roof source flutter lift exactly-1.5px/update')
  rec.burn=rec.burn+1;rec.minFuel=math.min(rec.minFuel,r('XgPitFuel'))
 elseif before.state==0 then assert(r('XgPitFuel')==60 and r('XgPitFlight')==0,'Actual grounded source recharge');if rec.burn>0 and not rec.recharged then assert(rec.landedAt and age==rec.landedAt+1,'First actual grounded source return follows collision landing');rec.recharged=true;rec.groundRechargeAt=age;event('actual-ground-recharge',r('XgPitFuel'))end
 else
  assert(r('XgPitFuel')==before.fuel,'Ineligible flutter never spends fuel')
  if before.tier~=2 or before.water~=0 or before.a==0 or before.down~=0 or before.fuel==0 or before.state==3 then assert(r('XgPitFlight')==0,'Native cancellation gate')end
  if before.flight~=0 and before.a==0 and before.fuel>0 then rec.releaseSeen=true end
 end
 flightPending=nil
end
hook('PitFlightStopReturn',flightExit);hook('PitFlightDoneReturn',flightExit)
hook('GameLoopFinish',function()
 if not entered or done or not rec then return end
 assert(not flightPending,'All real flight calls completed before GameLoop return')
 assert(r('MmDeathFlag')==0 and r('InjuryTimer')==0 and r('GuestHurtTicks')==0,'No injury/death/immunity injection')
 local task=C.plan[index]
 if phase=='collect'then
  if rec.transforms==30 and not rec.growthSample then rec.growthSample=true;screenshot=task.name..'.png'end
  if r('GuestPowerupActive')==0 and r('TimerControl')==0 and r('GameEngineSubroutine')==8 and rec.transforms>0 then
   assert(rec.collisions==1 and rec.beginSeen and rec.transforms==60 and r('PlayerStatus')==task.tier+1,'One actual mature pickup and complete60-call transform')
   finishCase()
  end
 else
  assert(r('PlayerStatus')==task.tier and r('GameEngineSubroutine')==8,'Actual acquired tier stays playable')
  if phase=='bow'and rec.firstShotDMA and dmas>=rec.firstShotDMA+2 and pool()>0 and not rec.sample and task.tier==0 then rec.sample=true;screenshot=task.name..'.png'end
  if phase=='hammer'and r('RgAttack')>0 then rec.meleeSeen=true;if not rec.sample then rec.sample=true;if task.tier==1 then screenshot=task.name..'.png'end end end
  if phase=='fullflight'or phase=='releaseflight'then
   if rec.burn>0 and r('XgPitFlight')~=0 then
    local pose=r('RgPose');rec.flapPoses[pose]=true
    assert(pose==C.poses.flap1 or pose==C.poses.flap2 or pose==C.poses.shot1 or pose==C.poses.shot2,'Genuine source flutter/flap-shot pose, no invented art')
   end
   if phase=='fullflight'and rec.burn==1 and not rec.firstFlap then rec.firstFlap=true;screenshot='flutter-first.png'end
   if phase=='fullflight'and rec.burn==30 and not rec.middleFlap then rec.middleFlap=true;screenshot='flutter-bow.png'end
   if rec.burn>0 and r('XgPitFuel')==0 and r('XgPitFlight')==0 then rec.exhausted=true end
   if rec.burn>0 and r('Player_State')==0 and not rec.landedAt then rec.landedAt=age;rec.landingFuel=r('XgPitFuel');event('actual-collision-landing',rec.landingFuel)end
   if rec.landedAt and age==rec.landedAt+1 then assert(rec.recharged and rec.groundRechargeAt==age and r('XgPitFuel')==60 and r('XgPitFlight')==0,'Exactly60 fuel at the first following grounded update');if phase=='fullflight'then screenshot='flutter-landed.png'end end
   if phase=='fullflight'and rec.landedAt and age>rec.landedAt and r('Player_State')~=0 then assert(r('XgPitFuel')==60 and r('XgPitFlight')==0,'Next native grounded jump retains recharge');rec.relaunched=true end
  end
  if age>=task.limit then
   assert(pool()==0 and r('RgAttack')==0 and r('RgShootPose')==0 and r('Player_State')==0,'Actual weapon/motion cleanup before next scene')
   if phase=='bow'then assert(rec.spawns==1 and rec.damage>0 and rec.hpWrites>0,'One real bow shot/contact/native damage')
   elseif phase=='hammer'then assert(rec.meleeSeen and rec.damage>0 and rec.hpWrites>0,'Real hammer/contact/native damage')
   elseif phase=='gate'then assert(rec.airSeen and rec.secondAirAttempt and rec.burn==0 and r('XgPitFuel')==60 and r('XgPitFlight')==0,'Tier0/1 real jump and secondA cannot enable wings')
   elseif phase=='fullflight'then assert(rec.burn==60 and rec.minFuel==0 and rec.exhausted and rec.recharged and rec.relaunched and rec.spawns==1,'Real60fuel/exhaust/landing/rejump and airborne bow')
   elseif phase=='releaseflight'then assert(rec.burn>0 and rec.burn<60 and rec.releaseSeen and rec.recharged and r('XgPitFuel')==60,'Real earlyA release/cancel/landing recharge')end
   finishCase()
  end
 end
 event('update');assert(age<task.limit+120,'Finite component update deadline')
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
 if phase=='bow'then input.b=age>=5 and age<8
 elseif phase=='hammer'then input.select=age>=5 and age<9
 elseif phase=='gate'or phase=='fullflight'or phase=='releaseflight'then
  input.a=age>=4 and age<10 or age>=16 and age<(phase=='releaseflight'and 35 or 110)
  if phase=='fullflight'then input.b=age>=40 and age<43;if rec.landedAt then input.a=input.a or age>=rec.landedAt+2 and age<rec.landedAt+8 end end
 end
 emu.setInput(input,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1;minSP=math.min(minSP,emu.getState()['cpu.sp'])
 if entered then local s=emu.getState();for i=0,11 do assert(s['mapper.chrBanks'..i]==physical[i],'Actual CHR hardware agrees with write-time latch model');chrChecks=chrChecks+1 end end
 if screenshot then assert(images<8,'At most8 actual whole-frame screenshots');local f=assert(io.open(OUTPUT..screenshot,'wb'));f:write(emu.takeScreenshot());f:close();images=images+1;screenshot=nil end
 assert(wall<8000,'At most8000wall frames')
 if done then
  assert(not pending and not flightPending and dmas>100 and irqCount>100 and nmis>100 and enables>100 and late==0,'Full native hardware/source guards exercised')
  local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=true,native_run=true,ROM_sha256=C.ROM_sha256,character=6,mode=C.mode,records=records,wall=wall,updates=updates,complete256_DMAs=dmas,NMI_checks=nmis,IRQ31_checks=irqCount,NMI_safe_enables=enables,CHR_checks=chrChecks,minSP=minSP,screenshots=images,goal_complete=false,scope='Mature mushroom/flower with actual60call transforms, native bow/hammer/jump and source60fuel wing flutter. No emergence/RNG/star/1up/campaign/allpixel/audio fidelity claim.'}));f:close();csv:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
