-- Prepared current-ROM collection/use components, not a natural route/RNG test.
-- No item ownership, tier, selection, ammo, projectile or outcome is seeded.
local C=assert(CURRENT_INVENTORY_POWERUPS)
local wall,updates,age,index=0,0,0,0
local entered,done,writing=false,false,false
local phase,menuPhase='menu',C.mode==1 and'options-focus'or'start'
local rec,records=nil,{}
local nmi,irq=nil,false
local minSP,dmas,enables,late,irqCount,nmis,images=255,0,0,0,0,0,0
local mask,pending=0,nil
local upper,physical,chrChecks=0,{},0
local screenshot=nil
local spend=nil
local csv=assert(io.open(OUTPUT..'inventory.csv','w'))
csv:write('event,wall,update,item,phase,age,ownedLo,ownedHi,selected,ammo,status,shots,playerX,playerY,value,pc,bank,cycle\n')
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(at)local p=emu.convertAddress(at);return p and p.address//8192 or-1 end
local function pool()local n=0;for i=0,9 do if r('RgShotType',i)~=0 then n=n+1 end end;return n end
local function stock(item)return r('InvAmmo',C.character*16+item)end
local function has(item)return((r('InvOwnedLo',C.character)+256*r('InvOwnedHi',C.character))&(1<<item))~=0 end
local function event(kind,value)
 local s=emu.getState();csv:write(table.concat({kind,wall,updates,index,phase,age,r('InvOwnedLo',C.character),r('InvOwnedHi',C.character),r('InvSelected',C.character),index>0 and stock(index)or-1,r('PlayerStatus'),pool(),r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),value or 0,s['cpu.pc'],bank(s['cpu.pc']),s['cpu.cycleCount']},',')..'\n')
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
local forbidden={InvOwnedLo=true,InvOwnedHi=true,InvViewedLo=true,InvViewedHi=true,InvSelected=true,InvAmmo=true,PlayerStatus=true,GuestPowerupActive=true,GameEngineSubroutine=true,InjuryTimer=true,MmDeathFlag=true,RgShotType=true,CheatInvincible=true}
local function w(n,v,i)
 assert(writing and not nmi and not irq and r('NmiDisable')&128~=0,'Fixture writes only in actual private GameLoop entry; no interrupt owner')
 assert(not forbidden[n]and C.setup_allowed[n],'No tested ownership/resource/outcome seeds: '..n)
 emu.write(assert(C.ram[n],n)+(i or 0),v&255,emu.memType.nesDebug)
end
local function transaction(fn)
 assert(not writing and not nmi and not irq and r('NmiDisable')==255,'One synchronous private-frame setup transaction')
 writing=true;fn();writing=false;event('disclosed-setup')
end
local function tile(page,col,row,id)
 assert(writing and not nmi and not irq,'Same synchronous map staging boundary')
 local function source(n)local p=C.metatiles[n];return emu.read(p.bank*8192+p.offset+id,emu.memType.nesPrgRom)end
 local function put(a,v)emu.write(a,v,emu.memType.nesPpuDebug)end
 local at=0x2000+page*1024+row*64+col*2
 put(at,source('MTileTopLeft'));put(at+1,source('MTileTopRight'));put(at+32,source('MTileBotLeft'));put(at+33,source('MTileBotRight'))
 local a=0x23c0+page*1024+(row//2)*8+col//2;local shift=row%2*4+col%2*2
 put(a,(emu.read(a,emu.memType.nesPpuDebug)&(~(3<<shift)))|((source('MTileAttribute')>>6)<<shift))
end
local function arena()
 assert(pool()==0 and r('SsHeld')==0,'Previous effects must really drain before new scene')
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do for row=2,14 do for col=0,15 do local id=row>=13 and 0x54 or 0;tile(p,col,row,id)end end end
 for p=0,1 do for row=11,12 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+row*16+col)end end end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_CollisionBits',0,i)end
 -- New staged scenes discard prior world drop actors, never their collected
 -- ammo. This profile does not claim natural drop delivery/expiry coverage.
 for i=0,3 do w('InvDropKind',0,i)end
 for _,n in ipairs({'Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','ScrollThirtyTwo','AreaParserTaskNum'})do w(n,0)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('ScrollLock',1);w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_X_Position',64);w('Player_PageLoc',0);w('MmOldX',64);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1);w('Player_MovingDir',1);w('Player_CollisionBits',255)
end
local function mature(item)
 w('Enemy_Flag',1,5);w('Enemy_ID',0x2e,5);w('Enemy_State',128,5)
 w('Enemy_BoundBoxCtrl',3,5);w('Enemy_X_Position',64,5);w('Enemy_PageLoc',0,5);w('Enemy_Y_Position',184,5);w('Enemy_Y_HighPos',1,5)
 w('Enemy_X_Speed',0,5);w('Enemy_Y_Speed',0,5);w('Enemy_SprAttrib',0,5)
 w('PowerUpType',item==0 and 0 or 1,5);w('InvPickupOwner',C.character,5);w('InvPickup',item,5)
 if item==254 then w('AvPickupAmmoItem',0,5)end
end
local function change(p)phase=p;age=0;event('phase')end
local function seedItem()
 assert(not has(index),'Acquisition item must be genuinely unowned beforehand')
 rec={item=index,collections=0,grants=0,spends=0,damageCalls=0,hpWrites=0,spawns=0,transforms=0,target=false,hud=false,cost=0,started=wall,source_types={},source_sfx={}}
 records[#records+1]=rec;transaction(function()arena();mature(index)end);change('collect')
end
local function controlledTarget()
 if rec.target then return end
 local item=C.items[index];local x,y
 if index==5 then
  if r('SsKick')~=1 or r('XgDash')==0 then return end
  x=r('Player_X_Position')+22;y=r('Player_Y_Position')+8
 else
  for i=0,9 do
   if r('RgShotType',i)==item.contact_type and r('SsHidden',i)==0 and(index~=1 or r('SsMode',i)==0)and(index~=3 or r('RgShotAge',i)>=10)and(index~=7 or r('SsWaterExpand')~=0 and r('SsWaterRadius')>=42)then
    local dx=math.abs(r('RgShotX',i)-r('Player_X_Position'))
    if r('RgShotPage',i)==0 and dx>=30 and r('RgShotX',i)>=16 and r('RgShotX',i)<232 and r('RgShotYHigh',i)==1 and r('RgShotY',i)>=48 and r('RgShotY',i)<216 then x=r('RgShotX',i)-6;y=r('RgShotY',i)-8;break end
   end
  end
 end
 if not x then return end
 assert(x>=0 and x<240 and y>=32 and y<216,'Valid live-effect-aligned Goomba placement')
 transaction(function()
  for _,a in ipairs({{'Enemy_Flag',1},{'Enemy_ID',6},{'Enemy_State',0},{'Enemy_X_Position',x},{'Enemy_PageLoc',0},{'Enemy_Y_Position',y},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_Y_MoveForce',0},{'Enemy_MovingDir',1},{'Enemy_BoundBoxCtrl',9},{'EnemyOffscrBitsMasked',0},{'Enemy_CollisionBits',0},{'MmEnemyHealthLo',0},{'MmEnemyHealthHi',0},{'MmEnemyFlash',0},{'RgEnemyStun',0}})do w(a[1],a[2],0)end
 end);rec.target=true;rec.target_x=x;rec.target_y=y;event('controlled-live-effect-target')
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
 local i=r('CrossoverMenuIndex');if i//6~=C.slot//6 then return{down=true}end
 if i~=C.slot then return{right=true}end
 if r('RlVariant')~=0 then return{select=true}end
 return{a=true}
end
hook('GameLoopOwned',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then
  if r('GameEngineSubroutine')~=8 then return end
  assert(r('SelectedCharacter')==C.character and r('RlVariant')==0 and r('CrossoverBehaviorVersion')==C.mode,'Cold actual requested owner and numeric mode')
  assert(r('PlayerStatus')==0 and r('InvOwnedLo',C.character)==0 and r('InvOwnedHi',C.character)==0 and r('CheatInvincible')==0,'No powered/invulnerable/owned starting seed')
  for i=1,7 do assert(stock(i)==C.items[i].initial_ammo,'Actual native cold inventory ammo initialization, never fixture refill')end
  entered=true;change('settle')
 end
 updates=updates+1;age=age+1
 assert(r('SelectedCharacter')==C.character and r('RlVariant')==0 and r('CrossoverBehaviorVersion')==C.mode and r('CheatInvincible')==0,'Actual owner/mode/default cheats preserved')
 if phase=='settle'and age==30 then seedItem()
 elseif phase=='next'then seedItem()
 elseif phase=='use-setup'then
  transaction(function()
   arena()
   if index==1 then w('Block_Buffer_1',0x51,165);tile(0,5,12,0x51)end
  end);rec.ammo_before=stock(index);change('use')
 elseif phase=='use'then controlledTarget()
 elseif phase=='balance-setup'then
  assert(r('InvSelected',C.character)==0 and has(8),'Native Select reaches normal with earned BALANCE')
  rec.refill_before={};rec.refill_item=0;local low=112
  for i=1,7 do local v=stock(i);rec.refill_before[i]=v;if has(i)and v<low then low=v;rec.refill_item=i end end
  assert(rec.refill_item>0,'BALANCE uses genuinely spent earned weapon energy')
  transaction(function()arena();mature(254)end);change('balance')
 end
end)
hook('PhysicalPickup',function(s)
 if entered and(phase=='collect'or phase=='balance')then
  assert(s['cpu.x']==5 and r('Enemy_Flag',5)~=0 and r('Enemy_ID',5)==0x2e and r('Enemy_State',5)>=128,'Real mature actor before native erase')
  assert(r('InvPickupOwner',5)==C.character and r('InvPickup',5)==(phase=='balance'and 254 or index),'Actual physical tested item owner')
  rec.collision_update=updates;event('actual-pre-erase-collision')
 end
end)
hook('InventoryCollect',function(s)
 if entered and(phase=='collect'or phase=='balance')then
  assert(s['cpu.x']==5 and rec.collision_update==updates and r('Enemy_Flag',5)==0 and r('Enemy_State',5)==0 and r('InvPickupOwner',5)==C.character,'Actual source collection follows the genuine collision and native erase')
  assert(r('InvPickup',5)==(phase=='balance'and 254 or index),'Actual tested reward ID')
  rec.collections=rec.collections+1;event('actual-collection-owner')
 end
end)
hook('InventoryGrant',function(s)
 if entered and phase=='collect'and index>0 then assert(s['cpu.a']==index,'Exact native grant item');rec.grants=rec.grants+1;event('actual-grant')end
end)
hook('GuestPowerupUpdate',function()
 if entered and index==0 and phase=='collect'and r('GuestPowerupActive')~=0 then rec.transforms=rec.transforms+1 end
end)
hook('InventorySpend',function(s)
 if not entered or phase~='use'then return end
 assert(not spend and s['cpu.a']==index and s['cpu.y']==C.items[index].cost,'Exact earned weapon spend owner and source cost')
 spend={item=index,before=stock(index),cost=s['cpu.y'],sp=s['cpu.sp']};event('actual-spend-entry',spend.cost)
end)
hook('InventorySpendDone',function(s)
 if not spend then return end
 assert(s['cpu.sp']==spend.sp,'Actual spend call returns in same stack frame')
 assert(spend.before>=spend.cost and stock(spend.item)==spend.before-spend.cost,'Exact native stock decrement before any later earned refill')
 rec.spends=rec.spends+1;rec.cost=rec.cost+spend.cost;spend=nil;event('actual-spend-accepted')
end)
hook('DamageEnemy',function(s)
 if entered and phase=='use'and rec.target and s['cpu.x']==0 then
  assert(r('MmBulletType')==C.items[index].damage_type,'Exact weapon proxy owns real target contact')
  rec.damageCalls=rec.damageCalls+1;event('actual-damage-owner',r('MmBulletType'))
 end
end)
emu.addMemoryCallback(function(a,v)
 if entered and phase=='use'and rec.target and rec.damageCalls>0 and not writing then rec.hpWrites=rec.hpWrites+1;event('native-enemy-hp-write',v)end
end,emu.callbackType.write,C.ram.MmEnemyHealthLo,C.ram.MmEnemyHealthHi)
emu.addMemoryCallback(function(a,v)
 if entered and phase=='use'and v~=0 and not writing then
  rec.source_types[v]=true;rec.spawns=rec.spawns+1;event('native-shot-type',v)
 end
end,emu.callbackType.write,C.ram.RgShotType,C.ram.RgShotType+9)
emu.addMemoryCallback(function(_,v)
 if entered and rec and not writing and v~=0 then rec.source_sfx[v]=true;event('native-special-sfx-request',v)end
end,emu.callbackType.write,C.ram.SsAudioRequest)
emu.addMemoryCallback(function(_,v)
 if entered and rec and phase=='collect'and v&C.powerup_sfx~=0 then rec.pickup_sfx=true;event('native-pickup-sfx-request',v)end
end,emu.callbackType.write,C.ram.Square2SoundQueue)
hook('GameLoopFinish',function()
 if not entered or done then return end
 assert(r('MmDeathFlag')==0 and r('InjuryTimer')==0 and r('GuestHurtTicks')==0,'No unrelated hurt/death or injected immunity')
 event('update')
 if phase=='collect'then
  assert(age<240,'Bounded real mature pickup collision')
  if r('Enemy_Flag',5)==0 and r('GuestPowerupActive')==0 and r('TimerControl')==0 and rec.collections>0 then
   assert(rec.collections==1 and has(index),'One real collection changes exact earned ownership')
   assert(rec.pickup_sfx,'Actual pickup sound request, separate from waveform fidelity')
   assert(r('PlayerStatus')==1,'Actual mushroom tier retained')
   assert(index~=0 or rec.transforms==60,'Mushroom completes60 real transform calls')
   if index>0 then assert(rec.grants==1,'One exact weapon grant')end
   rec.collected=wall
   if index==0 then index=1;change('next')else change('select')end
  end
 elseif phase=='select'then
  assert(age<180,'Real Select cycle reaches earned weapon')
  if r('InvSelected',C.character)==(index==8 and 0 or index)then change('hud')end
 elseif phase=='hud'and age>=20 then
  local item=C.items[index==8 and 0 or index]
  for i,v in ipairs(item.hud_name)do assert(emu.read(0x2023+i-1,emu.memType.nesPpuDebug)==v,'Actual committed selected HUD name')end
  rec.hud=true;change(index==8 and'balance-setup'or'use-setup')
 elseif phase=='use'then
  if index==1 and r('SsHeld')~=0 then assert(stock(index)==rec.ammo_before,'ARM lift/hold is free');rec.held=true end
  if index==5 and r('SsKick')==1 and r('XgDash')~=0 then rec.paidKick=true end
  if index==7 and r('SsWaterExpand')~=0 then rec.expanded=true end
  if age>=210 and pool()==0 and r('SsHeld')==0 and r('XgDash')==0 then
   assert(rec.target and rec.damageCalls>0 and rec.hpWrites>0,'Acquired intended weapon really damages source target')
   assert(rec.spawns>0 and rec.source_types[C.items[index].contact_type],'Actual intended effect allocated')
   assert(rec.spends==1 and rec.cost==C.items[index].cost,'One actual paid source action; no seeded resources')
   assert(C.items[index].sfx==0 or rec.source_sfx[C.items[index].sfx],'Actual source special sound request')
   assert(index~=1 or rec.held,'Actual ARM lift before throw')
   assert(index~=5 or rec.paidKick,'Actual paid KICK native dash')
   assert(index~=7 or rec.expanded,'Actual WATER orbit and second-B expansion')
   rec.native_cleanup=true;rec.completed=wall;index=index+1;change('next')
  end
  assert(age<480,'Native acquired effect/contact/cleanup is bounded')
 elseif phase=='balance'then
  assert(age<240,'Bounded native BALANCE refill')
  if r('Enemy_Flag',5)==0 and r('InvRefill')==0 and r('TimerControl')==0 and rec.collections==2 then
   for i=1,7 do assert(stock(i)==(i==rec.refill_item and math.min(112,rec.refill_before[i]+40)or rec.refill_before[i]),'Native Balancer selects the genuinely least-energy owned pool')end
   assert(rec.source_sfx[63]and rec.source_sfx[242],'Actual native continuous refill start and stop requests')
   rec.native_refill=true;rec.completed=wall;screenshot='item-08.png';done=true;change('complete')
  end
 end
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
 local s=emu.getState();assert(v==2 and s['cpu.pc']==C.hooks.DmaComplete.pc,'Actual native page2 DMA owner')
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
 if phase=='select'then input.select=age%8==1
 elseif phase=='use'then
  if index==5 then input.down=age>=4 and age<9;input.a=age>=5 and age<8
  elseif index==1 then input.b=age>=5 and age<9 or age>=16 and age<20
  elseif index==7 then input.b=age>=5 and age<8 or age>=125 and age<128
  else input.b=age>=5 and age<8 end
 end
 emu.setInput(input,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1;minSP=math.min(minSP,emu.getState()['cpu.sp'])
 if entered then local s=emu.getState();for i=0,11 do assert(s['mapper.chrBanks'..i]==physical[i],'Actual CHR hardware agrees with write-time latch model');chrChecks=chrChecks+1 end end
 if entered and phase=='use'and index<8 and not rec.sampled and rec.spawns>0 and pool()>0 then
  rec.sampled=true;rec.sample_wall=wall;screenshot=string.format('item-%02d.png',index)
 end
 if screenshot then assert(images<8,'Eight selected screenshots maximum');local f=assert(io.open(OUTPUT..screenshot,'wb'));f:write(emu.takeScreenshot());f:close();images=images+1;screenshot=nil end
 assert(wall<C.frame_limit,'Finite native profile frame cap')
 if done then
  assert(not pending and not spend and dmas>100 and irqCount>100 and nmis>100 and enables>100 and late==0,'Actual hardware/source guards exercised')
  local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=true,native_run=true,ROM_sha256=C.ROM_sha256,character=C.character,mode=C.mode,mature_actor_collection_only=true,full_block_reveal_rise=false,ownership_or_ammo_seeded=false,cases=records,wall=wall,updates=updates,complete256_DMAs=dmas,NMI_checks=nmis,IRQ31_checks=irqCount,NMI_safe_enables=enables,CHR_checks=chrChecks,late=late,screenshots=images,minSP=minSP,goal_complete=false}));f:close();csv:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
