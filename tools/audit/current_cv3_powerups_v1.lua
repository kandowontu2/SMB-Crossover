-- Earned Hard Grant/Sypha/Alucard components. Mature actors and private arenas are disclosed.
local C=assert(CURRENT_CV3_POWERUPS)
local wall,updates,age,index=0,0,0,1
local entered,done,writing=false,false,false
local phase,menuPhase='menu','options-focus'
local rec,records=nil,{}
local nmi,irq=nil,false
local minSP,dmas,enables,late,irqCount,nmis,images=255,0,0,0,0,0,0
local mask,pending,upper,physical,chrChecks=0,nil,0,{},0
local screenshot,spend,refill=nil,nil,nil
local csv=assert(io.open(OUTPUT..'earned-components.csv','w'))
csv:write('event,wall,update,case,phase,age,item,power,carried,hearts,status,shots,value,pc,bank,cycle\n')
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(at)local p=emu.convertAddress(at);return p and p.address//8192 or-1 end
local function pool()local n=0;for i=0,3 do if r('Cv3ShotType',i)~=0 then n=n+1 end end;return n end
local function owned()return r('Cv3Power',C.variant_value-1)end

local function stock(item)return r('Cv3Hearts',C.variant_value-1)end
local function event(kind,value)
 local s=emu.getState();local item=rec and rec.item or 0
 csv:write(table.concat({kind,wall,updates,index,phase,age,item,owned(),r('Cv3Subweapon',C.variant_value-1),stock(item<16 and item or C.plan[index].ammo_item),r('PlayerStatus'),pool(),value or 0,s['cpu.pc'],bank(s['cpu.pc']),s['cpu.cycleCount']},',')..'\n')
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
local forbidden={InvOwnedLo=true,InvOwnedHi=true,InvViewedLo=true,InvViewedHi=true,InvSelected=true,InvAmmo=true,PlayerStatus=true,PlayerSize=true,GuestPowerupActive=true,GuestPowerupTarget=true,GameEngineSubroutine=true,InjuryTimer=true,GuestHurtTicks=true,MmDeathFlag=true,Cv3Health=true,Cv3Hearts=true,Cv3Power=true,Cv3Subweapon=true,Cv3Ready=true,Cv3Bat=true,Cv3BatTransform=true,Cv3Climb=true,Cv3AttackAge=true,Cv3ShotType=true,AvStopwatch=true,Cv3FrozenTimer=true,AvFrozen=true,AvFrozenHi=true,CheatInvincible=true}
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
 assert(pool()==0 and r('Cv3AttackAge')==0 and r('Cv3Bat')==0 and r('Cv3Climb')==0 and r('AvStopwatch')==0 and r('Cv3DropType',0)==0 and r('Cv3DropType',1)==0,'Prior native CV3 effects/drops/abilities cleaned up')
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
 for _,a in ipairs({{'Enemy_Flag',1},{'Enemy_ID',0x2e},{'Enemy_State',128},{'Enemy_BoundBoxCtrl',3},{'Enemy_X_Position',64},{'Enemy_PageLoc',0},{'Enemy_Y_Position',184},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_SprAttrib',0},{'PowerUpType',item==208 and 0 or 1},{'InvPickupOwner',C.character},{'InvPickup',item}})do w(a[1],a[2],5)end
 w('Cv3PickupVariant',C.variant_value,5)
end
local function target(x,y)
 for _,a in ipairs({{'Enemy_Flag',1},{'Enemy_ID',6},{'Enemy_State',0},{'Enemy_X_Position',x},{'Enemy_PageLoc',0},{'Enemy_Y_Position',y},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_Y_MoveForce',0},{'Enemy_MovingDir',1},{'Enemy_BoundBoxCtrl',9},{'EnemyOffscrBitsMasked',0},{'Enemy_CollisionBits',0},{'MmEnemyHealthLo',0},{'MmEnemyHealthHi',0},{'MmEnemyFlash',0},{'RgEnemyStun',0}})do w(a[1],a[2],0)end
end
local function change(p)phase=p;age=0;event('phase')end

local function coldHearts()return r('Cv3Hearts',C.variant_value-1)end
local function change(p)phase=p;age=0;event('phase')end
local function beginCase()
 local task=assert(C.plan[index]);local h=C.variant_value-1
 assert(r('Cv3Health',h)==64 and r('Cv3Ready',h)==1,'Real source64HP initialization retained; no health/outcome seeds')
 if task.kind=='collect'and task.item~=208 then
  if C.variant_value==3 then assert(task.item==212,'Only naturally authored Alucard bolt upgrade stamp')
  else assert(task.item==208+(r('Cv3Subweapon',h)%3+1),'Real next-carried-subweapon source stamp')end
 end
 rec={case_index=index,name=task.name,item=task.item,kind=task.kind,started=wall,collections=0,heart_before=coldHearts(),health_before=r('Cv3Health',h),power_before=r('Cv3Power',h),sub_before=r('Cv3Subweapon',h),debits=0,credits=0,last_hearts=coldHearts(),heart_writes={},types={},allocations=0,defeats=0,pickup_sfx=false}
 records[#records+1]=rec
 transaction(function()
  arena()
  if task.kind=='collect'then mature(task.item)
  elseif task.kind=='heart'then
   for _,a in ipairs({{'Cv3DropType',task.item},{'Cv3DropX',72},{'Cv3DropPage',0},{'Cv3DropY',192},{'Cv3DropAge',0},{'Cv3DropVY',0},{'Cv3DropFrac',0}})do w(a[1],a[2],0)end
  elseif task.watch then target(192,184);w('Enemy_X_Speed',248,0);rec.target=true
  elseif task.kind=='wall'then for row=4,11 do w('Block_Buffer_1',0x54,row*16+7);tile(0,7,row+2,0x54)end
  elseif task.kind=='ceiling'then for col=2,9 do w('Block_Buffer_1',0x54,6*16+col);tile(0,col,8,0x54)end end
 end)
 change(task.kind)
end
local function finishCase()
 rec.completed=wall;rec.updates=age;rec.hearts_after=coldHearts();rec.health_after=r('Cv3Health',C.variant_value-1);rec.power_after=owned();rec.sub_after=r('Cv3Subweapon',C.variant_value-1);event('case-complete')
 if index==#C.plan then done=true;change('complete')else index=index+1;change('setup')end
end
local function controlledTarget()
 local task=C.plan[index]
 if rec.target or not rec.sampled then return end
 if task.melee and r('Cv3AttackAge')>=3 and r('Cv3AttackAge')<=10 then transaction(function()target(C.variant_value==1 and 89 or 92,184)end);rec.target=true;return end
 for i=0,3 do
  if task.shot>0 and r('Cv3ShotType',i)==task.shot and r('Cv3ShotPage',i)==0 and r('Cv3ShotX',i)>=100 and r('Cv3ShotX',i)<=220 and r('Cv3ShotY',i)>=40 and r('Cv3ShotY',i)<=208 then
   transaction(function()target(r('Cv3ShotX',i)-6,math.min(184,r('Cv3ShotY',i)-8))end);rec.target=true;event('real-effect-target');return
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
 local i=r('CrossoverMenuIndex');if i~=5 then local key=assert(C.navigation[i+1]);assert(key~='');return{[key]=true}end
 if r('Cv3Variant')~=C.variant_value then return{select=true}end;return{a=true}
end
hook('GameLoopOwned',function()
 if r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
 if not entered then
  if r('GameEngineSubroutine')~=8 then return end
  assert(r('SelectedCharacter')==5 and r('Cv3Variant')==C.variant_value and r('CrossoverBehaviorVersion')==1 and r('CheatInvincible')==0 and r('PlayerStatus')==0,'Genuine cold requestedCV3/Hard/cheats off')
  entered=true;change('settle')
 end
 updates=updates+1;age=age+1;assert(updates<=6500,'Finite actual update cap')
 assert(r('SelectedCharacter')==5 and r('Cv3Variant')==C.variant_value and r('CrossoverBehaviorVersion')==1 and r('CheatInvincible')==0,'Actual owner/mode stability')
 if phase=='settle'and age==30 then assert(coldHearts()==10 and owned()==0 and r('Cv3Subweapon',C.variant_value-1)==0,'Actual source cold stock/power/subweapon, never seeded');beginCase()
 elseif phase=='setup'then beginCase()elseif phase=='use'then controlledTarget()end
end)
hook('PhysicalPickup',function(s)
 if entered and phase=='collect'then assert(s['cpu.x']==5 and r('Enemy_Flag',5)~=0 and r('Enemy_ID',5)==46 and r('Enemy_State',5)>=128 and r('InvPickupOwner',5)==5 and r('InvPickup',5)==rec.item and r('Cv3PickupVariant',5)==C.variant_value,'Actual mature CV3 stamp before native actor erase');rec.collision_update=updates end
end)
local pickup
hook('Cv3CollectEntry',function(s)
 if entered and phase=='collect'then assert(s['cpu.x']==5 and rec.collision_update==updates and r('Enemy_Flag',5)==0 and r('InvPickup',5)==rec.item,'Same real collision/erase/collection owner');pickup=s['cpu.sp'];event('actual-cv3-collect-entry')end
end)
hook('Cv3CollectAccepted',function(s)
 if pickup then assert(s['cpu.sp']==pickup and r('InvPickup',5)==0 and r('Cv3PickupVariant',5)==0,'Genuine successful native pickup return');pickup=nil;rec.collections=rec.collections+1;event('actual-cv3-collect-accepted')end
end)
hook('Defeat',function(s)if entered and phase=='use'and rec.target and s['cpu.x']==0 then rec.defeats=rec.defeats+1;event('native-target-defeat')end end)
emu.addMemoryCallback(function(a,v)
 if not entered or not rec or writing or a~=C.ram.Cv3Hearts+C.variant_value-1 then return end
 local s=emu.getState();local found
 for _,o in ipairs(C.heart_writers)do if s['cpu.pc']==o.pc+3 and bank(o.pc)==o.bank then found=o;break end end
 assert(found,'Every actual heart write belongs to a compiled native store')
 for i,b in ipairs(found.bytes)do assert(emu.read(found.pc+i-1,emu.memType.nesDebug)==b,'Actual source heart-store bytes')end
 local previous=rec.last_hearts
 -- NMOS DEC's old-value RMW write is real bus traffic, not a new debit.
 if found.kind=='bat'and v==previous then event('actual-bat-rmw-old',v);return end
 if found.kind=='pickup'then assert(phase=='collect'and rec.item>=209 and rec.item<=211 and v==math.min(99,previous+5),'Actual carried pickup heart refill+5')
 elseif found.kind=='drop'then local amount=r('Cv3DropType',s['cpu.x']);assert((amount==1 or amount==5)and v==math.min(99,previous+amount),'Real physical heart actor source amount/cap');rec.credits=rec.credits+v-previous
 else assert((phase=='use'or phase=='bat')and previous>v and(previous-v==1 or found.kind=='watch-extra'and previous-v==4),'Actual native special/bat debit');rec.debits=rec.debits+previous-v end
 rec.last_hearts=v
 rec.heart_writes[#rec.heart_writes+1]={wall=wall,update=updates,previous=previous,value=v,owner=found.kind,pc=found.pc,bank=found.bank};event('native-heart-write',v)
end,emu.callbackType.write,C.ram.Cv3Hearts,C.ram.Cv3Hearts+2)
emu.addMemoryCallback(function(a,v)
 if entered and phase=='use'and v>0 and not writing then rec.types[v]=true;rec.allocations=rec.allocations+1;if v==C.plan[index].shot and not rec.allocation_dma then rec.allocation_dma=dmas end;event('native-cv3-allocation',v)end
end,emu.callbackType.write,C.ram.Cv3ShotType,C.ram.Cv3ShotType+3)
emu.addMemoryCallback(function(_,v)if entered and rec and phase=='collect'and v&C.powerup_sfx~=0 then rec.pickup_sfx=true end end,emu.callbackType.write,C.ram.Square2SoundQueue)
hook('GameLoopFinish',function()
 if not entered or done then return end
 assert(r('MmDeathFlag')==0 and r('Cv3HurtAge')==0 and r('Cv3Invul')==0 and r('GuestPowerupActive')==0,'No unrelated hurt/death or seeded protection/transform')
 if not rec then return end
 local task=C.plan[index];local h=C.variant_value-1;assert(coldHearts()==rec.last_hearts,'All native heart writes observed through committed GameLoop');event('update')
 if phase=='collect'then
  assert(age<90,'Bounded real mature collection')
  if rec.collections==1 then
   assert(r('PlayerStatus')==1 and rec.pickup_sfx and r('Enemy_Flag',5)==0,'Actual collection/status/SFX')
   if rec.item==208 then assert(r('Cv3Health',h)==math.min(64,rec.health_before+16),'Capped authentic64HP restoration')
   elseif rec.item==212 then assert(owned()==math.min(2,rec.power_before+1)and coldHearts()==rec.heart_before,'Actual bolt tier, no seeded upgrade')
   else assert(r('Cv3Subweapon',h)==rec.item-208 and coldHearts()==math.min(99,rec.heart_before+5),'Actual single carried replacement and5hearts')end
   if rec.item==208 then rec.display_dma=dmas;change('health-display')else finishCase()end
  end
 elseif phase=='health-display'or phase=='heart-display'then
  if age>=32 and dmas>=rec.display_dma+2 then screenshot=phase=='health-display'and'health-earned-capped.png'or'physical-heart-five.png';finishCase()end
 elseif phase=='heart'then
  assert(age<90,'Bounded mature physical heart collection')
  if r('Cv3DropType',0)==0 then assert(coldHearts()==math.min(99,rec.heart_before+task.item)and rec.credits==math.min(task.item,99-rec.heart_before),'Actual physical heart amount/cap');if task.item==5 then rec.display_dma=dmas;change('heart-display')else finishCase()end end
 elseif phase=='use'then
  assert(r('PlayerStatus')==1 and r('GameEngineSubroutine')==8 and r('Player_X_Position')==64,'Genuine powered owner in staged static arena')
  if task.melee and r('Cv3AttackAge')>0 and not rec.allocation_dma then rec.allocation_dma=dmas end
  if task.watch and r('AvStopwatch')>0 then
   rec.watch_ticks=(rec.watch_ticks or 0)+1;local x,y=r('Enemy_X_Position'),r('Enemy_Y_Position');assert(not rec.watch_x or rec.watch_x==x and rec.watch_y==y,'Watch genuinely freezes native actor');rec.watch_x=x;rec.watch_y=y
   rec.allocation_dma=rec.allocation_dma or dmas
   if dmas>=rec.allocation_dma+2 and not rec.sampled then rec.sampled=true;screenshot='watch-active-freeze.png'end
  end
  if r('Cv3FrozenTimer',0)>0 then rec.frozen_ticks=(rec.frozen_ticks or 0)+1;assert(r('AvFrozen',0)>0 and r('Enemy_ID',0)==6,'Actual source ice freeze owner')end
  if age>=task.limit then
   assert(pool()==0 and r('Cv3AttackAge')==0 and r('AvStopwatch')==0 and r('Cv3FrozenTimer',0)==0 and r('Cv3DropType',0)==0 and r('Cv3DropType',1)==0,'Native effect/freeze/drop cleanup')
   assert(rec.debits==(task.cost or 0)and coldHearts()==rec.heart_before-(task.cost or 0)+rec.credits,'Exact real spend plus only observed physical heart credits')
   if task.watch then assert(rec.watch_ticks==180 and r('Enemy_X_Position')~=rec.watch_x,'Strict authentic180watch updates then real resume')
   elseif task.ice then assert(rec.frozen_ticks and rec.frozen_ticks>=180,'Real sustained ice collision/freeze/expiry')
   else assert(rec.target and rec.defeats>0,'Real native target contact/defeat')end
   assert(rec.allocations==task.allocations and(task.shot==0 or rec.types[task.shot]),'Exact native projectile allocation/tier')
   assert(rec.sampled,'Intended native effect/pose survives two actual DMAs');finishCase()
  end
 elseif phase=='wall'or phase=='ceiling'then
  if r('Cv3Climb')~=0 then rec.climb_seen=true;rec.min_y=math.min(rec.min_y or 176,r('Player_Y_Position'));rec.allocation_dma=rec.allocation_dma or dmas end
  if r('Cv3Climb')==3 then rec.attached_at=rec.attached_at or age;rec.min_x=math.min(rec.min_x or 255,r('Player_X_Position'));rec.max_x=math.max(rec.max_x or 0,r('Player_X_Position'))end
  if not rec.sampled and r('Cv3Climb')~=0 and dmas>=(rec.allocation_dma or dmas)+2 and(phase=='wall'and rec.min_y<160 or phase=='ceiling'and rec.min_x<rec.max_x)then rec.sampled=true;screenshot=phase..'-native-active.png'end
  if age>=task.limit then assert(rec.sampled and r('Cv3Climb')==0 and r('Player_State')==0 and coldHearts()==rec.heart_before,'Innate climb/traverse/freshA leap/drop/landing without a resource seed');finishCase()end
 elseif phase=='bat'then
  local bat=r('Cv3Bat');rec.bat_states=rec.bat_states or{}
  if bat~=0 and(rec.bat_states[#rec.bat_states]or 0)~=bat then rec.bat_states[#rec.bat_states+1]=bat end
  if bat==2 then rec.flight_at=rec.flight_at or age;rec.flight_dma=rec.flight_dma or dmas end
  if not rec.sampled and bat==2 and r('Player_X_Position')>100 and r('Player_Y_Position')<150 and dmas>=(rec.flight_dma or dmas)+2 then rec.sampled=true;screenshot='bat-flight-native.png'end
  if age>=task.limit then assert(rec.sampled and #rec.bat_states==3 and rec.bat_states[1]==1 and rec.bat_states[2]==2 and rec.bat_states[3]==3 and bat==0 and r('Player_State')==0 and rec.debits>0 and coldHearts()==rec.heart_before-rec.debits+rec.credits,'Native36tick transforms/real flight/per60 drain/readback restore/ground');finishCase()end
 end
 if phase~='setup'and phase~='complete'then assert(age<(task.limit or 180)+60,'Finite component deadline')end
end)
-- INSERT_UNCHANGED_CURRENT_BASS_HARDWARE_GUARDS
emu.addEventCallback(function()
 if not entered then emu.setInput(menu(),0);return end
 local input={};local task=C.plan[index]
 if phase=='use'then if age>=5 and age<=8 then input.b=true;input.up=not task.primary end
 elseif phase=='wall'then if age<100 then input.right=true;input.up=true;input.a=age>=4 and age<=24 elseif age<104 then input.left=true;input.a=true end
 elseif phase=='ceiling'then
  if rec.attached_at then if age<rec.attached_at+20 then input.left=true;input.up=true elseif age<rec.attached_at+24 then input.a=true end
  else input.up=true;input.a=age>=4 and age<=28 end
 elseif phase=='bat'then
  local bat=r('Cv3Bat')
  if age<10 then input.down=age>=4 and age<=8;input.a=input.down
  elseif bat==2 then
   if age<(rec.flight_at or age)+44 then input.right=true;input.up=true
   elseif age<(rec.flight_at or age)+62 then input.right=true
   elseif r('Cv3Previous')&128==0 then input.down=true;input.a=true end
  end
 end
 emu.setInput(input,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 wall=wall+1;minSP=math.min(minSP,emu.getState()['cpu.sp'])
 if entered then local s=emu.getState();for i=0,11 do assert(s['mapper.chrBanks'..i]==physical[i],'ActualCHR hardware/latches exact');chrChecks=chrChecks+1 end end
 if entered and phase=='use'and not rec.sampled and rec.allocation_dma and dmas>=rec.allocation_dma+2 then
  local task=C.plan[index];local live=false
  if task.melee then live=r('Cv3AttackAge')>=3 and r('Cv3AttackAge')<=10
  elseif task.shot>0 then for i=0,3 do if r('Cv3ShotType',i)==task.shot and r('Cv3ShotPage',i)==0 and r('Cv3ShotX',i)>=100 and r('Cv3ShotX',i)<=232 and r('Cv3ShotY',i)>=32 and r('Cv3ShotY',i)<=216 then live=true;rec.sample_slot=i;break end end end
  if live then rec.sampled=true;rec.sample_dma=dmas;rec.sample_wall=wall;screenshot=task.name..'.png'end
 end
 if screenshot then assert(images<8,'Eight selected genuine effect images maximum');local f=assert(io.open(OUTPUT..screenshot,'wb'));f:write(emu.takeScreenshot());f:close();images=images+1;screenshot=nil end
 assert(wall<C.frame_limit,'Finite whole run cap')
 if done then
  assert(not pending and not pickup and dmas>100 and nmis>100 and irqCount>100 and enables>100 and late==0,'All original full hardware/source guards actually exercised')
  local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=true,native_run=true,ROM_sha256=C.ROM_sha256,identity=C.family,variant=C.variant_value,mode=1,cases=records,wall=wall,updates=updates,complete256_DMAs=dmas,NMI_checks=nmis,IRQ31_checks=irqCount,safe_enables=enables,CHR_checks=chrChecks,minSP=minSP,screenshots=images,mature_actor_only=true,natural_reveal_or_drop_lottery=false,owned_tier_hearts_health_transform_seeded=false,goal_complete=false}));f:close();csv:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
