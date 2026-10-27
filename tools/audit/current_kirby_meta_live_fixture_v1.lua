-- Actual Kirby inhale/Down acquisition and Meta native sword toolkit.
-- Disclosed scene/NPC/mature-food setup only; no tested ability/health seeds.
local C=assert(CURRENT_KIRBY_META_EARNED)
local wall,updates,age,stageAge,index=0,0,0,0,1
local entered,done,writing=false,false,false
local phase,menuPhase='menu','options-focus'
local rec,records=nil,{}
local nmi,irq=nil,false
local minSP,dmas,enables,late,irqCount,nmis,images=255,0,0,0,0,0,0
local mask,pending,upper,physical,chrChecks=0,nil,0,{},0
local screenshot=nil
local csv=assert(io.open(OUTPUT..'earned-components.csv','w'))
csv:write('event,wall,update,case,age,phase,stage_age,x,y,state,hp,copy,mouth,float,action,action_age,shots,value,pc,bank,cycle\n')
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(at)local p=emu.convertAddress(at);return p and p.address//8192 or-1 end
local function hp()return r('KbHealth')end
local function pool()local n=0;for i=0,2 do if r('KbShotType',i)~=0 then n=n+1 end end;return n end
local function world()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function snapshot()return{hp=hp(),copy=r('KbCopy'),mouth=r('KbMouth'),drop=r('KbDropKind'),food=r('KbFoodKind'),float=r('KbFloat'),action=r('KbAction'),pool=pool()}end
local function event(kind,value)
 local s=emu.getState();csv:write(table.concat({kind,wall,updates,rec and rec.case_index or index,age,phase,stageAge,world(),r('Player_Y_Position'),r('Player_State'),hp(),r('KbCopy'),r('KbMouth'),r('KbFloat'),r('KbAction'),r('KbActionAge'),pool(),value or 0,s['cpu.pc'],bank(s['cpu.pc']),s['cpu.cycleCount']},',')..'\n')
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
 assert(C.setup_allowed[n]and not forbidden[n],'No tested health/ability/input/outcome seed: '..n)
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
 assert(pool()==0 and r('KbMouth')==0 and r('KbCopy')==0 and r('KbDropKind')==0,'Prior source abilities and thrown copy star really cleaned up')
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do for row=2,14 do for col=0,15 do tile(p,col,row,row>=13 and 0x54 or 0)end end end
 for p=0,1 do for row=11,12 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+row*16+col)end end end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_CollisionBits',0,i)end
 for i=0,3 do w('InvDropKind',0,i)end
 for _,n in ipairs({'Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','ScrollThirtyTwo','AreaParserTaskNum'})do w(n,0)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('ScrollLock',1);w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_X_Position',112);w('Player_PageLoc',0);w('MmOldX',112);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1);w('Player_MovingDir',1);w('Player_CollisionBits',255)
end
local function actor(id,x,y,slot)
 slot=slot or 0
 for _,a in ipairs({{'Enemy_Flag',1},{'Enemy_ID',id},{'Enemy_State',0},{'Enemy_X_Position',x&255},{'Enemy_PageLoc',x//256},{'Enemy_Y_Position',y},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_Y_MoveForce',0},{'Enemy_MovingDir',2},{'Enemy_BoundBoxCtrl',9},{'EnemyOffscrBitsMasked',0},{'Enemy_CollisionBits',0},{'MmEnemyHealthLo',0},{'MmEnemyHealthHi',0},{'MmEnemyFlash',0},{'RgEnemyStun',0}})do w(a[1],a[2],slot)end
end
local function setup(task)
 arena()
 if task.kind=='food'then
  actor(0x2e,112,184,5)
  for _,a in ipairs({{'Enemy_State',128},{'Enemy_BoundBoxCtrl',3},{'PowerUpType',task.power},{'InvPickupOwner',13},{'InvPickup',0xfc}})do w(a[1],a[2],5)end
 elseif task.kind=='hurt'then actor(6,116,184,0)end
end
local function setPhase(p)phase=p;stageAge=0;rec.transitions[#rec.transitions+1]={phase=p,update=updates};event('phase')end
local function beginCase()
 local task=assert(C.plan[index]);age=0;stageAge=0
 rec={case_index=index,name=task.name,kind=task.kind,before=snapshot(),started=wall,owners={},captures=0,swallows=0,attacks=0,pickups=0,heals=0,injuries=0,guards=0,spawns={},types={},kinds={},sounds={},defeats={},target=false,minY=176,transitions={}}
 records[#records+1]=rec;transaction(function()setup(task)end);setPhase((task.kind=='copy'or task.kind=='spit')and'warm'or'use');event('case-start')
end
local function finishCase()
 assert(pool()==0 and r('KbCopy')==0 and r('KbMouth')==0 and r('KbDropKind')==0,'Exact native ability/shot/drop cleanup')
 rec.ending=snapshot();rec.completed=wall;rec.updates=age;event('case-complete');index=index+1
 if index>#C.plan then done=true;phase='complete'else phase='setup'end
end
local function target(task)
 if rec.target then return end
 local x,y
 if task.kind=='sword'then
  if r('KbAction')~=7 or r('MkCombo')~=task.combo or r('MkDamage')==0 or r('MkMoveTick')<6 then return end
  x=r('MkRectX')+256*r('MkRectPage')+r('MkRectW')-2;y=math.min(192,r('MkRectY')-8)
 elseif task.kind=='copy'and(task.family==1 or task.family==4 or task.family==9 or task.family==12 or task.family==14)then
  if r('KbAction')~=4 then return end
  x=world()+((task.family==4 or task.family==9)and 4 or 32);y=r('Player_Y_Position')+8
 elseif task.kind=='slide'then
  if r('KbAction')~=5 then return end;x=world()+24;y=r('Player_Y_Position')+8
 else
  for i=0,2 do if r('KbShotType',i)~=0 then x=r('KbShotX',i)+256*r('KbShotPage',i)+2;y=r('KbShotY',i)-3;break end end
 end
 if x and x>=8 and x<232 and y>=40 and y<=200 then transaction(function()actor(6,x,y,0)end);rec.target=true;rec.target_x=x;rec.target_y=y;event('source-effect-aligned-target')end
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
 if r('KbVariant')~=C.variant then return{select=true}end
 return{a=true}
end
hook('GameLoopOwned',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then
  if r('GameEngineSubroutine')~=8 then return end
  assert(r('SelectedCharacter')==13 and r('KbVariant')==C.variant and r('CrossoverBehaviorVersion')==1 and r('CheatInvincible')==0,'Actual cold Kirby/Meta/Hard1/cheats')
  entered=true;phase='settle';age=0
 end
 updates=updates+1;age=age+1;stageAge=stageAge+1;assert(updates<=3000,'At most3000 actual updates')
 assert(r('SelectedCharacter')==13 and r('KbVariant')==C.variant and r('CrossoverBehaviorVersion')==1 and r('CheatInvincible')==0,'Owner/variant/mode remain actual')
 if phase=='settle'and age>=30 then assert(hp()==6 and r('KbMarker')==0xa7 and r('KbCopy')==0,'Real native cold Ensure');beginCase()
 elseif phase=='setup'then beginCase()
 elseif rec then
  local task=C.plan[index]
  if rec.removeGuardTarget then transaction(function()w('Enemy_Flag',0,0)end);rec.removeGuardTarget=false end
  if task.kind=='hurt'and rec.damageSeen and not rec.hurtActorCleared then transaction(function()w('Enemy_Flag',0,0)end);rec.hurtActorCleared=true end
  if phase=='warm'and not rec.added and r('KbAction')==1 and r('KbActionAge')==0 then
   transaction(function()actor(task.enemy or 6,world()+8,r('Player_Y_Position')+8,0)end);rec.added=true;event('eligible-inhale-enemy')
  elseif phase=='use'or phase=='spit'then
   if task.kind=='copy'and task.family~=10 or task.kind=='spit'or task.kind=='float'or task.kind=='slide'or task.kind=='sword'then target(task)end
  end
 end
end)
local function owner(key,fn)
 hook(key,function(s)if entered and rec and phase~='setup'and not done then rec.owners[key]=(rec.owners[key]or 0)+1;if fn then fn(s)end end end)
end
owner('Capture',function(s)
 local task=C.plan[index];assert(phase=='warm'and s['cpu.x']==0 and r('Enemy_ID',0)==(task.enemy or 6),'Actual eligible native capture owner');rec.captures=rec.captures+1;event('real-capture')
end)
owner('Swallow',function()local t=C.plan[index];assert(r('KbMouth')~=0 and r('KbMouthCopy')==t.family,'Actual mouth family before Down swallow');rec.swallows=rec.swallows+1;event('real-swallow',t.family)end)
owner('CopyAttack',function()local t=C.plan[index];assert(t.kind=='copy'and r('KbCopy')==t.family,'Actual acquired family use');rec.attacks=rec.attacks+1;event('real-copy-action',t.family)end)
owner('Spawn',function(s)rec.spawns[s['cpu.a']]=true;event('actual-native-spawn-request',s['cpu.a'])end)
owner('Pickup',function(s)local t=C.plan[index];assert(t.kind=='food'and s['cpu.x']==5 and r('PowerUpType',5)==t.power,'Actual Kirby native food dispatch');rec.pickups=rec.pickups+1;event('actual-food-contact')end)
owner('Heal',function(s)assert(s['cpu.a']==C.plan[index].power,'Actual food heal source request');rec.heals=rec.heals+1;event('actual-heal-entry',s['cpu.a'])end)
owner('Injury',function()assert(C.plan[index].kind=='hurt','Only declared real hurt contact');rec.injuries=rec.injuries+1;event('actual-injury-entry')end)
owner('BodyContact',function(s)if C.plan[index].family==4 and r('KbAction')==4 and s['cpu.x']==0 then rec.guards=rec.guards+1 end end)
owner('MetaStart',function(s)assert(C.variant==1 and C.plan[index].kind=='sword'and s['cpu.a']==C.plan[index].combo,'Actual source sword selection');event('actual-sword-start',s['cpu.a'])end)
owner('DropCopy',function()event('actual-Select-drop',r('KbCopy'))end)
owner('Defeat',function(s)
 local ret=emu.read(256+(s['cpu.sp']+1)%256,emu.memType.nesDebug)+256*emu.read(256+(s['cpu.sp']+2)%256,emu.memType.nesDebug)+1
 local caller=bank(0xa000);local allowed=false
 for _,a in ipairs(C.defeat_returns)do if a.pc==ret and a.bank==caller then allowed=true end end
 if allowed then assert(rec.target and r('ObjectOffset')==0,'Actual selected target native defeat');rec.defeats[#rec.defeats+1]={returnPC=ret,bank=caller,update=updates};event('actual-native-defeat')end
end)
for _,n in ipairs({'Square1SoundQueue','Square2SoundQueue','NoiseSoundQueue'})do emu.addMemoryCallback(function(_,v)if entered and rec and not writing and v~=0 then rec.sounds[n..':'..v]=true end end,emu.callbackType.write,C.ram[n])end
hook('GameLoopFinish',function()
 if not entered or done or not rec then return end
 assert(r('MmDeathFlag')==0 and r('GameEngineSubroutine')==8,'No native death')
 local task=C.plan[index];rec.minY=math.min(rec.minY,r('Player_Y_Position'))
 for i=0,2 do if r('KbShotType',i)~=0 then rec.types[r('KbShotType',i)]=true;rec.kinds[r('KbShotKind',i)]=true end end
 if r('KbAction')==5 then rec.slideStarted=true end
 if C.variant==1 then assert(r('KbCopy')==0 and r('KbMouth')==0 and r('KbFloat')==0,'Meta has no invented inflation/copy path')end
 if task.image and not rec.sample and((task.kind=='copy'and r('KbAction')==4)or(task.kind=='spit'and pool()>0)or(task.kind=='float'and r('KbFloat')~=0 and stageAge>=20)or(task.kind=='slide'and r('KbAction')==5)or(task.kind=='sword'and r('MkDamage')~=0 and r('MkMoveTick')>=6))then rec.sample=true;screenshot=task.name..'.png'end
 if task.kind=='hurt'then
  if hp()<rec.before.hp then
   assert(hp()==rec.before.hp-1 and rec.injuries>0,'Exact actual source one-HP injury');rec.damageSeen=true
   if r('KbHurt')==0 and r('KbHurtMove')==0 and r('InjuryTimer')==0 and r('Player_State')==0 then assert(rec.hurtActorCleared,'Remove contact actor only after actual injury');finishCase()end
  end
 elseif task.kind=='food'and stageAge>=25 then
  assert(rec.pickups==1 and rec.heals==1 and r('Enemy_Flag',5)==0,'One real mature food collection through actual dispatch')
  assert(hp()==math.min(6,rec.before.hp+2)and r('KbFoodKind')==(rec.before.food~1),'Source heal2/clamp6 and real appearance toggle; no tiers')
  if task.image then screenshot=task.name..'.png'end;finishCase()
 elseif phase=='warm'and r('KbMouth')~=0 then
  assert(rec.captures==1 and r('KbMouth')==(task.enemy or 6)+1 and r('KbCopy')==0 and r('Enemy_Flag',0)==0,'Native inhale captured real enemy; ability not seeded')
  setPhase(task.kind=='copy'and'swallow'or'spit')
 elseif phase=='swallow'and stageAge>=28 then
  assert(r('KbCopy')==task.family and r('KbMouth')==0 and rec.swallows==1,'Actual Down swallow earned exact family');setPhase('use')
 elseif phase=='use'or phase=='spit'then
  if task.kind=='copy'and task.family==4 and rec.guards>0 and stageAge>=18 and not rec.guardProtected then
   assert(hp()==rec.before.hp and r('Enemy_Flag',0)==1,'Real guard protects contact without defeating enemy');rec.guardProtected=true;rec.clearGuardTarget=true
  end
  if rec.clearGuardTarget then rec.clearGuardTarget=false;rec.removeGuardTarget=true end
  if task.kind=='copy'and task.family==10 and stageAge>=18 and stageAge<=38 then
   assert(r('KbAction')==4 and r('MmVY',1)==0 and r('MmVY',2)==0,'Source cloud hover really cancels vertical velocity');rec.hover=rec.hover or{};rec.hover[#rec.hover+1]=r('Player_Y_Position')
  end
  if task.kind=='no-flight'and stageAge>=110 then assert(rec.minY<=112,'Actual normal Meta jump completed');finishCase()
  elseif stageAge>=110 and pool()==0 and r('Player_State')==0 and r('KbAction')==0 then
   if task.kind=='copy'then
    assert(rec.attacks>0 and hp()==rec.before.hp,'Acquired ability actually used with no unintended injury')
    if task.family==4 then assert(rec.guardProtected,'Real protected contact required')
    elseif task.family==10 then assert(rec.hover and #rec.hover>=16,'Actual bounded cloud hover');local lo,hi=255,0;for _,y in ipairs(rec.hover)do lo=math.min(lo,y);hi=math.max(hi,y)end;assert(hi-lo<=3,'Source hover position bound')
    else assert(rec.target and #rec.defeats>0,'Actual source-specific ability defeated native target')end
    setPhase('discard')
   else
    assert(rec.target and #rec.defeats>0 and hp()==rec.before.hp,'Real native basic/sword target defeat without injury')
    if task.kind=='spit'then assert(rec.types[1]and r('KbMouth')==0,'Actual spit-star and mouth release')end
    if task.kind=='float'then assert(rec.types[2]and r('KbFloat')==0,'Actual real inflation followed by fresh-B air puff/deflation')end
    if task.kind=='sword'then assert(rec.owners.MetaStart and rec.owners.MetaStart==1,'Actual one selected grounded/air sword action')end
    finishCase()
   end
  end
 elseif phase=='discard'then
  if stageAge==5 then assert(r('KbCopy')==0 and r('KbDropKind')==task.family,'Real Select creates matching discarded copy star')end
  if stageAge>=260 then assert(r('KbCopy')==0 and r('KbMouth')==0 and r('KbDropKind')==0,'Actual native dropped copy expiry');finishCase()end
 end
 event('update');assert(age<task.limit+120,'Finite current component deadline')
end)
-- Additive passive live draw -> completed Main -> physical DMA -> whole PPU.
-- Inserted in the frozen fixture's existing lexical scope; no gameplay writes.
local KR=assert(C.render_diagnostic)
local krLog=assert(io.open(OUTPUT..'live-render.jsonl','w'))
local krRows,krBytes,krDrawCount,krMainCount,krDmaCount,krFrames=0,0,0,0,0,0
local krPending,krDma,krLastDma,krBuilt,krEnable=nil,nil,nil,nil,nil
local krDraws,krRecent={},{}
local krUnmatched,krDuplicate,krCarry,krCarryMax,krLastCaptured=0,0,0,0,nil
local krMask=0
local krStamp={}
local krCodec=dofile(KR.codec)
local krCapture=krCodec.install(OUTPUT,{container_bytes=134217728,records=3000},function()return krStamp end)
local krFull=assert(io.open(OUTPUT..'actual-ppu.argb','wb'))
local function krNow()
 local s=emu.getState();return{ppu_frame=s['ppu.frameCount'],line=s['ppu.scanline'],dot=s['ppu.cycle'],cycle=s['cpu.cycleCount'],pc=s['cpu.pc'],bank=bank(s['cpu.pc']),sp=s['cpu.sp']}
end
local function krHex(at,kind)
 local t={};for i=0,255 do t[i+1]=string.format('%02x',emu.read(at+i,kind or emu.memType.nesDebug))end;return table.concat(t)
end
local function krState()
 local s={action=r('KbAction'),action_age=r('KbActionAge'),copy=r('KbCopy'),mouth=r('KbMouth'),mouth_copy=r('KbMouthCopy'),float=r('KbFloat'),float_age=r('KbFloatAge'),pose=r('KbPose'),pose_group=r('KbPoseGroup'),combo=r('MkCombo'),sword_tick=r('MkMoveTick'),sword_damage=r('MkDamage'),x=r('Player_X_Position')+256*r('Player_PageLoc'),y=r('Player_Y_Position'),state=r('Player_State'),slots={}}
 s.live=s.action~=0 or s.float~=0
 for i=0,2 do local q={slot=i,type=r('KbShotType',i),kind=r('KbShotKind',i),age=r('KbShotAge',i),x=r('KbShotX',i)+256*r('KbShotPage',i),y=r('KbShotY',i)};s.slots[#s.slots+1]=q;if q.type~=0 then s.live=true end end
 return s
end
local function krEmit(t)
 t.stamp=krNow();t.wall=wall;t.update=updates;t.case=rec and rec.case_index or 0;t.name=rec and rec.name or'';t.phase=phase
 local line=json(t)..'\n';krRows=krRows+1;krBytes=krBytes+#line
 assert(krRows<=20000 and krBytes<=67108864 and #line<=16384,'Bounded passive live render journal')
 krLog:write(line);krLog:flush()
end
local function krScope()return entered and r('SelectedCharacter')==13 and r('KbVariant')==C.variant and r('OperMode')==1 and r('GameEngineSubroutine')==8 end
local function krArm(kind,s)
 if not krScope()then return end
 assert(not krPending,'No nested tracked body/shot caller')
 krPending={kind=kind,entry=krNow(),entry_sp=s['cpu.sp'],state=krState(),source_before=krHex(0x200),writes={},render_entries=0}
 if kind=='shot'then
  local slot=r('KbSavedSlot');assert(slot<3 and r('KbShotType',slot)~=0,'Only genuine immediate live shot draw, not HUD/drop')
  krPending.slot=slot;krPending.shot_type=r('KbShotType',slot);krPending.shot_kind=r('KbShotKind',slot)
 end
end
hook('LiveBodyCall',function(s)krArm('body',s)end)
hook('LiveShotCall',function(s)krArm('shot',s)end)
hook('LiveRenderer',function(s)
 if not krPending then return end
 local p=krPending;assert(p.render_entries==0,'One real renderer per selected caller');p.render_entries=1
 local ptr=r('R0')+256*r('R1');local h=emu.read(ptr,emu.memType.nesDebug);local data={}
 for i=0,math.min(h,128)do data[#data+1]=emu.read(ptr+i,emu.memType.nesDebug)end
 p.renderer={stamp=krNow(),pointer=ptr,physical_C=bank(0xc000),shadow_C=r('CurrentBankC'),header=h,record=data,cursor=r('CurrentOAMOffset'),rotation=r('RgOamRotation'),rotation_active=r('GuestOamRotationActive'),x=r('R4'),page=r('R5'),y=r('R6'),attr=r('R3')}
 if p.kind=='body'then
  assert(ptr==r('SmPosePtr')+256*r('SmPosePtr',1),'Actual dynamic body pointer consumed by the renderer')
  assert(ptr==KR.outline_buffer or ptr>=0xc000 and ptr<0xe000 and bank(0xc000)==KR.art_bank,'Only real filtered-body RAM buffer or actual Kirby art bank')
 else assert(ptr>=0xc000 and ptr<0xe000 and bank(0xc000)==KR.art_bank,'Actual Kirby live-shot art bank; no HUD/RAM alias')end
end)
emu.addMemoryCallback(function(at,v)
 if krPending then assert(#krPending.writes<256,'Bounded actual draw emission');krPending.writes[#krPending.writes+1]={address=at,value=v}end
end,emu.callbackType.write,0x200,0x2ff)
local function krReturn(kind,s)
 if not krPending then return end
 local p=krPending;assert(p.kind==kind and p.render_entries==1 and p.entry_sp==s['cpu.sp'],'Genuine same caller return/SP, not a stale hook')
 krDrawCount=krDrawCount+1;p.draw=krDrawCount;p.source_after=krHex(0x200);p.completed=krNow();p.cursor_after=r('CurrentOAMOffset');p.live=p.state.live
 krDraws[#krDraws+1]=p;if p.live then p.event='actual-live-draw';krEmit(p)end;krPending=nil
end
hook('LiveBodyReturn',function(s)krReturn('body',s)end)
hook('LiveShotReturn',function(s)krReturn('shot',s)end)
hook('GameLoopFinish',function()
 if not krScope()then return end
 assert(not krPending,'No unfinished caller at completed Main')
 krMainCount=krMainCount+1
 local image={event='completed-Main-image',Main=krMainCount,source=krHex(0x200),state=krState(),draw_ids={},live_draw_ids={},draws=krDraws,case=rec and rec.case_index or 0}
 for _,d in ipairs(krDraws)do image.draw_ids[#image.draw_ids+1]=d.draw;if d.live then image.live_draw_ids[#image.live_draw_ids+1]=d.draw end end
 if #krDraws>0 then krBuilt=image end
 krRecent[#krRecent+1]=image;if #krRecent>32 then table.remove(krRecent,1)end
 krEmit({event=image.event,Main=image.Main,source=image.source,state=image.state,draw_ids=image.draw_ids,live_draw_ids=image.live_draw_ids});krDraws={}
end)
emu.addMemoryCallback(function(_,v)krMask=v;if v&24~=0 and krLastDma then krEnable={epoch=krLastDma.epoch,stamp=krNow()}end end,emu.callbackType.write,0x2001)
emu.addMemoryCallback(function(_,v)
 if not krScope()then return end
 assert(not krDma,'One actual DMA at a time');krDma={source=krHex(v*256),writes={},address_zero=emu.getState()['ppu.spriteRamAddr']==0,render_off=krMask&24==0}
end,emu.callbackType.write,0x4014)
emu.addMemoryCallback(function(_,v)
 if not krDma then return end
 local i=#krDma.writes;assert(i<256 and emu.getState()['ppu.spriteRamAddr']==i and krMask&24==0,'Actual256 byte/destination/render DMA protocol')
 krDma.writes[i+1]=string.format('%02x',v)
end,emu.callbackType.write,0x2004)
hook('DmaComplete',function()
 if not krDma then return end
 local p=krDma;local written=table.concat(p.writes);local hw=krHex(0,emu.memType.nesSpriteRam);local normal={}
 for i=1,256 do local v=tonumber(p.source:sub(i*2-1,i*2),16);if(i-1)%4==2 then v=v&0xe3 end;normal[i]=string.format('%02x',v)end
 assert(p.address_zero and p.render_off and #p.writes==256 and written==p.source and table.concat(normal)==hw,'All raw source/write and physical E3 DMA bytes remain exact')
 local matched,candidates=nil,0
 for i=#krRecent,1,-1 do if krRecent[i].source==p.source then candidates=candidates+1;if not matched then matched=krRecent[i]end end end
 if candidates>1 then krDuplicate=krDuplicate+1 end
 if rec and not matched then krUnmatched=krUnmatched+1;assert(krUnmatched<=32,'At most32 explicitly unmatched scoped DMA epochs')end
 local built=krBuilt and krBuilt.source==p.source and krBuilt or nil
 local retained={};if built then for _,d in ipairs(built.draws)do
  if d.live then local last={};for _,w in ipairs(d.writes)do last[w.address]=w.value end
   local count,same=0,true;for at,v in pairs(last)do count=count+1;if tonumber(p.source:sub((at-0x200)*2+1,(at-0x200)*2+2),16)~=v then same=false end end
   retained[#retained+1]={draw=d.draw,kind=d.kind,source_written_bytes=count,all_written_bytes_retained=same}
  end
 end end
 krDmaCount=krDmaCount+1;local state=emu.getState();local chr={};for i=0,11 do chr[i+1]=state['mapper.chrBanks'..i]end
 krLastDma={event='actual-complete-DMA',epoch=krDmaCount,source=p.source,written=written,physical=hw,raw_write_count=256,destination_order_0_through255=true,completed_Main=matched and matched.Main or nil,source_match_candidates=candidates,built_Main=built and built.Main or nil,built_live=built and #built.live_draw_ids>0 or false,live_draws=retained,live_state=matched and matched.state or krState(),chr=chr}
 krEmit(krLastDma);krDma=nil
end)
emu.addEventCallback(function()
 if krScope()and rec and krLastDma and(krLastDma.built_live or krState().live)then
  if krLastCaptured==krLastDma.epoch then krCarry=krCarry+1 else krCarry=0;krLastCaptured=krLastDma.epoch end;krCarryMax=math.max(krCarryMax,krCarry)
  if krCarry<8 then
   local screen=emu.getScreenBuffer();assert(#screen==61440,'Actual256x240 whole PPU pixels');local raw={};for i,v in ipairs(screen)do raw[i]=string.pack('<I4',v)end
   local actual=krHex(0,emu.memType.nesSpriteRam)
   krStamp={ppu=krNow(),case=rec.case_index,phase=phase,actual_DMA=krLastDma.epoch,Main=krLastDma.completed_Main,built_Main=krLastDma.built_Main}
   krFull:write(table.concat(raw));krFrames=krFrames+1
   krEmit({event='captured-whole-PPU',ordinal=krFrames,actual_DMA=krLastDma.epoch,completed_Main=krLastDma.completed_Main,built_Main=krLastDma.built_Main,physical_OAM_matches_DMA=actual==krLastDma.physical,render_enable=krEnable,live_state=krLastDma.live_state,carry_ordinal=krCarry,scope='Real pixels; page equality is content linkage, not a unique producer or opaque visibility proof.'})
  end
 end
 if done then
  assert(not krPending and not krDma,'No unfinished passive caller/DMA at terminal')
  krFull:close();krCapture.close();krEmit({event='passive-live-terminal',draws=krDrawCount,completed_Mains=krMainCount,actual_DMAs=krDmaCount,whole_frames=krFrames,unmatched_DMA=krUnmatched,duplicate_content_DMA=krDuplicate,max_carry=krCarryMax,capture=krCapture.stats(),limits='No extra PNGs, inputs, setup, mechanics or original guard changes. Duplicate source pages remain explicitly ambiguous; max8 captures per DMA and max32 unmatched scoped epochs. Physical E3 only; raw source/write bytes stay unmasked.'});krLog:close()
 end
end,emu.eventType.endFrame)

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
  if phase=='warm'then b.b=true
  elseif phase=='swallow'then b.down=r('KbMouth')~=0
  elseif phase=='discard'then b.select=r('KbCopy')~=0
  elseif phase=='spit'then b.b=stageAge>=3 and r('KbMouth')~=0 and r('KbPrevious')&64==0
  elseif task.kind=='copy'then
   if task.family==10 then b.a=stageAge<12;b.b=stageAge>=12 and stageAge<42
   else b.b=stageAge>=4 and(task.family==4 and stageAge<24 or task.family~=4 and rec.attacks==0)end
  elseif task.kind=='float'then b.up=stageAge<38;b.b=stageAge>=42 and r('KbFloat')~=0 and r('KbPrevious')&64==0
  elseif task.kind=='slide'then b.a=stageAge>=4 and not rec.slideStarted;b.down=b.a
  elseif task.kind=='no-flight'then b.a=stageAge>=5 and stageAge<16 or stageAge>=25 and stageAge<29;b.up=stageAge>=25 and stageAge<60
  elseif task.kind=='sword'then
   local k=task.combo;local started=rec.owners.MetaStart~=nil
   if k==0 or k==1 then b.b=stageAge>=5 and not started;b.up=b.b and k==1
   elseif k==2 then b.select=stageAge>=5 and not started
   elseif k==3 then b.a=stageAge>=5 and stageAge<35;b.b=stageAge>=20 and not started
   elseif k==4 then b.a=stageAge>=5 and stageAge<35;b.b=stageAge>=25 and not started;b.down=b.b
   else b.b=stageAge>=5 and not started;b.right=b.b or stageAge>=9 and stageAge<45 end
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
  rec.capture={file=screenshot,wall=wall,update=updates,PPU_frame=s['ppu.frameCount'],hardware_OAM=oam,physical_CHR=chr,note='Actual endFrame image plus hardware snapshot; visibility is independently reviewed, not inferred from source art IDs.'};screenshot=nil
 end
 assert(wall<8000,'At most8000wall frames')
 if done then
  assert(not pending and dmas>100 and irqCount>100 and nmis>100 and enables>100 and late==0,'Full original hardware/source guards exercised')
  local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=true,native_run=true,ROM_sha256=C.ROM_sha256,identity=C.identity,unit=C.unit,character=13,variant=C.variant,actual_numeric_mode=r('CrossoverBehaviorVersion'),cases=records,wall=wall,updates=updates,complete256_DMAs=dmas,NMI_checks=nmis,IRQ31_checks=irqCount,NMI_safe_enables=enables,CHR_checks=chrChecks,minSP=minSP,screenshots=images,goal_complete=false,scope='Actual native enemy inhale/Down copy, mature food and real hurt; Meta native sword/no inflation. Explicit bounded scene/actor setup; no tested ability/health/input-edge/resource/outcome seeds. No emergence/RNG/star/1up/underwater/allfacings/allpixel/audio-fidelity/full-route claim.'}));f:close();csv:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
