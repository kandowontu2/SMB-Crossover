"""Strict590 Gimmick genuine M then ordinary native1616 Star acquisition."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import replay_gimmick_natural_oneup_current_1115 as Previous

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN
Frozen,IDENTITIES,normalize=Previous.Frozen,Previous.IDENTITIES,Previous.normalize
PARENT_SOURCE='50577cb038ceb8218441f7817489f4c4c117422febc07725a93e9e5e416db25c'
PARENT_LUA='8c14fb7d3ee12d468a1cdc1490366455d71d8179fff1162db046cf21a2d3bdce'
once=Previous.once


@lru_cache(maxsize=1)
def bindings(raw,key='mr_gimmick'):
    q=deepcopy(Previous.bindings(raw,key));b=dict(W.Symbols.bundle(),raw=raw)
    q['ram']['AreaMusicQueue']=W.address(b,'AreaMusicQueue')
    at=W.location(b,'MarioSourcePowerupCollision');pc=W.address(b,'MarioSourcePowerupCollision')
    def sta(address):return bytes((0x85,address))if address<256 else bytes((0x8d,address&255,address>>8))
    head=bytes((0xa9,35))+sta(W.address(b,'StarInvincibleTimer'))+bytes((0xa9,64))
    pattern=head+sta(W.address(b,'AreaMusicQueue'))+bytes((0x60,))
    hits=[i for i in range(96-len(pattern))if raw[at+i:at+i+len(pattern)]==pattern]
    assert len(hits)==1,('Actual native Star timer35/music64 return',hits)
    delta=hits[0]+len(pattern)-1;bank=(at-16)//8192;start=16+bank*8192
    q['hooks']['StockStarReturn']=dict(pc=pc+delta,offset=at+delta-16,bytes=list(raw[at+delta:at+delta+8]),bank=bank,
        bank_SHA256=sha256(raw[start:start+8192]).hexdigest())
    return q


def policy():
    travel=Previous.Previous.TRAVEL;start=travel.index(' if c.x>=976');end=travel.index(' local star=',start)
    travel=travel[:start]+travel[end:]
    p=Previous.POLICY
    p=once(p,"if phase=='approach'and c.x<960 then return oldPolicy(c)end","if phase=='approach'and c.x<1552 then return transit(c)end")
    for old,new in(('stopping<1016','stopping<1608'),('stopping>1020','stopping>1612'),('c.x>=1014 and c.x<=1024','c.x>=1606 and c.x<=1616'),('c.block(1024,128)','c.block(1616,144)'),('a.kind==3','a.kind==2')):
        p=once(p,old,new)
    p=once(p,"  return{right=c.x<a.x-1,left=c.x>a.x+4}",r'''
  local b={right=c.x<a.x-8,left=c.x>a.x-3}
  gmStock.follow_trace=gmStock.follow_trace or{}
  if age%8==0 and#gmStock.follow_trace<24 then gmStock.follow_trace[#gmStock.follow_trace+1]={Main=c.frame,x=c.x,y=c.y,actor_x=a.x,actor_y=c.r('Enemy_Y_Position',i),ground=c.r('GmRam036E'),VY=c.r('GmRam00C2')}end
  if gmStock.follow_press then
   local g=gmStock.follow_press
   if(gmStock.jump_admissions or 0)>g.admissions then
    b.a=c.r('GmRam00C2')>=128
    if not b.a then gmStock.follow_press=nil;release=gate(c)end
   elseif gmTravel.polls-g.poll>=2 and(gmTravel.last_set['128']or 0)>g.read and(gmTravel.last_fresh_read or 0)>g.read then
    gmStock.follow_press=nil;release=gate(c);gmStock.follow_retries=(gmStock.follow_retries or 0)+1
   else b.a=true end
  elseif c.grounded and released(release)and c.r('GmPrevious')&128==0 and math.abs(a.x-(c.x+8))<28 and c.r('Enemy_Y_Position',i)>=128 then
   gmStock.follow_press=gate(c);gmStock.follow_press.admissions=gmStock.jump_admissions or 0;b.a=true
   gmStock.intercept_request=gmTravel.snapshot()
  end
  return b''')
    p=p.replace('hidden1UP','ordinary Star').replace('hidden-block','Star-block')
    return 'local transit=(function()\n'+travel+'\nend)()\n'+p


OBSERVE=r'''
hook('TravelJumpAccepted',function()
 if gmStock.active then
  assert(emu.getState()['cpu.a']==172,'Actual original Star-block jump writer')
  gmStock.jump_admissions=(gmStock.jump_admissions or 0)+1;gmStock.admission=gmTravel.snapshot()
 end
end)
hook('NrPickup',function()
 if not gmStock.active then return end
 local i=emu.getState()['cpu.x'];local a=item(i)
 assert(not gmStock.collector and gmStock.born and gmStock.mature and a.flag==1 and a.id==46 and a.kind==2 and a.state>=128,'Actual mature native Star collector')
 gmStock.collector={state=state(),actor=a,score=score(),hp=r('GmRam0346'),capacity=r('GmRam002B'),held=r('GmRam0039'),next=r('GmNextSpecial')}
end)
hook('MarioSourcePowerupCollision',function()
 if not gmStock.collector or gmStock.collected then return end
 local sp,ret=stackReturn();gmStockPending={sp=sp,ret=ret,slot=emu.getState()['cpu.x']}
 assert(gmStockPending.slot==gmStock.collector.actor.slot and r('StarInvincibleTimer')==0,'Actual native Star owner/no prior timer')
end)
hook('GmPickup',function()assert(not gmStockPending,'Native Star must not grant Gimmick capacity/inventory')end)
hook('EraseEnemyObject',function()
 if gmStockPending and emu.getState()['cpu.x']==gmStockPending.slot then gmStock.erase=state()end
end)
hook('SetupFloateyNumber',function()
 if gmStockPending then assert(emu.getState()['cpu.a']==6,'Actual native Star popup6');gmStock.popup={state=state(),control=6}end
end)
hook('StockStarReturn',function()
 if not gmStockPending then return end
 local sp,ret=stackReturn();assert(sp==gmStockPending.sp and ret==gmStockPending.ret,'Actual native Star caller PC/SP')
 local i=gmStockPending.slot
 assert(gmStock.erase and gmStock.popup and r('Enemy_Flag',i)==0 and r('FloateyNum_Control',i)==6,'Actual native Star erase/popup6')
 assert(r('StarInvincibleTimer')==35 and r('AreaMusicQueue')==64 and r('Square2SoundQueue')&32~=0,'Actual Star timer/music/cue producers')
 assert(r('GuestPowerupActive')==0 and r('NumberofLives')==2 and r('GmRam0346')==gmStock.collector.hp and r('GmRam002B')==gmStock.collector.capacity and r('GmRam0039')==gmStock.collector.held and r('GmNextSpecial')==gmStock.collector.next,'Star preserves Gimmick health/inventory and has no freeze')
 gmStock.collected={state=state(),moves=gmMoves,timer=35,music=64,cue=r('Square2SoundQueue')};gmStockPending=nil
end)
'''

RETURNS=r'''
 if gmStock.active and identity()then
  for i=0,5 do local a=item(i);if a.flag==1 and a.id==46 and a.kind==2 then
   if not gmStock.born then assert(a.x==1616,'Actual ordinary Star block1616');gmStock.born={state=state(),actor=a}end
   if a.state>=128 then gmStock.mature=gmStock.mature or{state=state(),actor=a}end
  end end
  if gmStock.collected then
   gmStock.resume=gmMoves-gmStock.collected.moves
   assert(gmStock.resume<=25 and r('StarInvincibleTimer')>0,'Bounded actual post-collector Star movements')
   gmStock.final_score=score()
   if score()>=gmStock.collector.score+1000 then gmStock.score_awarded=gmStock.score_awarded or{state=state(),score=score(),moves=gmMoves}end
   if gmStock.resume==25 then assert(gmStock.score_awarded,'Actual native Star1000 score credit');finish('natural-Star-and25-postcollector-GmMovement');return end
  end
 end
'''


@lru_cache(maxsize=1)
def controller(raw,key='mr_gimmick'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT_SOURCE
    text=Previous.controller(raw,key);assert sha256(text.encode()).hexdigest()==PARENT_LUA
    prefix='local C='+Previous.Previous.Text.lua(Previous.bindings(raw,key))+'\n';assert text.startswith(prefix)
    text='local C='+Previous.Previous.Text.lua(bindings(raw,key))+'\n'+text[len(prefix):]
    text=once(text,Previous.POLICY,policy())
    text=once(text,'x>=418 and x<1212 end','x>=418 and x<2100 end')
    text=once(text,'stock_oneup=gmStock,','stock_star=gmStock,')
    old=next(line for line in text.splitlines()if line.startswith(' local ok=reason=='))
    text=once(text,old," local ok=reason=='natural-Star-and25-postcollector-GmMovement'and firstMReady and gmStock.born and gmStock.mature and gmStock.collector and gmStock.collected and gmStock.erase and gmStock.popup and gmStock.score_awarded and gmStock.resume==25 and identity()and r('NumberofLives')==2 and r('GmRam0346')>0 and r('StarInvincibleTimer')>0")
    start=text.index("hook('TravelJumpAccepted',function()\n if gmStock.active then")
    end=text.index("hook('GmMovement',function()",start)
    text=text[:start]+OBSERVE+text[end:]
    start=text.index(' if gmStock.active and identity()then')
    tail="   if gmStock.resume==25 then finish('natural-hidden-oneup-and25-postwriter-GmMovement');return end\n  end\n end"
    end=text.index(tail,start)+len(tail)
    text=text[:start]+RETURNS.rstrip('\n')+text[end:]
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='mr_gimmick'):
    q=Previous.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        scope='Current590 Gimmick real M then mature ordinary1616 Star collector/native erase/popup6/timer35/music64/cue32/1000score and25 actual post-collector movements. No Flower/1UP/expiry/protected-hit/fullstage/audio/visual claim')
    return q
