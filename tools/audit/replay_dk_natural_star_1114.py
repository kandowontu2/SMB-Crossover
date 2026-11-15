"""Exact571 DK earned M/F, actual vertical barrel, then real native Star."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import replay_dk_natural_flower_1114 as Previous

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN
Frozen,IDENTITIES,normalize=Previous.Frozen,Previous.IDENTITIES,Previous.normalize
OLD_SOURCE_SHA='02088efaefd414b65a3d5e8db19a412195634b3cceb98e7b31d33b0c07f301e6'
OLD_LUA_SHA='2bca10e74de5bebbc93259cf5dfb36e215d83500f91aa821449d8d8485b4bc01'


@lru_cache(maxsize=1)
def bindings(raw,key='donkey_kong'):
    q=deepcopy(Previous.bindings(raw,key));b=dict(W.Symbols.bundle(),raw=raw)
    q['ram']['AreaMusicQueue']=W.address(b,'AreaMusicQueue')
    name='MarioSourcePowerupCollision';at=W.location(b,name);pc=W.address(b,name);bank=(at-16)//8192
    q['hooks'][name]=dict(pc=pc,offset=at-16,bytes=list(raw[at:at+8]),bank=bank)
    def sta(address):return bytes((0x85,address))if address<256 else bytes((0x8d,address&255,address>>8))
    head=bytes((0xa9,0x23))+sta(W.address(b,'StarInvincibleTimer'))+bytes((0xa9,))
    tail=sta(W.address(b,'AreaMusicQueue'))+bytes((0x60,));hits=[]
    for i in range(96-len(head)-len(tail)-1):
        if raw[at+i:at+i+len(head)]==head and raw[at+i+len(head)+1:at+i+len(head)+1+len(tail)]==tail:
            hits.append((i,raw[at+i+len(head)]))
    assert len(hits)==1,('Actual current native Star timer/music return',hits)
    delta,music=hits[0];delta+=len(head)+1+len(tail)-1;q['star_music']=music
    q['hooks']['MarioSourceStarReturn']=dict(pc=pc+delta,offset=at+delta-16,bytes=list(raw[at+delta:at+delta+8]),bank=bank)
    for h in q['hooks'].values():
        if'bank'in h:
            start=16+h['bank']*8192;h['bank_SHA256']=sha256(raw[start:start+8192]).hexdigest()
    return q


@lru_cache(maxsize=1)
def controller(raw,key='donkey_kong'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==OLD_SOURCE_SHA
    text=Previous.controller(raw,key);assert sha256(text.encode()).hexdigest()==OLD_LUA_SHA
    prefix='local C='+Frozen.lua(Previous.bindings(raw,key))+'\n';assert text.startswith(prefix)
    text='local C='+Frozen.lua(bindings(raw,key))+'\n'+text[len(prefix):]
    once=Previous.Previous.Previous.once
    text=once(text,'local function finish(reason)',r'''
local dkStar={phase='vertical-release',age=0,resume=0}
local dkStarPending
local function finish(reason)''')
    old=next(line for line in text.splitlines()if line.startswith(' local ok='))
    text=once(text,old," local ok=reason=='natural-star-vertical-and25-resume'and dkFlower.ready and dkStar.vertical_spawn and dkStar.vertical_motion and dkStar.born and dkStar.mature and dkStar.collector and dkStar.collected and dkStar.erase and dkStar.score and dkStar.resume==25 and identity()and r('NumberofLives')==2 and r('StarInvincibleTimer')>0")
    text=once(text,'natural_flower=dkFlower,','natural_flower=dkFlower,natural_star=dkStar,')
    text=once(text,'if dkFlower.collected and dkMoves~=dkFlower.lastMoves and active()then',
        'if dkFlower.collected and dkFlower.resume<25 and dkMoves~=dkFlower.lastMoves and active()then')
    text=once(text,"if dkFlower.resume==25 then finish('natural-flower-tier2-and25-resume');return end",
        'if dkFlower.resume==25 then dkFlower.ready=state()end')
    insert=r'''
hook('NrPickup',function()
 if not first or not identity()or not active()or not dkFlower.ready or dkStar.collected then return end
 local i=emu.getState()['cpu.x'];local a=dkItem(i)
 if a.kind~=2 or a.id~=46 then return end
 assert(dkStar.born and dkStar.mature and a.slot==dkStar.born.actor.slot and a.flag==1 and a.state>=128,'Actual mature Star at native collector')
 dkStar.collector={state=state(),actor=a,score=dkScore(),tier=r('DkTier'),player_box=dkBox('BoundingBox_UL_Corner'),item_box=dkBox('EnemyBoundingBoxCoord',i)}
end)
hook('MarioSourcePowerupCollision',function()
 if not dkStar.collector or dkStar.collected then return end
 assert(not dkStarPending and emu.getState()['cpu.x']==dkStar.collector.actor.slot,'Real native Star owner entry')
 local sp,ret=dkCall();dkStarPending={sp=sp,ret=ret,slot=emu.getState()['cpu.x'],tier=r('DkTier')}
 assert(r('StarInvincibleTimer')==0,'No Star timer before real pickup')
end)
hook('DkGrant',function()assert(not dkStarPending,'Native Star must not use DK tier grant')end)
hook('EraseEnemyObject',function()
 if dkStarPending and emu.getState()['cpu.x']==dkStarPending.slot then dkStar.erase={state=state(),slot=dkStarPending.slot}end
end)
hook('SetupFloateyNumber',function()
 if dkStarPending then assert(emu.getState()['cpu.a']==6,'Real Star score control6');dkStar.score={state=state(),control=6}end
end)
hook('MarioSourceStarReturn',function()
 if not dkStarPending then return end
 local sp,ret=dkCall();assert(sp==dkStarPending.sp and ret==dkStarPending.ret,'Actual native Star caller return')
 assert(dkStar.erase and dkStar.score and r('Enemy_Flag',dkStarPending.slot)==0,'Real Star erase and score')
 assert(r('StarInvincibleTimer')==35 and r('AreaMusicQueue')==C.star_music and r('Square2SoundQueue')&32~=0,'Actual native Star timer/music/cue producers')
 assert(r('DkTier')==dkStarPending.tier and r('PlayerStatus')==r('DkTier')and r('GuestPowerupActive')==0,'Star preserves earned tier without powerup freeze')
 dkStar.collected={state=state(),tier=r('DkTier'),timer=r('StarInvincibleTimer'),music=r('AreaMusicQueue'),cue=r('Square2SoundQueue'),returnPC=ret,returnSP=sp}
 dkStar.lastMoves=dkMoves;dkStarPending=nil
end)
'''
    text=once(text,"hook('DkMovement',function()",insert+"hook('DkMovement',function()")
    point=' pendingReturn=nil;updates=updates+1'
    text=once(text,point,point+r'''
 if first and identity()and dkFlower.ready then
  for i=0,5 do local a=dkItem(i);if a.flag==1 and a.id==46 and a.kind==2 then
   if not dkStar.born then assert(a.x==1616,'Actual ordinary Star block1616');dkStar.born={state=state(),actor=a}end
   if a.state>=128 then dkStar.mature=dkStar.mature or{state=state(),actor=a}end
  end end
  if dkStar.vertical_spawn and not dkStar.vertical_motion then
   local s=dkStar.vertical_spawn;local at=12*s.slot;local k=r('DkShots',at)
   local x=r('DkShots',at+4)+256*r('DkShots',at+5);local y=r('DkShots',at+6)
   if k==2 and y>=s.y+3 then assert(x==s.x,'True vertical barrel has no horizontal drift');dkStar.vertical_motion={state=state(),kind=k,x=x,y=y}end
   if k==1 then dkStar.vertical_motion={state=state(),kind=k,x=x,y=y,scope='Native vertical-to-rolling landing, not free-fall proof'}end
  end
  if dkStar.collected and dkMoves~=dkStar.lastMoves and active()then
   assert(dkMoves==dkStar.lastMoves+1 and r('StarInvincibleTimer')>0,'Actual resumed Star-protected DK movement')
   dkStar.lastMoves=dkMoves;dkStar.resume=dkStar.resume+1;dkStar.final_score=dkScore()
   assert(dkScore()>=dkStar.collector.score+1000,'Actual native Star score1000')
   if dkStar.resume==25 then finish('natural-star-vertical-and25-resume');return end
  end
 end''')
    text=once(text,'local function controls(c)','local function dkFlowerControls(c)')
    policy=r'''
local function controls(c)
 if not dkFlower.ready then return dkFlowerControls(c)end
 if dkStar.collected then return{}end
 dkStar.age=dkStar.age+1;assert(dkStar.age<1600,'Bounded ordinary Star continuation')
 local v=c.vx;if v>=128 then v=v-256 end
 local function floor(x)local t=c.block(x,208);return t~=0 and t~=0x23 and t~=0xc2 and t~=0xc3 end
 if dkStar.phase=='vertical-release'then
  if r('DkPrevious')&64~=0 or r('DkAttack')~=0 then return{}end
  assert(r('DkTier')==2,'Genuine Flower enables vertical barrel')
  dkStar.phase='vertical-request';dkStar.vertical_request=state();dkStar.vertical_count=dkBarrelProof.count
 end
 if dkStar.phase=='vertical-request'then
  if r('DkAttack')==2 then
   assert(r('SavedJoypadBits')&68==68 and r('DkPrevious')&68==68,'Actual earned Down+B attack admission')
   dkStar.vertical_admission=state();dkStar.phase='vertical-wait'
  end
  return{down=true,b=true}
 elseif dkStar.phase=='vertical-wait'then
  for _,row in ipairs(dkBarrelProof.rows)do if row.kind==2 and row.state.Main>=dkStar.vertical_request.Main then
   assert(row.actual_Cset and row.tier==2,'Real successful tier2 vertical-barrel commit')
   dkStar.vertical_spawn=row;dkStar.phase='leave-roof';break
  end end
  if not dkStar.vertical_spawn then return{down=true,b=true}end
 end
 if dkStar.phase=='leave-roof'then
  if c.grounded and c.yHigh==1 and c.y==176 and c.x>=1280 then dkStar.phase='pit'else return{right=true}end
 end
 if dkStar.phase=='pit'then
  if c.x>=1437 and floor(c.x-13)and floor(c.x+29)then dkStar.phase='lower';return{right=true}end
  if dkStar.pit_requested then
   if not dkStar.pit_admitted then
    if c.state==1 and c.vy>=128 then dkStar.pit_admitted=state()end
    return{right=true,b=true,a=true}
   end
   return{right=true,b=true,a=c.vy>=128}
  end
  if c.grounded and not c.lastA and(not floor(c.x+48)or c.block(c.x+30,c.y+8)~=0 or c.block(c.x+30,c.y+24)~=0)then
   dkStar.pit_requested=state();return{right=true,b=true,a=true}
  end
  return{right=true,b=true}
 elseif dkStar.phase=='lower'then
  if c.grounded and c.yHigh==1 and c.y==176 then dkStar.phase='align'else return{right=true}end
 end
 if dkStar.phase=='align'then
  local stopping=c.x+v*math.abs(v)/64
  if stopping<1613 then return{right=true}elseif stopping>1619 then return{left=true}end
  if not c.grounded or math.abs(v)>4 then return{left=v>0,right=v<0}end
  if c.lastA then return{}end
  assert(c.x>=1608 and c.x<=1623 and floor(c.x-13)and floor(c.x+29),'Actual ground under Star block')
  dkStar.phase='spawn-request';dkStar.request=state();dkStar.wait=0;return{a=true,b=true}
 elseif dkStar.phase=='spawn-request'then
  dkStar.wait=dkStar.wait+1;assert(dkStar.wait<32,'Actual Star-block jump admission')
  if c.state==1 and c.vy>=128 then dkStar.phase='spawn-rise';dkStar.admission=state()end
  return{a=true,b=true}
 elseif dkStar.phase=='spawn-rise'then
  if not dkStar.born then return{a=c.vy>=128}end
  dkStar.phase='follow'
 end
 if dkStar.phase=='follow'then
  local a=dkItem(dkStar.born.actor.slot)
  assert(a.flag==1 and a.id==46 and a.kind==2,'Follow the actual uncollected Star')
  if a.state<128 then return{}end
  return{right=c.x<a.x-1,left=c.x>a.x+4,b=true}
 end
 return{}
end
'''
    text=once(text,'dkDecide=function()',policy+'\ndkDecide=function()')
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='donkey_kong'):
    return dict(ROM_SHA256=PIN,identity=key,controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        parent_natural_F_SHA256=OLD_LUA_SHA,normal_controls_only=True,gameplay_seeds=0,outputs=0,Mesen_run=False,
        scope='Real M/F, earned Down+B vertical barrel, ordinary native kind2 Star collector/timer/music/score/erase and25 protected DK steps; no 1UP claim')
