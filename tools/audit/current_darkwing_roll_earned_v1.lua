-- Mature native actors and source-owned health/gas/energy. No tested resource seeds.
local C=assert(CURRENT_DARKWING_ROLL_EARNED)
local wall,updates,age,index=0,0,0,1
local entered,done,writing=false,false,false
local phase,menuPhase='menu','options-focus'
local rec,records=nil,{}
local nmi,irq=nil,false
local minSP,dmas,enables,late,irqCount,nmis,images=255,0,0,0,0,0,0
local mask,pending,upper,physical,chrChecks=0,nil,0,{},0
local screenshot,spend,credit=nil,nil,nil
local csv=assert(io.open(OUTPUT..'earned-components.csv','w'))
csv:write('event,wall,update,case,age,x,y,state,hp,stock,adaptor,mode,shots,value,pc,bank,cycle\n')
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(at)local p=emu.convertAddress(at);return p and p.address//8192 or-1 end
local function hp()return r(C.identity=='darkwing'and'DwHealth'or'RlHealth')end
local function stock()return r(C.identity=='darkwing'and'DwGas'or'RlEnergy')end
local function pool()local n=0;for i=0,(C.identity=='darkwing'and 9 or 3)do if r(C.identity=='darkwing'and'RgShotType'or'MmBulletType',i)~=0 then n=n+1 end end;return n end
local function snapshot()return{hp=hp(),stock=stock(),adaptor=r('DwAdaptor'),mode=r('DwMode'),food=r('RlFoodKind'),status=r('PlayerStatus'),chargeFired=r('RlChargeFired')}end
local function event(kind,value)
 local s=emu.getState();csv:write(table.concat({kind,wall,updates,rec and rec.case_index or index,age,r('Player_X_Position'),r('Player_Y_Position'),r('Player_State'),hp(),stock(),r('DwAdaptor'),r('DwMode'),pool(),value or 0,s['cpu.pc'],bank(s['cpu.pc']),s['cpu.cycleCount']},',')..'\n')
end
local function json(v)
 if type(v)=='table'then local a=#v>0;for k in pairs(v)do if type(k)~='number'or k<1 or k>#v or k%1~=0 then a=false end end
  local t={};if a then for _,x in ipairs(v)do t[#t+1]=json(x)end;return'['..table.concat(t,',')..']'end
  for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..json(x)end;table.sort(t);return'{'..table.concat(t,',')..'}'
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
local forbidden={};for _,n in ipairs(C.forbidden)do forbidden[n]=true end
local function w(n,v,i)
 assert(writing and not nmi and not irq and r('NmiDisable')==255,'Only private native GameLoop boundary')
 assert(C.setup_allowed[n]and not forbidden[n],'No tested health/resource/ownership/outcome seed: '..n)
 emu.write(assert(C.ram[n],n)+(i or 0),v&255,emu.memType.nesDebug)
end
local function transaction(fn)
 assert(not writing and not nmi and not irq and r('NmiDisable')==255,'Synchronous native-boundary scene setup')
 writing=true;fn();writing=false;event('disclosed-scene-setup')
end
local function tile(page,col,row,id)
 assert(writing and not nmi and not irq,'Same exclusive scene owner')
 local function source(n)local p=C.metatiles[n];return emu.read(p.bank*8192+p.offset+id,emu.memType.nesPrgRom)end
 local function put(a,v)emu.write(a,v,emu.memType.nesPpuDebug)end
 local at=0x2000+page*1024+row*64+col*2
 put(at,source('MTileTopLeft'));put(at+1,source('MTileTopRight'));put(at+32,source('MTileBotLeft'));put(at+33,source('MTileBotRight'))
 local a=0x23c0+page*1024+(row//2)*8+col//2;local shift=row%2*4+col%2*2
 put(a,(emu.read(a,emu.memType.nesPpuDebug)&(~(3<<shift)))|((source('MTileAttribute')>>6)<<shift))
end
local function arena()
 assert(pool()==0,'Prior source projectiles really cleaned up')
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do for row=2,14 do for col=0,15 do tile(p,col,row,row>=13 and 0x54 or 0)end end end
 for p=0,1 do for row=11,12 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+row*16+col)end end end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_CollisionBits',0,i)end
 -- Only discarded old world actors; collected resources remain native.
 for i=0,3 do w('InvDropKind',0,i)end
 for _,n in ipairs({'Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','ScrollThirtyTwo','AreaParserTaskNum'})do w(n,0)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('ScrollLock',1);w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_X_Position',112);w('Player_PageLoc',0);w('MmOldX',112);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1);w('Player_MovingDir',1);w('Player_CollisionBits',255)
end
local function enemy(x,y,direction)
 for _,a in ipairs({{'Enemy_Flag',1},{'Enemy_ID',6},{'Enemy_State',0},{'Enemy_X_Position',x},{'Enemy_PageLoc',0},{'Enemy_Y_Position',y},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_Y_MoveForce',0},{'Enemy_MovingDir',direction or 1},{'Enemy_BoundBoxCtrl',9},{'EnemyOffscrBitsMasked',0},{'Enemy_CollisionBits',0},{'MmEnemyHealthLo',0},{'MmEnemyHealthHi',0},{'MmEnemyFlash',0},{'RgEnemyStun',0}})do w(a[1],a[2],0)end
end
local function setup(task)
 arena()
 if task.kind=='collect'then
  for _,a in ipairs({{'Enemy_Flag',1},{'Enemy_ID',0x2e},{'Enemy_State',128},{'Enemy_BoundBoxCtrl',3},{'Enemy_X_Position',112},{'Enemy_PageLoc',0},{'Enemy_Y_Position',184},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_SprAttrib',0},{'PowerUpType',task.power or 1},{'InvPickupOwner',C.character},{'InvPickup',task.item}})do w(a[1],a[2],5)end
 elseif task.kind=='hurt'then enemy(116,184,2)
 elseif task.kind=='capsule'then
  for _,a in ipairs({{'InvDropKind',task.drop},{'InvDropX',120},{'InvDropPage',0},{'InvDropY',192},{'InvDropVY',0},{'InvDropVYMid',0},{'InvDropVYHi',0},{'InvDropFraction',0},{'InvDropFractionHi',0},{'InvDropAge',0},{'InvDropAgeHi',0},{'AvDropItem',task.health and 128 or 0}})do w(a[1],a[2],0)end
 elseif C.identity=='darkwing'and task.weapon==2 then w('Block_Buffer_1',0x54,173);tile(0,13,12,0x54)end
end
local function beginCase()
 local task=assert(C.plan[index]);age=0;phase=task.kind;spend=nil
 rec={case_index=index,name=task.name,kind=task.kind,before=snapshot(),started=wall,debits={},credits={},native_grants={},contacts=0,hpWrites=0,collisions=0,collects=0,rewards=0,refills=0,sounds={},types={},target=false}
 records[#records+1]=rec;transaction(function()setup(task)end)
 if C.identity=='darkwing'and task.kind=='use'and r('DwMode')~=task.mode then phase='select'end
 event('case-start')
end
local function finishCase()
 assert(not spend and not credit,'No unfinished debit/refill owner');rec.ending=snapshot();rec.completed=wall;rec.updates=age;event('case-complete')
 index=index+1;if index>#C.plan then done=true;phase='complete'else phase='setup'end
end
local function target(task)
 if rec.target then return end
 local x,y
 if C.identity=='darkwing'then
  for j=0,9 do local i=task.weapon==3 and 9-j or j
   if r('RgShotType',i)==task.contact and(task.weapon~=3 or r('RgShotVYHi',i)>=128)and r('RgShotPage',i)==0 then
    local sx,sy=r('RgShotX',i),r('RgShotY',i)
    if sx>=152 and sx<224 and sy>=48 and sy<216 then x=sx-6;y=sy-(task.weapon==3 and 12 or 8);break end
   end
  end
 else
  for i=0,3 do if r('MmBulletType',i)==task.contact and r('MmBulletPage',i)==0 then
   local sx,sy=r('MmBulletX',i),r('MmBulletY',i);if sx>=152 and sx<224 and sy>=48 and sy<216 then x=sx-6;y=sy-8;break end
  end end
 end
 if x then transaction(function()enemy(x,y,1)end);rec.target=true;rec.target_x=x;rec.target_y=y;event('source-effect-aligned-target')end
end
local function menu()
 if wall<90 or wall%12~=0 then return{}end
 if menuPhase=='options-focus'then menuPhase='options-open';return{down=true}end
 if menuPhase=='options-open'then menuPhase='mode';return{a=true}end
 if menuPhase=='mode'then
  if r('CrossoverMenuState')~=4 then return{}end
  if r('CrossoverOptionsFocus')~=1 then return{down=true}end
  if r('CrossoverBehaviorVersion')~=1 then menuPhase='back';return{a=true}end;menuPhase='back'
 end
 if menuPhase=='back'then menuPhase='start';return{b=true}end
 if menuPhase=='start'then if r('CrossoverMenuState')==2 then menuPhase='select'else return{start=true}end end
 if r('CrossoverMenuState')~=2 then return{}end
 local key=assert(C.navigation[r('CrossoverMenuIndex')+1]);if key~=''then return{[key]=true}end
 if r(C.variant_ram)~=1 then return{select=true}end
 return{a=true}
end
hook('GameLoopOwned',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then
  if r('GameEngineSubroutine')~=8 then return end
  assert(r('SelectedCharacter')==C.character and r(C.variant_ram)==1 and r('CrossoverBehaviorVersion')==1 and r('CheatInvincible')==0,'Actual cold owner/variant/Hard1/cheats')
  entered=true;phase='settle';age=0
 end
 updates=updates+1;age=age+1;assert(updates<=3000,'At most3000 actual updates')
 assert(r('SelectedCharacter')==C.character and r(C.variant_ram)==1 and r('CrossoverBehaviorVersion')==1 and r('CheatInvincible')==0,'Owner/mode remain actual')
 if phase=='settle'and age>=30 then
  if C.identity=='darkwing'then assert(hp()==4 and stock()==0 and r('DwAdaptor')==0 and r('DwMode')==0,'Native Darkwing initialization')
  else assert(hp()==28 and stock()==28 and r('RlReady')==0x52,'Actual Roll Ensure initialization')end
  beginCase()
 elseif phase=='setup'then beginCase()
 elseif rec then
  local task=C.plan[index]
  if phase=='select'and r('DwMode')==task.mode then phase='use';age=0;event('actual-selected-mode')end
  if task.kind=='hurt'and rec.damageSeen and not rec.hurtActorCleared then transaction(function()w('Enemy_Flag',0,0)end);rec.hurtActorCleared=true end
  if task.kind=='use'then target(task)end
 end
end)
hook('PhysicalPickup',function(s)
 if entered and phase=='collect'then
  local task=C.plan[index];assert(s['cpu.x']==5 and r('Enemy_Flag',5)==1 and r('Enemy_ID',5)==0x2e and r('Enemy_State',5)>=128 and r('InvPickupOwner',5)==C.character and r('InvPickup',5)==task.item,'Actual complete mature actor contact')
  rec.collisions=rec.collisions+1;event('actual-mature-collision',task.item)
 end
end)
hook('CollectOwner',function(s)
 if entered and phase=='collect'then assert(s['cpu.x']==5 and r('Enemy_Flag',5)==0 and r('Enemy_State',5)==0,'Actual dispatch collection after native erase');rec.collects=rec.collects+1;event('actual-collect-owner')end
end)
if C.identity=='darkwing'then
 hook('GiveItem',function(s)
  if entered and rec then rec.native_grants[#rec.native_grants+1]={item=s['cpu.a'],hp=hp(),gas=stock(),update=updates};event('actual-source-reward-entry',s['cpu.a'])end
  if entered and phase=='collect'then assert(s['cpu.a']==C.plan[index].item,'Actual source reward');rec.rewards=rec.rewards+1 end
 end)
 hook('Launch',function()if entered and phase=='use'then spend={before=stock(),kind=C.plan[index].weapon};event('source-launch-entry',stock())end end)
 hook('ShotInit',function()
  if entered and phase=='use'then assert(spend,'Actual launch owner before shot init');local cost=({[0]=0,2,3,2})[spend.kind];assert(r('RgTemp')==spend.kind and stock()==spend.before-cost,'Actual adaptor debit before native shot init');rec.debits[#rec.debits+1]={before=spend.before,cost=cost,after=stock(),update=updates};spend=nil;event('actual-source-debit',cost)end
 end)
else
 hook('ChargeSpawn',function(s)if entered and phase=='use'and s['cpu.a']==3 then spend={before=stock(),fired=r('RlChargeFired')};event('actual-autocharge-spawn-entry')end end)
 hook('ChargeReset',function()
  if entered and phase=='use'and spend then assert(stock()==spend.before-4 and r('RlChargeFired')==spend.fired+1,'Real successful autocharge costs4 and increments source counter');rec.debits[#rec.debits+1]={before=spend.before,cost=4,after=stock(),update=updates};spend=nil;event('actual-source-debit',4)end
 end)
 hook('Refill',function(s)
  if entered and rec then
   assert(not credit and(s['cpu.a']==8 or s['cpu.a']==40),'Actual one native scaled capsule request')
   local slot=r('InvDropSlot');assert(slot<4,'Real native drop slot');local health=r('AvDropItem',slot)&128~=0
   credit={health=health,before=health and hp()or stock(),request=s['cpu.a'],amount=s['cpu.a']//4,update=updates}
   if phase=='capsule'then assert(s['cpu.a']==(C.plan[index].drop==1 and 8 or 40)and health==C.plan[index].health,'Declared mature capsule type/health metadata');rec.refills=rec.refills+1 end
   event('actual-refill-request',s['cpu.a'])
  end
 end)
 local function refillSave(s,health)
  if entered and rec then
   assert(credit and credit.health==health and s['cpu.a']==math.min(28,credit.before+credit.amount),'Actual source refill writer/clamp')
   credit.after=s['cpu.a'];credit.delta=credit.after-credit.before;rec.credits[#rec.credits+1]=credit;event('actual-source-credit',credit.delta);credit=nil
  end
 end
 hook('RefillEnergySave',function(s)refillSave(s,false)end)
 hook('RefillHealthSave',function(s)refillSave(s,true)end)
end
hook('DamageEnemy',function(s)
 if entered and phase=='use'and s['cpu.x']==0 then
  local slot=C.identity=='roll'and r('MmSlot')or 0;assert(r('MmBulletType',slot)==C.plan[index].proxy,'Actual source-specific damage proxy')
  rec.contacts=rec.contacts+1;event('actual-source-contact',r('MmBulletType',slot))
 end
end)
emu.addMemoryCallback(function(_,v)if entered and rec and not writing and phase=='use'and rec.contacts>0 then rec.hpWrites=rec.hpWrites+1;event('actual-target-health-write',v)end end,emu.callbackType.write,C.ram.MmEnemyHealthLo,C.ram.MmEnemyHealthHi)
local shotBase=C.identity=='darkwing'and C.ram.RgShotType or C.ram.MmBulletType
emu.addMemoryCallback(function(_,v)if entered and rec and phase=='use'and not writing and v~=0 then rec.types[v]=true;event('actual-shot-type',v)end end,emu.callbackType.write,shotBase,shotBase+(C.identity=='darkwing'and 9 or 3))
for _,n in ipairs({'Square1SoundQueue','Square2SoundQueue','NoiseSoundQueue'})do emu.addMemoryCallback(function(_,v)if entered and rec and not writing and v~=0 then rec.sounds[n..':'..v]=true end end,emu.callbackType.write,C.ram[n])end
hook('GameLoopFinish',function()
 if not entered or done or not rec then return end
 assert(r('MmDeathFlag')==0 and r('GameEngineSubroutine')==8,'No native death')
 local task=C.plan[index]
 if task.kind=='hurt'then
  if hp()<rec.before.hp then
   assert(hp()==rec.before.hp-(C.identity=='darkwing'and 1 or 4),'Only actual source contact causes the exact health deficit');rec.damageSeen=true
   local settled=r('InjuryTimer')==0 and(C.identity=='darkwing'and r('RgBillBurst')==0 and r('RgBillBurstDelay')==0 or C.identity=='roll'and r('RlInvul')==0 and r('RlHurt')==0)
   if settled then assert(rec.hurtActorCleared,'Hurt target removed only after real damage');finishCase()end
  end
 elseif task.kind=='collect'and age>=24 then
  assert(rec.collisions==1 and rec.collects==1,'One real mature collection through complete dispatch')
  if C.identity=='darkwing'then
   assert(rec.rewards==1,'Exactly one genuine Darkwing reward')
   if task.item==0x22 then assert(hp()==math.min(4,rec.before.hp+1)and stock()==rec.before.stock,'Actual small health +1')
   elseif task.item==0x23 then assert(hp()==4 and stock()==rec.before.stock,'Actual full health')
   else
    assert(hp()==rec.before.hp and stock()==math.min(99,rec.before.stock+(task.item==0x25 and 1 or 10)),'Actual bounded gas refill')
    if task.item>=0x26 then assert(r('DwAdaptor')==({[0x26]=2,[0x27]=1,[0x28]=3})[task.item],'Single actual carried adaptor replacement')end
   end
  else assert(hp()==28 and stock()==28 and r('RlFoodKind')==1 and r('PlayerStatus')==1,'Actual mushroom/flower Roll food full restoration, not invented classic tiers')end
  if task.image then screenshot=task.name..'.png'end;finishCase()
 elseif task.kind=='capsule'and age>=24 then
  assert(rec.refills==1 and r('InvDropKind',0)==0,'One actual native capsule consumed')
  local value=task.health and hp()or stock();local before=task.health and rec.before.hp or rec.before.stock
  assert(value==math.min(28,before+(task.drop==1 and 2 or 10)),'Actual Roll scaled2/10 refill')
  if task.image then screenshot=task.name..'.png'end;finishCase()
 elseif task.kind=='use'then
  if task.image and rec.contacts>0 and not rec.sample then rec.sample=true;screenshot=task.name..'.png'end
  local enough=#rec.debits==(C.identity=='darkwing'and 1 or task.charges)
  if age>=210 and enough and rec.target and rec.contacts>0 and rec.hpWrites>0 and pool()==0 then
   if C.identity=='darkwing'then
    if task.weapon==1 then assert(rec.types[3]and rec.types[4],'Native Heavy parabola and shockwaves')
    elseif task.weapon==2 then assert(rec.types[8]and rec.types[5]and rec.types[6],'Native Arrow charge, flight and attached actor')
    elseif task.weapon==3 then assert(rec.types[8]and rec.types[7],'Native Thunder charge and diagonal split')end
   else
    local gained=0;for _,c in ipairs(rec.credits)do if not c.health then gained=gained+c.delta end end
    assert(#rec.debits==task.charges and stock()==rec.before.stock-4*task.charges+gained,'Atomic charge costs and separately witnessed native credits account for energy')
   end
   finishCase()
  end
 elseif task.kind=='select-no-inventory'and age>=24 then assert(r('InvSelected',9)==0 and r('RlVariant')==1 and pool()==0,'Roll Select is not an invented Bass equip action');finishCase()end
 event('update');assert(age<C.plan[math.min(index,#C.plan)].limit+120,'Finite component update deadline')
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
 local b={};local task=C.plan[index]
 if not done and rec and task and phase~='setup'then
  if C.identity=='darkwing'and task.kind=='use'then
   if phase=='select'then b.select=age%8==2 or age%8==3
   else b.b=age>=5 and age<8 end
  elseif C.identity=='roll'then
   if task.kind=='use'then b.b=age>=5 and(task.charges==0 and age<8 or #rec.debits<task.charges)end
   if task.kind=='select-no-inventory'then b.select=age%8==2 or age%8==3 end
  end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1;minSP=math.min(minSP,emu.getState()['cpu.sp'])
 if entered then local s=emu.getState();for i=0,11 do assert(s['mapper.chrBanks'..i]==physical[i],'Actual CHR hardware agrees with write-time latch model');chrChecks=chrChecks+1 end end
 if screenshot then
  assert(images<8,'At most8 actual whole-frame screenshots');local f=assert(io.open(OUTPUT..screenshot,'wb'));f:write(emu.takeScreenshot());f:close();images=images+1
  local s=emu.getState();local oam={};for i=0,255 do oam[i+1]=emu.read(i,emu.memType.nesSpriteRam)end
  local chr={};for i=0,11 do chr[i+1]=physical[i]end
  local owner=records[#records];owner.capture={file=screenshot,wall=wall,update=updates,PPU_frame=s['ppu.frameCount'],hardware_OAM=oam,physical_CHR=chr,note='Actual endFrame snapshot; no claim all source effect/body pixels were visible in this PPU epoch.'};screenshot=nil
 end
 assert(wall<8000,'At most8000wall frames')
 if done then
  assert(not pending and dmas>100 and irqCount>100 and nmis>100 and enables>100 and late==0,'Full native hardware/source guards exercised')
  local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=true,native_run=true,ROM_sha256=C.ROM_sha256,identity=C.identity,character=C.character,variant=1,actual_numeric_mode=r('CrossoverBehaviorVersion'),cases=records,wall=wall,updates=updates,complete256_DMAs=dmas,NMI_checks=nmis,IRQ31_checks=irqCount,NMI_safe_enables=enables,CHR_checks=chrChecks,minSP=minSP,screenshots=images,goal_complete=false,scope='Real mature actor collection and source hurt/debits/refills/use. Explicit native-boundary map/actor setup; no tested health/ammo/owned/tier/selection/projectile/outcome seeds. No emergence/RNG/star/1up/allfacings/pool/exhaustion/campaign/allpixel/audio-fidelity claim.'}));f:close();csv:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
