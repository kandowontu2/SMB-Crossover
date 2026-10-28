-- ZeldaII mature rewards and genuine paid abilities. No RPG/resource/outcome seeds.
local C=assert(CURRENT_ZELDA2_EARNED)
local wall,updates,entered,done,writing=0,0,false,false,false
local menuPhase=C.mode==1 and'options-focus'or'start'
local nmi,irq=nil,false
local minSP,dmas,enables,late,irqCount,nmis,images=255,0,0,0,0,0,0
local mask,pending,upper,physical,chrChecks=0,nil,0,{},0
local desired,taskName,phaseAge=0,'cold',0
local records,counts,screenshots={}, {}, {}
local screenshot=nil
local csv=assert(io.open(OUTPUT..'zelda2-components.csv','w'))
csv:write('event,wall,update,task,age,x,y,state,hp,mp,exp,levels,containers,learned,tech,active,selection,pause,panel,pending,value,pc,bank,cycle\n')
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(at)local p=emu.convertAddress(at);return p and p.address//8192 or-1 end
local function exp()return r('Z2ExpLo')+256*r('Z2ExpHi')end
local function shot()return r('Z2ShotKind')~=0 or r('Z2ShotKind',1)~=0 end
local function snap()local t={};for _,n in ipairs(C.final_fields)do t[n]=r(n)end;return t end
local function event(kind,value)
 local s=emu.getState();csv:write(table.concat({kind,wall,updates,taskName,phaseAge,r('Player_X_Position'),r('Player_Y_Position'),r('Player_State'),r('Z2Hp'),r('Z2Mp'),exp(),r('Z2LevelsLo'),r('Z2Containers'),r('Z2LearnedSpells'),r('Z2Tech'),r('Z2ActiveSpells'),r('Z2Selection'),r('GamePauseStatus'),r('Z2PanelActive'),r('Z2PanelPending'),value or 0,s['cpu.pc'],bank(s['cpu.pc']),s['cpu.cycleCount']},',')..'\n')
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
local function w(n,v,i)
 assert(writing and not nmi and not irq and r('NmiDisable')==255,'Only synchronous GameLoop+5 setup')
 assert(C.setup_allowed[n]and not C.forbidden[n],'No RPG/resource/health/outcome seed '..n)
 emu.write(assert(C.ram[n],n)+(i or 0),v&255,emu.memType.nesDebug)
end
local function transaction(fn)
 assert(not writing and not nmi and not irq and r('NmiDisable')==255,'Actual foreground scene owner')
 writing=true;fn();writing=false;event('disclosed-scene-setup')
end
local function tile(page,col,row,id)
 assert(writing,'Same native scene owner')
 local function source(n)local p=C.metatiles[n];return emu.read(p.bank*8192+p.offset+id,emu.memType.nesPrgRom)end
 local function put(a,v)emu.write(a,v,emu.memType.nesPpuDebug)end
 local at=0x2000+page*1024+row*64+col*2
 put(at,source('MTileTopLeft'));put(at+1,source('MTileTopRight'));put(at+32,source('MTileBotLeft'));put(at+33,source('MTileBotRight'))
 local a=0x23c0+page*1024+(row//2)*8+col//2;local shift=row%2*4+col%2*2
 put(a,(emu.read(a,emu.memType.nesPpuDebug)&(~(3<<shift)))|((source('MTileAttribute')>>6)<<shift))
end
local function scene()
 transaction(function()
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
  for p=0,1 do for row=2,14 do for col=0,15 do tile(p,col,row,row>=13 and 0x54 or 0)end end end
  for p=0,1 do for row=11,12 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+row*16+col)end end end
  for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_CollisionBits',0,i)end
  for _,n in ipairs({'Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','ScrollThirtyTwo','AreaParserTaskNum'})do w(n,0)end
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
  for n,v in pairs({ScrollLock=1,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,Player_X_Position=112,Player_PageLoc=0,MmOldX=112,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,PlayerFacingDir=1,Player_MovingDir=1,Player_CollisionBits=255})do w(n,v)end
 end)
end
local function actor(kind,x,y,slot)
 slot=slot or 0
 local vals={Enemy_Flag=1,Enemy_ID=kind,Enemy_State=kind==46 and 128 or 0,Enemy_BoundBoxCtrl=kind==46 and 3 or 9,Enemy_X_Position=x&255,Enemy_PageLoc=x//256,Enemy_Y_Position=y,Enemy_Y_HighPos=1,Enemy_X_Speed=0,Enemy_Y_Speed=0,Enemy_Y_MoveForce=0,Enemy_MovingDir=kind==46 and 1 or 2,Enemy_SprAttrib=0,EnemyOffscrBitsMasked=0,Enemy_CollisionBits=0,MmEnemyHealthLo=0,MmEnemyHealthHi=0,MmEnemyFlash=0,RgEnemyStun=0}
 transaction(function()for n,v in pairs(vals)do w(n,v,slot)end end)
end
local function begin(name)taskName=name;phaseAge=0;event('task-start')end
local function record(name,before,extra)local t=extra or{};t.name=name;t.before=before;t.after=snap();records[#records+1]=t;event('task-complete')end
local function request_image(name)assert(not screenshots[name]and images<8,'One selected actual sample');screenshots[name]=true;screenshot=name..'.png'end
-- A requested edge advances only after a real completed Main saw both source inputs.
-- This never writes SavedJoypad*, source pressed flags, or any tested result.
local function tick(bits)
 desired=bits or 0
 repeat coroutine.yield()until r('SavedJoypadBits')==desired and r('SavedJoypad1Bits')==desired
end
local function wait(pred,limit,bits)
 for _=1,limit do if pred()then return end;tick(bits or 0)end
 event('failed-wait');assert(false,'Finite task '..taskName)
end
local function edge(bits)tick(0);tick(bits);tick(0)end
local function open_panel()
 wait(function()return r('GamePauseTimer')==0 end,100);edge(16)
 wait(function()return r('GamePauseStatus')&1~=0 and r('Z2PanelActive')~=0 and r('Z2PanelPending')==0 end,60)
end
local function select_spell(spell)
 open_panel()
 if not screenshots['pause-spells']then request_image('pause-spells')end
 if r('Z2UiState')&1~=0 then edge(1)end
 wait(function()return r('Z2PanelPage')==0 and r('Z2PanelPending')==0 end,60)
 for _=1,8 do if r('Z2Selection')&7==spell then break end;edge(4)end
 assert(r('Z2Selection')&7==spell,'Real panel selected requested learned spell')
 edge(128);wait(function()return r('GamePauseStatus')&1==0 and r('Z2PanelActive')==0 and r('Z2PanelPending')==0 end,60)
end
local function cast(spell)
 begin('cast-'..spell);select_spell(spell);local before=snap();local magic=(r('Z2LevelsLo')>>3)&7
 local cost=C.spell_costs[spell*8+magic+1];local owner=counts.Cast or 0
 edge(32)
 assert((counts.Cast or 0)==owner+1 and r('Z2Mp')==before.Z2Mp-cost,'Actual learned Select cast pays exact native cost')
 record(taskName,before,{cost=cost})
end
local function drop(kind)
 begin('physical-drop-'..kind);scene();local before=snap()
 transaction(function()for n,v in pairs({Z2DropKind=kind,Z2DropX=120,Z2DropPage=0,Z2DropY=176,Z2DropVY=0,Z2DropFraction=0,Z2DropAge=0})do w(n,v,5)end end)
 tick();assert(r('Z2DropKind',5)==0,'Real mature jar/EXP actor collected')
 wait(function()return r('Z2MpPending')==0 and r('Z2ExpPendingLo')==0 and r('Z2ExpPendingHi')==0 end,350)
 record(taskName,before)
end
local function level(category)
 begin('earned-level-'..category)
 wait(function()return r('GamePauseStatus')&1~=0 and r('Z2PanelActive')~=0 and r('Z2PanelPending')==0 end,60)
 if r('Z2UiState')&1==0 then edge(1)end
 wait(function()return r('Z2PanelPage')==1 and r('Z2PanelPending')==0 end,60)
 for _=1,4 do if r('Z2UiCursor')==category then break end;edge(4)end
 assert(r('Z2UiCursor')==category,'Actual upgrade category')
 local before=snap();local old=exp();local cost=({200,100,50})[category+1];local c=counts.Level or 0
 if not screenshots['earned-level-panel']then request_image('earned-level-panel')end
 edge(128);wait(function()return r('Z2PanelPending')==0 end,60)
 assert(exp()==old-cost and(counts.Level or 0)==c+1,'Earned EXP exact actual purchase')
 record(taskName,before,{cost=cost})
end
local function injury(damage)
 begin('real-injury-'..damage);scene();actor(6,112,168);local before=snap();local n=counts.Damage or 0
 tick();tick();assert(r('Z2Hp')==before.Z2Hp-damage and(counts.Damage or 0)==n+1,'Actual contact creates source health deficit')
 transaction(function()w('Enemy_Flag',0)end);wait(function()return r('Z2HurtTimer')==0 end,80);record(taskName,before)
end
local function raised(col)
 transaction(function()for c=col,col+1 do w('Block_Buffer_1',0x54,160+c);tile(0,c,12,0x54)end end)
end
local function campaign()
 begin('cold-settle');for _=1,30 do tick()end
 assert(r('Z2Hp')==127 and r('Z2Mp')==127 and r('Z2Containers')==51 and r('Z2LearnedSpells')==0,'Genuine initial ZeldaII RPG record')
 injury(16)
 for i,p in ipairs(C.rewards)do
  if i==20 then injury(16);cast(4);assert(r('Z2Mp')==15,'CD true restore deficit')end
  begin(string.format('reward-%02X-%d',p.reward,i));scene();actor(46,112,184,5)
  local before=snap();local collect=counts.Collect or 0
  transaction(function()for n,v in pairs(p.prepared)do w(n,v,5)end end)
  wait(function()return r('Enemy_Flag',5)==0 and r('Z2HpPending')==0 and r('Z2MpPending')==0 end,160)
  assert((counts.Collect or 0)==collect+1,'One actual mature reward collision')
  if i==1 then request_image('first-mushroom-Jump')end
  record(taskName,before,{reward=p.reward,prepared=p.prepared})
 end
 assert(r('Z2LearnedSpells')==255 and r('Z2Tech')==148 and r('Z2Containers')==119 and r('Z2Hp')==255 and r('Z2Mp')==47,'All earned spells/tech/containers and CD restoration')
 drop(0x91);assert(r('Z2Mp')==255)
 cast(0);assert(r('Z2ActiveSpells')&1~=0)
 drop(0x90);assert(r('Z2Mp')==223);drop(0x91);assert(r('Z2Mp')==255)
 injury(8);cast(2);wait(function()return r('Z2HpPending')==0 end,100);assert(r('Z2Hp')==255,'Actual Life heals real deficit')
 cast(1);assert(r('Z2ActiveSpells')&2~=0);begin('paid-Jump-motion');scene();local before=snap();tick(128);local low=r('Player_Y_Position')
 for _=1,60 do tick(128);low=math.min(low,r('Player_Y_Position'))end
 wait(function()return r('Player_State')==0 end,150);assert(low<before.Player_Y_Position-64,'Actual Jump raises native arc');record(taskName,before,{minimumY=low})
 begin('sword-defeat-EXP');scene();tick();raised(8);actor(6,136,168);before=snap();local n=counts.Hit or 0;local award=counts.Award or 0
 for age=0,159 do tick((age%18==1 or age%18==2)and 64 or 0);if r('Enemy_State')&32~=0 then break end end
 assert(r('Enemy_State')&32~=0 and(counts.Hit or 0)>=n+2 and(counts.Award or 0)>award,'Real sword defeats and earns EXP')
 wait(function()return not shot()and r('Z2AttackTimer')==0 end,150);record(taskName,before)
 drop(0x8a);level(2);drop(0x8c);level(1);drop(0x8c);level(0)
 wait(function()return r('GamePauseStatus')&1==0 and r('Z2PanelPending')==0 end,60);assert(r('Z2LevelsLo')==73 and r('Z2LevelsHi')==128)
 cast(4);assert(r('Z2ActiveSpells')&16~=0);begin('Fire-level-benefit');scene();tick();raised(10);actor(6,160,168);before=snap();local seen=false;n=counts.Hit or 0
 for age=0,179 do tick((age%20==1 or age%20==2)and 64 or 0);seen=seen or r('Z2ShotKind')==2 or r('Z2ShotKind',1)==2
  if seen and not screenshots['Fire-live']then request_image('Fire-live')end
  if r('Enemy_State')&32~=0 then break end
 end
 assert(seen and r('Enemy_State')&32~=0 and(counts.Hit or 0)>=n+2,'Actual upgraded Fire kills real target');record(taskName,before)
 drop(0x91);cast(5);assert(r('Z2ActiveSpells')&32~=0);begin('Reflect-real-flame');scene();tick();actor(21,130,176);before=snap()
 wait(function()return r('Enemy_Flag')==0 and(r('Z2ShotKind')==2 or r('Z2ShotKind',1)==2)end,20)
 assert(r('Z2Hp')==before.Z2Hp,'Actual Reflect prevents flame injury');request_image('Reflect-live');record(taskName,before);wait(function()return not shot()end,150)
 drop(0x91);begin('Spell-real-transform');scene();tick();actor(0,180,184);before=snap();cast(6)
 assert(r('Enemy_ID')==6 and r('Z2ActiveSpells')&64==0,'Spell changes eligible real enemy into Goomba');record('Spell-real-transform',before)
 drop(0x91);begin('Thunder-real-defeat');scene();tick();actor(0,180,184);before=snap();n=counts.Hit or 0;cast(7)
 assert(r('Enemy_State')&32~=0 and r('Z2ActiveSpells')&128==0 and(counts.Hit or 0)>n,'Actual Thunder real50 damage/defeat');record('Thunder-real-defeat',before)
 begin('Glove-real-brick');scene();tick();transaction(function()w('Block_Buffer_1',0x51,152);tile(0,8,11,0x51)end);before=snap()
 for age=0,39 do tick(age==1 and 64 or 0);if r('Block_Buffer_1',152)~=0x51 then break end end
 assert(r('Block_Buffer_1',152)~=0x51,'Actual earned Glove sword breaks real brick');record(taskName,before)
 for _,down in ipairs({false,true})do
  begin(down and'Down-thrust'or'Up-thrust');scene();tick();tick(128|(down and 4 or 8));before=snap()
  wait(function()return r('Z2CachedPose')==(down and 9 or 8)end,40,128|(down and 4 or 8))
  actor(6,r('Player_X_Position')+4,r('Player_Y_Position')+(down and 16 or-16));n=counts.Hit or 0
  tick(128|(down and 4 or 8));assert((counts.Hit or 0)>n and r('Z2NativeVY')==(down and 254 or 0),'Real thrust contact and original bounce/stop-rise')
  if down then request_image('Down-thrust-contact')end
  record(taskName,before);transaction(function()w('Enemy_Flag',0)end);wait(function()return r('Player_State')==0 end,180)
 end
 drop(0x91);cast(3);assert(r('Z2ActiveSpells')&8~=0);begin('Fairy-real-controlled-motion');scene();tick();before=snap()
 for _=1,12 do tick(9)end
 assert(r('Player_X_Position')>before.Player_X_Position and r('Player_Y_Position')<before.Player_Y_Position and r('Player_State')==1,'Actual paid Fairy controlled motion')
 request_image('Fairy-live');record(taskName,before);desired=0;done=true
end
local co=coroutine.create(campaign)
local function menu()
 if wall<90 or wall%12~=0 then return{}end
 if menuPhase=='options-focus'then menuPhase='options-open';return{down=true}end
 if menuPhase=='options-open'then menuPhase='mode';return{a=true}end
 if menuPhase=='mode'then
  if r('CrossoverMenuState')~=4 then return{}end
  if r('CrossoverOptionsFocus')~=1 then return{down=true}end
  if r('CrossoverBehaviorVersion')~=C.mode then menuPhase='back';return{a=true}end;menuPhase='back'
 end
 if menuPhase=='back'then menuPhase='start';return{b=true}end
 if menuPhase=='start'then if r('CrossoverMenuState')==2 then menuPhase='select'else return{start=true}end end
 if r('CrossoverMenuState')~=2 then return{}end
 local i=r('CrossoverMenuIndex');local key=C.navigation[i+1];if key~=''then return{[key]=true}end
 if r('Z2Variant')~=1 then return{select=true}end;return{a=true}
end
hook('GameLoopOwned',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then
  if r('GameEngineSubroutine')~=8 then return end
  assert(r('SelectedCharacter')==4 and r('Z2Variant')==1 and r('CrossoverBehaviorVersion')==C.mode and r('CheatInvincible')==0 and r('PlayerStatus')==0,'Cold genuine Z2/default cheats/numeric mode')
  entered=true
 end
 updates=updates+1;phaseAge=phaseAge+1;assert(updates<=5000 and phaseAge<600,'Finite actual task/update bound')
 assert(r('SelectedCharacter')==4 and r('Z2Variant')==1 and r('CrossoverBehaviorVersion')==C.mode and r('CheatInvincible')==0,'Actual identity/mode remain unchanged')
 if not done then local ok,why=coroutine.resume(co);assert(ok,why)end
end)
hook('GameLoopFinish',function()
 if not entered then return end
 assert(r('MmDeathFlag')==0 and r('GameEngineSubroutine')==8,'No actual death or unintended engine change')
 if updates%8==0 or done then event('update')end
end)
for _,name in ipairs(C.owner_hooks)do hook(name,function(s)
 if entered then counts[name]=(counts[name]or 0)+1;event('owner-'..name,s['cpu.a'])end
end)end

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
 local s=emu.getState();local pc=s['cpu.pc'];local owner='NMI'
 if not(nmi and pc==C.dma_store_return)then
  owner=nil
  for _,h in ipairs(C.panel_dma)do
   if pc==h.request_pc and bank(pc)==h.bank then
    for i,v in ipairs(h.request_bytes)do assert(emu.read(h.request_pc-3+i-1,emu.memType.nesDebug)==v,'Exact genuine panel DMA STA')end
    assert(not nmi and not irq and r('NmiDisable')==255 and r('DisableScreenFlag')~=0 and r('Mirror_PPUMASK')&24==0 and r('GamePauseStatus')&1~=0 and r('Z2PanelActive')==1 and r('Z2PanelPending')==h.pending,'Exclusive real blanked pause-panel DMA owner')
    assert(s['cpu.sp']>=128,'Actual panel caller stack');owner=h.name
   end
  end
  assert(owner,'Only exact NMI or two genuine pause-panel DMA owners')
 end
 assert(v==2,'Actual native page2 DMA owner')
 assert(s['ppu.spriteRamAddr']==0,'Actual native DMA begins at OAM address zero')
 pending={source=bytes(v*256),writes=0,owner=owner,requestSP=s['cpu.sp']}
end,emu.callbackType.write,0x4014)
emu.addMemoryCallback(function(_,v)
 assert(pending and mask&24==0,'Actual DMA byte while rendering disabled')
 local i=pending.writes+1
 assert(i<=256 and v==pending.source[i]and emu.getState()['ppu.spriteRamAddr']==i-1,'All256 raw DMA source/value/destination bytes match')
 pending.writes=i
end,emu.callbackType.write,0x2004)
local function complete(owner)
 if not pending or pending.owner~=owner then return end
 local hw=bytes(0,emu.memType.nesSpriteRam);local same=true
 for i=1,256 do local want=pending.source[i];if(i-1)%4==2 then want=want&0xe3 end;if hw[i]~=want then same=false end end
 assert(pending.writes==256 and mask&24==0 and emu.getState()['ppu.spriteRamAddr']==0 and same,'All256 physical OAM bytes match hardware attribute E3 semantics')
 pending=nil;dmas=dmas+1
end
hook('DmaComplete',function()complete('NMI')end)
for _,h in ipairs(C.panel_dma)do
 hook(h.complete_hook,function(s)
  if pending and pending.owner==h.name then
   assert(not nmi and not irq and r('NmiDisable')==255 and r('DisableScreenFlag')~=0 and r('Mirror_PPUMASK')&24==0,'Panel remains exclusively blank through completion')
   assert(s['cpu.sp']==pending.requestSP+h.stack_delta,'Genuine panel completion stack')
   if h.stack_delta==-2 then local sp=s['cpu.sp'];local ret=emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug);assert(ret==h.request_pc+2,'Actual pause close JSR continuation')end
   complete(h.name)
  end
 end)
end
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
 local t={};for _,x in ipairs({{128,'a'},{64,'b'},{32,'select'},{16,'start'},{8,'up'},{4,'down'},{2,'left'},{1,'right'}})do t[x[2]]=desired&x[1]~=0 end;emu.setInput(t,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1;minSP=math.min(minSP,emu.getState()['cpu.sp'])
 if entered then local s=emu.getState();for i=0,11 do assert(s['mapper.chrBanks'..i]==physical[i],'Actual CHR hardware agrees with write-time latch model');chrChecks=chrChecks+1 end end
 if screenshot then
  assert(images<8,'At most8 selected actual whole-frame screenshots')
  local f=assert(io.open(OUTPUT..screenshot,'wb'));f:write(emu.takeScreenshot());f:close();images=images+1
  local s=emu.getState();local oam={};for i=0,255 do oam[i+1]=emu.read(i,emu.memType.nesSpriteRam)end
  local pchr={};for i=0,11 do pchr[i+1]=physical[i]end
  screenshots[screenshot]={file=screenshot,wall=wall,update=updates,task=taskName,PPU_frame=s['ppu.frameCount'],hardware_OAM=oam,physical_CHR=pchr,source=snap(),limit='Actual endFrame snapshot, not exact visible epoch or allpixel art proof.'};screenshot=nil
 end
 assert(wall<8000,'At most8000wall frames')
 if done then
  assert(not pending and dmas>100 and irqCount>100 and nmis>100 and enables>100 and late==0,'Full native hardware/source guards exercised')
  local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=true,native_run=true,ROM_sha256=C.ROM_sha256,character=4,variant=1,mode=C.mode,records=records,owners=counts,screenshots=screenshots,wall=wall,updates=updates,complete256_DMAs=dmas,NMI_checks=nmis,IRQ31_checks=irqCount,NMI_safe_enables=enables,CHR_checks=chrChecks,minSP=minSP,goal_complete=false,scope=C.scope}));f:close();csv:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
