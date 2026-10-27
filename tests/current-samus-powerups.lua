-- Current8487 Hard Samus mature-item components; not block emergence/RNG.
-- No owned flags, tier, selected weapon, ammo, forms or projectile outcomes seeded.
local C=assert(CURRENT_SAMUS_POWERUPS)
local wall,updates,age,index,caseIndex=0,0,0,0,0
local entered,done,writing=false,false,false
local phase,menuPhase='menu','options-focus'
local rec,records=nil,{}
local nmi,irq=nil,false
local minSP,dmas,enables,late,irqCount,nmis,images=255,0,0,0,0,0,0
local mask,pending=0,nil
local upper,physical,chrChecks=0,{},0
local screenshot,spend=nil,nil
local refill,dropCall,awaitDropClear=nil,nil,nil
local drops,samples={},{}
local ctrl=0
local csv=assert(io.open(OUTPUT..'samus-inventory.csv','w'))
csv:write('event,wall,update,item,phase,age,ownedLo,ownedHi,selected,missiles,status,shots,ball,crouch,flip,x,y,value,pc,bank,cycle\n')
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(at)local p=emu.convertAddress(at);return p and p.address//8192 or-1 end
local function stock()return r('InvAmmo',34)end
local function has(i)return((r('InvOwnedLo',2)+256*r('InvOwnedHi',2))&(1<<i))~=0 end
local function pool()local n=0;for i=0,9 do if r('RgShotType',i)~=0 then n=n+1 end end;for i=0,2 do if r('SmShotType',i)~=0 then n=n+1 end;if r('SmBombAge',i)~=0 then n=n+1 end end;return n end
local function event(kind,value)
 local s=emu.getState();csv:write(table.concat({kind,wall,updates,index,phase,age,r('InvOwnedLo',2),r('InvOwnedHi',2),r('InvSelected',2),stock(),r('PlayerStatus'),pool(),r('SmBall'),r('SmCrouch'),r('SmFlip'),r('Player_X_Position'),r('Player_Y_Position'),value or 0,s['cpu.pc'],bank(s['cpu.pc']),s['cpu.cycleCount']},',')..'\n')
end
local function json(v)
 if type(v)=='table'then local out={};if #v>0 then for _,x in ipairs(v)do out[#out+1]=json(x)end;return'['..table.concat(out,',')..']'end;for k,x in pairs(v)do out[#out+1]=string.format('%q',tostring(k))..':'..json(x)end;table.sort(out);return'{'..table.concat(out,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local function hook(name,fn)
 local h=assert(C.hooks[name],name)
 emu.addMemoryCallback(function()
  local actual=bank(h.pc);local allowed=false;for _,b in ipairs(h.banks)do if actual==b then allowed=true end end;if not allowed then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Actual hook '..name)end;fn(emu.getState())
 end,emu.callbackType.exec,h.pc)
end
local forbidden={InvOwnedLo=true,InvOwnedHi=true,InvSelected=true,InvAmmo=true,PlayerStatus=true,GuestPowerupActive=true,GameEngineSubroutine=true,InjuryTimer=true,GuestHurtTicks=true,MmDeathFlag=true,RgShotType=true,SmShotType=true,SmBombAge=true,SmBall=true,SmCrouch=true,SmFlip=true,CheatInvincible=true}
local function w(n,v,i)
 assert(writing and not nmi and not irq and r('NmiDisable')==255,'Setup only actual owned GameLoop, no active interrupt')
 assert(not forbidden[n]and C.setup_allowed[n],'No tested ownership/resource/form/outcome seeds: '..n);emu.write(assert(C.ram[n],n)+(i or 0),v&255,emu.memType.nesDebug)
end
local function transaction(fn)
 assert(not writing and not nmi and not irq and r('NmiDisable')==255,'Synchronous private-frame setup');writing=true;fn();writing=false;event('disclosed-setup')
end
local function tile(page,col,row,id)
 assert(writing and not nmi and not irq,'Same owned map staging boundary')
 local function source(n)local p=C.metatiles[n];return emu.read(p.bank*8192+p.offset+id,emu.memType.nesPrgRom)end
 local function put(a,v)emu.write(a,v,emu.memType.nesPpuDebug)end
 local at=0x2000+page*1024+row*64+col*2
 put(at,source('MTileTopLeft'));put(at+1,source('MTileTopRight'));put(at+32,source('MTileBotLeft'));put(at+33,source('MTileBotRight'))
 local a=0x23c0+page*1024+(row//2)*8+col//2;local shift=row%2*4+col%2*2
 put(a,(emu.read(a,emu.memType.nesPpuDebug)&(~(3<<shift)))|((source('MTileAttribute')>>6)<<shift))
end
local function arena()
 assert(pool()==0 and r('SmBall')==0,'Real previous projectile/bomb/form completion')
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do for row=2,14 do for col=0,15 do tile(p,col,row,row>=13 and 0x54 or 0)end end end
 for p=0,1 do for row=11,12 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+row*16+col)end end end
 -- Subsequent staged scenes remove old target/drop/freeze actors; no expiry or natural drop claim.
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_CollisionBits',0,i);w('AvFrozen',0,i);w('AvFrozenHi',0,i);w('RgEnemyStun',0,i);w('LsrFrozenPose',0,i)end
 assert(not refill and not dropCall and not awaitDropClear,'No native pickup/refill call is discarded by staged scene reset')
 for i=0,3 do
  if drops[i]then drops[i].staged_removal_update=updates;event('disclosed-uncollected-drop-removal',i)end
  w('InvDropKind',0,i)
  -- nesDebug setup writes bypass CPU memory callbacks. Invalidate only the
  -- observer's old provenance here, alongside its disclosed native-slot reset.
  drops[i]=nil
 end
 for _,n in ipairs({'Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','ScrollThirtyTwo','AreaParserTaskNum'})do w(n,0)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('ScrollLock',1);w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_X_Position',64);w('Player_PageLoc',0);w('MmOldX',64);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1);w('Player_MovingDir',1);w('Player_CollisionBits',255)
end
local function mature(i)
 w('Enemy_Flag',1,5);w('Enemy_ID',0x2e,5);w('Enemy_State',128,5);w('Enemy_BoundBoxCtrl',3,5)
 w('Enemy_X_Position',64,5);w('Enemy_PageLoc',0,5);w('Enemy_Y_Position',184,5);w('Enemy_Y_HighPos',1,5)
 w('Enemy_X_Speed',0,5);w('Enemy_Y_Speed',0,5);w('Enemy_SprAttrib',0,5)
 w('PowerUpType',i==0 and 0 or 1,5);w('InvPickupOwner',2,5);w('InvPickup',i,5);if i==254 then w('AvPickupAmmoItem',2,5)end
end
local function change(p)phase=p;age=0;event('phase')end
local function seedItem()
 caseIndex=caseIndex+1;index=assert(C.order[caseIndex]);local spec=C.items[index]
 if index~=0 and index~=7 and index~=254 then assert(not has(index),'Reward genuinely unowned before acquisition')end
 rec={item=index,collections=0,grants=0,transforms=0,spends=0,cost=0,earned_refill=0,refills={},native_drops={},damageCalls=0,hpWrites=0,spawns=0,target=false,source_types={},source_sfx={},missiles_before=stock(),owned_before=r('InvOwnedLo',2)};records[#records+1]=rec
 if index==7 then assert(has(7),'Mushroom authentically already granted Long; explicit mature reward is idempotent')end
 transaction(function()arena();mature(index)end);change('collect')
end
local function target(x,y)
 assert(x>=8 and x<240 and y>=32 and y<216,'Actual effect-aligned target is onscreen')
 transaction(function()
  for _,a in ipairs({{'Enemy_Flag',1},{'Enemy_ID',6},{'Enemy_State',0},{'Enemy_X_Position',x},{'Enemy_PageLoc',0},{'Enemy_Y_Position',y},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_Y_MoveForce',0},{'Enemy_MovingDir',1},{'Enemy_BoundBoxCtrl',9},{'EnemyOffscrBitsMasked',0},{'Enemy_CollisionBits',0},{'MmEnemyHealthLo',0},{'MmEnemyHealthHi',0},{'MmEnemyFlash',0},{'RgEnemyStun',0},{'AvFrozen',0},{'AvFrozenHi',0},{'LsrFrozenPose',0}})do w(a[1],a[2],0)end
 end);rec.target=true;rec.target_x=x;rec.target_y=y;event('controlled-live-effect-target')
end
local function controlledTarget()
 if rec.target or index==5 then return end
 if index==1 then for i=0,2 do if r('SmBombAge',i)>=58 then target(r('SmBombX',i)+12,r('SmBombY',i)-8);return end end
 elseif index==6 then if r('SmFlip')~=0 and r('Player_State')~=0 and r('Player_Y_Position')<160 then target(r('Player_X_Position')+6,r('Player_Y_Position')+8)end
 elseif index==2 or index==3 then
  for i=0,9 do if r('RgShotType',i)==C.items[index].rg_type and r('RgShotPage',i)==0 and r('RgShotX',i)>=112 and r('RgShotX',i)<232 then target(r('RgShotX',i)-6,r('RgShotY',i)-8);return end end
 elseif index==7 or index==4 then
  for i=0,2 do if r('SmShotType',i)==C.items[index].sm_type and r('SmShotPage',i)==0 and r('SmShotX',i)>=(index==4 and 176 or 112)and r('SmShotX',i)<232 then if index==4 then rec.wave_crossed_wall=true end;target(r('SmShotX',i)-6,r('SmShotY',i)-8);return end end
 end
end
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
 local i=r('CrossoverMenuIndex');if i//6~=C.slot//6 then return{down=true}end
 if i~=C.slot then return{right=true}end
 return{a=true}
end
hook('GameLoopOwned',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then
  if r('GameEngineSubroutine')~=8 then return end
  assert(r('SelectedCharacter')==2 and r('CrossoverBehaviorVersion')==1,'Cold actual Samus Hard1')
  assert(r('PlayerStatus')==0 and r('InvOwnedLo',2)==0 and r('InvOwnedHi',2)==0 and r('CheatInvincible')==0 and stock()==C.initial_missiles,'Unseeded native initial state')
  entered=true;change('settle')
 end
 updates=updates+1;age=age+1
 assert(r('SelectedCharacter')==2 and r('CrossoverBehaviorVersion')==1 and r('CheatInvincible')==0,'Owner/mode/default cheats remain genuine')
 if phase=='settle'and age==30 or phase=='next'then seedItem()
 elseif phase=='use-setup'then
  transaction(function()arena();if index==4 then for row=10,12 do tile(0,9,row,0x51);w('Block_Buffer_1',0x51,(row-2)*16+9)end end end);change('use')
 elseif phase=='use'then controlledTarget()end
end)
hook('PhysicalPickup',function(s)
 if entered and phase=='collect'then
  assert(s['cpu.x']==5 and r('Enemy_Flag',5)~=0 and r('Enemy_ID',5)==0x2e and r('Enemy_State',5)>=128 and r('InvPickupOwner',5)==2 and r('InvPickup',5)==index,'Real mature tested actor before erase')
  rec.collision_update=updates;event('actual-pre-erase-collision')
 end
end)
hook('InventoryCollect',function(s)
 if entered and phase=='collect'then
  assert(s['cpu.x']==5 and rec.collision_update==updates and r('Enemy_Flag',5)==0 and r('Enemy_State',5)==0 and r('InvPickupOwner',5)==2 and r('InvPickup',5)==index,'Actual collision -> erase -> tested collection')
  rec.collections=rec.collections+1;event('actual-collection-owner')
 end
end)
hook('InventoryGrant',function(s)if entered and phase=='collect'and index>0 and index<8 then assert(s['cpu.a']==index,'Exact grant item');rec.grants=rec.grants+1 end end)
hook('GuestPowerupUpdate',function()if entered and index==0 and phase=='collect'and r('GuestPowerupActive')~=0 then rec.transforms=rec.transforms+1 end end)
hook('InventorySpend',function(s)
 if not entered or phase~='use'then return end
 assert(index==2 and not spend and s['cpu.a']==2 and s['cpu.y']==C.missile_cost,'Only actual missile action spends one source ammo')
 spend={before=stock(),sp=s['cpu.sp']};event('actual-spend-entry')
end)
hook('InventorySpendDone',function(s)
 if not spend then return end;assert(s['cpu.sp']==spend.sp and stock()==spend.before-C.missile_cost,'Actual missile decrement in same call');rec.spends=rec.spends+1;rec.cost=rec.cost+C.missile_cost;spend=nil;event('actual-spend-accepted')
end)
-- Source provenance, not an allowance for unexplained ammo changes. Enemy
-- drops are produced by the native RNG, collide through its actual gates,
-- and must execute the source refill/store/return/clear sequence.
hook('EnemyDrop',function(s)
 if not entered or writing then return end
 assert(not dropCall and rec and phase=='use'and rec.target and s['cpu.x']==0,'Actual controlled enemy death owns native drop attempt')
 dropCall={enemy=s['cpu.x'],sp=s['cpu.sp'],update=updates}
end)
hook('DropPhysics',function(s)
 if not entered or writing then return end
 local d=assert(dropCall,'Native enemy drop origin');local i=s['cpu.x'];local kind=r('InvDropKind',i)
 event('native-drop-boundary',string.format('slot:%d;kind:%d;item:%d;enemy:%d;prior:%d',i,kind,r('AvDropItem',i),r('InvDropEnemy'),drops[i]and 1 or 0))
 assert(i>=0 and i<4 and not drops[i]and r('InvDropEnemy')==d.enemy and(kind==1 or kind==2)and r('AvDropItem',i)==2,'Actual new Samus missile drop slot/kind/item')
 local world=r('Enemy_X_Position',d.enemy)+256*r('Enemy_PageLoc',d.enemy)+8
 assert(r('InvDropX',i)+256*r('InvDropPage',i)==world and r('InvDropY',i)==(r('Enemy_Y_Position',d.enemy)+8)%256,'Native drop origin is actual defeated enemy center')
 drops[i]={slot=i,kind=kind,item=2,enemy=d.enemy,spawn_update=updates,x=r('InvDropX',i),page=r('InvDropPage',i),y=r('InvDropY',i)}
 rec.native_drops[#rec.native_drops+1]=drops[i];event('native-enemy-drop-spawn',kind)
end)
hook('EnemyDropReturn',function(s)
 if not entered or writing then return end
 assert(dropCall and s['cpu.sp']==dropCall.sp,'Native drop attempt restores stack');dropCall=nil
end)
hook('DropCollectAccepted',function(s)
 if not entered or writing then return end
 local i=s['cpu.x'];local d=assert(drops[i],'Accepted collision must have native spawn provenance')
 local dx=(r('Player_X_Position')+256*r('Player_PageLoc')+8-r('InvDropX',i)-256*r('InvDropPage',i)+11)%65536
 local dy=((r('Player_Y_Position')+16)%256-r('InvDropY',i)+18)%256
 assert(not refill and not awaitDropClear and r('Player_Y_HighPos')==1 and dx<23 and dy<37 and r('InvDropKind',i)==d.kind and r('AvDropItem',i)==2 and has(2),'Actual native world-drop collision geometry/ownership')
 refill={origin='enemy-drop',slot=i,kind=d.kind,item=2,request=d.kind==2 and 40 or 8,before=stock(),update=updates,dx=dx,dy=dy}
 d.collect_update=updates;event('native-drop-collision',i)
end)
hook('RefillPickup',function()
 if not entered then return end
 assert(not refill and phase=='collect'and index==254 and rec.collections==1 and r('AvRefillItem')==2,'Only physically collected mature FE actor owns refill pickup')
 refill={origin='typed-mature-FE',item=2,request=40,before=stock(),update=updates};event('actual-refill-pickup',40)
end)
hook('RefillAmount',function(s)
 if not entered then return end
 assert(refill and s['cpu.a']==refill.request and r('AvRefillItem')==2 and has(2),'Exact source refill request has earned pickup provenance');refill.amount_seen=true;event('actual-refill-amount',s['cpu.a'])
end)
hook('RemainingRefill',function(s)
 if not entered then return end
 assert(refill and refill.amount_seen and r('InvDropAmount')==refill.request and r('AvRefillItem')==2,'Actual Samus refill dispatch preserves request/item')
 refill.sp=s['cpu.sp'];event('actual-Samus-refill-entry',stock())
end)
emu.addMemoryCallback(function(_,v)
 if not entered or writing then return end
 if spend then assert(v==spend.before-C.missile_cost,'Only source missile debit is permitted');return end
 local f=assert(refill,'No unproven missile write is accepted');local s=emu.getState();local h=C.refill_store
 assert(bank(s['cpu.pc'])==h.bank and(s['cpu.pc']==h.pc or s['cpu.pc']==h.after)and s['cpu.x']==34 and f.sp and not f.write,'Actual native Samus refill owns ammo store')
 for i,b in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==b,'Actual refill store opcode')end
 f.expected=math.min(C.max_missiles,f.before+C.refill_amount);assert(v==f.expected,'Exact Samus earned +2 refill/cap, never a fabricated amount');f.write=true;event('native-earned-missile-store',v)
end,emu.callbackType.write,C.ram.InvAmmo+34)
hook('RemainingRefillDone',function(s)
 if not entered then return end
 local f=assert(refill,'Native refill return has pickup provenance')
 assert(f.write and s['cpu.sp']==f.sp and stock()==f.expected,'Same real refill call completed exact source store/cap')
 f.after=stock();f.delta=f.after-f.before;rec.earned_refill=rec.earned_refill+f.delta;rec.refills[#rec.refills+1]=f
 if f.origin=='enemy-drop'then awaitDropClear={slot=f.slot,update=updates}end
 refill=nil;event('native-earned-refill-complete',f.delta)
end)
emu.addMemoryCallback(function(a,v)
 local i=a-C.ram.InvDropKind
 if writing then if v==0 then drops[i]=nil end;return end
 if not entered or v~=0 or not drops[i]then return end
 if awaitDropClear and awaitDropClear.slot==i then
  local s=emu.getState();local h=C.drop_clear_store
  assert(updates==awaitDropClear.update and bank(s['cpu.pc'])==h.bank and(s['cpu.pc']==h.pc or s['cpu.pc']==h.after),'Actual collected drop cleared by same native caller')
  drops[i].cleared_update=updates;awaitDropClear=nil;event('native-collected-drop-cleared',i)
 else drops[i].expired_update=updates;event('native-uncollected-drop-removed',i)end
 drops[i]=nil
end,emu.callbackType.write,C.ram.InvDropKind,C.ram.InvDropKind+3)
emu.addMemoryCallback(function(_,v)ctrl=v end,emu.callbackType.write,0x2000)
hook('DamageEnemy',function(s)
 if entered and phase=='use'and rec.target and s['cpu.x']==0 then assert(r('MmBulletType')==C.items[index].damage_type,'Source intended weapon/body owns actual target contact');rec.damageCalls=rec.damageCalls+1;event('actual-contact-owner',r('MmBulletType'))end
end)
hook('RemainingPowerDone',function(s)if entered and phase=='use'and index==5 then assert(s['cpu.a']==2,'Earned Varia actual visual tier2');rec.varia_power=true end end)
emu.addMemoryCallback(function(_,v)if entered and phase=='use'and rec.target and rec.damageCalls>0 and not writing then rec.hpWrites=rec.hpWrites+1;event('native-enemy-hp-write',v)end end,emu.callbackType.write,C.ram.MmEnemyHealthLo,C.ram.MmEnemyHealthHi)
local function allocated(kind,slot,value)
 rec.spawns=rec.spawns+1;rec.source_types[kind..value]=true
 if rec.allocation_dma==nil then rec.allocation_dma=dmas;rec.allocation_wall=wall;rec.allocation_slot=slot end;event('native-'..kind..'-allocation',value)
end
emu.addMemoryCallback(function(a,v)if entered and phase=='use'and not writing and v~=0 then assert(v==C.items[index].rg_type,'Actual intended advanced pool type');allocated('rg',a-C.ram.RgShotType,v)end end,emu.callbackType.write,C.ram.RgShotType,C.ram.RgShotType+9)
emu.addMemoryCallback(function(a,v)if entered and phase=='use'and not writing and v~=0 then assert(v==C.items[index].sm_type,'Actual intended primary pool type');allocated('sm',a-C.ram.SmShotType,v)end end,emu.callbackType.write,C.ram.SmShotType,C.ram.SmShotType+2)
emu.addMemoryCallback(function(a,v)if entered and phase=='use'and not writing and v==1 then assert(index==1,'Actual Morph bomb owner');allocated('bomb',a-C.ram.SmBombAge,v)end end,emu.callbackType.write,C.ram.SmBombAge,C.ram.SmBombAge+2)
emu.addMemoryCallback(function(_,v)if entered and rec and not writing and v~=0 then rec.source_sfx[v]=true;event('typed-sfx-request',v)end end,emu.callbackType.write,C.ram.AvAudioRequest)
emu.addMemoryCallback(function(_,v)if entered and rec and not writing and v~=0 then rec.samus_sfx=(rec.samus_sfx or 0)|v;event('samus-sfx-flags',v)end end,emu.callbackType.write,C.ram.SmSfx)
emu.addMemoryCallback(function(_,v)if entered and rec and phase=='collect'and v&C.powerup_sfx~=0 then rec.pickup_sfx=true end end,emu.callbackType.write,C.ram.Square2SoundQueue)
hook('GameLoopFinish',function()
 if not entered or done then return end
 assert(r('MmDeathFlag')==0 and r('InjuryTimer')==0 and r('GuestHurtTicks')==0,'No hurt/death/injected immunity');event('update')
 if phase=='collect'then
  assert(age<240,'Finite actual mature collision')
  if rec.collections>0 and r('Enemy_Flag',5)==0 and r('GuestPowerupActive')==0 and r('TimerControl')==0 then
   assert(rec.collections==1 and r('PlayerStatus')==1,'One physical collection retains real tier')
   if index==254 then
    assert(stock()==math.min(C.max_missiles,rec.missiles_before+C.refill_amount),'Actual missile refill exact source amount/cap');rec.native_refill=true;rec.completed=wall;screenshot='samus-refill.png';done=true;change('complete')
   else
    assert(has(index)and r('InvOwnedLo',2)==C.items[index].expected_owned,'Exact legal source owned/exclusive state')
    assert(stock()==rec.missiles_before and rec.pickup_sfx,'Upgrade never invents ammo; real pickup sound request')
    assert(index~=0 or rec.transforms==60 and has(7),'Mushroom completes60 native calls and auto Long')
    assert(index==0 or rec.grants==1,'One actual explicit reward grant')
    rec.collected=wall;if index==0 then change('next')else change('hud')end
   end
  end
 elseif phase=='hud'and age>=20 then
  if r('InvHudActive')~=0 then local name=C.items[r('InvSelected',2)].hud_name;for i,v in ipairs(name)do assert(emu.read(0x2023+i-1,emu.memType.nesPpuDebug)==v,'Actual committed selected HUD name')end;rec.hud=true end;change('use-setup')
 elseif phase=='use'then
  if index==1 then if r('SmCrouch')~=0 then rec.crouched=true end;if r('SmBall')~=0 then rec.morphed=true end;for i=0,2 do if r('SmBombAge',i)>=58 then rec.exploded=true end;if r('SmBombBoosted',i)~=0 then rec.bomb_boost=true end end end
  if index==3 and r('AvFrozen',0)+256*r('AvFrozenHi',0)>0 then rec.freeze_seen=true;rec.freeze_remaining=r('AvFrozen',0)+256*r('AvFrozenHi',0);assert(r('RgEnemyStun',0)~=0,'Ice uses actual source STOP')end
  if index==5 and r('SmCrouch')~=0 then rec.crouched=true;if rec.form_dma==nil then rec.form_dma=dmas end end
  if index==6 and r('SmFlip')~=0 and r('Player_State')~=0 then rec.flipped=true;if rec.form_dma==nil then rec.form_dma=dmas end end
  if age>=210 and pool()==0 and r('SmBall')==0 and r('Player_State')==0 then
   assert(not refill and not awaitDropClear and stock()==rec.missiles_before-rec.cost+rec.earned_refill,'Exact conserved ammo: actual source spends plus proven earned refills; no fixture refill')
   if index~=5 then assert(rec.target and rec.damageCalls>0,'Actual intended target contact')end
   if index~=3 and index~=5 then assert(rec.hpWrites>0,'Actual damaging source target effect')end
   if index==1 then assert(rec.crouched and rec.morphed and rec.exploded and rec.bomb_boost and(rec.samus_sfx or 0)&12==12,'Native crouch/morph/bomb explosion/boost and cues')
   elseif index==2 then assert(rec.spends==1 and rec.cost==C.missile_cost and rec.source_sfx[C.missile_sfx],'Real Select missile/cost/source cue')
   elseif index==3 then assert(rec.freeze_seen and rec.hpWrites==0,'Ice freezes rather than damages first ordinary target')
   elseif index==4 then assert(rec.wave_crossed_wall and not has(3),'Actual Wave passes staged solid column; Ice replaced')
   elseif index==5 then assert(rec.crouched and rec.varia_power,'Varia actual powered visual and crouch')
   elseif index==6 then assert(rec.flipped and rec.source_sfx[C.screw_sfx],'Actual diagonal Screw jump/body/source cue')end
   if not rec.sampled then rec.sample_skipped='No intended live visual survived the required2 committed DMAs' end
   rec.native_cleanup=true;rec.completed=wall;change('next')
  end
  assert(age<480,'Bounded real action/cleanup')
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
 local input={}
 if phase=='use'then
  if index==1 then input.down=age==5 or age==9;input.b=age>=16 and age<19;input.up=age>=120 and age<124
  elseif index==2 then input.select=age>=6 and age<9
  elseif index==6 then input.a=age>=6 and age<19;input.right=age>=6 and age<19
  elseif index==5 then input.down=age>=5 and age<13;input.up=age>=15 and age<18
  else input.b=age>=6 and age<9 end
 end
 emu.setInput(input,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1;minSP=math.min(minSP,emu.getState()['cpu.sp'])
 if entered then local s=emu.getState();for i=0,11 do assert(s['mapper.chrBanks'..i]==physical[i],'Actual CHR hardware/write-latch model');chrChecks=chrChecks+1 end end
 if entered and phase=='use'and not rec.sampled then
  local active=false;local anchor=rec.allocation_dma
  if index==1 then for i=0,2 do if r('SmBombAge',i)>1 and r('SmBombAge',i)<58 then active=r('SmBall')~=0 end end
  elseif index==2 or index==3 then for i=0,9 do if r('RgShotType',i)==C.items[index].rg_type and r('SsHidden',i)==0 then active=true end end
  elseif index==7 or index==4 then for i=0,2 do if r('SmShotType',i)==C.items[index].sm_type and r('SmShotImpact',i)==0 then active=true end end
  elseif index==5 then anchor=rec.form_dma;active=r('SmCrouch')~=0 and rec.varia_power
  elseif index==6 then anchor=rec.form_dma;active=r('SmFlip')~=0 and r('Player_State')~=0 and r('SmJumpStartY')-r('Player_Y_Position')>=34 end
  if active and anchor~=nil and dmas>=anchor+2 then rec.sampled=true;rec.sample_wall=wall;rec.sample_dma=dmas;screenshot=string.format('samus-item-%02d.png',index)end
 end
 if screenshot then
  assert(images<8,'Eight selected PNGs max');local s=emu.getState();local sample={image=screenshot,wall=wall,update=updates,item=index,phase=phase,age=age,complete_DMAs=dmas,PPUCTRL=ctrl,ppu_scanline=s['ppu.scanline'],ppu_cycle=s['ppu.cycle'],nt_2000={},attributes={},pattern={},palette={},physical_OAM256=bytes(0,emu.memType.nesSpriteRam),source_OAM256=bytes(512),CHR_latches={},CHR_hardware={}}
  -- Actual HUD x184..199/y8..23: columns23/24 and rows1/2 in nametable2000.
  for row=1,2 do for col=23,24 do local a=0x2000+row*32+col;local t=emu.read(a,emu.memType.nesPpuDebug);sample.nt_2000[tostring(a)]=t;local attr=0x23c0+(row//4)*8+col//4;sample.attributes[tostring(attr)]=emu.read(attr,emu.memType.nesPpuDebug);local p=(ctrl&16~=0 and 0x1000 or 0)+t*16;local data={};for j=0,15 do data[#data+1]=emu.read(p+j,emu.memType.nesPpuDebug)end;sample.pattern[tostring(a)]=data end end
  for i=0,31 do sample.palette[#sample.palette+1]=emu.read(0x3f00+i,emu.memType.nesPpuDebug)end
  for i=0,11 do sample.CHR_latches[tostring(i)]=physical[i];sample.CHR_hardware[tostring(i)]=s['mapper.chrBanks'..i]end
  samples[#samples+1]=sample
  local f=assert(io.open(OUTPUT..'sample-metadata.json','w'));f:write(json(samples));f:close()
  f=assert(io.open(OUTPUT..screenshot,'wb'));f:write(emu.takeScreenshot());f:close();images=images+1;screenshot=nil
 end
 assert(wall<C.frame_limit,'16000 physical frame cap')
 if done then
  assert(not pending and not spend and dmas>100 and irqCount>100 and nmis>100 and enables>100 and late==0,'Actual full hardware/source guards exercised')
  local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=true,native_run=true,ROM_sha256=C.ROM_sha256,character=2,mode=1,mature_actor_collection_only=true,ownership_tier_ammo_form_seeded=false,full_block_reveal_rise=false,cases=records,wall=wall,updates=updates,complete256_DMAs=dmas,NMI_checks=nmis,IRQ31_checks=irqCount,NMI_safe_enables=enables,CHR_checks=chrChecks,late=late,screenshots=images,minSP=minSP,limits=C.limits,goal_complete=false}));f:close();csv:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
