-- Reuses historical native-items-core's head-bump/rise/post-rise placement,
-- and legacy-native-items-v3's cold menu/guarded native loop entry.
-- These three families own PlayerStatus, not the twelve-family inventory.
local C=assert(FINAL_ITEM_PROGRESSIVE)
for n,a in pairs(C.ram)do L[n]=a end
local wall,updates,age,index,nmis=0,0,0,1,0
local entered,done,writeBoundary=false,false,false
local phase,menuPhase='menu',C.hard and'focus'or'start'
local records,queue={},{}
local minSP,apuWrites=255,0
local irqStores,chrChecks,dmaChecks=0,0,0
local record=nil
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)assert(writeBoundary,'Fixture writes only at native GameLoop entry');assert(n~='PlayerStatus','Power tiers must be acquired');emu.write(assert(L[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
local function json(v)
 if type(v)=='table'then local o={};if #v>0 then for _,x in ipairs(v)do o[#o+1]=json(x)end;return'['..table.concat(o,',')..']'end
  for k,x in pairs(v)do o[#o+1]=string.format('%q',k)..':'..json(x)end;return'{'..table.concat(o,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)else return tostring(v)end
end
local log=assert(io.open(OUTPUT..'events.jsonl','w'))
local apu=assert(io.open(OUTPUT..'apu.csv','w'));apu:write('wall,update,case,phase,register,value,pc,bank,cycle\n')
local function bank(a)local p=emu.convertAddress(a);return p and p.address//8192 or-1 end
local function event(kind,data)local s=emu.getState();log:write(json({kind=kind,data=data,wall=wall,update=updates,case=index,phase=phase,pc=s['cpu.pc'],bank=bank(s['cpu.pc']),sp=s['cpu.sp']})..'\n');log:flush()end
local function hook(n,fn)
 local h=assert(C.hooks[n]);emu.addMemoryCallback(function()
  if bank(h.address)~=h.physical_bank then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Actual instruction '..n)end
  minSP=math.min(minSP,emu.getState()['cpu.sp']);fn()
 end,emu.callbackType.exec,h.address)
end
local function capture(n)queue[#queue+1]={name=n,update=updates,wall=wall,status=r('PlayerStatus')}end
-- Reuse the native CV3 observer's exact MMC5 write-time upper-latch model.
local upper=0;local physical={};local published,dma=nil,nil
local function bytes(at,kind)local s={};for i=0,255 do s[#s+1]=string.char(emu.read(at+i,kind))end;return table.concat(s)end
emu.addMemoryCallback(function(_,v)upper=v&3 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(a,v)physical[a-0x5120]=v+256*upper end,emu.callbackType.write,0x5120,0x512b)
hook('RosterOamReady',function()if entered and not done then published=bytes(L.Sprite_Data,emu.memType.nesDebug)end end)
emu.addMemoryCallback(function(_,v)
 dma=nil;if entered and not done and published then local s=bytes(v*256,emu.memType.nesDebug);if s==published then dma=s end end
end,emu.callbackType.write,0x4014)
for _,pc in ipairs(C.irq_scroll_stores)do
 emu.addMemoryCallback(function()
  if entered and not done then
   assert(bank(pc)==C.hooks.IrqScrollSplit.physical_bank,'Actual IRQ bank')
   assert(emu.getState()['ppu.scanline']==31,'Actual split scroll on line31');irqStores=irqStores+1
  end
 end,emu.callbackType.exec,pc)
end
local function tile(page,col,row,id)
 assert(writeBoundary,'Visible world staging at guarded update entry')
 local function rom(n)local q=C.art[n];return emu.read(q.bank*8192+q.address%8192+id,emu.memType.nesPrgRom)end
 local function p(a,v)emu.write(a,v,emu.memType.nesPpuDebug)end
 local a=0x2000+page*0x400+row*64+col*2
 p(a,rom('MTileTopLeft'));p(a+1,rom('MTileTopRight'));p(a+32,rom('MTileBotLeft'));p(a+33,rom('MTileBotRight'))
 local a=0x23c0+page*0x400+(row//2)*8+col//2;local shift=row%2*4+col%2*2
 p(a,(emu.read(a,emu.memType.nesPpuDebug)&(~(3<<shift)))|((rom('MTileAttribute')>>6)<<shift))
end
local function menu()
 if wall<90 or wall%12~=0 then return{}end
 if menuPhase=='focus'then menuPhase='open';return{down=true}end
 if menuPhase=='open'then menuPhase='mode';return{a=true}end
 if menuPhase=='mode'then
  if r('CrossoverMenuState')~=4 then return{}end
  if r('CrossoverOptionsFocus')~=1 then return{down=true}end
  if r('CrossoverBehaviorVersion')==0 then menuPhase='back';return{a=true}end
  menuPhase='back'
 end
 if menuPhase=='back'then menuPhase='start';return{b=true}end
 if menuPhase=='start'then if r('CrossoverMenuState')==2 then menuPhase='select'else return{start=true}end end
 if r('CrossoverMenuState')~=2 then return{}end
 local i=r('CrossoverMenuIndex');local row=i<12 and i//6 or 2;local target=C.slot<12 and C.slot//6 or 2
 if row~=target then return{down=true}end
 if i~=C.slot then return{right=true}end
 if C.family=='scrooge'and r('DarkwingVariant')~=0 then return{select=true}end
 return{a=true}
end
local function arena(delivery)
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do for col=0,15 do for row=11,12 do w('Block_Buffer_1',0x54,p*208+row*16+col)end end end
 for p=0,1 do for row=2,14 do for col=0,15 do tile(p,col,row,row>=13 and 0x54 or 0)end end end
 if delivery then w('Block_Buffer_1',0xc1,128+7);tile(0,7,10,0xc1)end
 for i=0,5 do assert(r('FloateyNum_Control',i)==0,'Previous score actor released');w('Enemy_Flag',0,i);w('Enemy_CollisionBits',0,i)end
 for i=0,3 do w('Block_State',0,i);w('BlockMetasprite',0,i);w('MmBulletType',0,i)end
 for i=0,1 do w('Block_RepFlag',0,i);w('MmXFraction',0,i);w('MmYFraction',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for _,n in ipairs({'BlockBounceTimer','RgCooldown','RgShootPose','RgAttack','Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','ScrollThirtyTwo','AreaParserTaskNum','InjuryTimer','StarInvincibleTimer'})do w(n,0)end
 w('ScrollLock',1);w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_X_Position',112);w('Player_PageLoc',0);w('MmOldX',112);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1);w('TimerControl',0)
end
local function seed()
 local q=C.steps[index];assert(r('PlayerStatus')==q.before,'Tier is previous native collection result')
 arena(true);record={before=q.before,expected=q.after,type=q.type,staged=wall,transformCalls=0,ownerCalls=0,attackObserved=false,cleanupObserved=false,apuBefore=apuWrites}
 records[index]=record
 phase='collect';age=0;event('visible-logical-block-staged',record);capture('block-'..index)
end
hook('GameLoop',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then
  if r('GameEngineSubroutine')~=8 then return end
  assert(r('SelectedCharacter')==C.character and r('CrossoverBehaviorVersion')==(C.hard and 1 or 0),'Actual cold selected owner/mode')
  if C.family=='scrooge'then assert(r('DarkwingVariant')==0,'Actual selected Scrooge')end
  assert(r('PlayerStatus')==0,'Cold selection starts unpowered');entered=true;phase='settle';age=0
 end
 updates=updates+1;age=age+1
 if phase=='settle'and age>=30 or phase=='next'then
  writeBoundary=true;seed();writeBoundary=false
 elseif phase=='collect'and record.mature and age>=110 and not record.collisionPlaced then
  -- The original physical-item fixture explicitly aligns the fully risen
  -- actor for its collision test. Never seed an item or its outcome early.
  assert(r('Enemy_Flag',5)~=0 and r('Enemy_State',5)>=128,'Full native rise before collision placement')
  writeBoundary=true
  w('Enemy_X_Position',r('Player_X_Position'),5);w('Enemy_PageLoc',r('Player_PageLoc'),5);w('Enemy_Y_Position',184,5);w('Enemy_X_Speed',0,5);w('Enemy_Y_Speed',0,5)
  writeBoundary=false;record.collisionPlaced=wall;event('explicit-post-rise-collision-placement',{})
 elseif phase=='attack-setup'then
  writeBoundary=true;arena();writeBoundary=false;phase='attack';age=0
 end
 assert(r('MmDeathFlag')==0,'Scene survives')
end)
hook('MarioSourcePowerupCollision',function()
 if entered and phase=='collect'then assert(emu.getState()['cpu.x']==5,'Physical actor owns grant');record.ownerCalls=record.ownerCalls+1;event('actual-physical-owner',{status=r('PlayerStatus'),type=r('PowerUpType',5)})end
end)
hook('GuestBeginPowerup',function()
 if entered and phase=='collect'then
  event('actual-guest-powerup-entry',{status=r('PlayerStatus')});record.beginCalls=(record.beginCalls or 0)+1
  assert(r('Square2SoundQueue')&C.powerup_sfx~=0,'Actual source item sound queued')
  record.heldX=r('Player_X_Position');record.heldPage=r('Player_PageLoc');record.heldY=r('Player_Y_Position');record.heldPose=r('RgPose')
 end
end)
hook('GuestPowerupUpdate',function()
 if entered and phase=='collect'and r('GuestPowerupActive')~=0 then
  record.transformCalls=record.transformCalls+1
  assert(r('PlayerStatus')==record.before,'Tier remains old through native transformation')
  assert(r('GuestPowerupAge')==record.transformCalls-1,'Consecutive source animation ages')
  assert(r('Player_X_Position')==record.heldX and r('Player_PageLoc')==record.heldPage and r('Player_Y_Position')==record.heldY,'Native transformation holds player position')
  assert(r('GuestPowerupPose')==record.heldPose,'Native transformation retains source pose')
  if record.transformCalls==6 or record.transformCalls==30 then capture('transform-'..index..'-'..record.transformCalls)end
  -- GameLoop decrements the previous FF master timer once before dispatch.
  assert(r('GuestPowerupTarget')==record.expected and r('TimerControl')==254,'Native target and world freeze')
 end
end)
emu.addMemoryCallback(function(a,v)
 if entered and not writeBoundary then event('native-tier-write',{before=r('PlayerStatus'),value=v})end
end,emu.callbackType.write,L.PlayerStatus)
hook('finish',function()
 if not entered or done then return end
 if phase=='collect'then
  assert(age<600,'Bounded real collection/transform')
  for i=0,3 do if r('Block_State',i)~=0 then assert(r('Block_X_Position',i)==112,'Actual head activates intended question block');record.headBlockObserved=true end end
  if r('Enemy_Flag',5)~=0 and r('Enemy_ID',5)==0x2e then
   assert(r('PowerUpType',5)==record.type,'Source block chooses actual progressive mushroom/flower')
   assert(r('InvPickup',5)==252,'Source fallback stamp stable')
   if not record.revealed then
    assert(record.headBlockObserved and r('Enemy_X_Position',5)==112 and r('Enemy_PageLoc',5)==0,'Reward comes from actual activated block')
    record.revealed=wall;record.revealY=r('Enemy_Y_Position',5);event('native-block-reveal',{state=r('Enemy_State',5),y=record.revealY});capture('reveal-'..index)
   end
   if r('Enemy_State',5)<128 then
    assert(r('PlayerStatus')==record.before and r('GuestPowerupActive')==0 and record.ownerCalls==0,'No grant while native actor rises')
   elseif not record.mature then
    assert(r('Enemy_Y_Position',5)<record.revealY,'Actual visible vertical emergence');record.mature=wall;event('native-full-rise',{});capture('mature-'..index)
   end
  end
  if record.revealed and r('Enemy_Flag',5)==0 and r('GuestPowerupActive')==0 and r('TimerControl')==0 then
   assert(record.mature and record.collisionPlaced and wall>=record.mature,'Grant after native full rise')
   assert(record.ownerCalls==1 and record.beginCalls==1,'One actual physical source grant')
   assert(r('PlayerStatus')==record.expected,'Actual acquired tier/cap')
   assert(record.transformCalls==(record.before<2 and 60 or 0),'Exact native60-update transform, no transform at cap')
   record.collected=wall;record.after=r('PlayerStatus');phase='score-release';age=0;capture('collected-'..index)
  end
 elseif phase=='score-release'and age>=50 and r('FloateyNum_Control',5)==0 then phase='attack-setup';age=0
 elseif phase=='attack'then
  local hadAttack=record.attackObserved
  if C.shot>0 then for i=0,9 do if r('RgShotType',i)==C.shot then record.attackObserved=true end end
  elseif r('ScAttack')>0 then record.attackObserved=true end
  if record.attackObserved and not hadAttack then record.attackAtUpdate=updates;capture('attack-first-'..index);event('actual-acquired-tier-attack',{})end
  if record.attackAtUpdate and updates==record.attackAtUpdate+4 then capture('attack-live-'..index)end
  if record.attackObserved and age>15 then
   local active=false
   if C.shot>0 then for i=0,9 do if r('RgShotType',i)==C.shot then active=true end end else active=r('ScAttack')>0 end
   if not active then record.cleanupObserved=true end
  end
  if age>=180 then
   assert(record.attackObserved and record.cleanupObserved,'Acquired-tier native B attack and cleanup')
   assert(apuWrites>record.apuBefore,'Native item/attack APU writes');capture('used-'..index);event('case-completed',record)
   index=index+1
   if index>#C.steps then
    assert(nmis>0 and minSP>=128,'NMI/stack exercised');done=true
    phase='complete'
   else phase='next';age=0 end
  end
 end
end)
-- Existing exact bank-publication semantics: an NMI can interrupt between the
-- software-shadow store and hardware store. Preserve that bounded window.
local saved=nil
local function store(pc,target)return emu.read(pc,emu.memType.nesDebug)==0x8d and emu.read(pc+1,emu.memType.nesDebug)==target%256 and emu.read(pc+2,emu.memType.nesDebug)==target//256 end
local function window(pc,target,shadow)
 if store(pc,target)then return store(pc-3,shadow)or(emu.read(pc-2,emu.memType.nesDebug)==0xa9 and store(pc-5,shadow))end
 return emu.read(pc,emu.memType.nesDebug)==0xa9 and store(pc+2,target)and store(pc-3,shadow)
end
hook('NonMaskableInterrupt',function()
 if not entered or done then return end
 local s=emu.getState();local sp=s['cpu.sp'];local pc=emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+3)%256,emu.memType.nesDebug)
 saved={a=bank(0xa000),c=bank(0xc000),sa=r('CurrentBank')&127,sc=r('CurrentBankC')&127,sp=sp,cpu_a=s['cpu.a'],fields={}}
 saved.wa=saved.a~=saved.sa and window(pc,0x5115,L.CurrentBank);saved.wc=saved.c~=saved.sc and window(pc,0x5116,L.CurrentBankC)
 for _,a in ipairs(C.smc_fields)do saved.fields[#saved.fields+1]=emu.read(a,emu.memType.nesDebug)end;nmis=nmis+1
end)
hook('NmiReturn',function()
 if not saved then return end
 assert(bank(0xa000)==(saved.wa and saved.sa or saved.a)and bank(0xc000)==(saved.wc and saved.sc or saved.c),'NMI actual foreground banks')
 assert(r('CurrentBank')&127==saved.sa and r('CurrentBankC')&127==saved.sc,'NMI shadow banks')
 assert(emu.getState()['cpu.sp']==saved.sp and emu.getState()['cpu.a']==saved.cpu_a,'NMI stack/register restore')
 for i,a in ipairs(C.smc_fields)do assert(emu.read(a,emu.memType.nesDebug)==saved.fields[i],'Five SMC operands restored')end
 saved=nil
end)
emu.addMemoryCallback(function()if entered and not done then assert(emu.getState()['cpu.sp']>=128,'Native lower stack guard')end end,emu.callbackType.write,0x17f)
emu.addMemoryCallback(function(a,v)
 if entered then local s=emu.getState();apuWrites=apuWrites+1;apu:write(table.concat({wall,updates,index,phase,a,v,s['cpu.pc'],bank(s['cpu.pc']),s['cpu.cycleCount']},',')..'\n')end
end,emu.callbackType.write,0x4000,0x4017)
emu.addEventCallback(function()
 if not entered then emu.setInput(menu(),0);return end
 local b={};if phase=='collect'then b.a=age>=10 and age<30;b.right=record.collisionPlaced~=nil elseif phase=='attack'then b.b=age>=5 and age<9 end;emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1
 if entered and not done then
  local st=emu.getState()
  for i=0,11 do assert(st['mapper.chrBanks'..i]==physical[i],'Hardware CHR agrees with write-time latch model');chrChecks=chrChecks+1 end
  if dma then assert(bytes(0,emu.memType.nesSpriteRam)==dma,'Committed native publication reaches OAM DMA');dmaChecks=dmaChecks+1;dma=nil end
 end
 for _,q in ipairs(queue)do
  local screen=emu.getScreenBuffer();assert(#screen==256*240,'Real PPU screen dimensions')
  local f=assert(io.open(OUTPUT..q.name..'.argb','wb'));for _,v in ipairs(screen)do f:write(string.pack('<I4',v))end;f:close()
  event('ppu-frame-captured',q)
 end;queue={}
 if done then
  assert(irqStores>100 and chrChecks>1200 and dmaChecks>100,'Native IRQ/CHR/DMA exercised')
  apu:close()
  local f=assert(io.open(OUTPUT..'native-progressive.json','w'));f:write(json({passed=true,goal_complete=false,family=C.family,hard=C.hard,cases=records,updates=updates,nmis=nmis,minSP=minSP,apuWrites=apuWrites,irq_scroll_stores=irqStores,hardware_chr_checks=chrChecks,complete_dma_checks=dmaChecks,scope='Actual head-bump/reveal/native full rise; explicit post-rise collision placement; cold selection and source-owned transformation/use. No campaign claim'}));f:close();emu.stop(0)
 end
 assert(wall<9000,'Bounded progressive fixture '..phase)
end,emu.eventType.endFrame)
