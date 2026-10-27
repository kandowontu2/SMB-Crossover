-- Earned Hard Ryu/Sophia components. Mature actors and private arenas are disclosed.
local C=assert(CURRENT_RYU_SOPHIA_POWERUPS)
local wall,updates,age,index=0,0,0,1
local entered,done,writing=false,false,false
local phase,menuPhase='menu','options-focus'
local rec,records=nil,{}
local nmi,irq=nil,false
local minSP,dmas,enables,late,irqCount,nmis,images=255,0,0,0,0,0,0
local mask,pending,upper,physical,chrChecks=0,nil,0,{},0
local screenshot,spend,refill=nil,nil,nil
local csv=assert(io.open(OUTPUT..'earned-components.csv','w'))
csv:write('event,wall,update,case,phase,age,item,owned,selected,stock,status,shots,value,pc,bank,cycle\n')
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(at)local p=emu.convertAddress(at);return p and p.address//8192 or-1 end
local function pool()local n=0;for i=0,9 do if r('RgShotType',i)~=0 then n=n+1 end end;return n end
local function owned()return r('InvOwnedLo',C.character)+256*r('InvOwnedHi',C.character)end
local function has(item)return owned()&(1<<item)~=0 end
local function stock(item)return r('InvAmmo',C.character*16+(C.character==10 and 0 or item))end
local function event(kind,value)
 local s=emu.getState();local item=rec and rec.item or 0
 csv:write(table.concat({kind,wall,updates,index,phase,age,item,owned(),r('InvSelected',C.character),stock(item<16 and item or C.plan[(rec and rec.case_index) or index].ammo_item),r('PlayerStatus'),pool(),value or 0,s['cpu.pc'],bank(s['cpu.pc']),s['cpu.cycleCount']},',')..'\n')
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
local forbidden={InvOwnedLo=true,InvOwnedHi=true,InvViewedLo=true,InvViewedHi=true,InvSelected=true,InvAmmo=true,PlayerStatus=true,PlayerSize=true,GuestPowerupActive=true,GuestPowerupTarget=true,GameEngineSubroutine=true,InjuryTimer=true,GuestHurtTicks=true,MmDeathFlag=true,RgShotType=true,RgAttack=true,RgShootPose=true,AvStopwatch=true,AvLimit=true,AvSlash=true,XgHover=true,XgHoverActive=true,XgWall=true,XgCeiling=true,CheatInvincible=true}
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
 assert(pool()==0 and r('RgAttack')==0 and r('RgShootPose')==0 and r('AvSlash')==0 and r('XgWall')==0 and r('XgCeiling')==0 and r('XgHoverActive')==0,'Prior genuine effects really cleaned up')
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
 assert(item==254 or task.kind~='collect'and has(item)or not has(item)or C.auto_mask&(1<<item)~=0,'No unearned use or preowned ordinary reward')
 if task.kind=='collect'and item>0 then local p=C.items[item].availability;if p==254 then assert(owned()&C.replacement_mask~=0,'Actual source replacement prerequisite')elseif p>0 and p<254 then assert(has(p),'Actual source prerequisite')end end
 rec={case_index=index,name=task.name,item=item,kind=task.kind,started=wall,collections=0,grants=0,transforms=0,spends=0,cost=0,contacts=0,hpWrites=0,types={},sounds={},credits={},credit_total=0,owned_before=owned(),stock_before=stock(item<16 and item or task.ammo_item),hover_before=r('XgHover'),minimum_hover=r('XgHover'),allocations=0}
 records[#records+1]=rec
 transaction(function()
  arena()
  if task.kind=='collect'or task.kind=='refill'then mature(item,task.ammo_item)
  elseif task.homing then target(176,184);rec.target=true
  elseif task.kind=='wall'then
   for row=4,11 do w('Block_Buffer_1',0x54,row*16+7);tile(0,7,row+2,0x54)end
  elseif task.kind=='ceiling'then for col=2,9 do w('Block_Buffer_1',0x54,6*16+col);tile(0,col,8,0x54)end
  end
 end)
 change(task.kind)
end
local function finishCase()
 rec.completed=wall;rec.updates=age;rec.owned_after=owned();rec.stock_after=stock(rec.item<16 and rec.item or C.plan[index].ammo_item);event('case-complete')
 if index==#C.plan then done=true;change('complete')else index=index+1;change('setup')end
end
local function controlledTarget()
 local task=C.plan[index]
 if rec.target or not rec.sampled then return end
 if task.melee and r('RgAttack')>0 and r('RgAttackAge')>=3 and r('RgAttackAge')<8 then transaction(function()target(102,176)end);rec.target=true;event('actual-melee-target');return end
 if task.slash and r('AvSlash')~=0 and r('Player_State')~=0 then transaction(function()target(r('Player_X_Position')+4,r('Player_Y_Position')+4)end);rec.target=true;event('actual-slash-body-target');return end
 if task.shot==0 then return end
 for i=0,9 do
  if r('RgShotType',i)==task.shot and r('RgShotImpact',i)==0 and r('RgShotPage',i)==0 and r('RgShotYHigh',i)==1 and r('RgShotX',i)>=100 and r('RgShotX',i)<=220 and r('RgShotY',i)>=40 and r('RgShotY',i)<=208 then
   local x=r('RgShotX',i)-6;local y=math.min(184,r('RgShotY',i)-8)
   transaction(function()target(x,y)end);rec.target=true;event('actual-effect-target');return
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
 if C.variant and r(C.variant)~=0 then return{select=true}end;return{a=true}
end
hook('GameLoopOwned',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then
  if r('GameEngineSubroutine')~=8 then return end
  assert(r('SelectedCharacter')==C.character and r('CrossoverBehaviorVersion')==1 and r('CheatInvincible')==0 and r('PlayerStatus')==0 and owned()==0,'Genuine cold requested owner/Hard/default cheats')
  for i=0,C.item_count do assert(r('InvAmmo',C.character*16+i)==C.items[i].initial_ammo,'Source cold stock, never seeded')end
  assert(r('XgHover')==8,'Genuine RosterClearState hover initialization')
  entered=true;change('settle')
 end
 updates=updates+1;age=age+1;assert(updates<=6500,'Finite actual update cap')
 assert(r('SelectedCharacter')==C.character and r('CrossoverBehaviorVersion')==1 and r('CheatInvincible')==0,'Native owner/mode/default cheat stability')
 if phase=='settle'and age==30 or phase=='setup'then beginCase()elseif phase=='use'then controlledTarget()end
end)
hook('PhysicalPickup',function(s)
 if entered and(phase=='collect'or phase=='refill')then
  assert(s['cpu.x']==5 and r('Enemy_Flag',5)~=0 and r('Enemy_ID',5)==0x2e and r('Enemy_State',5)>=128 and r('InvPickupOwner',5)==C.character and r('InvPickup',5)==rec.item,'Actual mature actor before native erase')
  rec.collision_update=updates;event('pre-erase-pickup')
 end
end)
hook('InventoryCollect',function(s)
 if entered and(phase=='collect'or phase=='refill')then
  assert(s['cpu.x']==5 and rec.collision_update==updates and r('Enemy_Flag',5)==0 and r('Enemy_State',5)==0 and r('InvPickupOwner',5)==C.character and r('InvPickup',5)==rec.item,'Actual collision/erase/exact source collection')
  rec.collections=rec.collections+1;event('actual-collection')
 end
end)
hook('InventoryGrant',function(s)if entered and phase=='collect'and rec.item>0 then assert(s['cpu.a']==rec.item,'Actual exact grant');rec.grants=rec.grants+1 end end)
hook('GuestPowerupUpdate',function()if entered and phase=='collect'and rec.item==0 and r('GuestPowerupActive')~=0 then rec.transforms=rec.transforms+1 end end)
hook('InventorySpend',function(s)
 if entered and phase=='use'then local cost=C.items[rec.item].cost;assert(not spend and cost>0 and s['cpu.a']==rec.item and s['cpu.y']==cost,'Actual earned item and cost');spend={before=stock(rec.item),cost=cost,sp=s['cpu.sp']};event('spend-entry',cost)end
end)
hook('InventorySpendDone',function(s)
 if spend then assert(s['cpu.sp']==spend.sp and spend.before>=spend.cost and stock(rec.item)==spend.before-spend.cost,'Same owner/frame exact native stock deduction');rec.spends=rec.spends+1;rec.cost=rec.cost+spend.cost;spend=nil;event('paid-native-action')end
end)
hook('DamageEnemy',function(s)
 if entered and phase=='use'and rec.target and s['cpu.x']==0 then assert(r('MmBulletType')==C.plan[index].proxy,'Actual intended proxy owns contact');rec.contacts=rec.contacts+1;event('native-damage-contact',r('MmBulletType'))end
end)
hook('PowerReturn',function(s)
 if entered and rec and r('PlayerStatus')~=0 then local expected=C.character==10 and(has(6)and 1 or 0)or(has(4)and 2 or(has(7)and 1 or 0));assert(s['cpu.a']==expected,'Actual acquired source power');rec.power=expected end
end)
hook('ScrollMaximumReturn',function(s)if entered and rec and C.character==10 and has(7)then assert(s['cpu.a']==99,'Actual earned scroll maximum99');rec.scroll_maximum=99 end end)
hook('RefillEntry',function(s)
 if entered and rec and(phase=='use'or phase=='refill')then
  assert(not refill,'No nested source refill')
  local item=C.character==10 and 0 or(r('AvRefillItem')==2 and 2 or 1)
  local amount=C.character==10 and(r('InvDropAmount')>=40 and 10 or 5)or(item==2 and 2 or 6)
  refill={item=item,before=stock(item),amount=amount,sp=s['cpu.sp'],wall=wall,update=updates}
  event('actual-refill-entry',amount)
 end
end)
hook('RefillDone',function(s)
 if refill then
  local maximum=C.character==10 and(has(7)and 99 or 50)or C.items[refill.item].max_ammo
  local after=stock(refill.item)
  assert(s['cpu.sp']==refill.sp and after==math.min(maximum,refill.before+refill.amount),'Actual same-owner source refill/cap exact; no assumed or seeded credit')
  refill.after=after;refill.actual_credit=after-refill.before;rec.credit_total=rec.credit_total+refill.actual_credit;rec.credits[#rec.credits+1]=refill;refill=nil;event('actual-refill-completed',after)
 end
end)
emu.addMemoryCallback(function(_,v)if entered and phase=='use'and rec.target and rec.contacts>0 and not writing then rec.hpWrites=rec.hpWrites+1;event('actual-target-health-write',v)end end,emu.callbackType.write,C.ram.MmEnemyHealthLo,C.ram.MmEnemyHealthHi)
emu.addMemoryCallback(function(a,v)
 if entered and phase=='use'and v~=0 and not writing then rec.types[v]=true;rec.allocations=rec.allocations+1;event('native-effect-type',v);if v==C.plan[index].shot and not rec.allocation_dma then rec.allocation_dma=dmas;rec.allocation_slot=a-C.ram.RgShotType end end
end,emu.callbackType.write,C.ram.RgShotType,C.ram.RgShotType+9)
emu.addMemoryCallback(function(_,v)if entered and rec and v~=0 and not writing then rec.sounds[v]=true end end,emu.callbackType.write,C.ram.AvAudioRequest)
emu.addMemoryCallback(function(_,v)if entered and rec and phase=='collect'and v&C.powerup_sfx~=0 then rec.pickup_sfx=true end end,emu.callbackType.write,C.ram.Square2SoundQueue)
hook('GameLoopFinish',function()
 if not entered or done then return end
 assert(r('MmDeathFlag')==0 and r('InjuryTimer')==0 and r('GuestHurtTicks')==0,'No unrelated injury/death or injected protection')
 if not rec then return end
 local task=C.plan[index];event('update')
 if phase=='collect'or phase=='refill'then
  assert(age<180,'Bounded genuine mature collection')
  if rec.collections>0 and r('Enemy_Flag',5)==0 and r('GuestPowerupActive')==0 and r('TimerControl')==0 then
   assert(rec.collections==1 and r('PlayerStatus')==1,'One actual collection; earned source tier retained')
   if phase=='collect'then
    assert(has(rec.item)and rec.pickup_sfx,'Actual ownership and pickup SFX request')
    assert(rec.item==0 and rec.transforms==60 or rec.item>0 and rec.grants==1,'Complete60-call transformation or one source grant')
    local expected=rec.item==0 and(rec.owned_before|C.auto_mask|1)or((rec.owned_before&(~C.items[rec.item].single_mask))|(1<<rec.item));assert(owned()==expected,'Actual exclusive weapon ownership transition')
    if rec.item==0 then screenshot='mushroom-earned.png'end
   else assert(stock(task.ammo_item)==rec.stock_before+task.amount,'Actual earned refill exact source increment')end
   if phase=='refill'and C.character==10 and has(7)then assert(rec.scroll_maximum==99,'Scroll actual refill maximum observed');rec.refill_commit_dma=dmas;change('refill-display')else finishCase()end
  end
 elseif phase=='refill-display'then
  assert(stock(task.ammo_item)==rec.stock_before+task.amount,'Earned scroll refill retained during real HUD presentation')
  if age>=12 and dmas>=rec.refill_commit_dma+2 then screenshot='scroll-earned-refill.png';finishCase()end
 elseif phase=='use'then
  assert(r('PlayerStatus')==1 and r('GameEngineSubroutine')==8 and r('Player_X_Position')==64,'Actual powered owner in authored scene')
  if task.melee and r('RgAttack')~=0 and not rec.allocation_dma then rec.allocation_dma=dmas end
  if task.slash and r('AvSlash')~=0 then rec.slash_seen=true;if not rec.allocation_dma then rec.allocation_dma=dmas end end
  if task.primary then for i=0,9 do if r('RgShotType',i)==6 then assert(r('SsMode',i)==task.power,'Actual Hyper/Crusher tier frozen at creation');rec.primary_power=task.power end end end
  if age==32 and not task.primary and not task.melee then for i,v in ipairs(C.items[rec.item].hud_name)do assert(emu.read(0x2023+i-1,emu.memType.nesPpuDebug)==v,'Actual committed selected source HUD name')end;rec.hud=true end
  if age>=task.limit then
   assert(pool()==0 and r('RgAttack')==0 and r('RgShootPose')==0 and r('AvSlash')==0,'Native shot/pose/slash cleanup, never fixture cleared')
   local cost=(task.primary or task.melee)and 0 or C.items[rec.item].cost
   assert(rec.spends==(cost>0 and 1 or 0)and rec.cost==cost and stock(rec.item)==rec.stock_before-cost+rec.credit_total,'Exact native cost plus only independently observed earned source-refill credits')
   assert(rec.target and rec.contacts>0 and rec.hpWrites>0,'Actual effect/source target health contact')
   assert(task.shot==0 or rec.types[task.shot],'Actual intended effect allocated')
   assert(not task.slash or rec.slash_seen,'Real airborne Jump Slash')
   assert(not task.triplet or rec.allocations==3,'One paid source missile triplet')
   assert(rec.sampled,'Live intended art survives two genuine completed DMAs');finishCase()
  end
 elseif phase=='hover'then
  local fuel=r('XgHover');rec.minimum_hover=math.min(rec.minimum_hover,fuel)
  if r('XgHoverActive')~=0 then rec.hover_seen=true;if not rec.allocation_dma then rec.allocation_dma=dmas end end
  if not rec.sampled and rec.hover_seen and fuel<rec.hover_before and r('XgHoverActive')~=0 and dmas>=rec.allocation_dma+2 then rec.sampled=true;screenshot='hover-earned-active.png'end
  if age>=task.limit then assert(rec.hover_seen and rec.minimum_hover<8 and fuel==8 and r('XgHoverActive')==0 and r('Player_State')==0 and stock(3)==rec.stock_before,'Actual hover boost/burn/natural recharge and landing; separate inventory cell unchanged');assert(rec.sampled);finishCase()end
 elseif phase=='wall'or phase=='ceiling'then
  if r('XgWall')~=0 then rec.wall_seen=true;rec.wall_min_y=math.min(rec.wall_min_y or 176,r('Player_Y_Position'));if not rec.allocation_dma then rec.allocation_dma=dmas end end
  if r('XgCeiling')~=0 then rec.ceiling_seen=true;rec.ceiling_at=rec.ceiling_at or age;rec.ceiling_min_x=math.min(rec.ceiling_min_x or 255,r('Player_X_Position'));rec.ceiling_max_x=math.max(rec.ceiling_max_x or 0,r('Player_X_Position'));if not rec.ceiling_dma then rec.ceiling_dma=dmas end end
  if not rec.sampled and(phase=='wall'and rec.wall_seen and rec.wall_min_y<160 and r('XgWall')~=0 and dmas>=rec.allocation_dma+2 or phase=='ceiling'and rec.ceiling_seen and rec.ceiling_min_x<rec.ceiling_max_x and r('XgCeiling')~=0 and dmas>=rec.ceiling_dma+2)then rec.sampled=true;screenshot=phase..'-earned-active.png'end
  if age>=task.limit then
   assert(r('XgWall')==0 and r('XgCeiling')==0 and r('XgHoverActive')==0 and r('Player_State')==0,'Native attachment/jump/drop cleanup and landing')
   assert(phase=='wall'and rec.wall_seen and rec.wall_min_y<160 or phase=='ceiling'and rec.ceiling_seen and rec.ceiling_min_x<rec.ceiling_max_x,'Actual acquired wall climb or ceiling traverse')
   assert(rec.sampled);finishCase()
  end
 end
 if phase~='setup'and phase~='complete'then assert(age<(task.limit or 180)+60,'Finite native component deadline')end
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
 local input={};local task=C.plan[index]
 if phase=='use'then
  if task.slash or task.air then input.a=age>=4 and age<12;input.select=age>=12 and age<15
  elseif task.primary or task.melee then input.b=age>=5 and age<8
  else input.select=age>=5 and age<8 end
 elseif phase=='hover'then input.a=age>=4 and age<=28 or age>=31 and age<=75
 elseif phase=='wall'then
  if age<70 then input.right=true;input.up=true;input.a=age>=4 and age<=30 elseif age<74 then input.left=true;input.a=true end
 elseif phase=='ceiling'then
  if rec.ceiling_at then if age<rec.ceiling_at+22 then input.left=true elseif age<rec.ceiling_at+26 then input.a=true end
  elseif age<110 then input.up=true;input.a=age>=4 and age<=30 end
 end
 emu.setInput(input,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1;minSP=math.min(minSP,emu.getState()['cpu.sp'])
 if entered then local s=emu.getState();for i=0,11 do assert(s['mapper.chrBanks'..i]==physical[i],'Actual CHR hardware agrees with write-time latch model');chrChecks=chrChecks+1 end end
 if entered and phase=='use'and not rec.sampled and rec.allocation_dma and dmas>=rec.allocation_dma+2 then
  local task=C.plan[index];local visible=false
  if task.melee then visible=r('RgAttack')~=0 and r('RgAttackAge')>=3 and r('RgAttackAge')<7
  elseif task.slash then visible=r('AvSlash')~=0 and r('Player_State')~=0 and r('Player_Y_Position')<160
  else for i=0,9 do if r('RgShotType',i)==task.shot and r('RgShotImpact',i)==0 and r('RgShotPage',i)==0 and r('RgShotYHigh',i)==1 and r('RgShotX',i)>=100 and r('RgShotX',i)<=232 and r('RgShotY',i)>=32 and r('RgShotY',i)<=216 then visible=true;rec.sample_slot=i;rec.sample_x=r('RgShotX',i);rec.sample_y=r('RgShotY',i);break end end end
  if visible then rec.sampled=true;rec.sample_dma=dmas;rec.sample_wall=wall;screenshot=task.name..'.png'end
 end
 if screenshot then assert(images<8,'Eight meaningful selected full-frame PNGs maximum');local f=assert(io.open(OUTPUT..screenshot,'wb'));f:write(emu.takeScreenshot());f:close();images=images+1;screenshot=nil end
 assert(wall<C.frame_limit,'Finite native frame cap')
 if done then
  assert(not pending and not spend and not refill and dmas>100 and nmis>100 and irqCount>100 and enables>100 and late==0,'Actual full hardware/source guards exercised')
  local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=true,native_run=true,ROM_sha256=C.ROM_sha256,character=C.character,mode=1,cases=records,wall=wall,updates=updates,complete256_DMAs=dmas,NMI_checks=nmis,IRQ31_checks=irqCount,safe_enables=enables,CHR_checks=chrChecks,minSP=minSP,screenshots=images,mature_actor_collection_only=true,full_reveal_rise_or_natural_drop=false,ownership_or_resources_seeded=false,goal_complete=false}));f:close();csv:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
