"""Strict590 Gimmick genuine M, hidden1UP and actual delayed life credit."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import replay_gimmick_pipe_handshake_current_1115 as Previous

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN
Frozen,IDENTITIES,normalize=Previous.Frozen,Previous.IDENTITIES,Previous.normalize
PARENT_SOURCE='1199acdfd81f540d2398f7f8c13623c539c7d2e362b7dd26b1161d469e70749d'
PARENT_LUA='a3e7f6b318154b046674f061ba6a54b815d6934d1e783e91a88588787fce17b3'
once=Previous.once


@lru_cache(maxsize=1)
def bindings(raw,key='mr_gimmick'):
    q=deepcopy(Previous.bindings(raw,key));b=dict(W.Symbols.bundle(),raw=raw)
    for name in('FloateyNum_Timer','GmLife','GuestPowerupActive','Square2SoundQueue'):
        q['ram'][name]=W.address(b,name)
    def hook(label,at,pc):
        bank=(at-16)//8192;start=16+bank*8192
        q['hooks'][label]=dict(pc=pc,offset=at-16,bytes=list(raw[at:at+8]),bank=bank,
            bank_SHA256=sha256(raw[start:start+8192]).hexdigest())
    for name in('EraseEnemyObject','SetupFloateyNumber'):
        hook(name,W.location(b,name),W.address(b,name))
    name='MarioSourcePowerupCollision';at=W.location(b,name);pc=W.address(b,name)
    hook(name,at,pc);ctrl=W.address(b,'FloateyNum_Control')
    store=bytes((0x95,ctrl))if ctrl<256 else bytes((0x9d,ctrl&255,ctrl>>8))
    pattern=bytes((0xa9,11))+store+bytes((0x60,))
    hits=[i for i in range(160-len(pattern))if raw[at+i:at+i+len(pattern)]==pattern]
    assert len(hits)==1,('Actual current popup11 return',hits)
    delta=hits[0]+len(pattern)-1;hook('StockOneupReturn',at+delta,pc+delta)
    name='FloateyNumbersCore';at=W.location(b,name);pc=W.address(b,name)
    life=W.address(b,'NumberofLives');queue=W.address(b,'Square2SoundQueue')
    inc=bytes((0xe6,life))if life<256 else bytes((0xee,life&255,life>>8))
    sta=bytes((0x85,queue))if queue<256 else bytes((0x8d,queue&255,queue>>8))
    hits=[i for i in range(128-len(inc)-len(sta)-2)if raw[at+i:at+i+len(inc)]==inc and raw[at+i+len(inc):at+i+len(inc)+2]==bytes((0xa9,64))and raw[at+i+len(inc)+2:at+i+len(inc)+2+len(sta)]==sta]
    assert len(hits)==1,('Actual delayed INC life/cue64',hits)
    delta=hits[0];hook('StockCreditBefore',at+delta,pc+delta)
    delta+=len(inc)+2+len(sta);hook('StockCreditAfter',at+delta,pc+delta)
    return q


POLICY=r'''
local phase,age='approach',0
local release,press,admitted
local function gate(c)return{poll=gmTravel.polls,read=gmTravel.reads,Main=c.frame}end
local function released(g)
 return g and gmTravel.polls-g.poll>=2 and(gmTravel.last_clear['128']or 0)>g.read
end
return function(c)
 if not firstMReady then return oldPolicy(c)end
 if phase=='approach'and c.x<960 then return oldPolicy(c)end
 if not gmStock.active then gmStock.active=true;gmTravel.request=nil;release=gate(c)end
 if gmStock.collected then return{}end
 age=age+1;assert(age<900,'Bounded ordinary hidden1UP continuation')
 local v=c.r('GmRam00CC');if v>=128 then v=v-256 end
 if phase=='approach'then
  if not c.grounded then return{left=v>0,right=v<0}end
  if c.y~=176 or c.yHigh~=1 then return{right=true}end
  phase='align'
 end
 if phase=='align'then
  local stopping=c.x+v*math.abs(v)/32
  if stopping<1016 then return{right=true}elseif stopping>1020 then return{left=true}end
  if not c.grounded or math.abs(v)>2 then return{left=v>0,right=v<0}end
  if not released(release)or c.r('GmPrevious')&128~=0 then return{}end
  assert(c.x>=1014 and c.x<=1024,'Actual center under hidden1UP')
  gmStock.hidden_tile=c.block(1024,128);assert(gmStock.hidden_tile~=0 and gmStock.hidden_tile~=0x23,'Actual parsed hidden tile')
  phase='request';press=gate(c);admitted=gmStock.jump_admissions or 0
  gmStock.request=gmTravel.snapshot();return{a=true}
 elseif phase=='release'then
  if released(release)and c.r('GmPrevious')&128==0 then phase='align'end
  return{}
 elseif phase=='request'then
  assert(c.frame-press.Main<48,'Bounded original hidden-block jump admission')
  if(gmStock.jump_admissions or 0)>admitted then phase='rise'
  elseif gmTravel.polls-press.poll>=2 and(gmTravel.last_set['128']or 0)>press.read and(gmTravel.last_fresh_read or 0)>press.read then
   phase='release';release=gate(c);gmStock.retries=(gmStock.retries or 0)+1;return{}
  else return{a=true}end
 end
 if phase=='rise'then
  if not gmStock.born then return{a=c.r('GmRam00C2')>=128}end
  phase='follow'
 end
 if phase=='follow'then
  local i=gmStock.born.actor.slot
  local a={flag=c.r('Enemy_Flag',i),id=c.r('Enemy_ID',i),kind=c.r('PowerUpType',i),state=c.r('Enemy_State',i),x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)}
  assert(a.flag==1 and a.id==46 and a.kind==3,'Follow actual hidden1UP')
  if a.state<128 then return{}end
  return{right=c.x<a.x-1,left=c.x>a.x+4}
 end
 return{}
end
'''


@lru_cache(maxsize=1)
def controller(raw,key='mr_gimmick'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT_SOURCE
    text=Previous.controller(raw,key);assert sha256(text.encode()).hexdigest()==PARENT_LUA
    prefix='local C='+Previous.Text.lua(Previous.bindings(raw,key))+'\n';assert text.startswith(prefix)
    text='local C='+Previous.Text.lua(bindings(raw,key))+'\nlocal gmStock={resume=0}\nlocal gmStockPending,gmCreditPending\n'+text[len(prefix):]
    old=Previous.Previous.Previous.policy();start=old.index("local phase,age='align',0")
    text=once(text,old[start:],POLICY.lstrip('\n'))
    text=once(text,"  if gmTravel.done then finish('four-pipes-and25-grounded-input-consumptions');return end\n",'')
    old=next(line for line in text.splitlines()if line.startswith(' local ok=reason=='))
    text=once(text,old," local ok=reason=='natural-hidden-oneup-and25-postwriter-GmMovement'and firstMReady and gmStock.born and gmStock.mature and gmStock.collector and gmStock.collected and gmStock.erase and gmStock.popup and gmStock.credit and gmStock.resume==25 and identity()and r('NumberofLives')==3 and r('GmLife')==3 and r('GmRam0346')>0")
    text=once(text,'pipe_input_diagnostic=travelReport(),','stock_oneup=gmStock,pipe_input_diagnostic=travelReport(),')
    text=once(text,"r('NumberofLives')~=2","not((not gmStock.credit and r('NumberofLives')==2)or(gmStock.credit and r('NumberofLives')==3))")
    text=once(text," if not firstMReady then return end\n local slot=emu.getState()['cpu.x'];assert(slot>=0 and slot<6)",
        " if not firstMReady or gmStock.active then return end\n local slot=emu.getState()['cpu.x'];assert(slot>=0 and slot<6)")
    observe=r'''
hook('TravelJumpAccepted',function()
 if gmStock.active then
  assert(emu.getState()['cpu.a']==172,'Actual original hidden-block jump writer')
  gmStock.jump_admissions=(gmStock.jump_admissions or 0)+1;gmStock.admission=gmTravel.snapshot()
 end
end)
hook('NrPickup',function()
 if not gmStock.active then return end
 local i=emu.getState()['cpu.x'];local a=item(i)
 assert(not gmStock.collector and gmStock.born and gmStock.mature and a.flag==1 and a.id==46 and a.kind==3 and a.state>=128,'Actual mature hidden1UP native collector')
 gmStock.collector={state=state(),actor=a,score=score(),hp=r('GmRam0346'),capacity=r('GmRam002B'),held=r('GmRam0039'),next=r('GmNextSpecial')}
end)
hook('MarioSourcePowerupCollision',function()
 if not gmStock.collector or gmStock.collected then return end
 local sp,ret=stackReturn();gmStockPending={sp=sp,ret=ret,slot=emu.getState()['cpu.x']}
 assert(gmStockPending.slot==gmStock.collector.actor.slot and r('NumberofLives')==2,'Actual native1UP owner entry')
end)
hook('GmPickup',function()assert(not gmStockPending,'Native1UP must not grant Gimmick capacity/inventory')end)
hook('EraseEnemyObject',function()
 if gmStockPending and emu.getState()['cpu.x']==gmStockPending.slot then gmStock.erase=state()end
end)
hook('SetupFloateyNumber',function()
 if gmStockPending then assert(emu.getState()['cpu.a']==6,'Actual popup setup6 before native1UP override');gmStock.popup_setup=state()end
end)
hook('StockOneupReturn',function()
 if not gmStockPending then return end
 local sp,ret=stackReturn();assert(sp==gmStockPending.sp and ret==gmStockPending.ret,'Actual native1UP caller PC/SP')
 local i=gmStockPending.slot
 assert(gmStock.erase and gmStock.popup_setup and r('Enemy_Flag',i)==0 and r('FloateyNum_Control',i)==11,'Actual erase and popup11 override')
 assert(r('GuestPowerupActive')==0 and r('NumberofLives')==2 and r('GmRam0346')==gmStock.collector.hp and r('GmRam002B')==gmStock.collector.capacity and r('GmRam0039')==gmStock.collector.held and r('GmNextSpecial')==gmStock.collector.next,'1UP preserves Gimmick health/inventory and has no freeze')
 gmStock.popup={state=state(),control=11,timer=r('FloateyNum_Timer',i)}
 gmStock.collected={state=state(),moves=gmMoves};gmStockPending=nil
end)
hook('StockCreditBefore',function()
 if not gmStock.collected or gmStock.credit then return end
 local i=emu.getState()['cpu.x'];if i~=gmStock.collector.actor.slot then return end
 assert(emu.getState()['cpu.y']==11 and r('NumberofLives')==2 and r('FloateyNum_Control',i)==11,'Actual delayed popup11 life writer')
 gmCreditPending={state=state(),slot=i,timer=r('FloateyNum_Timer',i),old_lives=r('NumberofLives'),moves=gmMoves}
end)
hook('StockCreditAfter',function()
 if not gmCreditPending then return end
 assert(r('NumberofLives')==3 and r('Square2SoundQueue')==64,'Actual INC lives2-to3/cue64')
 gmStock.credit={before=gmCreditPending,after=state(),moves=gmMoves,cue=64};gmCreditPending=nil
end)
'''
    text=once(text,"hook('GmMovement',function()",observe+"hook('GmMovement',function()")
    point=' pendingReturn=nil;updates=updates+1'
    text=once(text,point,point+r'''
 if gmStock.active and identity()then
  for i=0,5 do local a=item(i);if a.flag==1 and a.id==46 and a.kind==3 then
   if not gmStock.born then assert(a.x==1024,'Actual hidden1UP block1024');gmStock.born={state=state(),actor=a}end
   if a.state>=128 then gmStock.mature=gmStock.mature or{state=state(),actor=a}end
  end end
  if gmStock.credit then
   gmStock.resume=gmMoves-gmStock.credit.moves
   assert(gmStock.resume<=25,'Bounded strictly post-writer actual GmMovement entries')
   gmStock.final_score=score()
   if gmStock.resume==25 then finish('natural-hidden-oneup-and25-postwriter-GmMovement');return end
  end
 end''')
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='mr_gimmick'):
    q=Previous.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        scope='Current590 Gimmick genuine M, mature hidden1024/Y128 kind3 collector, native popup11/delayed INC2-to3/cue64/GmLife and25 actual post-writer movements. Source-only pending root native; no Star/fullstage/audio/visual claim')
    return q
