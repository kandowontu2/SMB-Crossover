-- Earned Chip/Dale components. Staged terrain/actors; native health/boxes/lives only.
local C=assert(CURRENT_CHIP_DALE)
local wall,updates,age,index=0,0,0,1
local entered,done,writing=false,false,false
local phase,menuPhase='menu','options-focus'
local rec,records=nil,{}
local nmi,irq=nil,false
local minSP,dmas,enables,late,irqCount,nmis,images=255,0,0,0,0,0,0
local mask,pending,upper,physical,chrChecks=0,nil,0,{},0
local screenshot
local csv=assert(io.open(OUTPUT..'earned-components.csv','w'))
csv:write('event,wall,update,case,phase,age,HP,status,held,hide,throwAge,lives,value,pc,bank,cycle\n')
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(at)local p=emu.convertAddress(at);return p and p.address//8192 or-1 end
local function event(kind,value)
 local s=emu.getState();csv:write(table.concat({kind,wall,updates,index,phase,age,r('CdHealth'),r('PlayerStatus'),r('CdHeld'),r('CdHide'),r('CdThrowAge'),r('NumberofLives'),value or 0,s['cpu.pc'],bank(s['cpu.pc']),s['cpu.cycleCount']},',')..'\n')
end
local function json(v)
 if type(v)=='table'then local out={};if #v>0 then for _,x in ipairs(v)do out[#out+1]=json(x)end;return'['..table.concat(out,',')..']'end
  for k,x in pairs(v)do out[#out+1]=string.format('%q',tostring(k))..':'..json(x)end;table.sort(out);return'{'..table.concat(out,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local function hook(name,fn)
 local h=assert(C.hooks[name],name)
 emu.addMemoryCallback(function()
  local ok=false;for _,b in ipairs(h.banks)do if bank(h.pc)==b then ok=true end end;if not ok then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Actual hook '..name)end
  fn(emu.getState())
 end,emu.callbackType.exec,h.pc)
end
local function w(n,v,i)
 assert(writing and not nmi and not irq and r('NmiDisable')==255,'Actual GameLoop+5 scene owner excludes interrupts')
 assert(C.setup_allowed[n]and not C.forbidden[n],'No acquired health/box/life/outcome seed: '..n)
 emu.write(assert(C.ram[n],n)+(i or 0),v&255,emu.memType.nesDebug)
end
local function transaction(fn)
 assert(not writing and not nmi and not irq and r('NmiDisable')==255,'Genuine setup boundary')
 writing=true;fn();writing=false;event('disclosed-scene-setup')
end
local function tile(page,col,row,id)
 assert(writing and not nmi and not irq,'Same genuine map owner')
 local function source(n)local p=C.metatiles[n];return emu.read(p.bank*8192+p.offset+id,emu.memType.nesPrgRom)end
 local function put(a,v)emu.write(a,v,emu.memType.nesPpuDebug)end
 local at=0x2000+page*1024+row*64+col*2
 put(at,source('MTileTopLeft'));put(at+1,source('MTileTopRight'));put(at+32,source('MTileBotLeft'));put(at+33,source('MTileBotRight'))
 local a=0x23c0+page*1024+(row//2)*8+col//2;local shift=row%2*4+col%2*2
 put(a,(emu.read(a,emu.memType.nesPpuDebug)&(~(3<<shift)))|((source('MTileAttribute')>>6)<<shift))
end
local function boxCount()
 local n=0;for i=0,5 do if r('CdBoxKind',i)~=0 then n=n+1 end end;return n
end
local function arena()
 for i=0,5 do assert(r('CdBoxKind',i)==0 or r('CdBoxMode',i)~=2,'Prior thrown objects genuinely expired')end
 assert(r('CdThrowAge')==0,'Prior authentic throw animation expired')
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do for row=2,14 do for col=0,15 do tile(p,col,row,row>=13 and 0x54 or 0)end end end
 for p=0,1 do for row=11,12 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+row*16+col)end end end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_CollisionBits',0,i)end
 for i=0,3 do w('InvDropKind',0,i)end
 for _,n in ipairs({'Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','ScrollThirtyTwo','AreaParserTaskNum'})do w(n,0)end
 for _,a in ipairs({{'MmVX',3},{'MmVY',3},{'MmXFraction',2},{'MmYFraction',2}})do for i=0,a[2]-1 do w(a[1],0,i)end end
 for _,a in ipairs({{'ScrollLock',1},{'ScreenLeft_X_Pos',0},{'ScreenLeft_PageLoc',0},{'ScreenRight_X_Pos',255},{'ScreenRight_PageLoc',0},{'Player_X_Position',112},{'Player_PageLoc',0},{'MmOldX',112},{'Player_Y_Position',176},{'Player_Y_HighPos',1},{'Player_State',0},{'PlayerFacingDir',1},{'Player_MovingDir',1},{'Player_CollisionBits',255}})do w(a[1],a[2])end
end
local function enemy(x,y)
 for _,a in ipairs({{'Enemy_Flag',1},{'Enemy_ID',6},{'Enemy_State',0},{'Enemy_X_Position',x},{'Enemy_PageLoc',0},{'Enemy_Y_Position',y},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_Y_MoveForce',0},{'Enemy_MovingDir',1},{'Enemy_BoundBoxCtrl',9},{'EnemyOffscrBitsMasked',0},{'Enemy_CollisionBits',0},{'MmEnemyHealthLo',0},{'MmEnemyHealthHi',0},{'MmEnemyFlash',0},{'RgEnemyStun',0}})do w(a[1],a[2],0)end
end
local function mature(pickup)
 for _,a in ipairs({{'Enemy_Flag',1},{'Enemy_ID',46},{'Enemy_State',128},{'Enemy_BoundBoxCtrl',3},{'Enemy_X_Position',112},{'Enemy_PageLoc',0},{'Enemy_Y_Position',184},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_SprAttrib',0},{'PowerUpType',pickup},{'InvPickupOwner',255},{'InvPickup',252}})do w(a[1],a[2],5)end
end
local function change(p)phase=p;age=0;event('phase')end
local function beginCase()
 local task=assert(C.plan[index]);rec={name=task.name,kind=task.kind,started=wall,HP_before=r('CdHealth'),status_before=r('PlayerStatus'),held_before=r('CdHeld'),lives_before=r('NumberofLives'),last_health=r('CdHealth'),collisions=0,food_entries=0,food_accepts=0,defeats=0,releases=0,health_writes={},life_increment=0,life_writes=0}
 records[#records+1]=rec
 assert(r('CdHealth')>0 and r('CdHurtTimer')==0 and r('InjuryTimer')==0,'No protection carried into a new component')
 if task.kind=='entrance'or task.kind=='lift'then assert(r('CdHeld')==0,'Acquire a real box, never seed held')end
 if task.kind=='hide'or task.kind=='life'or task.kind=='throw'then assert(r('CdHeld')>0,'Genuinely acquired prior held object')end
 if task.kind=='life'then assert(r('CdHealth')==3 and r('PlayerStatus')==1,'Real mushroom benefit before1Up')end
 transaction(function()
  arena()
  if task.kind=='entrance'then
   local found
   for i=0,5 do if r('CdBoxKind',i)~=0 and r('CdBoxMode',i)==0 then assert(not found,'One genuine entrance crate');found=i+1 end end
   assert(found,'Real CdSpawnEntrance created the crate');local i=found-1;local x=r('CdBoxX',i)-16
   assert(r('CdBoxPage',i)==0 and x>=24 and x<=208 and r('CdBoxY',i)>=176 and r('CdBoxY',i)<=208,'Native entrance object in reachable ground band')
   w('Player_X_Position',x);w('MmOldX',x);rec.entrance_slot=i
  elseif task.kind=='food'then mature(task.pickup)
  elseif task.kind=='life'then mature(3)
  elseif task.kind=='lift'then assert(boxCount()==0,'Previous real objects gone');w('Block_Buffer_1',0x51,10*16+8);tile(0,8,12,0x51)
  elseif task.kind=='hurt'then enemy(116,184)end
 end)
 change(task.kind)
end
local function finishCase()
 rec.completed=wall;rec.updates=age;rec.HP_after=r('CdHealth');rec.status_after=r('PlayerStatus');rec.held_after=r('CdHeld');rec.lives_after=r('NumberofLives');event('case-complete')
 if index==#C.plan then done=true;change('complete')else index=index+1;change('setup')end
end
local function controlledTarget()
 if rec.target or not rec.sampled then return end
 if phase=='hide'then transaction(function()enemy(116,184)end);rec.target=true;event('actual-hide-contact-target');return end
 if phase=='throw'and rec.thrown_slot then
  local i=rec.thrown_slot;local x,y=r('CdBoxX',i),r('CdBoxY',i)
  if r('CdBoxKind',i)~=0 and r('CdBoxMode',i)==2 and r('CdBoxPage',i)==0 and x>=80 and x<=220 and y>=56 and y<=184 then transaction(function()enemy(x+6,y-8)end);rec.target=true;event('actual-thrown-object-target')end
 end
end
local function menu()
 if wall<90 or wall%12~=0 then return{}end
 if menuPhase=='options-focus'then menuPhase='options-open';return{down=true}end
 if menuPhase=='options-open'then menuPhase='mode';return{a=true}end
 if menuPhase=='mode'then if r('CrossoverMenuState')~=4 then return{}end;if r('CrossoverOptionsFocus')~=1 then return{down=true}end;if r('CrossoverBehaviorVersion')~=1 then menuPhase='back';return{a=true}end;menuPhase='back'end
 if menuPhase=='back'then menuPhase='start';return{b=true}end
 if menuPhase=='start'then if r('CrossoverMenuState')==2 then menuPhase='select'else return{start=true}end end
 if r('CrossoverMenuState')~=2 then return{}end
 local i=r('CrossoverMenuIndex');if i~=C.menu then local key=assert(C.navigation[i+1]);assert(key~='');return{[key]=true}end
 if r('CdVariant')~=C.variant then return{select=true}end;return{a=true}
end
hook('GameLoopOwned',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then if r('GameEngineSubroutine')~=8 then return end;assert(r('SelectedCharacter')==14 and r('CdVariant')==C.variant and r('CrossoverBehaviorVersion')==1 and r('CheatInvincible')==0,'Actual cold identity/Hard/cheats off');entered=true;change('settle')end
 updates=updates+1;age=age+1;assert(updates<=6500,'Finite actual Main cap')
 assert(r('SelectedCharacter')==14 and r('CdVariant')==C.variant and r('CrossoverBehaviorVersion')==1 and r('CheatInvincible')==0,'Stable actual owner/mode')
 if phase=='settle'and age==30 then assert(r('CdHealth')==3 and r('CdMagic')==165 and r('CdReady')==67 and r('CdHeld')==0 and boxCount()==1,'Actual source initialized3HP/one native entrance crate');beginCase()
 elseif phase=='setup'then beginCase()
 elseif phase=='hurt'and rec.deficit and not rec.enemy_removed then transaction(function()w('Enemy_Flag',0,0)end);rec.enemy_removed=true
 elseif phase=='hide'or phase=='throw'then controlledTarget()end
end)
local pickup
hook('PhysicalPickup',function(s)
 if not entered or(phase~='food'and phase~='life')then return end
 local want=phase=='life'and 3 or C.plan[index].pickup
 assert(s['cpu.x']==5 and r('Enemy_Flag',5)~=0 and r('Enemy_ID',5)==46 and r('Enemy_State',5)>=128 and r('PowerUpType',5)==want and r('InvPickup',5)==252 and r('InvPickupOwner',5)==255,'Real mature physical source actor before any family erasure')
 rec.collisions=rec.collisions+1;rec.collision_update=updates;event('actual-physical-pickup',want)
end)
hook('FoodEntry',function(s)if entered and phase=='food'then assert(s['cpu.x']==5 and rec.collision_update==updates,'Actual family food collector');rec.food_entries=rec.food_entries+1;pickup=s['cpu.sp'];event('actual-food-entry')end end)
hook('FoodAccepted',function(s)if pickup then assert(s['cpu.sp']==pickup,'Genuine food success return');pickup=nil;rec.food_accepts=rec.food_accepts+1;event('actual-food-accepted')end end)
hook('Defeat',function(s)if entered and rec and(phase=='hide'or phase=='throw')then assert(s['cpu.x']==0 and rec.target and r('Enemy_Flag',0)~=0 and r('Enemy_ID',0)==6,'Actual intended body/box enemy contact');rec.defeats=rec.defeats+1;event('actual-native-box-defeat')end end)
hook('Injury',function()if entered and phase=='hurt'then assert(r('ObjectOffset')==0 and r('Enemy_ID',0)==6,'Actual Hard body contact');rec.injury_owner=true;event('actual-native-injury-entry')end end)
hook('Release',function()
 if entered and phase=='throw'and r('CdHeld')>0 then assert(rec.releases==0,'One real release');rec.releases=1;rec.thrown_slot=r('CdHeld')-1;rec.release_dma=dmas;rec.release_update=updates;event('actual-native-release')end
end)
hook('LifeIncrement',function(s)
 if entered and phase=='life'then assert(s['cpu.x']==5 and rec.collisions==1 and rec.life_increment==0 and r('NumberofLives')==rec.lives_before and r('FloateyNum_Control',5)==11 and r('FloateyNum_Timer',5)==42,'Native delayed1Up INC owner');rec.life_increment=1;rec.life_dma=dmas;event('actual-life-inc-entry')end
end)
emu.addMemoryCallback(function(_,v)
 if not entered or not rec or writing then return end
 local state=emu.getState();local found
 for _,o in ipairs(C.health_writers)do if state['cpu.pc']==o.pc+3 and bank(o.pc)==o.bank then found=o;break end end
 assert(found,'Every post-cold HP write has genuine source owner')
 for i,vv in ipairs(found.bytes)do assert(emu.read(found.pc+i-1,emu.memType.nesDebug)==vv,'Actual compiledHP store bytes')end
 if(found.bytes[1]==0xce or found.bytes[1]==0xee)and v==rec.last_health then event('actual-HP-rmw-old',v);return end
 if phase=='hurt'then assert(found.kind=='injury'and rec.injury_owner and v==rec.HP_before-1 and not rec.deficit,'One real1HP contact deficit');rec.deficit=true
 else assert(phase=='food'and found.kind==(C.plan[index].pickup==0 and'small-food'or'full-food')and v==(C.plan[index].pickup==0 and math.min(3,rec.HP_before+1)or 3),'Real food source replenishment/cap3')end
 rec.last_health=v;rec.health_writes[#rec.health_writes+1]={update=updates,value=v,pc=found.pc,bank=found.bank,kind=found.kind};event('actual-player-HP-write',v)
end,emu.callbackType.write,C.ram.CdHealth)
emu.addMemoryCallback(function(_,v)
 if not entered or phase~='life'or writing then return end
 local h=C.hooks.LifeIncrement;local s=emu.getState();assert(s['cpu.pc']==h.pc+3 and bank(h.pc)==h.banks[1]and rec.life_increment==1,'Actual life INC bus owner')
 if v==rec.lives_before then event('actual-life-rmw-old',v);return end
 assert(v==((rec.lives_before+1)&255)and rec.life_writes==0,'One real life gained');rec.life_writes=1;event('actual-life-gain',v)
end,emu.callbackType.write,C.ram.NumberofLives)
emu.addMemoryCallback(function(_,v)if entered and rec and phase=='food'and v&C.powerup_sfx~=0 then rec.pickup_sfx=true end;if entered and rec and phase=='life'and v&C.extra_life_sfx~=0 then rec.life_sfx=true end end,emu.callbackType.write,C.ram.Square2SoundQueue)
hook('GameLoopFinish',function()
 if not entered or done then return end
 assert(r('MmDeathFlag')==0 and r('GameEngineSubroutine')==8 and r('GuestPowerupActive')==0,'No death/transition/seeded transform')
 if not rec then return end
 assert(r('CdMagic')==165 and r('CdFlowers')==0 and r('CdStars')==0 and r('CdHealth')==rec.last_health,'ActualHP ownership and no invented counters');local task=C.plan[index];event('update')
 if phase~='hurt'then assert(r('CdHurtTimer')==0 and r('InjuryTimer')==0,'No unrelated native damage/protection')end
 if phase=='entrance'or phase=='lift'then
  if r('CdHeld')>0 then local i=r('CdHeld')-1;assert(r('CdBoxKind',i)==1 and r('CdBoxMode',i)==1,'Native B acquired/carried real wood');rec.active_dma=rec.active_dma or dmas end
  if phase=='lift'and r('CdHeld')>0 then assert(r('Block_Buffer_1',10*16+8)==0,'Real B lifted/erased authored brick')end
  if rec.sampled and age>=20 then finishCase()end
 elseif phase=='hide'then
  if rec.defeats>0 and age>=40 then assert(rec.defeats==1 and rec.target and r('CdHeld')==0 and boxCount()==0 and r('CdHealth')==rec.HP_before,'Native hidden-crate defense defeats enemy/consumes box withoutHP cost');finishCase()end
 elseif phase=='hurt'then
  assert(age<160,'Natural injury expiry bound')
  if rec.deficit then
   assert(r('CdHealth')==rec.HP_before-1 and rec.injury_owner,'Genuine real deficit retained through expiry');rec.max_hurt=math.max(rec.max_hurt or 0,r('CdHurtTimer'))
   if r('CdHurtTimer')==0 and r('InjuryTimer')==0 then assert(rec.max_hurt==60 and rec.enemy_removed,'Original60tick protection expired naturally');if task.image then screenshot=task.name..'.png'end;finishCase()end
  end
 elseif phase=='food'then
  if rec.food_accepts==1 then assert(rec.collisions==1 and rec.food_entries==1 and rec.pickup_sfx and r('Enemy_Flag',5)==0 and r('PlayerStatus')==(task.pickup~1),'Actual physical food, native success/erase/SFX/next-food status');rec.active_dma=rec.active_dma or dmas end
  if rec.sampled and age>=32 then finishCase()end
 elseif phase=='life'then
  assert(r('CdHealth')==rec.HP_before and r('PlayerStatus')==rec.status_before and r('CdHeld')==rec.held_before,'Physical1Up preserves earned HP/food status/real held object')
  assert(r('NumberofLives')==((rec.lives_before+rec.life_writes)&255),'Exactly real source1Up count')
  if rec.life_writes==1 then assert(rec.collisions==1 and rec.life_increment==1 and rec.life_sfx,'Physical1Up and actual native INC/SFX');if r('FloateyNum_Control',5)==0 and dmas>=rec.life_dma+2 then screenshot=task.name..'.png';finishCase()end end
 elseif phase=='throw'then
  if rec.release_update then
   if r('CdBoxKind',rec.thrown_slot)~=0 then assert(r('CdBoxMode',rec.thrown_slot)==2 and r('CdHeld')==0,'Released real native box, no projectile seeds')end
   if age>=150 then assert(rec.releases==1 and rec.target and rec.defeats==1 and rec.sampled and r('CdHeld')==0 and r('CdThrowAge')==0 and boxCount()==0,'Real directional throw/contact/animation/actor cleanup');finishCase()end
  end
 end
 if phase~='setup'and phase~='complete'then assert(age<task.limit+20,'Finite original component cap')end
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
 local input={};local task=C.plan[index]
 if(phase=='entrance'or phase=='lift'or phase=='throw')and age>=5 and age<=8 then input.b=true;if phase=='throw'and task.up then input.up=true end end
 if phase=='hide'and rec.defeats==0 then input.down=true end
 emu.setInput(input,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1;minSP=math.min(minSP,emu.getState()['cpu.sp'])
 if entered then local s=emu.getState();for i=0,11 do assert(s['mapper.chrBanks'..i]==physical[i],'ActualCHR write-time hardware/latch model');chrChecks=chrChecks+1 end end
 if entered and rec and not rec.sampled then
  local task=C.plan[index];local live=false;local start=rec.active_dma
  if(phase=='entrance'or phase=='lift')and r('CdHeld')>0 then local i=r('CdHeld')-1;live=r('CdBoxKind',i)==1 and r('CdBoxMode',i)==1
  elseif phase=='hide'and r('CdHide')~=0 and r('CdHeld')>0 then rec.active_dma=rec.active_dma or dmas;start=rec.active_dma;live=true
  elseif phase=='food'and rec.food_accepts==1 then live=true
  elseif phase=='throw'and rec.thrown_slot then local i=rec.thrown_slot;start=rec.release_dma;live=r('CdBoxKind',i)==1 and r('CdBoxMode',i)==2 and r('CdBoxPage',i)==0 and r('CdBoxX',i)>=80 and r('CdBoxX',i)<=232 and r('CdBoxY',i)>=40 and r('CdBoxY',i)<=200 end
  if live and start and dmas>=start+2 then rec.sampled=true;rec.sample_dma=dmas;rec.sample_wall=wall;if task.image then screenshot=task.name..'.png'end end
 end
 if screenshot then assert(images<8,'Eight selected original whole-frame PNGs maximum');local f=assert(io.open(OUTPUT..screenshot,'wb'));f:write(emu.takeScreenshot());f:close();images=images+1;screenshot=nil end
 assert(wall<C.frame_limit,'Finite16000 physical frames')
 if done then assert(not pending and not pickup and dmas>100 and nmis>100 and irqCount>100 and enables>100 and late==0,'All original strict hardware guards exercised');local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=true,native_run=true,ROM_sha256=C.ROM_sha256,identity=C.family,variant=C.variant,mode=1,cases=records,wall=wall,updates=updates,complete256_DMAs=dmas,NMI_checks=nmis,IRQ31_checks=irqCount,safe_enables=enables,CHR_checks=chrChecks,minSP=minSP,screenshots=images,mature_actor_only=true,natural_reveal_or_drop_lottery=false,acquired_HP_power_ammo_held_object_life_outcomes_seeded=false,goal_complete=false}));f:close();csv:close();emu.stop(0)end
end,emu.eventType.endFrame)
