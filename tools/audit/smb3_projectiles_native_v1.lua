-- Real menu selection; then explicit update-boundary actor/form arenas.
local C=assert(SMB3_PROJECTILES_NATIVE_CONFIG)
for n,a in pairs(C.ram)do L[n]=a end
local wall,index,age,nmis=0,0,0,0
local entered,done=false,false
local current=nil
local results,violations={},{}
local minSP,stackWrites=255,0
local irqStores,bodyDraws,shotDraws,hwShotFrames=0,0,0,0
local r=function(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local w=function(n,v,i)emu.write(assert(L[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
local function json(v)
 if type(v)=='table'then
  local o={};if #v>0 then for _,x in ipairs(v)do o[#o+1]=json(x)end;return'['..table.concat(o,',')..']'end
  for k,x in pairs(v)do o[#o+1]=string.format('%q',k)..':'..json(x)end;return'{'..table.concat(o,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)else return tostring(v)end
end
local function bank(a)local p=emu.convertAddress(a);return p and p.address//8192 or -1 end
local function valid(n)local h=C.hooks[n];return bank(h.address)==h.physical_bank end
local function bind(n)local h=C.hooks[n];for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Bound '..n..' opcode')end end
local function native()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function capture(name)
 local f=assert(io.open(OUTPUT..name..'.argb','wb'))
 for _,v in ipairs(emu.getScreenBuffer())do f:write(string.pack('<I4',v))end;f:close()
 local f=assert(io.open(OUTPUT..name..'.oam','wb'))
 for i=0,255 do f:write(string.char(emu.read(i,emu.memType.nesSpriteRam)))end;f:close()
end
local function problem(message,data)
 local row={case=index,age=age,wall=wall,message=message,data=data};violations[#violations+1]=row
 local f=assert(io.open(OUTPUT..'violations.json','w'));f:write(json(violations));f:close()
 capture('failure-'..index..'-'..age)
 assert(false,message)
end
-- NMI_GUARD_INSERT
local csv=assert(io.open(OUTPUT..'updates.csv','w'))
csv:write('wall,case,age,enemy,kind,hp,state,id,shot0,shot1,x,y,engine,launches,damageCalls,sfx1,sfx2,sp,enemyX,enemyY,shotX,shotY,shotVX,shotVY\n')
local expectedShots={}
local upper=0
local physicalBanks,verifiedPages={},{}
local chrChecks,bodyOamChecks,shotOamChecks,dmaChecks=0,0,0,0
local expectedFile=assert(io.open(C.raw_chr,'rb'));local expectedChr=expectedFile:read('*a');expectedFile:close()
emu.addMemoryCallback(function(_,v)upper=v&3 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(a,v)physicalBanks[a-0x5120]=v+256*upper end,emu.callbackType.write,0x5120,0x512b)
local function physicalPage(page)
 if verifiedPages[page]then return end
 local out={}
 for i=0,1023 do
  local v=emu.read(page*1024+i,emu.memType.nesChrRom)
  assert(v==expectedChr:byte(page*1024+i+1),'Actual physical sprite CHR exactly matches frozen candidate')
  out[#out+1]=string.char(v)
 end
 local f=assert(io.open(OUTPUT..'physical-chr-'..page..'.bin','wb'));f:write(table.concat(out));f:close();verifiedPages[page]=true
end
local prepared,completed,dma=nil,nil,nil
local function staging()
 local out={};for i=0,255 do out[#out+1]=string.char(r('Sprite_Data',i))end;return table.concat(out)
end
emu.addMemoryCallback(function()
 if entered and not done and valid('DrawAllMetasprites')then prepared={case=index,age=age,body=nil,shots={}}end
end,emu.callbackType.exec,C.hooks.DrawAllMetasprites.address)
local function renderer(name)
 if not entered or done or not prepared or not valid(name)then return end
 local ptr=r('R0')+256*r('R1');local body=C.body_records[tostring(ptr)];local shot=C.shot_records[tostring(ptr)]
 if not((body and bank(0xc000)==C.body_bank)or(shot and bank(0xc000)==C.shot_bank))then return end
 local parts=body or shot.parts
 local size=emu.read(ptr,emu.memType.nesDebug);assert(size==#parts*4,'Authentic source descriptor length')
 for i,part in ipairs(parts)do for j,v in ipairs(part)do assert(emu.read(ptr+(i-1)*4+j,emu.memType.nesDebug)==v,'Authentic body/projectile source descriptor')end end
 local row={x=r('R4')+256*r('R5'),y=r('R6')+256*r('R7'),attr=r('R3'),parts=parts,pointer=ptr,expected_page=r('SmChrBank')+256*r('M3SpritePageHi')}
 if shot then
  row.kind=shot.kind;prepared.shots[#prepared.shots+1]=row
  current.shot_draws=current.shot_draws+1;shotDraws=shotDraws+1
 else prepared.body=row end
end
emu.addMemoryCallback(function()renderer('MetaspriteRenderLoop')end,emu.callbackType.exec,C.hooks.MetaspriteRenderLoop.address)
emu.addMemoryCallback(function()renderer('RlNativeRenderDispatch')end,emu.callbackType.exec,C.hooks.RlNativeRenderDispatch.address)
emu.addMemoryCallback(function()
 if entered and not done and prepared and valid('RosterOamReady')then completed={bytes=staging(),meta=prepared}end
end,emu.callbackType.exec,C.hooks.RosterOamReady.address)
emu.addMemoryCallback(function(_,page)
 dma=nil;if not entered or done or not completed then return end
 local out={};for i=0,255 do out[#out+1]=string.char(emu.read(page*256+i,emu.memType.nesDebug))end
 if table.concat(out)==completed.bytes then dma=completed end
end,emu.callbackType.write,0x4014)
local function seed(q)
 assert(r('SelectedCharacter')==17 and r('M3Variant')==C.variant,'Actual SMB3 brother selected through menu')
 w('CrossoverBehaviorVersion',q.mode)
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i);w('MmEnemyFlash',0,i);w('Enemy_State',0,i)end
 for i=0,1 do w('M3ShotKind',0,i);w('Block_State',0,i);w('BlockMetasprite',0,i)end
 for i=0,8 do w('Misc_State',0,i);w('MiscMetasprite',0,i)end
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x);w('MmSolidTerrain',1,p*208+176+x)end end
 for _,n in ipairs({'TimerControl','GamePauseStatus','GuestHurtKind','GuestHurtTicks','PlayerChangeSizeFlag','MmDeathFlag','AreaParserTaskNum','ScrollThirtyTwo','EnemyFrenzyBuffer','EnemyFrenzyQueue','BlockBounceTimer','M3Growth','M3Poof','M3Previous','FireballThrowingTimer','CrouchingFlag','RgCrouch','DisableCollisionDet','GameTimerExpiredFlag'})do w(n,0)end
 w('GuestInvulTicks',240);w('InjuryTimer',240);w('StarInvincibleTimer',0)
 w('M3Form',q.kind==2 and 6 or 2);w('M3Ready',0);w('M3Marker',0xb3)
 w('Player_X_Position',q.face==1 and 64 or 144);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('Player_X_Scroll',0);w('PlayerSize',0);w('PlayerStatus',2);w('Player_CollisionBits',3);w('PlayerFacingDir',q.face)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0);w('ScrollLock',1)
 w('EnemyDataLow',L.E_GroundArea10%256);w('EnemyDataHigh',L.E_GroundArea10//256)
 w('GameTimerDisplay',3);w('GameTimerDisplay',0,1);w('GameTimerDisplay',0,2)
 local ex=q.kind==2 and(q.face==1 and 76 or 132)or(q.face==1 and 80 or 128)
 w('Enemy_Flag',1);w('Enemy_ID',q.enemy);w('Enemy_X_Position',ex);w('Enemy_PageLoc',0);w('Enemy_Y_Position',176);w('Enemy_Y_HighPos',1)
 w('Enemy_MovingDir',q.face==1 and 2 or 1);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('Enemy_Y_MoveForce',0);w('Enemy_YMoveForceFractional',0)
 w('Enemy_BoundBoxCtrl',q.enemy==45 and 10 or 3);w('Enemy_CollisionBits',0);w('EnemyOffscrBitsMasked',0);w('Enemy_SprAttrib',0)
 w('BowserHitPoints',q.hp);w('BowserFront_Offset',0);w('DuplicateObj_Offset',1);w('BowserBodyControls',0);w('BowserFeetCounter',32);w('BowserMovementSpeed',0);w('BowserOrigXPos',ex);w('MaxRangeFromOrigin',32);w('EnemyFrameTimer',255);w('BowserFireBreathTimer',255)
 if q.enemy==45 then w('Enemy_Flag',0x80,1);w('Enemy_ID',45,1);w('Enemy_BoundBoxCtrl',10,1);w('Enemy_Y_HighPos',1,1)end
 age=0;current={name=q.name,mode=q.mode,kind=q.kind,enemy=q.enemy,hp_before=q.hp,launches=0,damage_calls=0,weapon_updates=0,advance_calls=0,collision_calls=0,body_draws=0,shot_draws=0,minimum_hp=q.hp,dead=false,frames=0,hw_shot_frames=0,body_oam_checks=0,shot_oam_checks=0,sfx1=0,sfx2=0}
 prepared=nil;completed=nil;dma=nil
 expectedShots={}
 print('SMB3_PROJECTILE_SEED '..json({case=index,name=q.name,wall=wall}))
end
for _,name in ipairs({'M3Weapons','M3Throw','M3AdvanceShot','M3ShotEnemies','HandleEnemyFBallCol','M3DrawWorld','M3Graphics'})do
 emu.addMemoryCallback(function()
  if not entered or done or not valid(name)then return end
  bind(name)
  if name=='M3Weapons'then current.weapon_updates=current.weapon_updates+1
  elseif name=='M3Throw'then current.launches=current.launches+1
  elseif name=='M3AdvanceShot'then current.advance_calls=current.advance_calls+1
  elseif name=='M3ShotEnemies'then current.collision_calls=current.collision_calls+1
  elseif name=='HandleEnemyFBallCol'then current.damage_calls=current.damage_calls+1
  elseif name=='M3Graphics'then current.body_draws=current.body_draws+1;bodyDraws=bodyDraws+1 end
 end,emu.callbackType.exec,C.hooks[name].address)
end
emu.addMemoryCallback(function()
 if not entered or done or not valid('BowserGfxHandler')then return end
 if C.cases[index].enemy~=45 or r('Enemy_State')~=0 then return end
 local q=C.cases[index];local ex=q.kind==2 and(q.face==1 and 76 or 132)or(q.face==1 and 80 or 128)
 w('Enemy_X_Position',ex);w('Enemy_PageLoc',0);w('Enemy_Y_Position',176);w('Enemy_Y_HighPos',1)
 w('EnemyFrameTimer',255);w('BowserFireBreathTimer',255)
end,emu.callbackType.exec,C.hooks.BowserGfxHandler.address)
for _,pc in ipairs(C.irq_scroll_stores)do
 emu.addMemoryCallback(function()
  if not entered or done then return end
  assert(bank(pc)==C.hooks.IrqScrollSplit.physical_bank,'Actual visible IRQ bank')
  assert(emu.getState()['ppu.scanline']==31,'Visible scroll writes stay on line31')
  irqStores=irqStores+1
 end,emu.callbackType.exec,pc)
end
emu.addMemoryCallback(function(_,v)
 if not entered or done then return end
 if v~=0 then current.sfx1=current.sfx1|v end
end,emu.callbackType.write,L.Square1SoundQueue)
emu.addMemoryCallback(function(_,v)
 if not entered or done then return end
 if v~=0 then current.sfx2=current.sfx2|v end
end,emu.callbackType.write,L.Square2SoundQueue)
local function finishCase()
 local q=C.cases[index];current.hp_after=r('BowserHitPoints');current.enemy_state=r('Enemy_State');current.enemy_id_after=r('Enemy_ID')
 local killed=r('Enemy_Flag')==0 or r('Enemy_State')&32~=0 or r('Enemy_ID')~=q.enemy
 current.dead=killed
 local mechanics=current.launches==1 and current.advance_calls>0 and current.collision_calls>0 and current.body_draws>0
 local outcome=true
 if q.enemy==6 or(q.enemy==2 and q.kind==2)then outcome=killed
 elseif q.enemy==45 then outcome=current.minimum_hp<q.hp and(q.hp~=1 or killed)
 elseif q.enemy==2 or q.enemy==12 then outcome=not killed end
 current.passed=mechanics and outcome
 current.expected=q.enemy==45 and(q.hp==1 and 'native boss defeat' or 'native boss HP decreases')or((q.enemy==6 or(q.enemy==2 and q.kind==2))and 'enemy defeated' or 'immune enemy survives')
 assert(mechanics,'Real controller launch, native motion/collision/body paths execute exactly once')
 if not outcome then
  current.failure='Expected '..current.expected
  if C.observe~=1 then problem(current.failure,current)end
 end
 results[#results+1]=current
 print('SMB3_PROJECTILE_CASE '..json(current))
end
emu.addMemoryCallback(function()
 if not valid('PauseSkip')or done or not native()then return end
 if not entered then
  if r('SelectedCharacter')~=17 or r('M3Variant')~=C.variant then return end
  bind('PauseSkip');entered=true;index=1;seed(C.cases[index]);return
 end
 age=age+1
 current.minimum_hp=math.min(current.minimum_hp,r('BowserHitPoints'))
 csv:write(table.concat({wall,index,age,C.cases[index].enemy,C.cases[index].kind,r('BowserHitPoints'),r('Enemy_State'),r('Enemy_ID'),r('M3ShotKind'),r('M3ShotKind',1),r('Player_X_Position'),r('Player_Y_Position'),r('GameEngineSubroutine'),current.launches,current.damage_calls,r('Square1SoundQueue'),r('Square2SoundQueue'),emu.getState()['cpu.sp'],r('Enemy_X_Position'),r('Enemy_Y_Position'),r('M3ShotX',1),r('M3ShotY',1),r('M3ShotVX',1),r('M3ShotVY',1)},',')..'\n');csv:flush()
 if age>=42 then
  finishCase();index=index+1
  if index>#C.cases then done=true;return end
  seed(C.cases[index])
 end
end,emu.callbackType.exec,C.hooks.PauseSkip.address)
emu.addEventCallback(function()
 local b={}
 if not entered then
  if wall>=120 and wall%12==0 then
   if r('CrossoverMenuState')~=2 then b.start=true
   elseif r('CrossoverMenuIndex')~=16 then b[assert(C.menu_next[tostring(r('CrossoverMenuIndex'))])]=true
   elseif r('M3Variant')~=C.variant then b.select=true else b.a=true end
  end
 elseif not done and age>=4 and age<=7 then b.b=true end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1;assert(wall<5000,'Bounded SMB3 projectile arenas')
 if entered and not done then
  current.frames=current.frames+1
  local st=emu.getState()
  for i=0,11 do assert(st['mapper.chrBanks'..i]==physicalBanks[i],'Hardware CHR windows match write-time upper latch model');chrChecks=chrChecks+1 end
  if dma and dma.meta.case==index then
   local raw={};for i=0,255 do raw[#raw+1]=string.char(emu.read(i,emu.memType.nesSpriteRam))end
   assert(table.concat(raw)==dma.bytes,'Actual hardware OAM equals complete committed DMA list');dmaChecks=dmaChecks+1
   local function has(x,y,tile)
    for i=0,63 do local a=i*4;if raw[a+1]:byte()==y and raw[a+2]:byte()==tile and raw[a+4]:byte()==x then return true end end
    return false
   end
   local function parts(row)
    for _,part in ipairs(row.parts)do
     local dx=part[4]>=128 and part[4]-256 or part[4];local dy=part[3]>=128 and part[3]-256 or part[3]
     assert(has((row.x+dx)%256,(row.y+dy)%256,part[1]),'Every emitted source body/projectile part reaches hardware OAM')
    end
   end
   if dma.meta.body then
    parts(dma.meta.body)
    assert(st['mapper.chrBanks0']==dma.meta.body.expected_page,'Displayed body physical page matches source frame')
    physicalPage(st['mapper.chrBanks0']);bodyOamChecks=bodyOamChecks+1;current.body_oam_checks=current.body_oam_checks+1
   end
   if #dma.meta.shots>0 then
    assert(st['mapper.chrBanks4']==544,'Displayed weapon physical page is authored SMB3 projectile art')
    physicalPage(544)
    for _,row in ipairs(dma.meta.shots)do parts(row);shotOamChecks=shotOamChecks+1;current.shot_oam_checks=current.shot_oam_checks+1 end
    current.hw_shot_frames=current.hw_shot_frames+1;hwShotFrames=hwShotFrames+1
   end
   dma=nil
  end
  if age==3 or age==6 or age==12 or age==30 then capture(string.format('case-%02d-age-%02d-wall-%04d',index,age,wall))end
 end
 if done then
  assert(nmis>math.min(200,#C.cases*30)and irqStores>math.min(200,#C.cases*30)and minSP>0x40,'Actual interrupts and stack guard exercised')
  local failures=0;for _,q in ipairs(results)do if not q.passed then failures=failures+1 end end
  assert(bodyOamChecks>0 and shotOamChecks>0 and dmaChecks>0,'Actual body/projectile OAM/CHR evidence exists')
  local f=assert(io.open(OUTPUT..'proof.json','w'));f:write(json({passed=failures==0,cases=results,failed_cases=failures,nmis=nmis,irq_scroll_writes=irqStores,min_sp=minSP,stack_writes=stackWrites,nmi_mapper_store_windows=nmiWindows,body_draws=bodyDraws,shot_draws=shotDraws,hardware_shot_frames=hwShotFrames,body_oam_checks=bodyOamChecks,shot_oam_checks=shotOamChecks,complete_dma_checks=dmaChecks,hardware_chr_window_checks=chrChecks,staged=true,scope='Actual cold menu/alternate choice, then explicit native update-boundary form/enemy arenas with protected player. Fresh B launches authentic projectiles; native motion, generic collision, host boss HP/death and graphics execute. Bowser positions are pinned while living; SMB1 boss HP policy. Bank-qualified opcodes, line31 scroll, NMI five-SMC/bank/stack checks, complete OAM publication/source descriptor checks, physical body/weapon CHR bytes and PPU captures. Not controller-only traversal, physical power acquisition, source-complete armor/boss balance, acoustic or campaign proof.'}));f:close();csv:close()
  print('SMB3_NATIVE_COMPLETE '..failures..' failures');emu.stop(0)
 end
end,emu.eventType.endFrame)
