-- New current Bowser stock witnesses. Original M/F and traversal policy retained.
local moveEntries,moveReturns,tailEntries,tailReturns,coreEntries,coreReturns=0,0,0,0,0,0
local pendingMove,pendingTail,pendingCore,pendingStock,pendingScore
local dynamic={}
local function br(n,i)return read(assert(BStock.ram[n],n)+(i or 0))end
local function score()local n=0;for i=0,5 do local d=br('Player1ScoreDisplay',i);assert(d<10);n=n*10+d end;return n end
local function sample()
 local s=state();s.core=coreReturns;s.tail=tailReturns;s.tier=work3(0xbe28);s.power=r('PlayerStatus');s.star=br('StarInvincibleTimer');s.score=score();s.vx=br('Player_X_Speed');s.vy=br('Player_Y_Speed');return s
end
local function hook(name,fn)
 local h=BStock.hooks[name]
 emu.addMemoryCallback(guard(function()
  local q=emu.convertAddress(h.pc);local space=h.space=='work'and emu.memType.nesWorkRam or emu.memType.nesPrgRom
  if not q or q.memType~=space or q.address~=h.offset then return end
  for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Current owned stock hook '..name)end;fn()
 end),emu.callbackType.exec,h.pc)
end
local function returning(fn)
 local sp=emu.getState()['cpu.sp'];local pc=(read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1)&65535
 local t={pc=pc,sp=(sp+2)&255}
 if not dynamic[pc]then
  dynamic[pc]={};emu.addMemoryCallback(guard(function()
   local list=dynamic[pc];local sp=emu.getState()['cpu.sp']
   for i=#list,1,-1 do local p=list[i];if p.sp==sp then table.remove(list,i);p.fn(p)end end
  end),emu.callbackType.exec,pc)
 end
 t.fn=fn;dynamic[pc][#dynamic[pc]+1]=t;return t
end
hook('BwMovement',function()
 if not stock.readback then
  for i=1,#BStock.code_hex,2 do assert(work3(0xa000+(i-1)//2)==tonumber(BStock.code_hex:sub(i,i+1),16),'Actual entire loaded executable before first movement')end
  for i=1,#BStock.cookie,2 do assert(work3(0xbfe0+(i-1)//2)==tonumber(BStock.cookie:sub(i,i+1),16),'Actual loaded Bowser cookie')end
  stock.readback={pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],frame=frames,bytes=#BStock.code_hex//2,cookie=true}
 end
 assert(not pendingMove);moveEntries=moveEntries+1;pendingMove=returning(function()moveReturns=moveReturns+1;pendingMove=nil end)
end)
hook('BwWeaponTail',function()assert(not pendingTail);tailEntries=tailEntries+1;pendingTail=returning(function()tailReturns=tailReturns+1;pendingTail=nil end)end)
hook('BwCoreFinish',function()assert(not pendingCore);coreEntries=coreEntries+1;pendingCore=returning(function()coreReturns=coreReturns+1;pendingCore=nil end)end)
local function actor()for i=0,5 do local a=item(i);if a.flag==1 and a.id==46 and a.kind==BStock.kind then return a end end end
local function box(name,i)local q={};for j=0,3 do q[#q+1]=br(name,(i or 0)*4+j)end;return q end
hook('BwPickup',function()
 if not game or not stock.active then return end
 local i=emu.getState()['cpu.x'];local a=item(i);if a.flag~=1 or a.id~=46 or a.kind~=BStock.kind then return end
 assert(stock.born and stock.mature and a.state>=128 and not pendingStock,'Actual mature Bowser stock collector')
 local pb,ib=box('BoundingBox_UL_Corner'),box('EnemyBoundingBoxCoord',i)
 local w=math.min(pb[3],ib[3])-math.max(pb[1],ib[1])+1;local h=math.min(pb[4],ib[4])-math.max(pb[2],ib[2])+1
 assert(w>0 and h>0,'Native inclusive physical overlap')
 stock.collector={s=sample(),actor=a,player_box=pb,item_box=ib,overlap={w,h},pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp']}
 pendingStock=returning(function(t)
  local popup=BStock.kind==3 and 11 or 6
  assert(stock.erase and stock.setup and read(F.Enemy_Flag+i)==0 and read(F.FloateyNum_Control+i)==popup,'Real erase/popup')
  assert(r('Square2SoundQueue')==32 and r('GuestPowerupActive')==0,'Native stock grab cue and no upgrade freeze')
  if BStock.kind==2 then assert(br('StarInvincibleTimer')==35 and br('AreaMusicQueue')==64,'Real Star35/music64')end
  stock.collected={s=sample(),pc=t.pc,sp=t.sp,popup=popup};pendingStock=nil;pad=0
 end)
end)
hook('EraseEnemyObject',function()if pendingStock then stock.erase=sample()end end)
hook('SetupFloateyNumber',function()if pendingStock then assert(emu.getState()['cpu.a']==6);stock.setup=sample()end end)
hook('TimerDEC',function()
 if BStock.kind~=2 or not stock.collected or stock.credit or pendingScore then return end
 local cpu=emu.getState();local i=cpu['cpu.x']
 if i~=stock.collector.actor.slot or read(F.FloateyNum_Control+i)~=6 or br('FloateyNum_Timer',i)~=43 then return end
 assert(cpu['cpu.a']==43 and cpu['cpu.y']==6,'Real native timer43/control6 credit branch')
 stock.writer={s=sample(),pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],timer=43,control=6,slot=i};local before=score()
 pendingScore=returning(function(t)
  assert(score()==before+1000,'Actual delayed1000 credit return')
  stock.credit={s=sample(),core=coreReturns,tail=tailReturns,before=before,after=score(),pc=t.pc,sp=t.sp};pendingScore=nil
 end)
end)
hook('LifeBefore',function()
 if BStock.kind~=3 or not stock.collected or stock.life_credit then return end
 local cpu=emu.getState();local i=cpu['cpu.x'];if i~=stock.collector.actor.slot then return end
 assert(cpu['cpu.y']==11 and read(F.FloateyNum_Control+i)==11 and r('NumberofLives')==2,'Actual delayed1UP writer')
 stock.life_before={s=sample(),pc=cpu['cpu.pc'],sp=cpu['cpu.sp']}
end)
hook('LifeAfter',function()
 if not stock.life_before or stock.life_credit then return end
 assert(r('NumberofLives')==3 and r('Square2SoundQueue')==64,'Actual INC2->3/cue64')
 stock.life_credit={before=stock.life_before,s=sample(),cue=64};stock.credit={s=sample(),core=coreReturns,tail=tailReturns}
end)
local function direction(target)local at=x();return at<target and 1 or(at>target+1 and 2 or 0)end
function stockDrive()
 assert(updates-stock.since<1800,'Bounded ordinary stock continuation')
 assert(br('CrossoverBehaviorVersion')==0 and br('CheatInvincible')==0 and br('CheatStartLevel')==0,'Easy/default/no cheats')
 local s=sample();local a=actor()
 if a then
  if not stock.born then assert(a.x==(BStock.kind==3 and 1024 or 1616),'Authored native stock block');stock.born={s=s,actor=a}end
  if a.state>=128 then stock.mature=stock.mature or{s=s,actor=a}end
  if updates%16==0 and#stock.trace<16 then stock.trace[#stock.trace+1]={s=s,actor=a}end
 end
 if stock.collected then
  pad=0
  if stock.credit then
   stock.resumed=coreReturns-stock.credit.core;stock.tail_resumed=tailReturns-stock.credit.tail
   assert(stock.resumed<=25,'Exactly25 original full-step returns')
   if stock.resumed==25 then
    assert(stock.tail_resumed==25 and#pending==0 and not pendingMove and not pendingTail and not pendingCore,'Actual Main return after25 complete guest/tail returns')
    assert(stock.born and stock.mature and stock.collector and stock.erase and stock.setup and stock.readback,'Full real stock lifecycle')
    assert(work3(0xbe28)==stock.collector.s.tier and r('PlayerStatus')==stock.collector.s.power,'Stock preserves earned Bowser tier')
    if BStock.kind==3 then assert(stock.life_credit and s.lives==3)else assert(s.lives==2 and s.star>0)end
    stock.counts={movement_entries=moveEntries,movement_returns=moveReturns,tail_entries=tailEntries,tail_returns=tailReturns,core_entries=coreEntries,core_returns=coreReturns}
    stock.actual_Main_return={pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],updates=updates}
    finish(true,'Natural Bowser '..BStock.key..' and25 original full-step/outer-tail returns at actual Main return')
   end
  end;return
 end
 if a then
  if BStock.kind==3 and(a.state<128 or a.y<s.y-16)then stock.phase='intercept';pad=direction(1058);return end
  if a.state<128 then pad=0;return end
  stock.phase='collect';pad=direction(a.x-4)
  if s.native_state==0 and a.y<s.y-12 and math.abs(a.x-s.x)<48 and updates-(stock.lastJump or-100)>40 then stock.lastJump=updates end
  if stock.lastJump and updates-stock.lastJump<18 then pad=pad|128 end
  return
 end
 if stock.phase=='star-travel'then
  if s.x<1592 then traversalDrive();return end
  stock.phase='align';stock.release=nil;pad=0
 end
 if stock.phase=='align'then
  local target=BStock.kind==3 and 1016 or 1608
  pad=direction(target)
  if s.x>=target and s.x<=target+1 and s.native_state==0 then
   pad=0;stock.release=stock.release or updates
   if updates-stock.release>=4 and br('PreviousA_B_Buttons')&128==0 then
    stock.phase='head';stock.headAt=updates;stock.request=s;stock.tile=tile(BStock.kind==3 and 1024 or 1616,BStock.kind==3 and 128 or 144)
    assert(BStock.kind~=3 or stock.tile==96,'Actual hidden60 tile');pad=128
   end
  else stock.release=nil end
 elseif stock.phase=='head'then
  assert(updates-stock.headAt<150,'Ordinary head-bump admission bound');pad=updates-stock.headAt<12 and 128 or 0
 end
end
