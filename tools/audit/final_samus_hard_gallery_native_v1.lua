-- Eight controlled Hard Samus cases. Explicit complete boundary seeds are B-use
-- setup, never acquisitions. Inputs/effects/costs/contacts/cleanup remain native.
local current=nil
local taskIndex=1
local bodyPrepared,bodyPublished,bodyDma,bodyDisplayed=nil,nil,nil,nil
local drawContext=nil
local function samusPool()
 local n=0;for i=0,2 do if r('SmShotType',i)~=0 then n=n+1 end end
 for i=0,9 do if r('RgShotType',i)==41 or r('RgShotType',i)==46 then n=n+1 end end
 return n
end
local function bombs()local n=0;for i=0,2 do if r('SmBombAge',i)~=0 then n=n+1 end end;return n end
local function effects()return samusPool()+bombs()end
local function sourceCue(kind,value,mask)
 for _,q in ipairs(current.stage.sourceSfx)do if q.kind==kind and(mask and q.value&value~=0 or not mask and q.value==value)then return true end end
 return false
end
local function shotRows()
 local z={};for i=0,2 do z[#z+1]={pool='native',slot=i,type=r('SmShotType',i),age=r('SmShotAge',i),x=r('SmShotX',i),page=r('SmShotPage',i),y=r('SmShotY',i),dir=r('SmShotDir',i),impact=r('SmShotImpact',i),bombAge=r('SmBombAge',i)}end
 for i=0,9 do if r('RgShotType',i)~=0 then z[#z+1]={pool='shared',slot=i,type=r('RgShotType',i),age=r('RgShotAge',i),x=r('RgShotX',i),page=r('RgShotPage',i),y=r('RgShotY',i),dir=r('RgShotDir',i)}end end;return z
end
local function stateRow()return{mode=r('CrossoverBehaviorVersion'),status=r('PlayerStatus'),owned=r('InvOwnedLo',2),selected=r('InvSelected',2),ammo=r('InvAmmo',34),ball=r('SmBall'),crouch=r('SmCrouch'),spin=r('SmFlip'),playerX=r('Player_X_Position'),playerY=r('Player_Y_Position'),state=r('Player_State'),frozen=r('AvFrozen')+256*r('AvFrozenHi'),shots=shotRows()}end
local function beginPhase(p)phase=p;age=0;event('samus-phase',{phase=p,state=stateRow()});FINAL_ABILITY_PHASE={name=current and current.q.name,phase=p}end
local function entity(slot,id,x,y)
 for _,q in ipairs({{'Enemy_Flag',1},{'Enemy_ID',id},{'Enemy_State',0},{'Enemy_X_Position',x%256},{'Enemy_PageLoc',x//256},{'Enemy_Y_Position',y},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_X_MoveForce',0},{'Enemy_Y_MoveForce',0},{'Enemy_MovingDir',1},{'Enemy_BoundBoxCtrl',9},{'EnemyOffscrBitsMasked',0},{'Enemy_CollisionBits',0},{'Enemy_SprAttrib',0},{'MmEnemyHealthLo',0},{'MmEnemyHealthHi',0},{'MmEnemyFlash',0},{'RgEnemyStun',0},{'RgShotHitsNow',0},{'AvFrozen',0},{'AvFrozenHi',0},{'LsrFrozenPose',0}})do w(q[1],q[2],slot)end
end
local function setupTask()
 local t=current.t
 -- Admission waits for a genuine empty Buffer1. It never discards prior VRAM.
 if r('VRAM_Buffer1_Offset')~=0 or r('VRAM_Buffer_AddrCtrl')~=0 then return false end
 writeBoundary=true;arena(false)
 for _,q in ipairs(C.clear_ranges)do for i=0,q.bytes-1 do w(q.name,0,i)end end
 for _,n in ipairs(C.clear_scalars)do w(n,0)end
 for i=0,5 do w('FloateyNum_Control',0,i);w('InvPickup',252,i);w('InvPickupOwner',255,i);w('EnemyMetasprite',0,i);w('MmEnemyHealthLo',0,i);w('MmEnemyHealthHi',0,i);w('MmEnemyFlash',0,i);w('RgEnemyStun',0,i);w('LsrFrozenPose',0,i)end
 for i=0,3 do w('InvDropKind',0,i);w('InvDropAge',0,i);w('InvDropAgeHi',0,i)end
 for i=0,9 do for _,n in ipairs(C.shared_arrays)do w(n,0,i)end end
 w('PlayerStatus',t.status or current.q.status);w('InvOwnedLo',t.owned or current.q.owned,2);w('InvOwnedHi',0,2)
 if not t.keepSelection then w('InvSelected',0,2)end
 w('InvAmmo',t.stock or 0,34);w('PlayerFacingDir',t.face);w('Player_MovingDir',t.face);w('InvDirty',1)
 w('HorizontalScroll',0);w('VerticalScroll',0)
 if t.kind=='wave-up' then
  w('Player_X_Position',t.face==1 and 244 or 252);w('MmOldX',t.face==1 and 244 or 252)
  w('ScreenLeft_X_Pos',133);w('ScreenRight_X_Pos',132);w('ScreenRight_PageLoc',1)
  w('HorizontalScroll',133)
  w('SmWavePolarity',t.face==1 and 0 or 1)
  -- Complete authored question block on the upward path; Wave bypasses terrain.
  w('Block_Buffer_1',0xc1,9*16+15);tile(0,15,11,0xc1)
 end
 if t.kind=='block' or t.kind=='wave-block' then
  local col=t.face==1 and 10 or 5;w('Block_Buffer_1',0xc1,9*16+col);tile(0,col,11,0xc1)
 end
 if t.kind=='pool' then
  -- Three complete far-from-player Long records occupy the native shared cap.
  for i=0,2 do w('SmShotType',2,i);w('SmShotX',90+i*10,i);w('SmShotPage',0,i);w('SmShotY',72,i);w('SmShotDir',t.face,i)end
 end
 if t.kind=='firebar' or t.kind=='firebar-no-varia' then
  -- Exact post-InitShortFirebar state: center already received its native +4.
  entity(0,27,116,176);w('FirebarSpinState_Low',0);w('FirebarSpinState_High',0);w('FirebarSpinSpeed',40);w('FirebarSpinDirection',0);w('FirebarPartCount',0)
 end
 if t.kind=='ordinary-hurt'then entity(0,6,116,184)end
 -- Initial palette is a complete CPU-derived GetPlayerColors packet for the
 -- seeded legal form. It is setup data, not a claim of native acquisition.
 local palette=C.palette_packets[tostring(t.owned or current.q.owned)]
 assert(palette and #palette>3 and palette[#palette]==0,'Exact complete source initial palette packet')
 for i,v in ipairs(palette)do w('VRAM_Buffer1',v,i-1)end
 w('VRAM_Buffer1_Offset',#palette-1)
 writeBoundary=false
 current.stage={kind=t.kind,face=t.face,started=wall,spawns={},debits={},draws={},hits=0,freezes=0,thaws=0,freezeSteps=0,bodyProtects=0,damageCalls=0,blockCalls=0,bombAttempts=0,bombRefusals=0,boosts=0,firebarCalls=0,injuries=0,sourceSfx={}}
 current.stages[#current.stages+1]=current.stage
 beginPhase('run');capture(current.q.name..'-'..taskIndex..'-setup')
 event('B-native-boundary-complete-setup',{task=t,owned=r('InvOwnedLo',2),stock=r('InvAmmo',34),source_palette_packet=palette,disclosure='World/player/motion/input history/pools/drops/native actor initialization/resource seeds only at GameLoop entry; no acquisition, RNG, target result or damage writes.'})
 return true
end
local function liveTarget()
 local s=current.stage;local t=current.t
 if s.target or not(t.kind=='contact'or t.kind=='missile-paid'or t.kind=='ice-thaw'or t.kind=='ice-break'or t.kind=='wave-contact'or t.kind=='bombs'or t.kind=='screw')then return end
 local x,y,world
 if t.kind=='screw'then
  if r('SmFlip')==0 or r('Player_State')==0 or r('Player_Y_Position')>160 then return end
  world=r('Player_X_Position')+256*r('Player_PageLoc')+4;y=r('Player_Y_Position')+8
 elseif t.kind=='bombs'then
  for i=0,2 do if r('SmBombAge',i)>=59 and r('SmBombAge',i)<76 and r('Player_Y_Position')<170 then world=r('SmBombX',i)+256*r('SmBombPage',i)+8;y=r('SmBombY',i)-8;break end end
 else
  for i=0,2 do
   if r('SmShotType',i)~=0 and r('SmShotImpact',i)==0 and r('SmShotAge',i)>=4 then
    local q=r('SmShotX',i)+256*r('SmShotPage',i);local dx=math.abs(q-r('Player_X_Position')-256*r('Player_PageLoc'))
    if dx>=32 then world=q-6;y=r('SmShotY',i)-8;break end
   end
  end
  if not world then for i=0,9 do if r('RgShotType',i)==41 or r('RgShotType',i)==46 then
   local q=r('RgShotX',i)+256*r('RgShotPage',i);local dx=math.abs(q-r('Player_X_Position')-256*r('Player_PageLoc'))
   if dx>=32 and r('RgShotYHigh',i)==1 then world=q-6;y=r('RgShotY',i)-8;break end
  end end end
 end
 if not world then return end
 local relative=world-r('ScreenLeft_X_Pos')-256*r('ScreenLeft_PageLoc')
 assert(relative>=8 and relative<232 and y>=40 and y<208,'Source-valid controlled target geometry')
 writeBoundary=true;entity(0,6,world,y);writeBoundary=false;s.target=wall
 event('controlled-real-Goomba',{world=world,y=y,disclosure='Complete falling native actor aligned to a live source projectile/body at a GameLoop boundary. Native motion/contact/damage remains real; B-only contact.'})
end
local function afterTask()
 local s=current.stage;s.completed=wall;s.passed=true;s.effectCleanupObserved=effects()==0;capture(current.q.name..'-'..taskIndex..'-complete');event('samus-subphase-complete',{task=current.t,state=stateRow()})
 taskIndex=taskIndex+1
 if taskIndex>#current.q.tasks then current.completed=wall;index=index+1;taskIndex=1;beginPhase('next')else current.t=current.q.tasks[taskIndex];beginPhase('setup')end
end
local function markSpawn(kind,typ,slot,dir)
 local s=current.stage;s.spawns[#s.spawns+1]={kind=kind,type=typ,slot=slot,dir=dir,wall=wall,update=updates}
 event('actual-Samus-spawn',s.spawns[#s.spawns]);capture(current.q.name..'-'..taskIndex..'-spawn-'..#s.spawns)
end
hook('SamusWeapons::Spawn',function()
 if not entered or phase~='run'then return end
 local before={};for i=0,2 do before[i]=r('SmShotType',i)end
 onReturn('Samus-native-spawn',function()for i=0,2 do if before[i]==0 and r('SmShotType',i)~=0 then
  local typ=r('SmShotType',i);assert(typ==current.q.native_type,'Actual owned beam type')
  markSpawn('native',typ,i,r('SmShotDir',i))
 end end end)
end)
hook('SamusWeapons',function()
 if not entered or phase~='run'or current.q.case~=1 or(current.t.kind~='free'and current.t.kind~='up')then return end
 local before={};for i=0,2 do before[i]={type=r('SmShotType',i),age=r('SmShotAge',i)}end
 onReturn('Samus-short-expiration',function()for i=0,2 do if before[i].type==1 and r('SmShotType',i)==0 then
  assert(before[i].age==11 and r('SmShotAge',i)==12,'Unblocked short beam expires at actual source age12')
  current.stage.shortExpiry=true;event('actual-short-age12-expiry',{slot=i,before=before[i].age,after=r('SmShotAge',i)})
 end end end)
end)
hook('RemainingWeapons::Spawn',function()
 if not entered or phase~='run'then return end
 local typ=r('AvType');local before={};for i=0,9 do before[i]=r('RgShotType',i)end
 onReturn('Samus-shared-spawn',function()for i=0,9 do if before[i]==0 and r('RgShotType',i)~=0 then
  assert(r('RgShotType',i)==typ and typ==(current.q.case==4 and 41 or 46),'Actual Samus missile/Ice owner')
  markSpawn('shared',typ,i,r('RgShotDir',i))
 end end end)
end)
hook('InventorySpend',function()
 if not entered or phase~='run'then return end
 local st=emu.getState();local item,cost,before=st['cpu.a'],st['cpu.y'],r('InvAmmo',34)
 assert(item==2 and cost==1,'Samus missile is the only paid gallery item')
 onReturn('Samus-real-debit',function()
  local after=r('InvAmmo',34);local free=r('StarInvincibleTimer')~=0;assert(not free,'No star or infinite-resource exception seeded')
  local paid=before>=cost;assert(after==(paid and before-cost or before),'Native debit/refusal has exact source arithmetic')
  local row={before=before,cost=cost,after=after,accepted=paid,wall=wall,update=updates};current.stage.debits[#current.stage.debits+1]=row
  if paid and after==0 then current.stage.sourceZeroWitness=row end
  event('actual-missile-debit',row);capture('missile-debit-'..wall)
 end)
end)
hook('InventorySelectionCommit',function()
 if not entered or phase~='run'or current.t.kind~='missile-select'then return end
 local st=emu.getState();assert(st['cpu.x']==2,'Actual Samus selection slot');local wanted=st['cpu.a']
 onReturn('Samus-controller-selection',function()assert(r('InvSelected',2)==wanted,'Actual selection commit');current.stage.selected=wanted;event('actual-paused-selection',{wanted=wanted,paused=r('GamePauseStatus')&1})end)
end)
hook('SamusWeapons::DropBomb',function()
 if not entered or phase~='run'then return end
 local before=bombs();current.stage.bombAttempts=current.stage.bombAttempts+1
 onReturn('Samus-bomb-attempt',function()
  local after=bombs();assert(after==math.min(3,before+1),'Three independent native bomb slots')
  if before==3 then current.stage.bombRefusals=current.stage.bombRefusals+1 else markSpawn('bomb',10,3-before,current.t.face)end
 end)
end)
hook('SamusWeapons::BombBoost',function()
 if not entered or phase~='run'then return end
 local i=emu.getState()['cpu.x'];local before=r('SmBombBoosted',i)
 onReturn('Samus-bomb-boost',function()if before==0 and r('SmBombBoosted',i)~=0 then assert(r('Player_State')~=0 and r('SmSourceJumped')==1,'Native modern bomb boost launches source airborne state');current.stage.boosts=current.stage.boosts+1;event('actual-bomb-boost',stateRow());capture('bomb-boost-'..wall)end end)
end)
hook('SamusWeapons::Move',function()
 if not entered or phase~='run'or current.t.kind~='wave-up'then return end
 local i=emu.getState()['cpu.x'];local oldPage=r('SmShotPage',i);local center=r('SmShotCenter',i);local a=r('SmShotAge',i);local pol=r('SmShotPolarity',i)
 onReturn('Samus-upward-Wave',function()
  if r('SmShotType',i)==3 then
   local off=C.wave[a];if off>=128 then off=off-256 end;if pol==0 then off=-off end
   local expected=current.t.center+off;assert(center==current.t.center%256 and r('SmShotX',i)+256*r('SmShotPage',i)==expected,'Actual upward Wave keeps complete world page')
   current.stage.waveMoves=(current.stage.waveMoves or 0)+1
   if oldPage~=r('SmShotPage',i)then current.stage.pageCrossings=(current.stage.pageCrossings or 0)+1;event('actual-wave-page-cross',{expected=expected,oldPage=oldPage,page=r('SmShotPage',i),age=a});capture('Wave-page-'..wall)end
  end
 end)
end)
hook('MegaManWeapons::Blocks',function()if entered and phase=='run'then current.stage.blockCalls=current.stage.blockCalls+1 end end)
hook('MegaManWeapons::DamageEnemy',function()
 if not entered or phase~='run'or emu.getState()['cpu.x']~=0 then return end
 local typ=r('MmBulletType');local before={state=r('Enemy_State'),flag=r('Enemy_Flag'),hp=r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')}
 current.stage.damageCalls=current.stage.damageCalls+1
 onReturn('Samus-native-damage',function()
  local after={state=r('Enemy_State'),flag=r('Enemy_Flag'),hp=r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')}
  if before.state~=after.state or before.flag~=after.flag or before.hp~=after.hp then current.stage.hits=current.stage.hits+1;event('actual-Samus-contact',{type=typ,before=before,after=after});capture('contact-'..wall)end
 end)
end)
hook('SamusHardEnemyAdmission',function()
 if not entered or phase~='run'or emu.getState()['cpu.x']~=0 then return end
 local f=r('AvFrozen')+256*r('AvFrozenHi');local hp=r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi');local typ=r('MmBulletType')
 onReturn('Samus-real-freeze',function()
  local after=r('AvFrozen')+256*r('AvFrozenHi');local s=current.stage
  if f==0 and after~=0 then assert(typ==73 and after==360 and r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')==hp,'Ice first accepted freeze is360 without HP damage');s.freezes=s.freezes+1;s.freezeAge=age;s.freezeWall=wall;s.freezePosition={x=r('Enemy_X_Position'),page=r('Enemy_PageLoc'),y=r('Enemy_Y_Position')};event('actual-Ice-freeze',{beforeHP=hp,afterHP=hp,ticks=after,position=s.freezePosition});capture('Ice-freeze-'..wall)
  elseif f~=0 and after==0 then s.breaks=(s.breaks or 0)+1;event('actual-Ice-break',{previous_ticks=f,type=typ});capture('Ice-break-'..wall)end
 end)
end)
hook('SamusFrozenDecrement',function()
 if not entered or phase~='run'or emu.getState()['cpu.x']~=0 then return end
 local before=r('AvFrozen')+256*r('AvFrozenHi')
 onReturn('Samus-real-thaw-clock',function()
  local after=r('AvFrozen')+256*r('AvFrozenHi');assert(before>0 and after==before-1,'Every actual freeze update decrements exactly one')
  current.stage.freezeSteps=current.stage.freezeSteps+1
  if after==0 then current.stage.thaws=current.stage.thaws+1;assert(r('RgEnemyStun')==0 and r('LsrFrozenPose')==0,'Source freeze releases STOP/pose');event('actual-Ice-thaw',{steps=current.stage.freezeSteps});capture('Ice-thaw-'..wall)end
 end)
end)
hook('GuestBodyContact',function()
 if not entered or phase~='run'or current.t.kind~='screw'or emu.getState()['cpu.x']~=0 then return end
 local spin=r('SmFlip')~=0 and r('Player_State')~=0
 onReturn('Samus-real-body',function()local st=emu.getState();local p=st['cpu.ps']or st['cpu.p'];if p and p&1~=0 then assert(spin,'Screw protection requires native airborne spin');current.stage.bodyProtects=current.stage.bodyProtects+1 end end)
end)
hook('FirebarCollision',function()if entered and phase=='run'and(current.t.kind=='firebar'or current.t.kind=='firebar-no-varia')then current.stage.firebarCalls=current.stage.firebarCalls+1 end end)
hook('GuestInjuryStart',function()
 if not entered or phase~='run'then return end
 assert(current.t.kind=='ordinary-hurt'or current.t.kind=='firebar-no-varia','No unrelated injury in isolated ability arena')
 current.stage.injuries=current.stage.injuries+1;event('actual-intended-injury',stateRow());capture('intended-injury-'..wall)
end)
emu.addMemoryCallback(function(_,v)
 if entered and phase=='run'and not writeBoundary and v~=0 then current.stage.sourceSfx[#current.stage.sourceSfx+1]={kind='SmSfx',value=v,wall=wall,pc=emu.getState()['cpu.pc']}end
end,emu.callbackType.write,L.SmSfx)
emu.addMemoryCallback(function(_,v)
 if entered and phase=='run'and not writeBoundary and v~=0 then current.stage.sourceSfx[#current.stage.sourceSfx+1]={kind='AvAudioRequest',value=v,wall=wall,pc=emu.getState()['cpu.pc']}end
end,emu.callbackType.write,L.AvAudioRequest)
emu.addMemoryCallback(function(_,v)
 if entered and phase=='run'and not writeBoundary and v~=0 then current.stage.sourceSfx[#current.stage.sourceSfx+1]={kind='Square1SoundQueue',value=v,wall=wall,pc=emu.getState()['cpu.pc']}end
end,emu.callbackType.write,L.Square1SoundQueue)
-- Source art admission is separate from the later physical PPU pixel review.
hook('DrawAllMetasprites',function()bodyPrepared=nil end)
hook('DrawMetasprite',function()
 if not entered or emu.getState()['cpu.y']~=0 then return end
 drawContext={kind='body'};onReturn('Samus-body-art-scope',function()drawContext=nil end)
end)
hook('SamusDrawShots::Draw',function()
 if not entered or phase~='run'then return end
 local y=emu.getState()['cpu.y'];local k=y-C.native_effect_base+1
 drawContext={kind='native',expected=assert(C.native_effect_records[k]),face=r('SmShotDir',r('SmSlot')),explosion=y>=C.native_bomb_base+2}
 onReturn('Samus-native-art-scope',function()drawContext=nil end)
end)
hook('RemainingDraw::ArtPointer',function()
 if not entered or phase~='run'then return end
 local art=emu.getState()['cpu.a'];local dir=r('AvDrawDirection');local expected=C.shared_effect_records[art+1]
 onReturn('Samus-shared-art-scope',function()
  local st=emu.getState();local p=st['cpu.ps']or st['cpu.p'];if p and p&1~=0 then drawContext={kind='shared',expected=assert(expected),face=dir}end
 end)
end)
hook('MetaspriteRenderLoop',function()
 if not entered or not drawContext then return end
 local ptr=r('R0')+256*r('R1');local cb=bank(0xc000);local expected
 if drawContext.kind=='body'then
  expected=C.body_records[tostring(cb)..':'..tostring(ptr)];assert(expected,'Actual selected body pointer is a bound Samus record')
  assert(r('CurrentCHRBank')==r('SmChrBank'),'Body logical page is its current source page')
  bodyPrepared={logical=r('SmChrBank'),physical=C.legacy_chr[r('SmChrBank')+1],pose=r('SmPose'),pointer=ptr,bank=cb,update=updates}
  if phase=='run'and current and current.stage then
   if bodyPrepared.pose>=C.ball_pose_low and bodyPrepared.pose<=C.ball_pose_low+3 then current.stage.ballDraw=true end
   if bodyPrepared.pose>=C.flip_pose_low and bodyPrepared.pose<=C.flip_pose_low+3 then current.stage.flipDraw=true end
  end
 else expected=drawContext.expected[drawContext.face==2 and 2 or 1]end
 assert(expected and expected.bank==cb and expected.address==ptr,'Exact real body/effect source pointer and C-bank')
 for i,v in ipairs(expected.bytes)do assert(emu.read(cb*8192+ptr%8192+i-1,emu.memType.nesPrgRom)==v,'Actual immutable Samus source record bytes')end
 if phase=='run'and current and current.stage then
  local key=drawContext.kind..':'..tostring(ptr);current.stage.draws[key]=(current.stage.draws[key]or 0)+1
  if drawContext.explosion then current.stage.explosionDraw=true end
  if current.stage.draws[key]==1 then event('actual-Samus-art',{kind=drawContext.kind,pointer=ptr,bank=cb,bytes=expected.bytes});capture('art-'..current.q.case..'-'..taskIndex..'-'..key:gsub(':','-'))end
 end
 onReturn('Samus-record-draw-completed',function()drawContext=nil end)
end)
hook('RosterOamReady',function()if entered and bodyPrepared then bodyPublished=bodyPrepared end end)
emu.addMemoryCallback(function(_,page)
 bodyDma=nil;if entered and bodyPublished and bytes(page*256,emu.memType.nesDebug)==published then bodyDma=bodyPublished end
end,emu.callbackType.write,0x4014)
emu.addMemoryCallback(function()if entered then bodyDisplayed=bodyDma end end,emu.callbackType.exec,C.dma_protocol.complete_pc)
emu.addEventCallback(function()
 if entered and bodyDisplayed then assert(emu.getState()['mapper.chrBanks0']==bodyDisplayed.physical,'Actual committed Samus legacy body CHR matches its completed DMA epoch')end
end,emu.eventType.startFrame)
hook('GameLoop',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 or r('GameEngineSubroutine')~=8 then return end
 if not entered then assert(r('SelectedCharacter')==2 and r('CrossoverBehaviorVersion')==1,'Cold selected Samus numeric Hard1');entered=true;beginPhase('next')end
 updates=updates+1;age=age+1
 assert(r('SelectedCharacter')==2 and r('CrossoverBehaviorVersion')==1,'Actual Samus/Hard owner remains')
 if phase=='next'then
  if index>#C.cases then done=true;return end
  current={q=C.cases[index],stages={},started=wall};records[#records+1]=current;current.t=current.q.tasks[taskIndex];beginPhase('setup')
 end
 if phase=='setup'then assert(age<150,'Prior actual VRAM queue clears before complete next fixture');setupTask()
 elseif phase=='run'then
  liveTarget()
  -- Retire the single controlled hazard after native injury admission; never
  -- reset the real player injury/owned/HP outcome or its recovery clock.
  if current.stage.injuries>0 and not current.stage.hazardRetired then writeBoundary=true;w('Enemy_Flag',0);writeBoundary=false;current.stage.hazardRetired=wall;event('controlled-single-contact-hazard-retired',{})end
 end
end)
local function samusInput()
 if not current or phase~='run'then return{}end
 local t=current.t;local b={}
 if t.kind=='morph-deny'or t.kind=='bombs'then
  b.down=(age>=5 and age<9)or(age>=15 and age<19)
  if t.kind=='bombs'then b.b=(age>=30 and age<33)or(age>=40 and age<43)or(age>=50 and age<53)or(age>=60 and age<63);b.up=age>=145 and age<150 end
 elseif t.kind=='missile-select'then b.start=(age>=5 and age<9)or(age>=65 and age<69);b.right=age>=20 and age<24
 elseif t.kind=='missile-paid'then b.select=(age>=5 and age<8)or(age>=45 and age<48)
 elseif t.kind=='missile-empty'or t.kind=='missile-pool'then b.select=age>=5 and age<8
 elseif t.kind=='screw'then b.a=age>=5 and age<14;if age>=5 and age<9 then b[t.face==1 and'right'or'left']=true end
 elseif t.kind~='firebar'and t.kind~='ordinary-hurt'and t.kind~='firebar-no-varia'then
  b.b=age>=5 and age<8
  if t.kind=='ice-break'and current.stage.freezeAge and age>=current.stage.freezeAge+25 and age<current.stage.freezeAge+28 then b.b=true end
  if t.kind=='wave-up'or t.kind=='up'then b.up=age>=4 and age<9 end
 end
 return b
end
hook('finish',function()
 if not entered or done or not current or phase~='run'then return end
 local t,s=current.t,current.stage
 assert(r('MmDeathFlag')==0,'Controlled ability arena survives')
 if t.kind~='ordinary-hurt'and t.kind~='firebar-no-varia'then assert(r('GuestHurtTicks')==0,'No unrelated hurt during isolated ability')end
 if t.kind=='missile-select'then
  if age>=85 then assert(s.selected==2 and r('InvSelected',2)==2 and r('GamePauseStatus')&1==0,'Actual pause/right selection/unpause completes')
   for i,v in ipairs(C.missile_hud_name)do assert(emu.read(0x2023+i-1,emu.memType.nesPpuDebug)==v,'Actual committed MISSILE name')end
   capture('missile-selected-HUD');afterTask()
  end
 elseif t.kind=='morph-deny'then if age>=25 then assert(r('SmBall')==0 and r('SmCrouch')==1,'Without Morph fresh second Down remains crouch');afterTask()end
 elseif t.kind=='bombs'then
  if age==20 then assert(r('SmBall')==1 and r('SmCrouch')==0,'Actual two fresh Down edges enter Morph');capture('Morph-ball')end
  if age>=170 and bombs()==0 and r('SmBall')==0 and r('Player_State')==0 then assert(s.bombAttempts==4 and s.bombRefusals==1 and s.boosts>0 and s.hits>0,'Three bombs, pool refusal, source boost and actual explosion contact');assert(s.ballDraw and s.explosionDraw,'Actual bound Morph and explosion source art was emitted');assert(sourceCue('SmSfx',2,true)and sourceCue('SmSfx',4,true)and sourceCue('SmSfx',8,true),'Actual Morph/set-bomb/explosion sound requests');afterTask()end
 elseif t.kind=='ice-thaw'then
  if s.freezePosition and r('AvFrozen')+256*r('AvFrozenHi')>0 then assert(r('Enemy_X_Position')==s.freezePosition.x and r('Enemy_PageLoc')==s.freezePosition.page and r('Enemy_Y_Position')==s.freezePosition.y,'Actual frozen enemy AI position remains stopped')end
  if s.freezeAge and(age-s.freezeAge==90 or age-s.freezeAge==350)then assert(r('AvFrozen')+256*r('AvFrozenHi')>0 and r('RgEnemyStun')>0,'Real freeze STOP remains until source timer');capture('Ice-held-'..age)end
  if s.thaws==1 and effects()==0 then assert(s.freezes==1 and s.freezeSteps==360,'Actual360 committed freeze decrements and one natural thaw');assert(sourceCue('Square1SoundQueue',C.beam_sfx,true),'Actual Ice shoot sound request');afterTask()end
 elseif t.kind=='ice-break'then if s.breaks and s.breaks>0 and effects()==0 then assert(s.freezes==1 and s.damageCalls>0 and s.hits>0,'Second actual Ice contact removes freeze then reaches damage');assert(sourceCue('Square1SoundQueue',C.beam_sfx,true),'Actual second Ice shoot sound request');afterTask()end
 elseif t.kind=='firebar'then if age>=45 then assert(s.firebarCalls>10 and s.injuries==0 and r('PlayerStatus')==1 and r('InvOwnedLo',2)==161,'Varia protects actual native firebar contacts');assert(r('SmChrBank')==C.varia_stand_chr,'Current Varia third-form source art');afterTask()end
 elseif t.kind=='ordinary-hurt'or t.kind=='firebar-no-varia'then
  if s.injuries>0 and age>=90 and r('GuestHurtTicks')==0 then assert(r('PlayerStatus')==0 and r('InvOwnedLo',2)==0,'Real isolated injury drains owned form and naturally recovers');afterTask()end
 elseif t.kind=='screw'then if age>=90 and r('Player_State')==0 then assert(s.hits==1 and s.damageCalls==1 and s.bodyProtects>0 and s.flipDraw and r('SmFlip')==0 and r('AvScrewSound')==0,'One actual spin body attack/art then landing releases source spin/sound latch');assert(sourceCue('AvAudioRequest',C.screw_sfx,false),'Actual native Screw SFX request');afterTask()end
 elseif t.kind=='pool'or t.kind=='missile-pool'then
  if age>=12 then assert(#s.spawns==0 and #s.debits==0,'Actual shared three-slot pool refuses without cost');afterTask()end
 elseif t.kind=='missile-empty'then if age>=30 then assert(r('InvAmmo',34)==0 and #s.spawns==0,'Actual zero-stock missile refusal');afterTask()end
 elseif t.kind=='missile-paid'then
  if age>=115 and effects()==0 then assert(#s.debits==2 and s.sourceZeroWitness and #s.spawns==2 and s.hits>0,'Exact two paid missiles exhaust via source0 witness and contact');assert(sourceCue('AvAudioRequest',C.missile_sfx,false),'Actual typed missile SFX request');afterTask()end
 else
  if t.kind=='free'and age==15 and current.q.native_type==2 then assert(samusPool()>0,'Long survives the short lifetime');capture('Long-beyond-short-range')end
  if t.kind=='wave-up'and age>=90 and effects()==0 then assert((s.waveMoves or 0)>2 and(s.pageCrossings or 0)>0 and s.blockCalls==0,'Wave page crossing and source terrain bypass');afterTask()
  elseif t.kind~='wave-up'and age>=90 and effects()==0 then
   assert(#s.spawns>0,'Real B creates intended source effect')
   if current.q.case==1 and(t.kind=='free'or t.kind=='up')then assert(s.shortExpiry,'Actual source age12 expiration was observed')end
   if t.kind=='contact'or t.kind=='wave-contact'then assert(s.hits>0,'Real emitted effect hits intended target')end
   if t.kind=='block'then assert(s.blockCalls>0,'Normal/Long retains actual terrain query')end
   if t.kind=='wave-block'then assert(s.blockCalls==0,'Wave never invokes normal terrain collision')end
   local seen=false;for k in pairs(s.draws)do if not k:find('body',1,true)then seen=true end end;assert(seen,'Effect reaches actual bound source renderer')
   assert(sourceCue('Square1SoundQueue',C.beam_sfx,true),'Actual source beam sound queue write')
   afterTask()
  end
 end
 assert(age<700,'Finite source-specific Samus subphase '..t.kind)
end)
