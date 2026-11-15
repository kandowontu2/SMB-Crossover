"""Exact571 DK first earned mushroom: real actor/collector/tier/freeze/resume."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import replay_dk_full11_roof_score_current_1114 as Previous

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN
Frozen,IDENTITIES,normalize=Previous.Frozen,Previous.IDENTITIES,Previous.normalize
OLD_SOURCE_SHA='1990013a196589290002f9f157bca02d0899122b3cbe86d8b5b2a75f422fc2c3'
OLD_LUA_SHA='06fc29a92b783cba6dc5b86fa1c1e08bee737dec7f706a561d8b5ff4502e50cf'


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new,1)


@lru_cache(maxsize=1)
def bindings(raw,key='donkey_kong'):
    q=deepcopy(Previous.bindings(raw,key));b=dict(W.Symbols.bundle(),raw=raw)
    for name in('DkSpawn','GuestPowerupActive','Square2SoundQueue','Player1ScoreDisplay',
                 'FloateyNum_Control','BoundingBox_UL_Corner','EnemyBoundingBoxCoord','PlayerFacingDir','InjuryTimer'):
        q['ram'][name]=W.address(b,name)
    for name in('NrPickup','DkHostCollect','DkGrant','EraseEnemyObject','SetupFloateyNumber'):
        at=W.location(b,name);pc=W.address(b,name);bank=(at-16)//8192
        q['hooks'][name]=dict(pc=pc,offset=at-16,bytes=list(raw[at:at+8]),bank=bank)
        if name in('DkHostCollect','DkGrant'):
            size=int(b['syms'][name]['size'],0);assert 0<size<192
            exits=[i for i in range(size)if raw[at+i]==0x60];assert exits
            for i,delta in enumerate(exits):
                q['hooks'][name+'Exit'+str(i)]=dict(pc=pc+delta,offset=at+delta-16,
                    bytes=list(raw[at+delta:at+delta+8]),bank=bank)
    for h in q['hooks'].values():
        at=16+h['offset'];assert raw[at:at+len(h['bytes'])]==bytes(h['bytes'])
        if'bank'in h:
            at=16+h['bank']*8192;h['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
    return q


@lru_cache(maxsize=1)
def controller(raw,key='donkey_kong'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==OLD_SOURCE_SHA
    text=Previous.controller(raw,key);assert sha256(text.encode()).hexdigest()==OLD_LUA_SHA
    prefix='local C='+Frozen.lua(Previous.bindings(raw,key))+'\n';assert text.startswith(prefix)
    text='local C='+Frozen.lua(bindings(raw,key))+'\n'+text[len(prefix):]
    text=once(text,'local function finish(reason)',r'''
local dkMush={phase='settle',age=0,resume=0}
local dkMushPending,dkGrantPending,dkCollector
local function dkScore()
 local n=0;for i=0,5 do local d=r('Player1ScoreDisplay',i);assert(d<10,'Numeric native score');n=n*10+d end;return n
end
local function dkItem(i)return{slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),kind=r('PowerUpType',i),
 state=r('Enemy_State',i),x=pos('Enemy_X_Position','Enemy_PageLoc',i),y=r('Enemy_Y_Position',i),high=r('Enemy_Y_HighPos',i)}end
local function dkCall()
 local sp=emu.getState()['cpu.sp'];return sp,emu.read(256+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(256+((sp+2)&255),emu.memType.nesDebug)+1
end
local function dkBox(name,i)local a={};for n=0,3 do a[#a+1]=r(name,(i or 0)*4+n)end;return a end
local function finish(reason)''')
    begin=text.index('\n local ok=');end=text.index('\n print(',begin)
    text=text[:begin]+"\n local ok=reason=='natural-mushroom-tier-and25-resume'and dkMush.born and dkMush.mature and dkMush.before and dkMush.grant and dkMush.collected and dkMush.erase and dkMush.score and dkMush.cue and dkMush.resume==25 and identity()and r('NumberofLives')==2 and r('DkTier')==1 and r('PlayerStatus')==1 and r('GuestPowerupActive')==0\n"+text[end:]
    text=once(text,'actual_DkMovement_calls=dkMoves,','natural_mushroom=dkMush,actual_DkMovement_calls=dkMoves,')
    insert=r'''
hook('NrPickup',function()
 if not first or not identity()or not active()then return end
 local i=emu.getState()['cpu.x'];local a=dkItem(i)
 assert(not dkCollector and a.flag==1 and a.id==46 and a.kind==0 and a.state>=128,'Actual first mature mushroom at native collector')
 dkCollector={state=state(),actor=a,score=dkScore(),player_box=dkBox('BoundingBox_UL_Corner'),item_box=dkBox('EnemyBoundingBoxCoord',i)}
end)
hook('DkHostCollect',function()
 if not first or not identity()or not active()then return end
 assert(dkCollector and dkMush.born and dkMush.mature and not dkMushPending,'Real emerged actor precedes DK collector')
 local sp,ret=dkCall();dkMushPending={sp=sp,ret=ret,slot=emu.getState()['cpu.x']}
 dkMush.before={native=dkCollector,state=state(),tier=r('DkTier'),power=r('PlayerStatus'),score=dkScore(),DK_moves=dkMoves}
 assert(r('DkTier')==0 and r('PlayerStatus')==0,'Genuinely unpowered first collector')
end)
hook('DkGrant',function()
 if not dkMushPending then return end
 assert(emu.getState()['cpu.a']==0 and not dkGrantPending,'Actual physical mushroom callback kind0')
 local sp,ret=dkCall();dkGrantPending={sp=sp,ret=ret}
end)
hook('EraseEnemyObject',function()
 if dkMushPending and emu.getState()['cpu.x']==dkMushPending.slot then
  dkMush.erase={Main=updates,state=state(),slot=dkMushPending.slot,actual_entry=true}
 end
end)
hook('SetupFloateyNumber',function()
 if dkMushPending then
  assert(emu.getState()['cpu.a']==6,'Native mushroom score control6')
  dkMush.score={Main=updates,control=6,slot=emu.getState()['cpu.x']}
 end
end)
for name in pairs(C.hooks)do
 if name:match('^DkGrantExit')then hook(name,function()
  if not dkGrantPending then return end
  local sp,ret=dkCall();assert(sp==dkGrantPending.sp and ret==dkGrantPending.ret,'Actual DK grant caller return')
  assert(emu.getState()['cpu.ps']&1~=0 and r('DkTier')==1 and r('PlayerStatus')==1,'Physical mushroom earns tier1')
  dkMush.grant={state=state(),returnPC=ret,returnSP=sp,tier=r('DkTier')};dkGrantPending=nil
 end)
 elseif name:match('^DkHostCollectExit')then hook(name,function()
  if not dkMushPending then return end
  local sp,ret=dkCall();assert(sp==dkMushPending.sp and ret==dkMushPending.ret,'Actual DK collector caller return')
  assert(dkMush.grant and dkMush.erase and dkMush.score and r('Enemy_Flag',dkMushPending.slot)==0,'Real collector erases the actual actor')
  assert(r('Square2SoundQueue')&32~=0 and r('GuestPowerupActive')==1,'Native powerup cue and real hosted freeze')
  dkMush.cue={Main=updates,queue=r('Square2SoundQueue'),code=32}
  dkMush.collected={state=state(),tier=r('DkTier'),score=dkScore(),returnPC=ret,returnSP=sp,DK_moves=dkMoves}
  dkMush.lastMoves=dkMoves;dkMushPending=nil
 end)end
end
'''
    text=once(text,"hook('DkMovement',function()",insert+"hook('DkMovement',function()")
    marker=' pendingReturn=nil;updates=updates+1'
    text=once(text,marker,marker+r'''
 if first and identity()then
  for i=0,5 do local a=dkItem(i);if a.flag==1 and a.id==46 then
   assert(a.kind==0,'Actual first spawn chain yields a mushroom')
   dkMush.born=dkMush.born or{state=state(),actor=a}
   if a.state>=128 then dkMush.mature=dkMush.mature or{state=state(),actor=a}end
  end end
  if dkMush.collected and dkMoves~=dkMush.lastMoves and active()then
   assert(dkMoves==dkMush.lastMoves+1,'Actual resumed DK movement steps')
   dkMush.lastMoves=dkMoves;dkMush.resume=dkMush.resume+1
   assert(dkScore()>=dkMush.before.score+1000,'Actual mushroom score1000')
   if dkMush.resume==25 then finish('natural-mushroom-tier-and25-resume');return end
  end
 end''')
    old='local function controls(c)return choose(c)end'
    new=r'''local function controls(c)
 if dkMush.collected then return{}end
 local item
 for i=0,5 do local a=dkItem(i);if a.flag==1 and a.id==46 then item=a end end
 if item then
  if item.state<128 then return{}end
  return{right=c.x<item.x-1,left=c.x>item.x+4}
 end
 dkMush.age=dkMush.age+1
 assert(c.poll<1800,'Bounded ordinary first mushroom route')
 if dkMush.phase=='settle'then
  if dkMush.age<4 then return{}end;dkMush.phase='approach';dkMush.age=0
 end
 if dkMush.phase=='jump'then
  if not dkMush.admitted then
   assert(dkMush.age<32,'Actual first-block native jump admission')
   if c.state==1 and c.vy>=128 then dkMush.admitted=true;dkMush.age=0 end
   return{a=true}
  end
  return{a=dkMush.age<18}
 end
 local e=c.enemy()
 if e and e.id==6 and e.dx>0 and e.dx<=100 then return{b=c.poll%18<2}end
 if c.x>=328 then
  assert(c.grounded and not c.lastA,'Real grounded fresh jump below the first item block')
  dkMush.phase='jump';dkMush.age=0;return{a=true}
 end
 return{right=true}
end'''
    text=once(text,old,new)
    text=once(text,'if frame>=16000 or updates>=10000','if frame>=6000 or updates>=2600')
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='donkey_kong'):
    return dict(ROM_SHA256=PIN,identity=key,controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        parent_controller_SHA256=OLD_LUA_SHA,normal_controls_only=True,gameplay_seeds=0,outputs=0,Mesen_run=False,
        scope='First real mature mushroom; native collector/DK grant tier0-to1/erase/score/cue/freeze and25 resumed DK steps; no full-stage claim')
