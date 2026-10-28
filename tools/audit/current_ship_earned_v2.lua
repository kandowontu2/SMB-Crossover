-- Earned native ship bar/Bell components. Only disclosed complete scene/pickup actors are staged.
local C=assert(CURRENT_SHIP_EARNED)
local wall,updates,index=0,0,1
local entered,done,writing=false,false,false
local phase,menuPhase='menu',C.mode==1 and'options-focus'or'start'
local rec,records=nil,{}
local nmi,irq=nil,false
local minSP,dmas,enables,late,irqCount,nmis,images=255,0,0,0,0,0,0
local mask,pending,upper,physical,chrChecks=0,nil,0,{},0
local nextTarget,screenshot=nil,nil
local csv=assert(io.open(OUTPUT..'ship-components.csv','w'))
csv:write('event,wall,update,case,age,stage,stageAge,meter,speed,gun,options,shield,bells,skin,red,shots,value\n')
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(at)local p=emu.convertAddress(at);return p and p.address//8192 or-1 end
local function shots()
 local out={}
 if C.variant==0 then for i=3,11 do if r('VvObjAnim',i)~=0 then out[#out+1]={i,r('VvObjAnim',i),r('VvObjSub',i)}end end
 else for i=6,27 do if r('PnActive',i)~=0 then out[#out+1]={i,r('PnType',i),r('PnActive',i)}end end end
 return out
end
local function world()return r('VvObjX')-8+r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')end
local function score()local n=0;for i=0,5 do n=n*10+r('Player1ScoreDisplay',i)end;return n end
local function event(kind,value)
 csv:write(table.concat({kind,wall,updates,rec and rec.case_index or index,rec and rec.age or 0,rec and rec.stage or phase,rec and rec.stageAge or 0,r('VvMeter'),r('VvSpeed'),r('VvGun'),C.variant==0 and r('VvOptions')or(r('VvGun')&7),C.variant==0 and r('VvShield')or r('PnAux'),r('PnBellFlags'),r('PnSkin'),r('PnRedRemaining'),#shots(),value or 0},',')..'\n')
end
local function json(v)
 if type(v)=='table'then local t={};if #v>0 then for _,x in ipairs(v)do t[#t+1]=json(x)end;return'['..table.concat(t,',')..']'end
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
 assert(writing and not nmi and not irq and r('NmiDisable')==255,'Only private native GameLoop boundary')
 assert(C.setup_allowed[n]and not C.forbidden[n],'No owned ship equipment/resource/outcome seeds: '..n)
 emu.write(assert(C.ram[n],n)+(i or 0),v&255,emu.memType.nesDebug)
end
local function transaction(fn)
 assert(not writing and not nmi and not irq and r('NmiDisable')==255,'Synchronous complete fixture owner')
 writing=true;fn();writing=false;event('disclosed-scene-or-actor-setup')
end
local function tile(page,col,row,id)
 assert(writing and not nmi and not irq,'Same native scene owner')
 local function source(n)local p=C.metatiles[n];return emu.read(p.bank*8192+p.offset+id,emu.memType.nesPrgRom)end
 local function put(a,v)emu.write(a,v,emu.memType.nesPpuDebug)end
 local at=0x2000+page*1024+row*64+col*2
 put(at,source('MTileTopLeft'));put(at+1,source('MTileTopRight'));put(at+32,source('MTileBotLeft'));put(at+33,source('MTileBotRight'))
 local a=0x23c0+page*1024+(row//2)*8+col//2;local shift=row%2*4+col%2*2
 put(a,(emu.read(a,emu.memType.nesPpuDebug)&(~(3<<shift)))|((source('MTileAttribute')>>6)<<shift))
end
local function arena()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do for row=2,14 do for col=0,15 do tile(p,col,row,0)end end end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_CollisionBits',0,i)end
 w('ScrollLock',1);w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0);w('ScrollThirtyTwo',0);w('AreaParserTaskNum',0)
end
local function actor(kind,x,y,slot,power)
 for _,a in ipairs({{'Enemy_Flag',1},{'Enemy_ID',kind},{'Enemy_State',kind==46 and 128 or 0},{'Enemy_BoundBoxCtrl',kind==46 and 3 or 9},{'Enemy_X_Position',x&255},{'Enemy_PageLoc',x//256},{'Enemy_Y_Position',y},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_Y_MoveForce',0},{'Enemy_MovingDir',2},{'Enemy_SprAttrib',0},{'EnemyOffscrBitsMasked',0},{'Enemy_CollisionBits',0},{'MmEnemyHealthLo',0},{'MmEnemyHealthHi',0},{'MmEnemyFlash',0},{'RgEnemyStun',0}})do w(a[1],a[2],slot)end
 if kind==46 then w('PowerUpType',power,slot);w('InvPickupOwner',255,slot);w('InvPickup',252,slot)end
end
local function capsule(kind)
 local x=world()
 for _,a in ipairs({{'PnCapActive',kind},{'PnCapX',x&255},{'PnCapPage',x//256},{'PnCapY',r('Player_Y_Position')+8},{'PnCapAge',0},{'PnCapFraction',0},{'PnCapVX',0},{'PnCapVXF',0},{'PnCapHits',4},{'PnCapChange',0},{'PnCapAnim',0}})do w(a[1],a[2],0)end
end
local function beginCase()
 local t=assert(C.plan[index])
 rec={name=t.name,case_index=index,stage=t.kind=='gear'and'caps'or t.kind,age=0,stageAge=0,collections=0,takes=0,defeats=0,red_fires=0,specialTicks=0,big_ticks=0,live=0,types={},roulette={},skins={},owners={},sounds={},target=false,startLives=r('NumberofLives'),startScore=score()}
 records[#records+1]=rec;phase='case'
 transaction(function()arena();if t.kind=='contact'then actor(6,world()+4,r('Player_Y_Position')-(C.variant==0 and 1 or 9),0)elseif t.kind=='bell'then capsule(t.pickup)end end)
 event('case-start')
end
local function finishCase()
 local t=C.plan[index]
 if t.kind=='gear'then assert(rec.collections>0,'Actual mature native bar capsules collected')end
 if t.kind=='bell'then assert(rec.takes==1,'Exactly one native physical Bell collection')end
 rec.final={};for _,n in ipairs(C.final_fields)do rec.final[n]=r(n)end
 rec.completed=wall;event('case-complete');index=index+1;nextTarget=nil
 if index>#C.plan then done=true;phase='complete'else phase='setup'end
end
local function stage(name)rec.stage=name;rec.stageAge=0;event('stage')end
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
 local i=r('CrossoverMenuIndex');if i~=17 then return{[C.navigation[i+1]]=true}end
 if r('VvVariant')~=C.variant then return{select=true}end;return{a=true}
end
hook('GameLoopOwned',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then
  if r('GameEngineSubroutine')~=8 then return end
  assert(r('SelectedCharacter')==18 and r('VvVariant')==C.variant and r('CrossoverBehaviorVersion')==C.mode and r('PlayerStatus')==0 and r('CheatInvincible')==0,'Actual cold ship/variant/numeric mode/default cheats')
  entered=true;phase='settle';rec=nil
 end
 updates=updates+1;assert(updates<=C.update_cap,'Finite actual ship update cap')
 assert(r('SelectedCharacter')==18 and r('VvVariant')==C.variant and r('CrossoverBehaviorVersion')==C.mode and r('CheatInvincible')==0,'Actual owner/mode remain native')
 if phase=='settle'and updates>=30 or phase=='setup'then beginCase()end
 if phase~='case'then return end
 if nextTarget then local t=nextTarget;transaction(function()actor(6,t.x,t.y,0)end);nextTarget=nil end
 if rec.stage=='caps'and r('VvMeter')~=C.plan[index].cell and r('Enemy_Flag',5)==0 then
  local y=r('Player_Y_Position')-(C.variant==0 and 0 or 8)
  transaction(function()actor(46,world(),y,5,1)end)
 end
end)
hook('PhysicalPickup',function(s)
 if entered and rec and phase=='case'then
  assert(rec.stage=='caps'and s['cpu.x']==5 and r('Enemy_Flag',5)~=0 and r('Enemy_ID',5)==46 and r('Enemy_State',5)>=128,'Actual typed mature ship capsule before native erase')
  rec.collections=rec.collections+1;event('actual-mature-collision',r('PowerUpType',5))
 end
end)
for _,name in ipairs(C.owner_hooks)do
 hook(name,function()
  if not entered or not rec or phase~='case'then return end
  rec.owners[name]=(rec.owners[name]or 0)+1
  if name=='VvTake'or name=='PnTakeKind'then rec.takes=rec.takes+1;event('actual-take',name)
  elseif name=='Defeat'then rec.defeats=rec.defeats+1;event('actual-native-defeat')
  elseif name=='RedFire'then rec.red_fires=rec.red_fires+1;event('actual-paid-red-fire')
  elseif name=='BombDamage'then rec.specialTicks=rec.specialTicks+1
  elseif name=='BigDecrement'then
   assert(r('PnBigTimerLo')+256*r('PnBigTimerHi')==1279-rec.big_ticks,'Actual16-bit Big timer before genuine decrement')
   rec.big_ticks=rec.big_ticks+1
  end
 end)
end
for _,name in ipairs({'Square1SoundQueue','Square2SoundQueue','NoiseSoundQueue'})do
 emu.addMemoryCallback(function(_,v)if entered and rec and not writing and v~=0 then rec.sounds[name..':'..v]=true end end,emu.callbackType.write,C.ram[name])
end
hook('GameLoopFinish',function()
 if not entered or done or not rec or phase~='case'then return end
 assert(r('GameEngineSubroutine')==8 and r('MmDeathFlag')==0 and r('PlayerStatus')==0,'Actual ship remains alive/default tier')
 if C.variant~=0 then assert(r('PnMissing')==0,'All native Parodius dispatches implemented')end
 rec.age=rec.age+1;rec.stageAge=rec.stageAge+1
 local t=C.plan[index];local s,a=rec.stage,rec.stageAge;local active=shots()
 if #active>0 then rec.live=rec.live+1;for _,z in ipairs(active)do rec.types[z[2]..':'..z[3]]=true end end
 if(s=='fire'or s=='blue'or s=='red')and not rec.target and #active>0 then
  local i=active[1][1];local x,y
  if C.variant==0 then x=r('VvObjX',i)-8+r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc');y=r('VvObjY',i)+32
  else x=r('PnX',i)+r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc');y=r('PnY',i)+15 end
  if x+16>=8 and x+16<232 and y>=32 and y<200 then nextTarget={x=x+16,y=y};rec.target=true end
 end
 if s=='caps'and r('VvMeter')==t.cell then stage('buy')
 elseif s=='buy'and a>=8 then
  assert(r(t.field)&(t.mask or 255)==t.value,'Actual bar upgrade/cap source value')
  if t.refuse then assert(r('VvMeter')==t.cell,'Full equipment leaves real meter unconsumed');finishCase()
  else
   assert(r('VvMeter')==0,'Actual purchase consumes bar cell')
   if t.reset then assert(r('VvSpeed')==0 and r('VvGun')==0,'Actual !? power-down removes speed/gun/options')end
   if t.fire then stage('fire')else finishCase()end
  end
 elseif s=='fire'and a>=130 then assert(rec.live>0 and rec.defeats>0 and #active==0,'Real live weapon, target defeat and native projectile expiry');finishCase()
 elseif s=='contact'and a>=20 then
  local shield=C.variant==0 and r('VvShield')or r('PnAux')
  assert(shield==t.shield and rec.defeats==1,'One actual body enemy hit debits exactly one shield and defeats target');finishCase()
 elseif s=='bell'then
  local k,flag=t.pickup,r('PnBellFlags')
  if k==5 and flag&16~=0 then stage('roulette')
  elseif k==6 and a>=50 then assert(rec.takes==1 and score()==rec.startScore+500,'Native first Gold bell awards500');rec.score_delta=score()-rec.startScore;finishCase()
  elseif k==7 and flag&1~=0 then stage('blue')
  elseif k==9 and flag&4~=0 then assert(r('PnRedRemaining')==3,'Actual Red collection grants exactly three charges');stage('red')
  elseif k==8 and flag&2~=0 then stage('big')
  elseif k==10 and a>=20 then assert(r('NumberofLives')==rec.startLives+1,'Actual White Bell grants1UP');finishCase()end
 elseif s=='roulette'then
  rec.roulette[r('VvMeter')]=true
  if r('PnBellFlags')&16==0 and a>=13 then local n=0;for _ in pairs(rec.roulette)do n=n+1 end;assert(n>=3,'Roulette traverses three real cells before B purchase');finishCase()end
 elseif s=='blue'and r('PnBellFlags')&1==0 and a>10 then assert(rec.specialTicks>0 and rec.defeats>0,'Actual Blue world damage and native cleanup');finishCase()
 elseif s=='red'and r('PnBellFlags')&4==0 and a>10 then assert(r('PnRedRemaining')==0 and rec.red_fires==3,'Three actual Red debits exhaust owned charges');finishCase()
 elseif s=='big'then
  rec.skins[r('PnSkin')]=true
  if r('PnSkin')~=C.variant and not rec.target then nextTarget={x=world()+4,y=r('Player_Y_Position')-9};rec.target=true end
  if r('PnBellFlags')&2==0 and a>20 then
   local other=false;for skin in pairs(rec.skins)do if skin~=C.variant then other=true end end
   assert(r('PnSkin')==C.variant and rec.defeats==1 and other and rec.big_ticks==1279,'Actual protected Big contact/full1279 decrements/skin restoration');finishCase()
  end
 end
 event('update');if phase=='case'then assert(rec.age<t.limit,'Finite source-qualified case update deadline')end
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
 if not entered or not rec or phase~='case' or not C.plan[index].image or rec.capture or rec.captureArmed then return end
 local active=shots();local kind=C.plan[index].kind
 if #active==0 and kind~='gear' and rec.stage~='big' then return end
 if kind=='gear'and C.plan[index].fire and #active==0 then return end
 if kind=='gear'and not C.plan[index].fire and rec.stage~='buy'then return end
 if rec.stage=='big'and r('PnSkin')==C.variant then return end
 rec.captureArmed=true;local st=emu.getState();local oam,chr,source={},{},{}
 for i=0,255 do oam[i+1]=emu.read(i,emu.memType.nesSpriteRam);source[i+1]=emu.read(0x200+i,emu.memType.nesDebug)end
 for i=0,11 do chr[i+1]=physical[i]end
 screenshot={record=rec,file=string.format('item-%02d.png',index),wall=wall,update=updates,age=rec.age,stage=rec.stage,completeDMA=dmas,actual_OAM=oam,source_OAM=source,physical_CHR=chr,live_shots=active,skin=r('PnSkin'),PPU_frame=st['ppu.frameCount'],scanline=st['ppu.scanline'],cycle=st['ppu.cycle'],note='Actual complete DMA source/destination and physical CHR at E008; PNG taken following endFrame. Admission/visibility and exact RGB fetch epoch require separate image review; no allpixel claim.'}
end)
emu.addEventCallback(function()
 if not entered then emu.setInput(menu(),0);return end
 local bits=0
 if phase=='case'then
  local s,a=rec.stage,rec.stageAge
  if s=='roulette'and a>=12 and r('VvMeter')&(~r('VvFlags')&255)~=0 then bits=64
  elseif s=='buy'and a>=4 then bits=64
  elseif s=='fire'and a>=5 and a<40 then bits=128
  elseif(s=='blue'or s=='red')and a>=5 and r('PnActive',27)==0 and r('VvPrevious')&128==0 then bits=128 end
 end
 emu.setInput({a=bits&128~=0,b=bits&64~=0},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1;minSP=math.min(minSP,emu.getState()['cpu.sp'])
 if entered then local s=emu.getState();for i=0,11 do assert(s['mapper.chrBanks'..i]==physical[i],'Actual CHR hardware agrees with write-time latch model');chrChecks=chrChecks+1 end end
 if screenshot then
  assert(images<8,'At most8 selected actual whole-frame screenshots')
  local f=assert(io.open(OUTPUT..screenshot.file,'wb'));f:write(emu.takeScreenshot());f:close();images=images+1
  screenshot.record.capture=screenshot;screenshot.record=nil;screenshot=nil
 end
 assert(wall<8000,'At most8000 wall frames')
 if done then
  assert(not pending and dmas>100 and irqCount>100 and nmis>100 and enables>100 and late==0,'Original strict native hardware/source guards exercised')
  local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=true,native_run=true,ROM_sha256=C.ROM_sha256,character=18,variant=C.variant,mode=C.mode,records=records,wall=wall,updates=updates,complete256_DMAs=dmas,NMI_checks=nmis,IRQ31_checks=irqCount,NMI_safe_enables=enables,CHR_checks=chrChecks,minSP=minSP,screenshots=images,goal_complete=false,scope=C.scope}));f:close();csv:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
