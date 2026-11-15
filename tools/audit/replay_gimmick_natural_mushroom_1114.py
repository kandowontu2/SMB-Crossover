"""Exactf11 Gimmick natural capacity pickup; ordinary controls, zero outputs."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import compose_battletoads_camera_handoff_1114 as Current
import replay_gimmick_private_window7_1114 as Base

R,ROM,W,N,PIN=Base.R,Base.ROM,Base.W,Base.N,Current.CANDIDATE
IDENTITIES=Base.IDENTITIES
POLICY=r'''
local phase,clock,seenShot='approach',0,false
return function(c)
 if c.r('GmRam002B')>2 then return{}end
 local item
 for i=0,5 do
  if c.r('Enemy_Flag',i)==1 and c.r('Enemy_ID',i)==46 then
   assert(c.r('PowerUpType',i)==0,'First ordinary mushroom kind')
   item={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i)}
  end
 end
 if item then
  if item.state<128 then return{}end
  return{right=c.x<item.x-1,left=c.x>item.x+4}
 end
 local star=c.r('GmRam0091')
 if c.x>=216 then seenShot=true end
 local b={b=not seenShot or star==0 or(star>=128 and star<169)}
 if phase=='approach'then
  if c.x>=306 then phase='align'else b.right=true end
 end
 if phase=='align'then
  local v=c.r('GmRam00CC');if v>=128 then v=v-256 end
  local stopping=c.x+v*math.abs(v)/32
  b.right=stopping<330;b.left=stopping>334
  if c.grounded and c.x>=329 and c.x<=334 and math.abs(v)<=2 then phase='jump';clock=c.frame;return{a=true}end
 elseif phase=='jump'then
  return{a=c.frame-clock<25}
 end
 return b
end
'''


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new,1)


def normalize(raw):return Base.normalize(Current.inverse(raw))


class Frozen:
    LuaRuntime=Base.Frozen.LuaRuntime
    normalize=staticmethod(normalize)


@lru_cache(maxsize=1)
def bindings(raw,key='mr_gimmick'):
    assert key=='mr_gimmick'and sha256(raw).hexdigest()==PIN
    parent=Current.inverse(raw);q=deepcopy(Base.bindings(parent,key));q['sha']=PIN
    b=dict(W.Symbols.bundle(),raw=raw)
    for name in('GmRam0036','GmRam0037','GmRam0038','GmNextSpecial','GmCues','GmCueCount',
                 'Player1ScoreDisplay','FloateyNum_Control','Enemy_Y_HighPos','ObjectOffset'):
        q['ram'][name]=W.address(b,name)
    for name in('NrPickup','GmPickup','GmQueueSound'):
        at=W.location(b,name);stop=at+int(b['syms'][name]['size'],0)
        assert 0<stop-at<192
        pc=W.address(b,name);bank=(at-16)//8192
        q['hooks'][name]=dict(pc=pc,offset=at-16,bytes=list(raw[at:at+8]),bank=bank)
        exits=[i for i in range(stop-at)if raw[at+i]==96]if name!='NrPickup'else[]
        assert exits or name=='NrPickup'
        for i,delta in enumerate(exits):
            q['hooks'][name+'Exit'+str(i)]=dict(pc=pc+delta,offset=at+delta-16,bytes=list(raw[at+delta:at+delta+8]),bank=bank)
    for h in q['hooks'].values():
        at=16+h['offset'];assert raw[at:at+len(h['bytes'])]==bytes(h['bytes'])
        if'bank'in h:
            lo=16+h['bank']*8192;h['bank_SHA256']=sha256(raw[lo:lo+8192]).hexdigest()
    return q


@lru_cache(maxsize=1)
def controller(raw,key='mr_gimmick'):
    parent=Current.inverse(raw);old=Base.controller(parent,key)
    assert sha256(old.encode()).hexdigest()=='84834664a8399bb5debcff2fde65912e0d6fc5fb06ed6e6223bc84786d81b3e9'
    prefix='local C='+Base.Stage.Frozen.lua(Base.bindings(parent,key))+'\n';assert old.startswith(prefix)
    q=bindings(raw,key);body=old[len(prefix):]
    body=once(body,Base.Stage.POLICY,POLICY)
    body=once(body,'local function finish(reason)',r'''
local born,mature,beforePickup,afterPickup,queued,eraseAt,resume,inspectLast=nil,nil,nil,nil,nil,nil,0,nil
local pendingPickup,pendingCue,nativeCollector
local function score()
 local value=0;for i=0,5 do local d=r('Player1ScoreDisplay',i);assert(d<10,'Numeric native score');value=10*value+d end;return value
end
local function item(i)return{slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),kind=r('PowerUpType',i),state=r('Enemy_State',i),x=pos('Enemy_X_Position','Enemy_PageLoc',i),y=r('Enemy_Y_Position',i),high=r('Enemy_Y_HighPos',i)}end
local function stackReturn()
 local sp=emu.getState()['cpu.sp'];return sp,emu.read(256+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(256+((sp+2)&255),emu.memType.nesDebug)+1
end
local function finish(reason)''')
    begin=body.index(' local ok=reason==');end=body.index('\n print(',begin)
    body=body[:begin]+" local ok=reason=='natural-mushroom-capacity-and25-resume'and born and mature and beforePickup and afterPickup and queued and eraseAt and resume==25 and identity()and r('NumberofLives')==2 and r('GmRam002B')==3 and r('GmRam0346')==3 and score()>=beforePickup.score+1000\n"+body[end:]
    body=once(body,'Gm_movement_calls=gmMoves',
        'natural_birth=born,natural_mature=mature,pickup_before=beforePickup,pickup_return=afterPickup,sound_producer=queued,erase_Main=eraseAt,resumed_source_steps=resume,final_score=score(),scope="Natural mushroom capacity/refill/collector/erase/score/cue and25 resumed source calls; not full-stage or audible-output proof",Gm_movement_calls=gmMoves')
    insert=r'''
hook('NrPickup',function()
 if not first or not active()or not identity()then return end
 assert(not nativeCollector,'Exactly one ordinary native collector')
 local slot=emu.getState()['cpu.x'];assert(slot>=0 and slot<6,'Actual native actor slot')
 local a=item(slot);assert(a.flag==1 and a.id==46 and a.kind==0 and a.state>=128,'Real mature actor at native collector before erase')
 nativeCollector={state=state(),actor=a,score=score()}
end)
hook('GmPickup',function()
 if not first or not active()or not identity()then return end
 assert(not pendingPickup and not beforePickup,'Exactly one real native collector')
 local s=emu.getState();assert(s['cpu.a']==0,'Actual mushroom callback kind0')
 local found=nativeCollector and nativeCollector.actor
 assert(found and born and mature,'Physical mature mushroom at native collector before erase')
 local sp,ret=stackReturn();pendingPickup={sp=sp,returnPC=ret}
 beforePickup={state=state(),actor=found,score=nativeCollector.score,callback_score=score(),native_collector=nativeCollector,source_HP=r('GmRam0346'),source_max=r('GmRam002B'),source_steps=gmMoves}
 assert(beforePickup.source_max==2,'Genuine initial capacity')
end)
hook('GmQueueSound',function()
 if pendingPickup and emu.getState()['cpu.a']==69 then local sp,ret=stackReturn();pendingCue={sp=sp,returnPC=ret,index=r('GmCueCount')}end
end)
for name in pairs(C.hooks)do
 if name:match('^GmQueueSoundExit')then hook(name,function()
  if not pendingCue then return end
  local sp,ret=stackReturn();assert(sp==pendingCue.sp and ret==pendingCue.returnPC,'Actual sound producer return caller')
  assert(r('GmCues',pendingCue.index)==69,'Actual original cue45 queued')
  queued={Main=updates,state=state(),code=69,index=pendingCue.index,count=r('GmCueCount')};pendingCue=nil
 end)
 elseif name:match('^GmPickupExit')then hook(name,function()
  if not pendingPickup then return end
  local sp,ret=stackReturn();assert(sp==pendingPickup.sp and ret==pendingPickup.returnPC,'Actual collector return caller')
  local p=emu.getState()['cpu.ps'];assert(p&1~=0,'Source callback accepted physical pickup')
  assert(r('GmRam002B')==3 and r('GmRam0346')==3 and queued,'Capacity and health refill after real cue')
  afterPickup={state=state(),source_steps=gmMoves,returnPC=ret,returnSP=sp};inspectLast=gmMoves;pendingPickup=nil
 end)end
end
'''
    body=once(body,"hook('GmMovement',function()",insert+"hook('GmMovement',function()")
    point=' pendingReturn=nil;updates=updates+1'
    body=once(body,point,point+r'''
 if first and active()and identity()then
  for i=0,5 do local a=item(i);if a.flag==1 and a.id==46 and a.kind==0 then
   born=born or{Main=updates,state=state(),actor=a}
   if a.state>=128 then mature=mature or{Main=updates,state=state(),actor=a}end
  end end
  if afterPickup then
   local a=item(beforePickup.actor.slot)
   if a.flag==0 then eraseAt=eraseAt or updates end
   if gmMoves~=inspectLast then resume=resume+1;inspectLast=gmMoves end
   if resume==25 then finish('natural-mushroom-capacity-and25-resume');return end
  end
 end''')
    body=once(body,'if frame>=16000 or updates>=10000','if frame>=5000 or updates>=2400')
    text='local C='+Base.Stage.Frozen.lua(q)+'\n'+body
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='mr_gimmick'):
    q=bindings(raw,key)
    return dict(ROM_SHA256=PIN,identity=key,controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        navigation=q['navigation'],normal_controls_only=True,gameplay_seeds=0,outputs=0,Mesen_run=False,
        scope='First natural kind0, capacity2-to3/refill, collector/erase/score/cue and25 resumed source calls')
