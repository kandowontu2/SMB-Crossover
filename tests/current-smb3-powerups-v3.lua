-- Typed source-classified emerging suits; native rise, physical grant and use.
local C=assert(CURRENT_SMB3_POWERUPS)
local wall,updates,age,index=0,0,0,1
local entered,done,writing=false,false,false
local phase,menuPhase='menu','options-focus'
local rec,records=nil,{}
local nmi,irq=nil,false
local minSP,dmas,enables,late,irqCount,nmis,images=255,0,0,0,0,0,0
local mask,pending,upper,physical,chrChecks=0,nil,0,{},0
local screenshot,imagePending=nil,nil
local csv=assert(io.open(OUTPUT..'components.csv','w'))
csv:write('event,wall,update,case,phase,age,form,x,page,y,state,power,fly,wag,statue,shot0,shot1,star,lives,value\n')
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function nr(n)local name=assert(C.native[n],n);return r(name)end
local function bank(at)local p=emu.convertAddress(at);return p and p.address//8192 or-1 end
local function event(kind,value)
 csv:write(table.concat({kind,wall,updates,index,phase,age,r('M3Form'),r('Player_X_Position'),r('Player_PageLoc'),r('Player_Y_Position'),r('Player_State'),nr('Power'),nr('FlyTime'),nr('WagCount'),nr('Statue'),r('M3ShotKind',0),r('M3ShotKind',1),r('StarInvincibleTimer'),r('NumberofLives'),value or 0},',')..'\n')
end
local function json(v)
 if type(v)=='table'then local a={};if #v>0 then for _,x in ipairs(v)do a[#a+1]=json(x)end;return'['..table.concat(a,',')..']'end
  for k,x in pairs(v)do a[#a+1]=string.format('%q',tostring(k))..':'..json(x)end;table.sort(a);return'{'..table.concat(a,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local function hook(name,fn)
 local h=assert(C.hooks[name],name)
 emu.addMemoryCallback(function()
  local yes=false;for _,b in ipairs(h.banks)do if bank(h.pc)==b then yes=true end end;if not yes then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Actual hook '..name)end
  fn(emu.getState())
 end,emu.callbackType.exec,h.pc)
end
local function w(n,v,i)
 assert(writing and not nmi and not irq and r('NmiDisable')==255,'Only native GameLoop+5 typed setup')
 assert(C.setup_allowed[n]and not C.resource_bans[n],'No acquired form/private physics/resource/outcome seed: '..n)
 emu.write(assert(C.ram[n],n)+(i or 0),v&255,emu.memType.nesDebug)
end
local function transaction(fn)assert(not writing and not nmi and not irq and r('NmiDisable')==255);writing=true;fn();writing=false;event('typed-scene-setup')end
local function tile(page,col,row,id)
 local function source(n)local p=C.metatiles[n];return emu.read(p.bank*8192+p.offset+id,emu.memType.nesPrgRom)end
 local function put(a,v)assert(writing and not nmi and not irq);emu.write(a,v,emu.memType.nesPpuDebug)end
 local at=0x2000+page*1024+row*64+col*2
 put(at,source('MTileTopLeft'));put(at+1,source('MTileTopRight'));put(at+32,source('MTileBotLeft'));put(at+33,source('MTileBotRight'))
 local a=0x23c0+page*1024+(row//2)*8+col//2;local shift=row%2*4+col%2*2
 put(a,(emu.read(a,emu.memType.nesPpuDebug)&(~(3<<shift)))|((source('MTileAttribute')>>6)<<shift))
end
local function quiet()
 return r('Player_State')==0 and r('Player_X_Speed')==0 and r('M3Growth')==0 and r('M3Poof')==0 and r('M3ShotKind',0)==0 and r('M3ShotKind',1)==0 and nr('Statue')==0 and nr('FlyTime')==0 and r('Block_State',0)==0 and r('Block_State',1)==0
end
local function actor(kind,x,y,slot,state)
 for _,a in ipairs({{'Enemy_Flag',1},{'Enemy_ID',kind},{'Enemy_State',state or 0},{'Enemy_BoundBoxCtrl',kind==46 and 3 or 9},{'Enemy_X_Position',x},{'Enemy_PageLoc',0},{'Enemy_Y_Position',y},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_Y_MoveForce',0},{'Enemy_MovingDir',1},{'Enemy_SprAttrib',0},{'EnemyOffscrBitsMasked',0},{'Enemy_CollisionBits',0}})do w(a[1],a[2],slot)end
end
local function arena(t)
 assert(quiet(),'Prior native movement/suit/shot/particle cleanup')
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do for row=2,14 do for col=0,15 do tile(p,col,row,row>=13 and 0x54 or 0)end end end
 for p=0,1 do for row=11,12 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+row*16+col)end end end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_CollisionBits',0,i)end
 for _,n in ipairs({'Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','ScrollThirtyTwo','AreaParserTaskNum'})do w(n,0)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('AreaType',t.kind=='swim'and 0 or 1);w('ScrollLock',1);w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_X_Position',t.kind=='flight'and 16 or 112);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',t.face or 1);w('Player_MovingDir',t.face or 1);w('Player_CollisionBits',255)
 if t.kind=='head'then w('Block_Buffer_1',0x51,7*16+7);tile(0,7,9,0x51)end
 if t.kind=='tailblock'then w('Block_Buffer_1',0x51,10*16+8);tile(0,8,12,0x51)end
 if t.kind=='shot'then actor(6,t.form==6 and(t.face==2 and 56 or 176)or(t.face==2 and 80 or 144),184,0,0)end
 if t.kind=='tail'then actor(6,t.face==2 and 88 or 136,184,0,0)end
 if t.kind=='hurt'then actor(6,112,184,0,0)end
 if t.kind=='pickup'then
  local predicted=r('M3Form')==0 and 1 or r('PseudoRandomBitReg',2)%5+2
  assert(predicted==t.to,'Genuine current RNG class before staged emerging pickup')
  rec.rng_at_birth=r('PseudoRandomBitReg',2);actor(46,112,200,5,1)
  w('PowerUpType',1,5);w('InvPickupOwner',17,5);w('InvPickup',0xd0+t.to,5);w('InvRisePhase',0,5)
 elseif t.kind=='star'or t.kind=='life'then actor(46,112,184,5,128);w('PowerUpType',t.kind=='star'and 2 or 3,5);w('InvPickupOwner',17,5);w('InvPickup',0xfc,5)end
end
local function beginCase()
 local t=assert(C.plan[index]);assert(r('M3Form')==t.form,'Carried physically earned form')
 rec={name=t.name,kind=t.kind,age=0,collect=0,started_main=updates,form_before=r('M3Form'),lives_before=r('NumberofLives'),rise_seen=0,peakY=176};records[#records+1]=rec
 phase=t.kind;age=0;transaction(function()arena(t)end);event('case-start')
end
local function complete()
 rec.completed=updates;rec.updates=age;rec.form_after=r('M3Form');rec.lives_after=r('NumberofLives');event('case-complete');index=index+1
 if index>#C.plan then done=true;phase='complete'else phase='setup';age=0 end
end
local function menu()
 if wall<90 or wall%12~=0 then return{}end
 if menuPhase=='options-focus'then menuPhase='options-open';return{down=true}end
 if menuPhase=='options-open'then menuPhase='mode';return{a=true}end
 if menuPhase=='mode'then if r('CrossoverMenuState')~=4 then return{}end;if r('CrossoverOptionsFocus')~=1 then return{down=true}end;if r('CrossoverBehaviorVersion')~=1 then menuPhase='back';return{a=true}end;menuPhase='back'end
 if menuPhase=='back'then menuPhase='start';return{b=true}end
 if menuPhase=='start'then if r('CrossoverMenuState')==2 then menuPhase='select'else return{start=true}end end
 if r('CrossoverMenuState')~=2 then return{}end
 local i=r('CrossoverMenuIndex');if i~=C.menu then return{[assert(C.navigation[i+1])]=true}end
 if r('M3Variant')~=C.variant then return{select=true}end
 return{a=true}
end
hook('GameLoopOwned',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then if r('GameEngineSubroutine')~=8 then return end;assert(r('SelectedCharacter')==17 and r('M3Variant')==C.variant and r('CrossoverBehaviorVersion')==1 and r('CheatInvincible')==0,'Actual cold Hard identity/alternate');entered=true;phase='settle';age=0 end
 updates=updates+1;age=age+1;if rec then rec.render=nil end;assert(updates<5000,'Bounded native Main updates')
 assert(r('SelectedCharacter')==17 and r('M3Variant')==C.variant and r('CrossoverBehaviorVersion')==1 and r('CheatInvincible')==0,'Actual owner/variant/Hard retained')
 if phase=='settle'and age>=30 then assert(r('M3Form')==0 and quiet(),'Actual cold small character');beginCase()
 elseif phase=='setup'then
  local t=C.plan[index];assert(age<512,'Finite genuine random-classification wait')
  if quiet()and(t.kind~='pickup'or t.to==1 or r('PseudoRandomBitReg',2)%5+2==t.to)then beginCase()end
 elseif rec then
  if phase=='statue'and nr('Statue')~=0 and not rec.target then transaction(function()actor(6,112,184,0,0)end);rec.target=true end
  if phase=='star'and r('StarInvincibleTimer')~=0 and not rec.target then transaction(function()actor(6,112,184,0,0)end);rec.target=true;rec.star_grant_at=age end
  if phase=='hurt'and rec.remove then transaction(function()w('Enemy_Flag',0,0);w('Enemy_CollisionBits',0,0)end);rec.remove=false end
  if phase=='swim'and age==91 then transaction(function()w('AreaType',1)end)end
 end
end)
hook('Collect',function(s)
 if not entered or r('PowerUpType',s['cpu.x'])>=2 then return end
 assert(rec and phase=='pickup'and s['cpu.x']==5 and r('Enemy_ID',5)==46 and r('Enemy_Flag',5)~=0 and r('Enemy_State',5)>=128 and r('InvPickupOwner',5)==17 and r('InvPickup',5)==0xd0+C.plan[index].to,'Actual mature source-classified suit collection')
 assert(updates-rec.started_main+1>=48 and rec.collect==0,'No pickup during original48-update emergence');rec.rise_Main_calls=updates-rec.started_main+1;rec.collect=rec.collect+1;rec.collected_at=age;event('actual-suit-collection',C.plan[index].to)
end)
hook('PhysicalPickup',function(s)
 if not entered then return end
 assert(rec and(phase=='star'or phase=='life')and s['cpu.x']==5 and r('Enemy_ID',5)==46 and r('Enemy_State',5)>=128 and r('PowerUpType',5)==(phase=='star'and 2 or 3),'Actual physical Star/1Up collision');rec.physical=(rec.physical or 0)+1;event('actual-physical-common-pickup')
end)
for _,name in ipairs({'Throw','Tail','TailBlock','Defeat','ProjectileDamage','StarContact','LifeIncrement','AreaMusic'})do
 hook(name,function(s)
  if not entered or not rec or phase=='setup'or phase=='settle'then return end
  rec[name]=(rec[name]or 0)+1
  if name=='Defeat'or name=='ProjectileDamage'then assert((phase=='shot'or phase=='tail'or phase=='statue')and s['cpu.x']==0,'Planned real source target damage')end
  if name=='StarContact'then assert(phase=='star'and r('StarInvincibleTimer')>0,'Native protected Star contact');rec.protected=true end
  if name=='LifeIncrement'then assert(phase=='life'and rec.physical==1,'Actual delayed physical1Up popup credit')end
  event('actual-source-'..name,s['cpu.x'])
 end)
end
hook('Injury',function()
 if not entered or not rec then return end
 assert(phase=='hurt'and r('Enemy_Flag',0)~=0 and r('GuestInvulTicks')==0,'Only planned unprotected real contact');assert(not rec.injured,'One injury per phase');rec.injured=true;rec.remove=true;event('actual-native-injury')
end)
hook('RosterReady',function()if entered and rec then rec.roster_update=updates end end)
hook('ShotRender',function()
 if not entered or not rec or phase~='shot'then return end
 local i=r('InvDrawSlot');assert(i<2 and r('M3ShotKind',i)>0,'Real live native shot render slot')
 rec.render={slot=i,kind=r('M3ShotKind',i),x=r('M3ShotX',i),page=r('M3ShotPage',i),y=r('M3ShotY',i),age=r('M3ShotAge',i),wall=wall,update=updates,bankC=bank(0xc000),pointer=r('R0')+256*r('R1')}
end)
local function mainImage()local a={};for i=0,255 do a[i+1]=emu.read(0x200+i,emu.memType.nesDebug)end;return a end
hook('GameLoopFinish',function()
 if not entered or done or not rec or phase=='setup'or phase=='settle'then return end
 local t=C.plan[index];assert(r('MmDeathFlag')==0 and r('GameEngineSubroutine')==8,'No staged death/transition')
 local expected=phase=='pickup'and(rec.collect==1 and t.to or t.form)or phase=='hurt'and(rec.injured and t.to or t.form)or t.form
 assert(r('M3Form')==expected,'Exact native form grant/injury only');assert(r('NumberofLives')==rec.lives_before+((phase=='life'and(rec.LifeIncrement or 0)>0)and 1 or 0),'Exact actual life credit only')
 rec.jump=rec.jump or r('Player_State')~=0;rec.duck=rec.duck or r('CrouchingFlag')~=0;rec.fly=rec.fly or nr('FlyTime')>0;rec.wag=rec.wag or nr('WagCount')>0;rec.hop=rec.hop or nr('FrogHopCnt')>0;rec.swim=rec.swim or(nr('InWater')>0 and r('Player_State')~=0);rec.statue=rec.statue or nr('Statue')>0;rec.peakY=math.min(rec.peakY,r('Player_Y_Position'))
 if phase=='pickup'and r('Enemy_Flag',5)~=0 then rec.rise_seen=rec.rise_seen+1 end
 if(phase=='shot'or phase=='tail'or phase=='statue')and(r('Enemy_State',0)&32~=0 or r('Enemy_Flag',0)==0)then rec.defeated=true;if phase=='statue'then rec.protected=true end end
 if phase=='shot'and(r('M3ShotKind',0)>0 or r('M3ShotKind',1)>0)then rec.live_shot_seen=true end
 if phase=='flight'and nr('Power')==127 and not rec.charged then rec.charged=age;event('naturally-earned-P127')end
 local want=t.picture and rec.roster_update==updates and not rec.pictured and not imagePending and((phase=='pickup'and rec.collect==1 and quiet())or(phase=='shot'and rec.render and(r('M3ShotKind',0)>0 or r('M3ShotKind',1)>0))or(phase=='flight'and nr('FlyTime')>0 and r('Player_Y_Position')<140)or(phase=='swim'and nr('InWater')>0 and r('Player_State')~=0)or(phase=='statue'and nr('Statue')~=0 and rec.protected)or(phase=='star'and rec.protected and r('StarInvincibleTimer')>0)or(phase=='hurt'and rec.injured and quiet()and r('GuestInvulTicks')==0))
 if want then imagePending={name=t.picture,source=mainImage(),record=rec,wall=wall,update=updates,form=r('M3Form'),render=rec.render}end
 local finish=false
 if phase=='pickup'then finish=rec.collect==1 and r('M3Form')==t.to and quiet()and age>=50
 elseif phase=='jump'then finish=rec.jump and quiet()and age>=60
 elseif phase=='head'then finish=rec.duck and r('Block_Buffer_1',7*16+7)==0 and quiet()and age>=100
 elseif phase=='shot'or phase=='tail'then finish=rec.defeated and(phase~='shot'or rec.live_shot_seen)and quiet()and age>=90
 elseif phase=='tailblock'then finish=r('Block_Buffer_1',10*16+8)==0 and quiet()and age>=100
 elseif phase=='flight'then finish=rec.fly and rec.wag and rec.charged and quiet()and age-rec.charged>270
 elseif phase=='swim'then finish=rec.swim and quiet()and age>=150
 elseif phase=='statue'then finish=rec.statue and rec.protected and nr('Statue')==0 and quiet()and age>=100
 elseif phase=='star'then finish=rec.protected and r('StarInvincibleTimer')==0 and(rec.AreaMusic or 0)>0 and quiet()
 elseif phase=='life'then finish=r('NumberofLives')==rec.lives_before+1 and r('FloateyNum_Control',5)==0 and rec.LifeIncrement==1 and quiet()
 elseif phase=='hurt'then finish=rec.injured and r('M3Form')==t.to and r('GuestInvulTicks')==0 and r('InjuryTimer')==0 and quiet()end
 if finish and(not t.picture or rec.pictured)then complete()end
 assert(age<1100,'Finite native component bound');event('update')
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
hook('DmaComplete',function()
 if not imagePending then return end
 local a=imagePending;local yes=true
 for i=1,256 do local want=a.source[i];if(i-1)%4==2 then want=want&0xe3 end;if emu.read(i-1,emu.memType.nesSpriteRam)~=want then yes=false end end
 if yes then a.record.pictured={wall=wall,update=a.update,DMA=dmas,form=a.form,render=a.render};screenshot=a.name;imagePending=nil end
end)
emu.addEventCallback(function()
 if not entered then emu.setInput(menu(),0);return end
 local b={};local t=C.plan[index]
 if t and phase~='setup'and phase~='settle'then
  if phase=='jump'then b.a=age>=7 and age<15
  elseif phase=='head'then b.down=age>=3 and age<15;b.a=age>=21 and age<29
  elseif phase=='shot'or phase=='tail'or phase=='tailblock'then if age>=3 and age<7 then if t.face==2 then b.left=true else b.right=true end end;b.b=age>=7 and age<11
  elseif phase=='flight'then
   if not rec.charged then b.b=true;b.right=true
   elseif age-rec.charged<8 then b.a=true;b.b=true;b.right=true
   elseif age-rec.charged>=12 and age-rec.charged<20 and(age-rec.charged)%4<2 then b.a=true end
  elseif phase=='swim'then if age>=7 and age<17 then b.a=true;b.right=true elseif age>=23 and age<39 then b.a=true;b.up=true elseif age>=44 and age<54 then b.a=true;b.left=true end
  elseif phase=='statue'then b.b=age>=7 and age<11;b.down=age>=7 and age<64 end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1;minSP=math.min(minSP,emu.getState()['cpu.sp'])
 if entered then local s=emu.getState();for i=0,11 do assert(s['mapper.chrBanks'..i]==physical[i],'Actual CHR hardware agrees with write-time latch model');chrChecks=chrChecks+1 end end
 if screenshot then assert(images<8,'At most8 meaningful whole-frame PNGs');local f=assert(io.open(OUTPUT..screenshot,'wb'));f:write(emu.takeScreenshot());f:close();images=images+1;screenshot=nil end
 assert(wall<8000,'At most8000 physical frames')
 if done then
  assert(not pending and not imagePending and dmas>100 and nmis>100 and enables>100 and irqCount>100 and late==0,'Actual strict hardware guards exercised')
  local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=true,native_run=true,ROM_sha256=C.ROM_sha256,identity=C.identity,mode=1,variant=C.variant,records=records,updates=updates,wall=wall,complete256_DMAs=dmas,NMI_checks=nmis,IRQ31_checks=irqCount,NMI_safe_enables=enables,CHR_checks=chrChecks,minSP=minSP,PNGs=images,goal_complete=false,scope=C.scope}));f:close();csv:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
