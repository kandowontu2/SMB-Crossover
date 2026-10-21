-- Seed only initial map/character/equipment. Actual controller B creates each
-- weapon. Read actual legacy/advanced draw pointers; never alter OAM or CHR.
local C=assert(LASER_RENDER);local A,H=C.ram,C.hooks
local frame,index,age,phase=0,0,0,'boot'
local current,stats=nil,nil
local pending=nil
local events=assert(io.open(C.out..'events.jsonl','w'))
local function r(n,i)return emu.read(assert(A[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(A[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
local function json(t)local b={};for k,v in pairs(t)do b[#b+1]=string.format('%q',tostring(k))..':'..(type(v)=='string'and string.format('%q',v)or tostring(v))end;table.sort(b);return'{'..table.concat(b,',')..'}'end
local function log(t)events:write(json(t)..'\n');events:flush()end
local function hook(n,fn)
 local h=assert(H[n],n)
 emu.addMemoryCallback(function()
  local p=emu.convertAddress(h.address)
  if not p or p.memType~=emu.memType.nesPrgRom or p.address//8192~=h.physical_bank then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Actual physical draw hook '..n)end
  if current then fn()end
 end,emu.callbackType.exec,h.address)
end
hook('LegacyPointer',function()
 local slot=r('RgSlot');local typ=r('RgShotType',slot)
 stats.legacy=stats.legacy+1
 if typ>=32 then
  stats.foreign=stats.foreign+1
  log({event='foreign-legacy-pointer',case=index,frame=frame,slot=slot,type=typ,pointer=r('R0')+256*emu.getState()['cpu.a']})
 end
end)
hook('AdvancedArt',function()
 if r('AvDrawIndex')>=10 then return end
 local slot=r('AvSlot');local typ=r('RgShotType',slot)
 if typ==42 or typ==43 then
  local art=emu.getState()['cpu.a'];assert(art==(typ==42 and 2 or 1),'Laser/Flare always select their own actual source art')
  stats.advanced=stats.advanced+1
  if typ==42 then stats.laser=stats.laser+1 end
  pending={typ=typ,slot=slot,direction=r('AvDrawDirection')}
 end
end)
hook('AdvancedNext',function()pending=nil end)
hook('ActualRender',function()
 if not pending then return end
 local name=(pending.typ==42 and'laser'or'flare')..(pending.direction==2 and'Left'or'Right')
 local expected=assert(C.art[name]);local ptr=r('R0')+256*r('R1')
 assert(ptr==expected.address,'Actual emitted advanced metadata always owns its laser/flare graphic')
 local mapped=emu.convertAddress(ptr)
 assert(mapped and mapped.memType==emu.memType.nesPrgRom and mapped.address//8192==expected.physical_bank,'Actual source-art data bank')
 for i,v in ipairs(expected.bytes)do assert(emu.read(ptr+i-1,emu.memType.nesDebug)==v,'Actual emitted source-art bytes')end
 stats.emitted=stats.emitted+1
end)
local function setup(c)
 current=c;age=0;pending=nil;stats={foreign=0,legacy=0,advanced=0,laser=0,live=0,shots=0,visible=0,emitted=0}
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('InvPickup',0xfc,i);w('InvPickupOwner',0xff,i)end
 for i=0,9 do for _,n in ipairs({'RgShotType','RgShotAge','RgShotImpact','RgShotFracX','RgShotFracY','RgShotHits','RgShotHitsNow','SsHidden','SsMode','SsAngleLo','SsAngleHi'})do w(n,0,i)end end
 for i=0,3 do w('InvDropKind',0,i);w('MmBulletType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 for _,n in ipairs({'TimerControl','InjuryTimer','StarInvincibleTimer','MmDeathFlag','GuestPowerupActive','GuestHurtKind','GuestHurtTicks','GuestInvulTicks','DisableCollisionDet','RgCooldown','RgShootPose','RgAttack','RgBillCadence','RgBillBurst','RgBillBurstDelay','RgPreviousButtons','RgWeaponButtons','PreviousA_B_Buttons','A_B_Buttons','SavedJoypadBits','InvRefill','Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','MmLastXSpeed','MmFrictionYActive','RgCrouch','ScrollAmount','AreaParserTaskNum','ScrollThirtyTwo','EnemyFrenzyBuffer','EnemyFrenzyQueue'})do w(n,0)end
 w('SelectedCharacter',3);w('BillVariant',c.variant);w('CrossoverBehaviorVersion',1);w('PlayerStatus',1);w('PlayerSize',0)
 w('InvOwnedLo',1+(c.weapon==0 and 0 or(1<<c.weapon)),3);w('InvOwnedHi',0,3);w('InvSelected',c.weapon,3);w('InvDirty',1)
 w('Player_X_Position',128);w('Player_PageLoc',0);w('Player_Y_Position',c.pose=='air'and 96 or 176);w('Player_Y_HighPos',1);w('Player_State',c.pose=='air'and 2 or 0);w('PlayerFacingDir',c.facing);w('Player_CollisionBits',3)
 w('GameEngineSubroutine',8);w('SwimmingFlag',0);w('AreaType',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0);w('ScrollLock',1)
 phase='observe';log({event='seed',case=index,variant=c.variant,weapon=c.weapon,pose=c.pose,facing=c.facing})
end
emu.addEventCallback(function()
 local b={start=frame==60 or frame==240}
 if current then
  b.b=age%12>=3 and age%12<8
  if current.pose=='prone'then b.down=true elseif current.pose=='air'then b.up=true;b[current.facing==1 and'right'or'left']=true end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
local failures=0
emu.addEventCallback(function()
 frame=frame+1;if frame<600 then return end
 if phase=='boot'or phase=='next'then
  index=index+1
  if not C.cases[index]then
   events:close();local f=assert(io.open(C.out..'result.json','w'));f:write(json({status=failures==0 and'PASS_SINGLE_WEAPON_RENDERER'or'REPRO_FOREIGN_LEGACY_RENDER',cases=index-1,foreign_cases=failures,frames=frame,route_proof=false}));f:close()
   print('RENDER COMPLETE '..(index-1)..' cases foreign='..failures);emu.stop(failures==0 and 0 or 1);return
  end
  assert(r('OperMode')==1 and r('OperMode_Task')==3,'Actual ordinary boot reaches gameplay');setup(C.cases[index]);return
 end
 age=age+1
 for i=0,9 do if r('RgShotType',i)~=0 then stats.live=stats.live+1 end end
 if age==28 and current.weapon==2 and current.pose=='stand'and current.facing==1 then
  local f=assert(io.open(C.out..'laser-v'..current.variant..'.png','wb'));f:write(emu.takeScreenshot());f:close()
 end
 if current.weapon==2 and current.pose=='stand'and current.facing==1 and current.variant==0 and age>=10 and age<=38 and age%4==2 then
  local f=assert(io.open(C.out..'laser-age'..age..'.png','wb'));f:write(emu.takeScreenshot());f:close()
 end
 if age>=48 then
  assert(stats.live>0,'Real controller-created projectiles')
  if current.weapon==2 or current.weapon==3 then assert(stats.advanced>0 and stats.emitted>0,'Actual advanced renderer emitted source art')
  else assert(stats.legacy>0,'Native ordinary weapon rendering retained')end
  if stats.foreign>0 then failures=failures+1 end
  stats.event='case';stats.case=index;stats.weapon=current.weapon;stats.variant=current.variant;stats.pose=current.pose;stats.facing=current.facing;log(stats)
  current=nil;phase='next'
 end
end,emu.eventType.endFrame)
