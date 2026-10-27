-- Exact earned reward credits; included lexically by the v4 shared producer.
local rewardCfg=assert(C.rewards)
local rewardBorn,rewardCollection,rewardPending={}
local rewardEvents,rewardCredits={},{}
local rewardZ,rewardQueue,rewardTick,rewardRoll
local function reward_emit(name,h,t)
 t=t or{};t.event=name;t.writer_pc=h.pc;t.physical_bank=bank(h.pc)
 t.wall=wall;t.update=updates;t.phase=phase;rewardEvents[#rewardEvents+1]=t
end
local function reward_prepare(name,field,index,want,a,h,item,award,amount)
 assert(not rewardPending,'No overlapping resource credit')
 local at=assert(C.ram[field])+index
 local ix=assert(rewardCfg.resource_index[tostring(at)])+1
 local old=r(field,index)
 assert(initial and initial[ix]==old and a==want,'Exact source resource arithmetic and conserved old value')
 rewardPending={writer_pc=h.pc,physical_bank=bank(h.pc),address=at,field=field,index=index,
  old=old,new=a,item_kind=item,award_count=award or 0,award_amount=amount or 0,rule=name,
  wall=wall,update=updates,phase=phase}
end
local function reward_event(name,s)
 if not initial then return end
 assert(r('SelectedCharacter')==rewardCfg.character,'Actual reward owner')
 local h=assert(C.hooks[name]);local a,x,y=s['cpu.a'],s['cpu.x'],s['cpu.y']
 local family=rewardCfg.family
 if name=='RewardGenericSpawn'then
  assert(phase=='contact'and counts.starContact==1 and x>=0 and x<4 and r('InvDropKind',x)==0 and r('InvDropEnemy')==0 and r('Enemy_ID',0)==6,'Actual protected enemy drop spawn')
  local rng=r('PseudoRandomBitReg',2)
  assert(r('PseudoRandomBitReg',1)&3==0 and a==(rng<192 and 1 or 2),'Actual source drop chance/size')
  rewardBorn[x]={kind=a,rng=rng,published=false,consumed=false}
  reward_emit(name,h,{slot=x,old=0,new=a,item_kind=a,award_count=0})
 elseif name=='RewardGenericPublished'then
  local b=assert(rewardBorn[x]);assert(not b.published,'One source publication')
  local kind,item=r('InvDropKind',x),r('AvDropItem',x)
  assert(kind==(b.rng<(family=='generic'and 205 or 192)and 1 or 2),'Actual post-family drop size')
  assert(item==(family=='generic'and 0 or rewardCfg.darkwing_items[(b.rng&7)+1]),'Actual final private item')
  b.kind,b.item,b.published=kind,item,true
  reward_emit(name,h,{slot=x,item_kind=item,drop_size=kind,award_count=0})
 elseif name=='RewardGenericCollect'then
  local b=assert(rewardBorn[x])
  assert(phase=='expiry'and b.published and not b.consumed and r('InvDropKind',x)==b.kind and r('AvDropItem',x)==b.item,'Real spawned drop reaches passed collision predicate')
  assert(r('InvDropSlot')==x and r('InvDropAge',x)>0 and r('InvDropAgeHi',x)==0 and not rewardCollection,'Actual private collector slot/age')
  rewardCollection={slot=x,kind=b.kind,item=b.item,amount=b.kind==2 and 40 or 8,refill=false,credited=false,give=false}
  reward_emit(name,h,{slot=x,item_kind=b.item,drop_size=b.kind,award_count=1})
 elseif name=='RewardRefillEntry'then
  local q=assert(rewardCollection)
  assert(not q.refill and a==q.amount and r('AvRefillItem')==q.item and r('InvDropSlot')==q.slot,'Actual refill route after physical collection');q.refill=true
 elseif name=='RewardGenericAmmo'then
  local q=assert(rewardCollection)
  assert(family=='generic'and q.refill and not q.credited and q.item==0 and x==16*rewardCfg.character and r('InvItem')==0 and r('InvDropAmount')==q.amount,'Actual owner/item refill writer')
  local amount
  if rewardCfg.character==5 then amount=q.amount==40 and 5 or 1 else amount=q.amount==40 and 10 or 5 end
  local cap=rewardCfg.generic_caps[tostring(rewardCfg.character)]
  if rewardCfg.character==10 and r('InvOwnedLo',10)&128~=0 then cap=99 end
  reward_prepare(name,'InvAmmo',x,math.min(r('InvAmmo',x)+amount,cap),a,h,q.item,1,amount);q.credited=true
 elseif name=='RewardDwEntry'then
  local q=assert(rewardCollection)
  assert(q.refill and not q.give and a==q.item and a>=0x22 and a<=0x25,'Actual Darkwing source item grant')
  assert(r('DwHealth')==4,'Star protection retains full cold health before reward heal');q.give=true
 elseif name=='RewardDwGas'then
  local q=assert(rewardCollection)
  assert(family=='darkwing'and q.give and not q.credited and(q.item==0x24 or q.item==0x25),'Actual collected gas item')
  local amount=q.item==0x24 and 10 or 1
  reward_prepare(name,'DwGas',0,math.min(r('DwGas')+amount,99),a,h,q.item,1,amount);q.credited=true
 elseif name=='RewardGenericReturn'then
  local q=assert(rewardCollection)
  assert(q.refill and((family=='generic'or q.item==0x24 or q.item==0x25)and q.credited or family=='darkwing'and(q.item==0x22 or q.item==0x23)and q.give),'No credit from spawn alone')
  assert(r('InvDropKind',q.slot)==q.kind,'Actual collected drop retains type before clear')
  rewardBorn[q.slot].consumed=true;rewardCollection=nil
 elseif name=='RewardZ2Accepted'then
  assert(phase=='contact'and counts.starContact==1 and x==0 and r('Enemy_ID',0)==6 and r('Z2EnemyExpReceipt',0)&128==0 and a==(r('Z2EnemyExpReceipt',0)|128)and not rewardZ,'One actual accepted Goomba defeat receipt')
  assert(rewardCfg.enemy_exp==2 and rewardCfg.enemy_group==1,'Actual compiled Goomba reward table')
  rewardZ={exp=r('Z2ExpLo')+256*r('Z2ExpHi'),queued=false,rolled=false}
  reward_emit(name,h,{enemy_slot=0,item_kind='Goomba-EXP2/weak-counter',old=r('Z2EnemyExpReceipt',0),new=a,award_count=0})
 elseif name=='RewardZ2Queue'then
  assert(rewardZ and not rewardZ.queued and a==2 and y==0 and r('Z2HitSlot')==0,'Exact accepted reward queue entry')
  rewardQueue=r('Z2ExpPendingLo')+256*r('Z2ExpPendingHi')+a;assert(rewardQueue<=65535,'Cold Goomba cannot overflow');rewardZ.queued=true
 elseif name=='RewardZ2QueueLo'or name=='RewardZ2QueueHi'then
  assert(rewardQueue,'Actual reward queue context')
  local low=name=='RewardZ2QueueLo'
  reward_prepare(name,low and'Z2ExpPendingLo'or'Z2ExpPendingHi',0,low and(rewardQueue&255)or(rewardQueue>>8),a,h,'EXP2',low and 1 or 0,low and 2 or 0)
 elseif name=='RewardZ2QueueLoCap'or name=='RewardZ2QueueHiCap'then error('Cold Goomba EXP2 cannot overflow')
 elseif name=='RewardZ2Roll'then
  assert(rewardZ and not rewardZ.rolled and a==1 and r('Z2DropCounters')==0,'Actual first weak-defeat count');rewardRoll=1;rewardZ.rolled=true
 elseif name=='RewardZ2Counter'then
  assert(rewardRoll==1,'Accepted source drop counter context')
  reward_prepare(name,'Z2DropCounters',0,1,a,h,'weak-defeat-counter',0,1)
 elseif name=='RewardZ2CounterWrap'then error('One cold Goomba cannot wrap source drop count')
 elseif name=='RewardZ2Tick'then
  local pending=r('Z2ExpPendingLo')+256*r('Z2ExpPendingHi')
  if pending>0 then
   assert(rewardZ and rewardZ.queued,'Exact previously earned pending EXP')
   local amount=pending>=10 and 10 or 1
   rewardTick={pending=pending-amount,exp=(r('Z2ExpLo')+256*r('Z2ExpHi')+amount)&65535,amount=amount}
  else rewardTick=nil end
 elseif name:sub(1,12)=='RewardZ2Tick'then
  local t=assert(rewardTick)
  local fields={RewardZ2TickPendingLo='Z2ExpPendingLo',RewardZ2TickPendingHi='Z2ExpPendingHi',RewardZ2TickExpLo='Z2ExpLo',RewardZ2TickExpHi='Z2ExpHi'}
  local field=assert(fields[name]);local value=name:find('Pending',1,true)and t.pending or t.exp
  value=name:sub(-2)=='Lo'and(value&255)or(value>>8)
  reward_prepare(name,field,0,value,a,h,'EXP-transfer',0,t.amount)
 else error('Unbound reward rule '..name)end
end
for _,name in ipairs(rewardCfg.order)do hook(name,function(s)reward_event(name,s)end)end
for _,target in ipairs(rewardCfg.targets)do
 emu.addMemoryCallback(function(at,value)
  if not initial then return end
  local ix=assert(rewardCfg.resource_index[tostring(at)])+1
  if rewardPending then
   local p=rewardPending;local s=emu.getState()
   assert(at==p.address and value==p.new and s['cpu.pc']==p.writer_pc+3 and bank(p.writer_pc)==p.physical_bank,'Actual exact committed resource writer PC/bank/value')
   assert(emu.read(at,emu.memType.nesDebug)==p.old,'Actual resource old value at writer')
   p.observed_write_callback_pc=s['cpu.pc'];initial[ix]=value;rewardCredits[#rewardCredits+1]=p;rewardPending=nil
  else assert(value==initial[ix],'Uncredited resource change remains forbidden')end
 end,emu.callbackType.write,target)
end
local function reward_finish()
 assert(not rewardPending and not rewardCollection,'Every exact credit committed through real collection')
 for _,b in pairs(rewardBorn)do assert(b.consumed,'Spawn alone is never an earned resource credit')end
 if rewardCfg.family=='z2'then
  assert(rewardZ and rewardZ.queued and rewardZ.rolled and r('Z2ExpPendingLo')==0 and r('Z2ExpPendingHi')==0,'Complete exact accepted EXP transfer')
  assert(r('Z2ExpLo')+256*r('Z2ExpHi')==rewardZ.exp+2 and r('Z2DropCounters')==1,'Exact final Goomba reward/counter conservation')
 end
end
