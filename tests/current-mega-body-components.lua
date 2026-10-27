-- Prepared current-ROM collection/use components, not a natural route/RNG test.
-- No item ownership, tier, selection, ammo, projectile or outcome is seeded.
local C=assert(CURRENT_MEGA_BODY_COMPONENTS)
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
local events={}
local rushSlot=nil
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(at)local p=emu.convertAddress(at);return p and p.address//8192 or-1 end
local function pool()local n=0;for i=0,9 do if r('RgShotType',i)~=0 then n=n+1 end end;return n end
local function stock(item)return r('InvAmmo',C.character*16+item)end
local function has(item)return((r('InvOwnedLo',C.character)+256*r('InvOwnedHi',C.character))&(1<<item))~=0 end
local function event(kind,value)
 local s=emu.getState();assert(#events<512,'Bounded component event records')
 events[#events+1]={kind=kind,wall=wall,update=updates,phase=phase,value=value,pc=s['cpu.pc'],bank=bank(s['cpu.pc']),cycle=s['cpu.cycleCount']}
 print('MMBODY '..kind..' phase='..phase..' update='..updates..' value='..tostring(value))
end
local function json(v)
 if type(v)=='table'then local out={};local array=#v>0
  for k in pairs(v)do if type(k)~='number'or k<1 or k>#v or k%1~=0 then array=false end end
  if array then for _,x in ipairs(v)do out[#out+1]=json(x)end;return'['..table.concat(out,',')..']'end
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
local forbidden={MmBulletType=true,MmChargeFrames=true,MmCharging=true,SsMode=true,MmRushLandRequest=true,InvOwnedLo=true,InvOwnedHi=true,InvViewedLo=true,InvViewedHi=true,InvSelected=true,InvAmmo=true,PlayerStatus=true,GuestPowerupActive=true,GameEngineSubroutine=true,InjuryTimer=true,MmDeathFlag=true,RgShotType=true,CheatInvincible=true}
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
 for i=0,3 do assert(r('InvDropKind',i)==0,'No earned world capsule is discarded by a new scene')end
 for _,n in ipairs({'Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','ScrollThirtyTwo','AreaParserTaskNum'})do w(n,0)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('ScrollLock',1);w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_X_Position',64);w('Player_PageLoc',0);w('MmOldX',64);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1);w('Player_MovingDir',1);w('Player_CollisionBits',255)
end
local function mature(item)
 assert(item==0 or item==8,'Only typed mushroom/Coil actor metadata in this profile')
 w('Enemy_Flag',1,5);w('Enemy_ID',0x2e,5);w('Enemy_State',128,5)
 w('Enemy_BoundBoxCtrl',3,5);w('Enemy_X_Position',64,5);w('Enemy_PageLoc',0,5);w('Enemy_Y_Position',184,5);w('Enemy_Y_HighPos',1,5)
 w('Enemy_X_Speed',0,5);w('Enemy_Y_Speed',0,5);w('Enemy_SprAttrib',0,5)
 w('Enemy_Y_MoveForce',0,5);w('Enemy_MovingDir',1,5);w('EnemyOffscrBitsMasked',0,5)
 w('PowerUpType',item==0 and 0 or 1,5);w('InvPickupOwner',C.character,5);w('InvPickup',item,5)
end
local function change(p)phase=p;age=0;event('phase')end

-- One finite Hard component: mature mushroom0 -> real charge/slide/jump ->
-- mature Coil8 -> realSelect/free summon/land/buster/spring/departure.
-- RushFly is departure; this profile does not invent a playable Rush Jet.
rec={collections={},grants={},transforms=0,charge={},primary={},slide=false,jump=false,rushModes={},rushStock=nil,allocation_dma={}}
records[1]=rec
local function identity()
 assert(r('SelectedCharacter')==C.character and r(C.variant_ram)==C.variant and r('CrossoverBehaviorVersion')==C.mode,'Actual cold menu identity/variant/Hard')
 assert(r('CheatInvincible')==0 and r('CheatStartLevel')==0,'Default cheats off')
end
local function primaryCount()local n=0;for i=0,3 do if r('MmBulletType',i)~=0 then n=n+1 end end;return n end
local function primaryLive(t)for i=0,3 do if r('MmBulletType',i)==t then return true end end;return false end
local function shotEmpty()return primaryCount()==0 and pool()==0 and r('SsHeld')==0 end
local function stagePickup(item)
 assert(not has(item) and shotEmpty()and r('InvRefill')==0,'Unowned item and naturally drained effects before staged actor')
 assert(r('Enemy_Flag',5)==0,'No prior native pickup actor is overwritten')
 index=item;transaction(function()arena();mature(item)end);change(item==0 and'mushroom'or'coil-collect')
 event('typed-mature-actor',item)
end
local function nextPhase(name)change(name);rec.phase_dma=dmas end
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
 local i=r('CrossoverMenuIndex');local key=C.navigation[i+1]
 if key~=''then return{[key]=true}end
 if r(C.variant_ram)~=C.variant then return{select=true}end
 return{a=true}
end
hook('GameLoopOwned',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then
  if r('GameEngineSubroutine')~=8 then return end
  identity()
  assert(r('PlayerStatus')==0 and r('InvOwnedLo',C.character)==0 and r('InvOwnedHi',C.character)==0,'Actual unpowered unowned cold start')
  assert(stock(8)==C.rush.initial_ammo,'Actual native cold Coil stock; no fixture refill')
  entered=true;nextPhase('settle')
 end
 updates=updates+1;age=age+1;identity()
 if phase=='settle'and age>=30 then stagePickup(0)
 elseif phase=='coil-setup'then stagePickup(8)
 elseif phase=='rush-contact-setup'then
  assert(rushSlot and r('RgShotType',rushSlot)==20 and r('SsMode',rushSlot)==1 and r('RgShotY',rushSlot)==208,'Actual Rush landed before disclosed falling-player placement')
  transaction(function()
   local x=r('RgShotX',rushSlot)-8
   w('Player_X_Position',x);w('MmOldX',x);w('Player_PageLoc',r('RgShotPage',rushSlot))
   w('Player_Y_Position',160);w('Player_Y_HighPos',1);w('Player_State',2);w('Player_Y_Speed',2)
   w('Player_X_Speed',0);w('Player_X_MoveForce',0);w('Player_Y_MoveForce',0);w('MmFrictionYActive',0)
   for i=0,1 do w('MmVX',0,i);w('MmVY',0,i);w('MmXFraction',0,i);w('MmYFraction',0,i)end
   w('MmVX',0,2);w('MmVY',2,2)
  end)
  event('disclosed-player-contact-alignment',rushSlot);nextPhase('rush-contact')
 end
end)
hook('PhysicalPickup',function(s)
 if not entered or phase~='mushroom'and phase~='coil-collect'then return end
 assert(s['cpu.x']==5 and r('Enemy_Flag',5)~=0 and r('Enemy_ID',5)==0x2e and r('Enemy_State',5)>=128,'Actual mature item before physical native collision erase')
 assert(r('InvPickupOwner',5)==C.character and r('InvPickup',5)==index,'Actual typed pickup actor ID/owner')
 rec.collision_update=updates;event('actual-mature-collision',index)
end)
hook('InventoryCollect',function(s)
 if not entered or phase~='mushroom'and phase~='coil-collect'then return end
 assert(s['cpu.x']==5 and rec.collision_update==updates and r('Enemy_Flag',5)==0 and r('Enemy_State',5)==0,'Actual collision/erase precedes native collection')
 assert(r('InvPickupOwner',5)==C.character and r('InvPickup',5)==index,'Native collect exact item')
 rec.collections[index]=(rec.collections[index]or 0)+1;event('actual-collect',index)
end)
hook('InventoryGrant',function(s)
 if entered and phase=='coil-collect'then assert(s['cpu.a']==8,'Actual Coil item8 grant');rec.grants[8]=(rec.grants[8]or 0)+1;event('actual-grant',8)end
end)
hook('GuestPowerupUpdate',function()
 if entered and phase=='mushroom'and r('GuestPowerupActive')~=0 then rec.transforms=rec.transforms+1 end
end)
hook('PrimarySpawn',function(s)
 if not entered or phase~='weak'and phase~='full'and phase~='rush-existing'then return end
 local t=s['cpu.a'];local charge=r('MmChargeFrames')
 if t==2 then assert(phase=='weak'and charge>=C.charge.weak and charge<C.charge.full,'Actual weak threshold')
 elseif t==3 then assert(phase=='full'and charge==C.charge.full,'Actual full charge cap')
 else assert(t==1,'Only earned tier1 primary types in this profile')end
 rec.pendingPrimary={type=t,charge=charge,update=updates,phase=phase};event('actual-primary-entry',t)
end)
emu.addMemoryCallback(function(a,v)
 if not entered or writing or v==0 then return end
 local s=emu.getState();local h=C.primary_store
 if bank(s['cpu.pc'])~=h.bank or(s['cpu.pc']~=h.pc and s['cpu.pc']~=h.after)then return end
 for i,x in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==x,'Actual primary allocation store opcode')end
 if phase=='weak'or phase=='full'or phase=='rush-existing'then
  local q=assert(rec.pendingPrimary,'Real primary source entry before type write')
  assert(v==q.type,'Native primary type matches actual source call')
  q.slot=a-C.ram.MmBulletType;rec.primary[#rec.primary+1]=q;rec.charge[v]=true;rec.pendingPrimary=nil
  rec.allocation_dma[v]=dmas
  if q.phase=='rush-existing'then rec.existingBuster=true end
  event('native-primary-allocation',v)
 end
end,emu.callbackType.write,C.ram.MmBulletType,C.ram.MmBulletType+3)
hook('RushAttack',function()
 if entered and(phase=='rush-summon'or phase=='rush-existing')then
  assert(has(8)and r('InvSelected',C.character)==8 and stock(8)>=C.rush.summon_gate,'Actual earned/funded Coil owner')
  rec.rushAttackBefore=stock(8);event('actual-rush-attack-entry',stock(8))
 end
end)
hook('RushBounce',function()
 if entered and phase=='rush-contact'then
  assert(not rec.bounce_entry and r('StarInvincibleTimer')==0,'One real non-star Coil bounce')
  rec.bounce_entry=updates;rec.bounce_before=stock(8);event('actual-rush-bounce-entry',stock(8))
 end
end)
emu.addMemoryCallback(function(_,v)
 if entered and not writing and rec.bounce_entry and not rec.debit then
  assert(v==math.max(0,rec.bounce_before-C.rush.bounce_cost),'Actual source Coil debit at native stock store')
  rec.debit={before=rec.bounce_before,after=v,update=updates};event('actual-rush-debit',v)
 end
end,emu.callbackType.write,C.ram.InvAmmo+C.rush.ammo_index)
hook('GameLoopFinish',function()
 if not entered or done then return end
 identity();assert(r('MmDeathFlag')==0 and r('NumberofLives')>=2,'Component survives without death')
 if phase=='mushroom'or phase=='coil-collect'then
  assert(age<240,'Bounded genuine mature item collection/transform')
  if rec.collections[index]and r('Enemy_Flag',5)==0 and r('GuestPowerupActive')==0 and r('TimerControl')==0 then
   assert(rec.collections[index]==1 and has(index)and r('PlayerStatus')==1,'Native earned ownership/tier, one collection')
   if index==0 then
    assert(rec.transforms==60 and has(10),'Actual60-call mushroom transform grants passive charge')
    rec.powered_dma=dmas;nextPhase('weak')
   else
    assert(rec.grants[8]==1 and stock(8)==C.rush.initial_ammo,'Actual Coil grant preserves native initialized stock')
    rec.rushStock=stock(8);nextPhase('select-coil')
   end
  end
 elseif phase=='weak'or phase=='full'then
  assert(r('InvSelected',C.character)==0,'Charge uses actual default buster')
  if phase=='weak'and age>=130 and shotEmpty()then
   assert(rec.charge[2]and rec.weakSample,'Real weak charge released/allocated and sampled after completed DMAs');nextPhase('full')
  elseif phase=='full'and age>=210 and shotEmpty()then
   assert(rec.charge[3]and rec.fullSample and r('MmChargeFrames')==0,'Real full charge released/sampled and drained');nextPhase('slide')
  end
  if not rec.poweredSample and dmas>=rec.powered_dma+2 then rec.poweredSample=true;screenshot='01-powered.png'end
  if phase=='weak'and rec.charge[2]and not rec.weakSample and primaryLive(2)and dmas>=rec.allocation_dma[2]+2 then rec.weakSample=true;screenshot='02-weak.png'end
  if phase=='full'and rec.charge[3]and not rec.fullSample and primaryLive(3)and dmas>=rec.allocation_dma[3]+2 then rec.fullSample=true;screenshot='03-full.png'end
  assert(age<300,'Charge/cleanup finite')
 elseif phase=='slide'then
  if r('MmSliding')~=0 then rec.slide=true;rec.slide_dma=rec.slide_dma or dmas;if not rec.slideSample and dmas>=rec.slide_dma+2 then rec.slideSample=true;screenshot='04-slide.png'end end
  if age>=100 and r('MmSliding')==0 and r('Player_State')==0 then assert(rec.slide and rec.slideSample,'Actual Down+A slide and sampled body');nextPhase('jump')end
  assert(age<200,'Native slide completes')
 elseif phase=='jump'then
  if r('Player_State')==1 and r('MmVY',2)>=128 then rec.jump=true;rec.jump_dma=rec.jump_dma or dmas;if not rec.jumpSample and dmas>=rec.jump_dma+2 then rec.jumpSample=true;screenshot='05-jump.png'end end
  if age>=120 and r('Player_State')==0 then assert(rec.jump and rec.jumpSample,'Actual A-only jump and sampled body');nextPhase('coil-setup')end
  assert(age<240,'Native jump lands')
 elseif phase=='select-coil'then
  assert(age<120,'Real Select reaches earned Coil')
  if r('InvSelected',C.character)==8 then nextPhase('rush-summon')end
 elseif phase=='rush-summon'or phase=='rush-existing'or phase=='rush-contact'then
  for i=0,9 do if r('RgShotType',i)==20 then
   rushSlot=i;local mode=r('SsMode',i);rec.rushModes[mode]=true
   if mode==1 and not rec.rushLanded then
    assert(r('RgShotY',i)==208 and stock(8)==rec.rushStock,'Free real Rush fall and native floor landing')
    rec.rushLanded=updates;event('native-rush-landed',i)
   end
  end end
  if phase=='rush-summon'and rec.rushLanded and updates-rec.rushLanded>=24 then
   assert(stock(8)==rec.rushStock,'Standing/summon free');screenshot='06-rush-standing.png';nextPhase('rush-existing')
  elseif phase=='rush-existing'and age>=55 then
   assert(rec.existingBuster and stock(8)==rec.rushStock,'Existing Rush gives free actual ordinary buster')
   if primaryCount()==0 then nextPhase('rush-contact-setup')end
  elseif phase=='rush-contact'and rec.debit and r('Player_State')==1 then
   assert(r('MmVY',2)>=128 and r('MmJumpReleased')==1 and r('MmFrictionYActive')==0,'Native Coil produces real upward player launch')
   rec.launch=true;rec.spring_dma=dmas;nextPhase('rush-depart')
  end
  assert(age<300,'Actual Rush summon/contact bounded')
 elseif phase=='rush-depart'then
  if rushSlot and r('RgShotType',rushSlot)==20 then rec.rushModes[r('SsMode',rushSlot)]=true end
  if not rec.springSample and dmas>=rec.spring_dma+2 then rec.springSample=true;screenshot='07-rush-spring.png'end
  if rec.rushModes[4]then rec.depart_dma=rec.depart_dma or dmas end
  if not rec.departSample and rec.depart_dma and dmas>=rec.depart_dma+2 then rec.departSample=true;screenshot='08-rush-departure.png'end
  if rushSlot and r('RgShotType',rushSlot)==0 and age>=100 and r('Player_State')==0 then
   assert(rec.launch and rec.rushModes[0]and rec.rushModes[1]and rec.rushModes[2]and rec.rushModes[3]and rec.rushModes[4],'Actual Coil fall/stand/spring/exit/departure, not Jet')
   assert(stock(8)==rec.rushStock-C.rush.bounce_cost,'Exactly one earned Coil spring debit')
   done=true;nextPhase('complete')
  end
  assert(age<300,'Native Rush departure/drain bounded')
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
 local b={}
 if phase=='weak'then b.b=age>=4 and age<63
 elseif phase=='full'then b.b=age>=4 and age<113
 elseif phase=='slide'then b.down=age>=5 and age<12;b.a=age>=6 and age<10
 elseif phase=='jump'then b.a=age>=5 and age<16
 elseif phase=='select-coil'then b.select=age%8==1
 elseif phase=='rush-summon'or phase=='rush-existing'then b.b=age>=5 and age<9 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1;minSP=math.min(minSP,emu.getState()['cpu.sp'])
 if entered then local s=emu.getState();for i=0,11 do assert(s['mapper.chrBanks'..i]==physical[i],'Actual CHR hardware agrees with write-time latch model');chrChecks=chrChecks+1 end end
 if screenshot then assert(images<8,'Eight actual whole-PPU PNGs maximum');local f=assert(io.open(OUTPUT..screenshot,'wb'));f:write(emu.takeScreenshot());f:close();images=images+1;screenshot=nil end
 assert(wall<C.frame_limit,'Finite component frame bound')
 if done then
  assert(not pending and dmas>100 and irqCount>100 and nmis>100 and enables>100 and late==0,'Strict native hardware guards exercised')
  local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=true,native_run=true,ROM_sha256=C.ROM_sha256,identity=C.identity,variant=C.variant,mode=C.mode,actor_metadata_staged=true,ownership_tier_ammo_projectile_seeded=false,block_reveal_rise_RNG=false,RushJet_supported=false,record=rec,events=events,wall=wall,updates=updates,complete256_DMAs=dmas,NMI_checks=nmis,IRQ31_checks=irqCount,safe_enables=enables,CHR_checks=chrChecks,screenshots=images,minSP=minSP,limits='Powered primary/support and body poses only. Right-facing/default non-star/nonempty pool. No natural lottery/reveal, zeroammo/fullpool, dense-world/per-shot fairness or original palette/audio-fidelity claim.'}));f:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
