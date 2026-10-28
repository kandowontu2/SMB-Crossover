-- Shared earned Star/1-Up: mature actor scenes, never resource/outcome seeds.
local C=assert(CURRENT_NORMALIZED_MUSHROOM)
local wall,updates,age=0,0,0
local entered,done,writing=false,false,false
local phase,menuPhase='menu',C.mode==1 and'options-focus'or'start'
local nmi,irq=nil,false
local minSP,dmas,enables,late,irqCount,nmis,images=255,0,0,0,0,0,0
local mask,pending,upper,physical,chrChecks=0,nil,0,{},0
local screenshot,initial,lives,starAt,expiryAt,lifeAt
local counts={starCollision=0,lifeCollision=0,starContact=0,lifeIncrement=0,starMusic=0,areaRestore=0,lifeSound=0}
local csv=assert(io.open(OUTPUT..'normalized-mushroom.csv','w'))
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

local pickups,ownerCalls,erasures,rec=0,0,0,{}
local function values(want)
 for _,p in ipairs(want)do if C.identity=='mike'and want==C.after and p.name=='PlayerStatus'then assert(r('PlayerStatus')==0 or r('PlayerStatus')==1,'Only real next-update Mike display projection');else assert(r(p.name,p.index)==p.value,'Actual source-normalized benefit '..p.name..'['..p.index..']')end end
end
local function identity()
 assert(r('SelectedCharacter')==C.character and(not C.variant_name or r(C.variant_name)==C.variant)and r('CrossoverBehaviorVersion')==1 and r('CheatInvincible')==0,'Actual Hard owner/alternate')
 assert(r('NumberofLives')==lives and r('InjuryTimer')==0 and r('MmDeathFlag')==0,'No injury/death/life outcome seeds')
end
hook('GameLoopOwned',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then if r('GameEngineSubroutine')~=8 then return end;entered=true;phase='settle';age=0;lives=r('NumberofLives')end
 updates=updates+1;age=age+1;assert(updates<500,'Finite normalized pickup updates');identity()
 if phase=='settle'and age>=30 then
  values(C.before);phase='collect';age=0
  transaction(function()
   arena();actor(46,5,0);w('Enemy_Y_Position',r('Player_Y_Position')+8,5)
   for n,v in pairs(C.prepared_actor)do w(n,v,5)end
  end)
 end
end)
hook('PhysicalPickup',function(s)
 if not entered then return end
 assert(phase=='collect'and s['cpu.x']==5 and r('Enemy_Flag',5)~=0 and r('Enemy_ID',5)==46 and r('Enemy_State',5)>=128,'Real mature normalized pickup')
 for n,v in pairs(C.prepared_actor)do assert(r(n,5)==v,'Frozen actual Prepare output before erase')end
 pickups=pickups+1;event('physical-normalized-pickup',r('InvPickup',5))
end)
hook('CollectOwner',function(s)
 if entered and phase=='collect'then assert(pickups==1 and s['cpu.x']==5 and r('Enemy_Flag',5)~=0,'Genuine Mike collector precedes native erase');ownerCalls=ownerCalls+1;event('genuine-pre-erase-collector',r('JnHealth'))end
end)
hook('NativeEraseReturn',function(s)
 if not entered or phase~='collect'then return end
 assert(pickups==1 and ownerCalls==1 and s['cpu.x']==5 and r('Enemy_Flag',5)==0,'Genuine Mike successful collector then actual EraseEnemyObject return')
 assert(emu.read(256+(s['cpu.sp']+1)%256,emu.memType.nesDebug)==5,'Actual pending saved pickupX at native PLA')
 erasures=erasures+1;rec.erase_update=updates;event('actual-native-erase-return',r('JnHealth'))
end)
hook('GameLoopFinish',function()
 if not entered or done or phase=='settle'then return end
 identity();assert(r('GuestPowerupActive')==0 and r('GameEngineSubroutine')==8,'Private item never masquerades as a power transformation')
 if phase=='collect'then
  if pickups==1 then
   assert(ownerCalls==1 and erasures==1 and r('Enemy_Flag',5)==0,'One physical normalized reward, real collector and completed native erase');values(C.after)
   rec.collected_update=updates;rec.publish_dma=dmas;phase='publish';age=0
  end
  assert(age<60,'Bounded actual normalized pickup')
 elseif phase=='publish'then
  values(C.after)
  if dmas>=rec.publish_dma+2 then screenshot='normalized-mushroom.png';phase='effect';age=0 end
  assert(age<60,'Bounded real benefit publication')
 elseif phase=='effect'then
  if age>=20 then values(C.final)end
  if age>=120 then rec.finished_update=updates;done=true;phase='complete' end
 end
 event('update',pickups)
end)
local function input()return C.identity=='darkwing'and phase=='effect'and age<4 and{select=true}or{}end
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
emu.addEventCallback(function()if not entered then emu.setInput(menu(),0)else emu.setInput(input(),0)end end,emu.eventType.inputPolled)

emu.addEventCallback(function()
 wall=wall+1;minSP=math.min(minSP,emu.getState()['cpu.sp'])
 if entered then local s=emu.getState();for i=0,11 do assert(s['mapper.chrBanks'..i]==physical[i],'Actual CHR hardware agrees with write-time latch model');chrChecks=chrChecks+1 end end
 if screenshot then assert(images<4,'At most4 original PNGs');local f=assert(io.open(OUTPUT..screenshot,'wb'));f:write(emu.takeScreenshot());f:close();images=images+1;screenshot=nil end
 assert(wall<1600,'Finite normalized mature pickup')
 if done then
  assert(not pending and dmas>100 and irqCount>100 and nmis>100 and enables>100 and late==0,'Original actual hardware guards exercised')
  local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=true,native_run=true,ROM_sha256=C.ROM_sha256,identity=C.identity,actual_mode=1,raw_source_request=0,prepared_actor=C.prepared_actor,pickups=pickups,collector_calls=ownerCalls,native_erase_returns=erasures,record=rec,wall=wall,updates=updates,complete256_DMAs=dmas,NMI_checks=nmis,IRQ31_checks=irqCount,NMI_safe_enables=enables,CHR_checks=chrChecks,minSP=minSP,images=images,scope=C.scope}));f:close();csv:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
