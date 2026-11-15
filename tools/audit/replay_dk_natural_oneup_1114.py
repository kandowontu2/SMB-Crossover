"""Exact571 DK genuine M then ordinary hidden1UP/real native life credit."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import replay_dk_earned_mushroom_full11_1114 as Previous

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN
Frozen,IDENTITIES,normalize=Previous.Frozen,Previous.IDENTITIES,Previous.normalize
OLD_SOURCE_SHA='0e676063ef8bbf7cc8f2ab576662eb3aac697286a29326034f52788891d21438'
OLD_LUA_SHA='4601d3a2e38181a865436dda92101aa47f15bac56b58c382aaaacc3bea50289f'


@lru_cache(maxsize=1)
def bindings(raw,key='donkey_kong'):
    q=deepcopy(Previous.bindings(raw,key));b=dict(W.Symbols.bundle(),raw=raw)
    for name in('FloateyNum_Timer','DkLife'):q['ram'][name]=W.address(b,name)
    name='MarioSourcePowerupCollision';at=W.location(b,name);pc=W.address(b,name);bank=(at-16)//8192
    q['hooks'][name]=dict(pc=pc,offset=at-16,bytes=list(raw[at:at+8]),bank=bank)
    ctrl=W.address(b,'FloateyNum_Control')
    store=bytes((0x95,ctrl))if ctrl<256 else bytes((0x9d,ctrl&255,ctrl>>8))
    pattern=bytes((0xa9,11))+store+bytes((0x60,));hits=[i for i in range(160-len(pattern))if raw[at+i:at+i+len(pattern)]==pattern]
    assert len(hits)==1,('Actual native1UP popup11 return',hits)
    delta=hits[0]+len(pattern)-1
    q['hooks']['MarioSourceOneupReturn']=dict(pc=pc+delta,offset=at+delta-16,bytes=list(raw[at+delta:at+delta+8]),bank=bank)
    name='FloateyNumbersCore';at=W.location(b,name);pc=W.address(b,name);bank=(at-16)//8192
    life=W.address(b,'NumberofLives');queue=W.address(b,'Square2SoundQueue')
    inc=bytes((0xe6,life))if life<256 else bytes((0xee,life&255,life>>8))
    sta=bytes((0x85,queue))if queue<256 else bytes((0x8d,queue&255,queue>>8))
    hits=[]
    for i in range(128-len(inc)-len(sta)-2):
        if raw[at+i:at+i+len(inc)]==inc and raw[at+i+len(inc)]==0xa9 and raw[at+i+len(inc)+2:at+i+len(inc)+2+len(sta)]==sta:
            hits.append((i,raw[at+i+len(inc)+1]))
    assert len(hits)==1,('Actual native delayed1UP credit',hits)
    delta,cue=hits[0];q['life_cue']=cue
    for label,off in(('NativeLifeCreditBefore',delta),('NativeLifeCreditAfter',delta+len(inc)+2+len(sta))):
        q['hooks'][label]=dict(pc=pc+off,offset=at+off-16,bytes=list(raw[at+off:at+off+8]),bank=bank)
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
    once=Previous.Previous.once
    text=once(text,'local function finish(reason)',r'''
local dkLife={phase='lower',age=0,resume=0}
local dkLifePending,dkLifeCreditPending
local function finish(reason)''')
    old=next(line for line in text.splitlines()if line.startswith(' local ok='))
    text=once(text,old," local ok=reason=='natural-oneup-credit-and25-resume'and dkMush.ready and dkLife.born and dkLife.mature and dkLife.collector and dkLife.collected and dkLife.erase and dkLife.popup and dkLife.credit and dkLife.resume==25 and identity()and r('NumberofLives')==3 and r('DkLife')==3")
    text=once(text,'natural_mushroom=dkMush,','natural_mushroom=dkMush,natural_oneup=dkLife,')
    text=once(text,"r('NumberofLives')~=2", "not((not dkLife.credit and r('NumberofLives')==2)or(dkLife.credit and r('NumberofLives')==3))")
    text=once(text,"and r('InjuryTimer')==90 and r('NumberofLives')==2,'Earned tier absorbs one ordinary hit'",
        "and r('InjuryTimer')==90 and r('NumberofLives')==dkInjuryPending.before.lives,'Earned tier absorbs one ordinary hit'")
    insert=r'''
hook('NrPickup',function()
 if not first or not identity()or not active()or not dkMush.ready or dkLife.collected then return end
 local i=emu.getState()['cpu.x'];local a=dkItem(i)
 if a.kind~=3 or a.id~=46 then return end
 assert(dkLife.born and dkLife.mature and a.slot==dkLife.born.actor.slot and a.flag==1 and a.state>=128,'Actual mature hidden1UP at native collector')
 dkLife.collector={state=state(),actor=a,score=dkScore(),tier=r('DkTier'),player_box=dkBox('BoundingBox_UL_Corner'),item_box=dkBox('EnemyBoundingBoxCoord',i)}
end)
hook('MarioSourcePowerupCollision',function()
 if not dkLife.collector or dkLife.collected then return end
 assert(not dkLifePending and emu.getState()['cpu.x']==dkLife.collector.actor.slot,'Actual native1UP owner entry')
 local sp,ret=dkCall();dkLifePending={sp=sp,ret=ret,slot=emu.getState()['cpu.x'],tier=r('DkTier')}
 assert(r('NumberofLives')==2,'Real initial lives before1UP')
end)
hook('DkGrant',function()assert(not dkLifePending,'Native1UP must not use DK tier grant')end)
hook('EraseEnemyObject',function()
 if dkLifePending and emu.getState()['cpu.x']==dkLifePending.slot then dkLife.erase={state=state(),slot=dkLifePending.slot}end
end)
hook('SetupFloateyNumber',function()
 if dkLifePending then assert(emu.getState()['cpu.a']==6,'Real native popup setup before1UP override');dkLife.popup_setup={state=state(),control=6}end
end)
hook('MarioSourceOneupReturn',function()
 if not dkLifePending then return end
 local sp,ret=dkCall();assert(sp==dkLifePending.sp and ret==dkLifePending.ret,'Actual native1UP caller return')
 assert(dkLife.erase and dkLife.popup_setup and r('Enemy_Flag',dkLifePending.slot)==0 and r('FloateyNum_Control',dkLifePending.slot)==11,'Real1UP erase/popup11')
 assert(r('Square2SoundQueue')&32~=0 and r('DkTier')==dkLifePending.tier and r('GuestPowerupActive')==0,'1UP preserves tier without powerup freeze')
 dkLife.popup={state=state(),control=11,timer=r('FloateyNum_Timer',dkLifePending.slot)}
 dkLife.collected={state=state(),tier=r('DkTier'),returnPC=ret,returnSP=sp};dkLife.lastMoves=dkMoves;dkLifePending=nil
end)
hook('NativeLifeCreditBefore',function()
 if not dkLife.collected or dkLife.credit then return end
 local i=emu.getState()['cpu.x'];if i~=dkLife.collector.actor.slot then return end
 assert(emu.getState()['cpu.y']==11 and r('FloateyNum_Control',i)==11 and r('NumberofLives')==2,'Actual delayed popup11 life writer')
 dkLifeCreditPending={state=state(),slot=i,timer=r('FloateyNum_Timer',i),old_lives=r('NumberofLives')}
end)
hook('NativeLifeCreditAfter',function()
 if not dkLifeCreditPending then return end
 assert(r('NumberofLives')==3 and r('Square2SoundQueue')==C.life_cue,'Real INC life and native extra-life cue')
 dkLife.credit={before=dkLifeCreditPending,after=state(),cue=r('Square2SoundQueue')};dkLifeCreditPending=nil
end)
'''
    text=once(text,"hook('DkMovement',function()",insert+"hook('DkMovement',function()")
    point=' pendingReturn=nil;updates=updates+1'
    text=once(text,point,point+r'''
 if first and identity()and dkMush.ready then
  for i=0,5 do local a=dkItem(i);if a.flag==1 and a.id==46 and a.kind==3 then
   if not dkLife.born then assert(a.x==1024,'Actual hidden1UP block1024');dkLife.born={state=state(),actor=a}end
   if a.state>=128 then dkLife.mature=dkLife.mature or{state=state(),actor=a}end
  end end
  if dkLife.collected and dkMoves~=dkLife.lastMoves and active()then
   assert(dkMoves==dkLife.lastMoves+1,'Actual resumed DK steps after1UP')
   dkLife.lastMoves=dkMoves
   if dkLife.credit then
    dkLife.resume=dkLife.resume+1;dkLife.final_score=dkScore();dkLife.final_lease_life=r('DkLife')
    if dkLife.resume==25 then finish('natural-oneup-credit-and25-resume');return end
   end
  end
 end''')
    text=once(text,'local function controls(c)','local function dkMushControls(c)')
    policy=r'''
local function controls(c)
 if not dkMush.ready or(c.x<960 and dkLife.phase=='lower')then return dkMushControls(c)end
 local v=c.vx;if v>=128 then v=v-256 end
 if dkLife.collected then return{left=v>2,right=v< -2}end
 dkLife.age=dkLife.age+1;assert(dkLife.age<1000,'Bounded natural hidden1UP route')
 if dkLife.phase=='lower'then
  if not c.grounded then return{left=v>0,right=v<0}end
  if c.yHigh~=1 or c.y~=176 then return{right=true}end
  dkLife.phase='align'
 end
 if dkLife.phase=='align'then
  local stopping=c.x+v*math.abs(v)/64
  if stopping<1017 then return{right=true}elseif stopping>1021 then return{left=true}end
  if not c.grounded or math.abs(v)>4 then return{left=v>0,right=v<0}end
  if c.lastA then return{}end
  assert(c.x>=1016 and c.x<=1031,'Actual center under hidden1UP')
  dkLife.hidden_tile=c.block(1024,128);assert(dkLife.hidden_tile~=0 and dkLife.hidden_tile~=0x23,'Actual parsed hidden block exists')
  dkLife.phase='request';dkLife.request=state();dkLife.wait=0;return{a=true}
 elseif dkLife.phase=='request'then
  dkLife.wait=dkLife.wait+1;assert(dkLife.wait<32,'Actual hidden-block jump admission')
  if c.state==1 and c.vy>=128 then dkLife.phase='rise';dkLife.admission=state()end
  return{a=true}
 elseif dkLife.phase=='rise'then
  if not dkLife.born then return{a=c.vy>=128}end
  dkLife.phase='follow'
 end
 if dkLife.phase=='follow'then
  local a=dkItem(dkLife.born.actor.slot)
  assert(a.flag==1 and a.id==46 and a.kind==3,'Follow the actual hidden1UP')
  if a.state<128 then return{left=v>2,right=v< -2}end
  return{right=c.x<a.x-1,left=c.x>a.x+4}
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
        parent_earned_M_full_SHA256=OLD_LUA_SHA,normal_controls_only=True,gameplay_seeds=0,outputs=0,Mesen_run=False,
        scope='Real M then hidden1024/Y128 mature kind3 collector/popup11/actual delayed life2-to3/cue/+25 resumed DK calls; no Star or full-stage inference')
