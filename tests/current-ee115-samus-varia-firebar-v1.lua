-- Shared earned Star/1-Up: mature actor scenes, never resource/outcome seeds.
local C=assert(CURRENT_SAMUS_VARIA)
local wall,updates,age=0,0,0
local entered,done,writing=false,false,false
local phase,menuPhase='menu',C.mode==1 and'options-focus'or'start'
local nmi,irq=nil,false
local minSP,dmas,enables,late,irqCount,nmis,images=255,0,0,0,0,0,0
local mask,pending,upper,physical,chrChecks=0,nil,0,{},0
local screenshot,initial,lives,starAt,expiryAt,lifeAt
local counts={starCollision=0,lifeCollision=0,starContact=0,lifeIncrement=0,starMusic=0,areaRestore=0,lifeSound=0}
local csv=assert(io.open(OUTPUT..'varia-firebar.csv','w'))
csv:write('event,wall,update,phase,age,star,lives,injury,x,y,enemy,enemyState,value\n')
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(at)local p=emu.convertAddress(at);return p and p.address//8192 or-1 end
local function event(kind,value)
 csv:write(table.concat({kind,wall,updates,phase,age,r('StarInvincibleTimer'),r('NumberofLives'),r('InjuryTimer'),r('Player_X_Position'),r('Player_Y_Position'),r('Enemy_Flag',0),r('Enemy_State',0),value or 0},',')..'\n')
end
local function json(v)
 if type(v)=='table'then local out={};if #v>0 then for _,x in ipairs(v)do out[#out+1]=json(x)end;return'['..table.concat(out,',')..']'end
  for k,x in pairs(v)do out[#out+1]=string.format('%q',tostring(k))..':'..json(x)end;table.sort(out);return'{'..table.concat(out,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local function hook(name,fn)
 local h=assert(C.hooks[name],name)
 emu.addMemoryCallback(function()
  local allowed=false;for _,b in ipairs(h.banks)do if bank(h.pc)==b then allowed=true end end;if not allowed then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Actual hook '..name)end
  fn(emu.getState())
 end,emu.callbackType.exec,h.pc)
end
local function resources()
 local a={};for _,p in ipairs(C.resources)do for i=0,p.count-1 do a[#a+1]=r(p.name,p.index+i)end end;return a
end
local function resourcesSame()
 local a=resources();for i,v in ipairs(initial)do assert(a[i]==v,'Star/1-Up never changes observed health, tier or owned inventory')end
 assert(r('InjuryTimer')==0 and r('MmDeathFlag')==0,'Protected contact never starts injury/death')
end
local function w(n,v,i)
 assert(writing and not nmi and not irq and r('NmiDisable')==255,'Only private GameLoop+5 scene setup')
 assert(C.setup_allowed[n]and not C.resource_bans[n],'Never seed resources/timers/lives/health/ownership/hurt/kill outcomes: '..n)
 emu.write(assert(C.ram[n],n)+(i or 0),v&255,emu.memType.nesDebug)
end
local function transaction(fn)
 assert(not writing and not nmi and not irq and r('NmiDisable')==255,'Actual native setup owner')
 writing=true;fn();writing=false;event('disclosed-scene-setup')
end
local function tile(page,col,row,id)
 assert(writing and not nmi and not irq,'Same native map setup owner')
 local function source(n)local p=C.metatiles[n];return emu.read(p.bank*8192+p.offset+id,emu.memType.nesPrgRom)end
 local function put(a,v)emu.write(a,v,emu.memType.nesPpuDebug)end
 local at=0x2000+page*1024+row*64+col*2
 put(at,source('MTileTopLeft'));put(at+1,source('MTileTopRight'));put(at+32,source('MTileBotLeft'));put(at+33,source('MTileBotRight'))
 local a=0x23c0+page*1024+(row//2)*8+col//2;local shift=row%2*4+col%2*2
 put(a,(emu.read(a,emu.memType.nesPpuDebug)&(~(3<<shift)))|((source('MTileAttribute')>>6)<<shift))
end
local function arena()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do for row=2,14 do for col=0,15 do tile(p,col,row,row>=13 and 0x54 or 0)end end end
 for p=0,1 do for row=11,12 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+row*16+col)end end end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_CollisionBits',0,i)end
 w('ScrollLock',1);w('ScrollThirtyTwo',0);w('AreaParserTaskNum',0)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 -- Ships retain their genuine live native object coordinates; actors align to them.
 if C.character~=18 then
  for _,n in ipairs(C.motion)do w(n,0)end
  w('Player_X_Position',112);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
  w('Player_State',0);w('PlayerFacingDir',1);w('Player_MovingDir',1);w('Player_CollisionBits',255)
 end
end
local function actor(kind,slot,pickup)
 local y=r('Player_Y_Position')-8;assert(y>=24 and y<=200,'Legal native contact band')
 local x,page=r('Player_X_Position'),r('Player_PageLoc')
 if C.character==18 then local world=r('VvObjX')-8+r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc');x,page=world&255,(world>>8)&255 end
 for _,a in ipairs({{'Enemy_Flag',1},{'Enemy_ID',kind},{'Enemy_State',kind==0x2e and 128 or 0},{'Enemy_BoundBoxCtrl',kind==0x2e and 3 or 9},{'Enemy_X_Position',x},{'Enemy_PageLoc',page},{'Enemy_Y_Position',y},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_Y_MoveForce',0},{'Enemy_MovingDir',1},{'Enemy_SprAttrib',0},{'EnemyOffscrBitsMasked',0},{'Enemy_CollisionBits',0}})do w(a[1],a[2],slot)end
 if pickup then w('PowerUpType',pickup,slot);w('InvPickupOwner',C.character,slot);w('InvPickup',0xfc,slot)end
end
local function menu()
 if wall<90 or wall%12~=0 then return{}end
 if menuPhase=='options-focus'then menuPhase='options-open';return{down=true}end
 if menuPhase=='options-open'then menuPhase='mode';return{a=true}end
 if menuPhase=='mode'then if r('CrossoverMenuState')~=4 then return{}end;if r('CrossoverOptionsFocus')~=1 then return{down=true}end;if r('CrossoverBehaviorVersion')~=C.mode then menuPhase='back';return{a=true}end;menuPhase='back'end
 if menuPhase=='back'then menuPhase='start';return{b=true}end
 if menuPhase=='start'then if r('CrossoverMenuState')==2 then menuPhase='select'else return{start=true}end end
 if r('CrossoverMenuState')~=2 then return{}end
 local i=r('CrossoverMenuIndex');if i~=C.menu then local key=assert(C.navigation[i+1]);assert(key~='','Real compiled menu path');return{[key]=true}end
 if C.variant_name and r(C.variant_name)~=C.variant then return{select=true}end
 return{a=true}
end

local item,stage,rec=0,0,nil
local records,contacts={},{}
local injuryCalls,variaCalls,injuryStarts=0,0,0
local function identity()
 assert(r('SelectedCharacter')==2 and r('CrossoverBehaviorVersion')==1 and r('CheatInvincible')==0 and r('StarInvincibleTimer')==0,'Actual uncheated SamusHard without Star protection')
 assert(r('NumberofLives')==lives and r('MmDeathFlag')==0,'No death or life changes')
end
local function scene()
 arena()
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('MmOldX',r('Player_X_Position'))
end
local function pickup(i)
 item=i;rec={item=i,stage=stage,collisions=0,growth=0,grants=0};records[#records+1]=rec
 transaction(function()scene();actor(46,5,i==0 and 0 or 1);w('Enemy_Y_Position',184,5);w('InvPickup',i,5)end)
 phase='collect';age=0
end
local function firebar()
 scene()
 for n,v in pairs(C.firebar)do w(n,v,0)end
 w('Enemy_X_Position',r('Player_X_Position')+4,0);w('Enemy_PageLoc',r('Player_PageLoc'),0)
 w('Enemy_Y_Position',r('Player_Y_Position')+12,0)
end
hook('GameLoopOwned',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then if r('GameEngineSubroutine')~=8 then return end;entered=true;phase='settle';age=0;lives=r('NumberofLives')end
 updates=updates+1;age=age+1;assert(updates<900,'Finite actual Varia component');identity()
 if phase=='settle'and age>=30 then
  assert(r('PlayerStatus')==0 and r('InvOwnedLo',2)==0 and r('InvOwnedHi',2)==0,'Unpowered actual cold Samus')
  stage=1;pickup(0)
 elseif phase=='unprotected-setup'then
  assert(r('PlayerStatus')==1 and r('InvOwnedLo',2)==129 and r('InjuryTimer')==0,'Earned Long/mushroom, no Varia or protection')
  transaction(firebar);phase='unprotected';age=0
 elseif phase=='remove-hazard'then
  transaction(function()w('Enemy_Flag',0,0)end);phase='recovery';age=0
 elseif phase=='second-mushroom'then stage=2;pickup(0)
 elseif phase=='varia-setup'then stage=3;pickup(5)
 elseif phase=='protected-setup'then
  assert(r('PlayerStatus')==1 and r('InvOwnedLo',2)==161 and r('InvOwnedHi',2)==0 and r('InjuryTimer')==0 and r('GuestHurtTicks')==0 and r('GuestInvulTicks')==0 and r('SmFlip')==0,'Only earned Varia can protect this contact')
  transaction(firebar);phase='protected';age=0;rec={kind='Varia-firebar',before_injury_calls=injuryCalls,before_starts=injuryStarts,branch_calls=0};records[#records+1]=rec
 elseif phase=='protected-remove'then transaction(function()w('Enemy_Flag',0,0)end);phase='drain';age=0 end
end)
hook('PhysicalPickup',function(s)
 if not entered then return end
 assert(phase=='collect'and s['cpu.x']==5 and r('Enemy_Flag',5)~=0 and r('Enemy_ID',5)==46 and r('Enemy_State',5)>=128 and r('InvPickupOwner',5)==2 and r('InvPickup',5)==item,'Actual earned mature Samus pickup')
 rec.collisions=rec.collisions+1;event('actual-pickup',item)
end)
hook('InventoryGrant',function(s)if entered and phase=='collect'then assert(item==5 and s['cpu.a']==5,'Only actual Varia grant');rec.grants=rec.grants+1 end end)
hook('GuestPowerupUpdate',function()if entered and phase=='collect'and r('GuestPowerupActive')~=0 then rec.growth=rec.growth+1 end end)
hook('FirebarBranch',function(s)
 if not entered then return end
 assert(phase=='unprotected'or phase=='protected','Firebar only in disclosed comparison scenes')
 assert(r('ObjectOffset')==0 and r('Enemy_ID',0)==27 and r('Enemy_Flag',0)~=0,'Actual native firebar owner')
 local carry=assert(s['cpu.ps'],'Actual CPU flags')&1
 assert(carry==(phase=='protected'and 1 or 0),'Real InventoryHasVaria return controls actual native firebar branch')
 contacts[#contacts+1]={phase=phase,update=updates,carry=carry,x=r('R6'),y=r('R7'),playerX=r('Player_Rel_XPos'),playerY=r('Player_Y_Position'),pc=s['cpu.pc'],bank=bank(s['cpu.pc'])}
 if phase=='protected'then variaCalls=variaCalls+1;rec.branch_calls=rec.branch_calls+1 end
 event('actual-firebar-distance-admitted',carry)
end)
hook('FirebarInjure',function()if entered then assert(phase=='unprotected','Earned Varia must bypass actual InjurePlayer call');injuryCalls=injuryCalls+1;event('actual-unprotected-firebar-injury-call')end end)
hook('InjuryStarted',function()if entered then assert(phase=='unprotected','Only actual unprotected comparison can start injury');injuryStarts=injuryStarts+1;event('real-injury-start')end end)
hook('GameLoopFinish',function()
 if not entered or done or phase=='settle'then return end
 identity()
 if phase=='collect'then
  if rec.collisions==1 and r('GuestPowerupActive')==0 then
   assert(r('Enemy_Flag',5)==0 and r('PlayerStatus')==1 and r('InvOwnedLo',2)==(item==5 and 161 or 129),'Actual acquired state comes only from collision')
   assert(rec.growth==(item==0 and 60 or 0)and rec.grants==(item==5 and 1 or 0),'Exact real growth/grant counts')
   rec.publish_dma=dmas;rec.complete_update=updates;phase='publish';age=0
  end
  assert(age<120,'Bounded real pickup/transform')
 elseif phase=='publish'then
  if dmas>=rec.publish_dma+2 then screenshot=stage==1 and'01-earned-before-hazard.png'or stage==2 and'03-reacquired-mushroom.png'or'04-earned-varia.png';phase=stage==1 and'unprotected-setup'or stage==2 and'varia-setup'or'protected-setup';age=0 end
  assert(age<60,'Bounded actual publication')
 elseif phase=='unprotected'then
  if injuryStarts>0 then
   assert(injuryStarts==1 and injuryCalls>0 and r('PlayerStatus')==0 and r('InvOwnedLo',2)==0 and r('InjuryTimer')~=0,'Same real firebar damages unprotected earned Samus')
   phase='remove-hazard';age=0
  end
  assert(age<40,'Actual unprotected contact required')
 elseif phase=='recovery'then
  if age>=90 and r('InjuryTimer')==0 and r('GuestHurtTicks')==0 and r('GuestInvulTicks')==0 and r('Player_State')==0 then
   screenshot='02-real-injury-recovered.png';phase='second-mushroom';age=0
  end
  assert(age<300,'Natural recoil/protection expiry and landing')
 elseif phase=='protected'then
  assert(r('PlayerStatus')==1 and r('InvOwnedLo',2)==161 and r('InjuryTimer')==0 and r('GuestHurtTicks')==0 and r('GuestInvulTicks')==0 and r('SmFlip')==0 and r('Player_State')==0,'Actual Varia retains power through unprotected body contact')
  assert(injuryCalls==rec.before_injury_calls and injuryStarts==rec.before_starts and r('FirebarPartCount',0)==6,'Actual six-part native firebar without injury')
  if age>=4 and variaCalls>0 and not rec.sample_dma then rec.sample_dma=dmas end
  if rec.sample_dma and dmas>=rec.sample_dma+2 and not rec.sampled then screenshot='05-varia-real-firebar-contact.png';rec.sampled=true end
  if age>=24 then assert(rec.branch_calls>=24 and rec.sampled,'Repeated real distance-admitted contacts and actual live sample');phase='protected-remove';age=0 end
 elseif phase=='drain'then
  assert(r('PlayerStatus')==1 and r('InvOwnedLo',2)==161 and r('InjuryTimer')==0,'Protection does not hide delayed damage')
  if age>=45 then done=true;phase='complete' end
 end
 event('update',r('PlayerStatus'))
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
emu.addEventCallback(function()if not entered then emu.setInput(menu(),0)else emu.setInput({},0)end end,emu.eventType.inputPolled)

emu.addEventCallback(function()
 wall=wall+1;minSP=math.min(minSP,emu.getState()['cpu.sp'])
 if entered then local s=emu.getState();for i=0,11 do assert(s['mapper.chrBanks'..i]==physical[i],'Actual CHR hardware agrees with write-time latch model');chrChecks=chrChecks+1 end end
 if screenshot then assert(images<8,'At most8 original PNGs');local f=assert(io.open(OUTPUT..screenshot,'wb'));f:write(emu.takeScreenshot());f:close();images=images+1;screenshot=nil end
 assert(wall<2600,'Finite Varia comparison physical frames')
 if done then
  assert(not pending and dmas>100 and irqCount>100 and nmis>100 and enables>100 and late==0,'Original actual hardware guards exercised')
  local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=true,native_run=true,ROM_sha256=C.ROM_sha256,identity='samus',actual_mode=1,records=records,contacts=contacts,unprotected_injury_calls=injuryCalls,real_injury_starts=injuryStarts,protected_Varia_branches=variaCalls,wall=wall,updates=updates,complete256_DMAs=dmas,NMI_checks=nmis,IRQ31_checks=irqCount,NMI_safe_enables=enables,CHR_checks=chrChecks,minSP=minSP,images=images,scope=C.scope}));f:close();csv:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
