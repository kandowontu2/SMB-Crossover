-- Earned Hard Link/Simon components. Mature actors and private arenas are disclosed.
local C=assert(CURRENT_LINK_SIMON_POWERUPS)
local wall,updates,age,index=0,0,0,1
local entered,done,writing=false,false,false
local phase,menuPhase='menu','options-focus'
local rec,records=nil,{}
local nmi,irq=nil,false
local minSP,dmas,enables,late,irqCount,nmis,images=255,0,0,0,0,0,0
local mask,pending,upper,physical,chrChecks=0,nil,0,{},0
local screenshot,spend=nil,nil
local csv=assert(io.open(OUTPUT..'earned-components.csv','w'))
csv:write('event,wall,update,case,phase,age,item,owned,selected,stock,status,shots,value,pc,bank,cycle\n')
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(at)local p=emu.convertAddress(at);return p and p.address//8192 or-1 end
local function pool()local n=0;for i=0,9 do if r('RgShotType',i)~=0 then n=n+1 end end;return n end
local function owned()return r('InvOwnedLo',C.character)+256*r('InvOwnedHi',C.character)end
local function has(item)return owned()&(1<<item)~=0 end
local function stock(item)return r('InvAmmo',C.character*16+(C.character==5 and 0 or item))end
local function event(kind,value)
 local s=emu.getState();local item=rec and rec.item or 0
 csv:write(table.concat({kind,wall,updates,index,phase,age,item,owned(),r('InvSelected',C.character),stock(item<16 and item or C.plan[index].ammo_item),r('PlayerStatus'),pool(),value or 0,s['cpu.pc'],bank(s['cpu.pc']),s['cpu.cycleCount']},',')..'\n')
end
local function json(v)
 if type(v)=='table'then local out={};if #v>0 then for _,x in ipairs(v)do out[#out+1]=json(x)end;return'['..table.concat(out,',')..']'end
  for k,x in pairs(v)do out[#out+1]=string.format('%q',tostring(k))..':'..json(x)end;table.sort(out);return'{'..table.concat(out,',')..'}'
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
local forbidden={InvOwnedLo=true,InvOwnedHi=true,InvViewedLo=true,InvViewedHi=true,InvSelected=true,InvAmmo=true,PlayerStatus=true,PlayerSize=true,GuestPowerupActive=true,GuestPowerupTarget=true,GameEngineSubroutine=true,InjuryTimer=true,GuestHurtTicks=true,MmDeathFlag=true,RgShotType=true,RgAttack=true,RgShootPose=true,AvStopwatch=true,AvLimit=true,CheatInvincible=true}
local function w(n,v,i)
 assert(writing and not nmi and not irq and r('NmiDisable')==255,'Only synchronous private GameLoop+5 setup')
 assert(C.setup_allowed[n]and not forbidden[n],'No tested resource/action/outcome seeds: '..n)
 emu.write(assert(C.ram[n],n)+(i or 0),v&255,emu.memType.nesDebug)
end
local function transaction(fn)
 assert(not writing and not nmi and not irq and r('NmiDisable')==255,'No interrupt or asynchronous setup owner')
 writing=true;fn();writing=false;event('disclosed-scene-setup')
end
local function tile(page,col,row,id)
 assert(writing and not nmi and not irq,'Same native scene transaction')
 local function source(n)local p=C.metatiles[n];return emu.read(p.bank*8192+p.offset+id,emu.memType.nesPrgRom)end
 local function put(a,v)emu.write(a,v,emu.memType.nesPpuDebug)end
 local at=0x2000+page*1024+row*64+col*2
 put(at,source('MTileTopLeft'));put(at+1,source('MTileTopRight'));put(at+32,source('MTileBotLeft'));put(at+33,source('MTileBotRight'))
 local a=0x23c0+page*1024+(row//2)*8+col//2;local shift=row%2*4+col%2*2
 put(a,(emu.read(a,emu.memType.nesPpuDebug)&(~(3<<shift)))|((source('MTileAttribute')>>6)<<shift))
end
local function arena()
 assert(pool()==0 and r('RgAttack')==0 and r('RgShootPose')==0 and r('AvStopwatch')==0,'Prior genuine effects really cleaned up')
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do for row=2,14 do for col=0,15 do tile(p,col,row,row>=13 and 0x54 or 0)end end end
 for p=0,1 do for row=11,12 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+row*16+col)end end end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_CollisionBits',0,i)end
 for i=0,3 do w('InvDropKind',0,i)end
 for _,n in ipairs({'Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','ScrollThirtyTwo','AreaParserTaskNum'})do w(n,0)end
 for _,a in ipairs({{'MmVX',3},{'MmVY',3},{'MmXFraction',2},{'MmYFraction',2}})do for i=0,a[2]-1 do w(a[1],0,i)end end
 for _,a in ipairs({{'ScrollLock',1},{'ScreenLeft_X_Pos',0},{'ScreenLeft_PageLoc',0},{'ScreenRight_X_Pos',255},{'ScreenRight_PageLoc',0},{'Player_X_Position',64},{'Player_PageLoc',0},{'MmOldX',64},{'Player_Y_Position',176},{'Player_Y_HighPos',1},{'Player_State',0},{'PlayerFacingDir',1},{'Player_MovingDir',1},{'Player_CollisionBits',255}})do w(a[1],a[2])end
end
local function mature(item,ammo)
 for _,a in ipairs({{'Enemy_Flag',1},{'Enemy_ID',0x2e},{'Enemy_State',128},{'Enemy_BoundBoxCtrl',3},{'Enemy_X_Position',64},{'Enemy_PageLoc',0},{'Enemy_Y_Position',184},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_SprAttrib',0},{'PowerUpType',item==0 and 0 or 1},{'InvPickupOwner',C.character},{'InvPickup',item}})do w(a[1],a[2],5)end
 if item==254 then w('AvPickupAmmoItem',ammo,5)end
end
local function target(x,y)
 for _,a in ipairs({{'Enemy_Flag',1},{'Enemy_ID',6},{'Enemy_State',0},{'Enemy_X_Position',x},{'Enemy_PageLoc',0},{'Enemy_Y_Position',y},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_Y_MoveForce',0},{'Enemy_MovingDir',1},{'Enemy_BoundBoxCtrl',9},{'EnemyOffscrBitsMasked',0},{'Enemy_CollisionBits',0},{'MmEnemyHealthLo',0},{'MmEnemyHealthHi',0},{'MmEnemyFlash',0},{'RgEnemyStun',0}})do w(a[1],a[2],0)end
end
local function change(p)phase=p;age=0;event('phase')end
local function beginCase()
 local task=assert(C.plan[index]);local item=task.item
 assert(item==254 or task.kind=='use'and has(item)or not has(item)or C.auto_mask&(1<<item)~=0,'No unearned use or silently preowned ordinary pickup')
 if task.kind=='collect'and item>0 then local prerequisite=C.items[item].availability;if prerequisite==254 then assert(owned()&108~=0,'Actual DOUBLE requires an acquired throwable')elseif prerequisite>0 and prerequisite<254 then assert(has(prerequisite),'Actual source item prerequisite')end end
 rec={case_index=index,name=task.name,item=item,kind=task.kind,started=wall,collections=0,grants=0,transforms=0,spends=0,cost=0,contacts=0,hpWrites=0,types={},sounds={},owned_before=owned(),stock_before=stock(item<16 and item or task.ammo_item)}
 records[#records+1]=rec
 transaction(function()arena();if task.kind~='use'then mature(item,task.ammo_item)elseif task.watch then target(192,184);w('Enemy_X_Speed',248,0);rec.target=true end end)
 if task.kind=='use'then change(r('InvSelected',C.character)==item and'use'or'pause-open')else change(task.kind)end
end
local function finishCase()
 rec.completed=wall;rec.updates=age;rec.owned_after=owned();rec.stock_after=stock(rec.item<16 and rec.item or C.plan[index].ammo_item);event('case-complete')
 if index==#C.plan then done=true;change('complete')else index=index+1;change('setup')end
end
local function controlledTarget()
 local task=C.plan[index]
 if rec.target or task.watch or not rec.sampled then return end
 for i=0,9 do
  if r('RgShotType',i)==task.shot and r('RgShotPage',i)==0 and r('RgShotYHigh',i)==1 and r('RgShotX',i)>=(task.shot==34 and 16 or 100)and r('RgShotX',i)<=220 and r('RgShotY',i)>=48 and r('RgShotY',i)<=208 then
   local x=task.shot==34 and r('RgShotX',i)+12 or r('RgShotX',i)-6;local y=math.min(184,r('RgShotY',i)-8)
   assert(x>=16 and x<=232 and y>=32 and y<=184,'Live source-effect target geometry')
   transaction(function()target(x,y)end);rec.target=true;rec.target_x=x;rec.target_y=y;event('actual-effect-aligned-target');return
  end
 end
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
 local i=r('CrossoverMenuIndex');if i//6~=C.slot//6 then return{down=true}end;if i~=C.slot then return{right=true}end
 if r(C.variant)~=0 then return{select=true}end;return{a=true}
end
hook('GameLoopOwned',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then
  if r('GameEngineSubroutine')~=8 then return end
  assert(r('SelectedCharacter')==C.character and r(C.variant)==0 and r('CrossoverBehaviorVersion')==1 and r('CheatInvincible')==0,'Cold requested owner/variant/numeric Hard/default cheats')
  assert(r('PlayerStatus')==0 and owned()==0,'No powered/owned initial seeds')
  for i=0,C.item_count do assert(r('InvAmmo',C.character*16+i)==C.items[i].initial_ammo,'Actual cold initialized stock')end
  entered=true;change('settle')
 end
 updates=updates+1;age=age+1;assert(updates<=6000,'Finite actual update cap')
 assert(r('SelectedCharacter')==C.character and r(C.variant)==0 and r('CrossoverBehaviorVersion')==1 and r('CheatInvincible')==0,'Native owner/mode/default cheat stability')
 if phase=='settle'and age==30 or phase=='setup'then beginCase()elseif phase=='use'then controlledTarget()end
end)
hook('PhysicalPickup',function(s)
 if entered and(phase=='collect'or phase=='refill')then
  assert(s['cpu.x']==5 and r('Enemy_Flag',5)~=0 and r('Enemy_ID',5)==0x2e and r('Enemy_State',5)>=128,'Genuine mature actor before native erase')
  assert(r('InvPickupOwner',5)==C.character and r('InvPickup',5)==rec.item,'Actual exact item/owner')
  rec.collision_update=updates;event('pre-erase-pickup')
 end
end)
hook('InventoryCollect',function(s)
 if entered and(phase=='collect'or phase=='refill')then
  assert(s['cpu.x']==5 and rec.collision_update==updates and r('Enemy_Flag',5)==0 and r('Enemy_State',5)==0 and r('InvPickupOwner',5)==C.character and r('InvPickup',5)==rec.item,'Actual native collision/erase/collection order')
  rec.collections=rec.collections+1;event('actual-collection')
 end
end)
hook('InventoryGrant',function(s)if entered and phase=='collect'and rec.item>0 then assert(s['cpu.a']==rec.item,'Actual exact grant');rec.grants=rec.grants+1;event('actual-grant')end end)
hook('GuestPowerupUpdate',function()if entered and phase=='collect'and rec.item==0 and r('GuestPowerupActive')~=0 then rec.transforms=rec.transforms+1 end end)
hook('InventorySpend',function(s)
 if entered and phase=='use'then
  local cost=C.items[rec.item].cost;assert(not spend and cost>0 and s['cpu.a']==rec.item and s['cpu.y']==cost,'Exact acquired action item/cost')
  spend={before=stock(rec.item),cost=cost,sp=s['cpu.sp']};event('spend-entry',cost)
 end
end)
hook('InventorySpendDone',function(s)
 if spend then assert(s['cpu.sp']==spend.sp and spend.before>=spend.cost and stock(rec.item)==spend.before-spend.cost,'Same-frame exact native stock decrement');rec.spends=rec.spends+1;rec.cost=rec.cost+spend.cost;spend=nil;event('paid-native-action')end
end)
hook('DamageEnemy',function(s)if entered and phase=='use'and rec.target and s['cpu.x']==0 then assert(r('MmBulletType')==C.plan[index].proxy,'Exact acquired damaging proxy');rec.contacts=rec.contacts+1;event('native-damage-contact',r('MmBulletType'))end end)
hook('BoomerangStop',function(s)if entered and phase=='use'and C.plan[index].stop then assert(rec.target and s['cpu.x']==0 and r('MmBulletType')==18,'Actual zero-damage boomerang source STOP');rec.contacts=rec.contacts+1;event('native-boomerang-stop')end end)
hook('PowerReturn',function(s)if entered and rec and(owned()&(C.character==4 and 16 or 2))~=0 and r('PlayerStatus')~=0 then assert(s['cpu.a']==2,'Actual earned ring/whip source power');rec.power2=true end end)
emu.addMemoryCallback(function(_,v)if entered and phase=='use'and rec.target and rec.contacts>0 and not writing then rec.hpWrites=rec.hpWrites+1;event('native-target-health-write',v)end end,emu.callbackType.write,C.ram.MmEnemyHealthLo,C.ram.MmEnemyHealthHi)
emu.addMemoryCallback(function(a,v)
 if entered and phase=='use'and v~=0 and not writing then rec.types[v]=true;event('native-effect-type',v);if v==C.plan[index].shot and not rec.allocation_dma then rec.allocation_dma=dmas;rec.allocation_slot=a-C.ram.RgShotType end end
end,emu.callbackType.write,C.ram.RgShotType,C.ram.RgShotType+9)
emu.addMemoryCallback(function(_,v)if entered and rec and v~=0 and not writing then rec.sounds[v]=true;event('native-source-sfx-request',v)end end,emu.callbackType.write,C.ram.AvAudioRequest)
emu.addMemoryCallback(function(_,v)if entered and rec and(phase=='collect'or phase=='refill')and v&C.powerup_sfx~=0 then rec.pickup_sfx=true end end,emu.callbackType.write,C.ram.Square2SoundQueue)
hook('GameLoopFinish',function()
 if not entered or done then return end
 assert(r('MmDeathFlag')==0 and r('InjuryTimer')==0 and r('GuestHurtTicks')==0,'No unrelated injury/death or injected protection')
 if not rec then return end
 local task=C.plan[index];event('update')
 if phase=='collect'or phase=='refill'then
  assert(age<180,'Bounded actual mature collection')
  if rec.collections>0 and r('Enemy_Flag',5)==0 and r('GuestPowerupActive')==0 and r('TimerControl')==0 then
   assert(rec.collections==1 and r('PlayerStatus')==1,'One actual mature collection, earned mushroom tier retained')
   if phase=='collect'then
    assert(has(rec.item)and rec.pickup_sfx,'Actual ownership and pickup sound request')
    assert(rec.item==0 and rec.transforms==60 or rec.item>0 and rec.grants==1,'Complete60-call source transform or exact native grant')
    local expected=rec.item==0 and(rec.owned_before|C.auto_mask|1)or((rec.owned_before&(~C.items[rec.item].single_mask))|(1<<rec.item));assert(owned()==expected,'Exact source ownership transition, including mutually exclusive Simon subweapons')
    if rec.item==0 then screenshot='mushroom-earned.png'end
   else assert(stock(task.ammo_item)==rec.stock_before+task.amount,'Actual source heart/bomb refill exact increment')end
   finishCase()
  end
 elseif phase=='pause-open'then
  assert(age<180,'Bounded genuine pause entry');if r('GamePauseStatus')&1~=0 then change('pause-cycle')end
 elseif phase=='pause-cycle'then
  assert(age<240,'Bounded actual paused weapon selection');if r('InvSelected',C.character)==rec.item then change('pause-close')end
 elseif phase=='pause-close'then
  assert(age<180,'Bounded native pause exit');if r('GamePauseStatus')&1==0 then change('use')end
 elseif phase=='use'then
  assert(r('PlayerStatus')==1 and r('GameEngineSubroutine')==8 and r('Player_State')==0 and r('Player_X_Position')==64 and r('Player_Y_Position')==176,'Source-powered grounded hero remains in staged scene')
  if task.expected_limit and rec.spends>0 then assert(r('AvLimit')==task.expected_limit,'Actual acquired DOUBLE/TRIPLE throw admission limit');rec.limit_seen=true end
  if task.watch then
   local v=r('AvStopwatch')
   if v>0 then
    rec.watch_seen=true;rec.watch_ticks=(rec.watch_ticks or 0)+1
    if rec.watch_x then assert(r('Enemy_X_Position')==rec.watch_x and r('Enemy_Y_Position')==rec.watch_y,'Actual native enemy remains frozen during stopwatch')end
    rec.watch_x=r('Enemy_X_Position');rec.watch_y=r('Enemy_Y_Position')
    if not rec.watch_allocation_dma then rec.watch_allocation_dma=dmas end
   elseif rec.watch_seen then rec.watch_expired=true;rec.watch_motion=rec.watch_motion or r('Enemy_X_Position')~=rec.watch_x end
  elseif task.stop and rec.contacts>0 and not rec.stopped then assert(r('RgEnemyStun')>0,'Zero-damage boomerang actual STOP property');rec.stopped=true end
  if task.shot==34 then for i=0,9 do if r('RgShotType',i)==34 and math.abs(r('RgShotX',i)-(r('Player_X_Position')+8))<19 and math.abs(r('RgShotY',i)-(r('Player_Y_Position')+18))<25 then assert(has(5)and r('AvBombHurt')==0,'Earned BLUE RING protects actual self-blast overlap');rec.blue_ring_overlap=true end end end
  if age==24 then for i,v in ipairs(C.items[rec.item].hud_name)do assert(emu.read(0x2023+i-1,emu.memType.nesPpuDebug)==v,'Actual committed selected source HUD name')end;rec.hud_name=true end
  if age>=task.limit then
   assert(pool()==0 and r('RgAttack')==0 and r('RgShootPose')==0 and r('AvStopwatch')==0,'Native effect/pose/watch cleanup, never fixture-cleared')
   local cost=C.items[rec.item].cost;assert(rec.spends==(cost>0 and 1 or 0)and rec.cost==cost and stock(rec.item)==rec.stock_before-cost,'One real action and exact earned stock cost')
   assert(rec.hud_name,'Actual committed earned weapon HUD name observed')
   if task.watch then assert(rec.watch_seen and rec.watch_ticks==180 and rec.watch_expired and rec.watch_motion and rec.sampled,'Actual180-update stopwatch freeze, natural expiry, resumed enemy motion and committed sample')
   else
    assert(rec.types[task.shot]and(not task.initial or rec.types[task.initial])and rec.target and rec.contacts>0,'Actual acquired projectile phases and real target contact')
    assert(task.stop and rec.stopped and rec.hpWrites==0 or not task.stop and rec.hpWrites>0,'Source zero-damage STOP versus genuine damaging action')
    assert(rec.sampled,'Intended live effect survived to two completed genuine DMAs')
   end
   assert(not task.expected_limit or rec.limit_seen,'Actual multiplier admission observed')
   assert(task.shot~=34 or rec.blue_ring_overlap,'Blue ring exercised in actual self-blast geometry');finishCase()
  end
  assert(age<task.limit+60,'Bounded action deadline')
 end
end)
-- INSERT_UNCHANGED_CURRENT_BASS_HARDWARE_GUARDS
emu.addEventCallback(function()
 if not entered then emu.setInput(menu(),0);return end
 local input={}
 if phase=='pause-open'or phase=='pause-close'then input.start=wall%12==1
 elseif phase=='pause-cycle'then input.right=wall%8==1
 elseif phase=='use'then input.select=age>=5 and age<8 end
 emu.setInput(input,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1;minSP=math.min(minSP,emu.getState()['cpu.sp'])
 if entered then local s=emu.getState();for i=0,11 do assert(s['mapper.chrBanks'..i]==physical[i],'Actual CHR hardware agrees with write-time latch model');chrChecks=chrChecks+1 end end
 if entered and phase=='use'and C.plan[index].watch and not rec.sampled and rec.watch_allocation_dma and dmas>=rec.watch_allocation_dma+2 and r('AvStopwatch')>0 then rec.sampled=true;rec.sample_dma=dmas;rec.sample_wall=wall;screenshot='stopwatch-active.png'end
 if entered and phase=='use'and not rec.sampled and rec.allocation_dma and dmas>=rec.allocation_dma+2 then
  local task=C.plan[index]
  for i=0,9 do
   if r('RgShotType',i)==task.shot and r('RgShotPage',i)==0 and r('RgShotYHigh',i)==1 and r('RgShotX',i)>=8 and r('RgShotX',i)<=248 and r('RgShotY',i)>=32 and r('RgShotY',i)<=224 then
    rec.sampled=true;rec.sample_dma=dmas;rec.sample_wall=wall;rec.sample_slot=i;rec.sample_type=task.shot;rec.sample_x=r('RgShotX',i);rec.sample_y=r('RgShotY',i)
    if images<8 then screenshot=task.name..'.png'end;break
   end
  end
 end
 if screenshot then assert(images<8,'Eight selected full-frame PNGs maximum');local f=assert(io.open(OUTPUT..screenshot,'wb'));f:write(emu.takeScreenshot());f:close();images=images+1;screenshot=nil end
 assert(wall<C.frame_limit,'Finite native profile cap')
 if done then
  assert(not pending and not spend and dmas>100 and nmis>100 and irqCount>100 and enables>100 and late==0,'Full source/hardware guards exercised')
  local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=true,native_run=true,ROM_sha256=C.ROM_sha256,character=C.character,mode=1,cases=records,wall=wall,updates=updates,complete256_DMAs=dmas,NMI_checks=nmis,IRQ31_checks=irqCount,safe_enables=enables,CHR_checks=chrChecks,minSP=minSP,screenshots=images,mature_actor_collection_only=true,full_reveal_rise_or_natural_drop=false,ownership_or_resources_seeded=false,goal_complete=false}));f:close();csv:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
