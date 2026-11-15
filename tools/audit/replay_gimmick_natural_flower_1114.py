"""Current571 Gimmick earned mushroom followed by the real second Flower."""
from functools import lru_cache
from hashlib import sha256
import sys
from unittest.mock import patch

import check_native_floatey_score_1114 as Previous
import check_mr_gimmick_full11_current_1114 as Original
import check_smb1_alts_full11_1114 as Runner

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN
Frozen,IDENTITIES,normalize,bindings=Previous.Frozen,Previous.IDENTITIES,Previous.normalize,Previous.bindings
once=Previous.Previous.once


def policy():
    opening=Previous.Previous.POLICY
    travel=Previous.Previous.Base.Stage.POLICY
    return "local opening=(function()\n"+opening+"\nend)()\nlocal travel=(function()\n"+travel+"\nend)()\n"+r'''
local phase,age='travel',0
return function(c)
 if not firstMReady then return opening(c)end
 if flower.after then return{}end
 local item
 for i=0,5 do
  if c.r('Enemy_Flag',i)==1 and c.r('Enemy_ID',i)==46 then
   assert(c.r('PowerUpType',i)==1,'Real second block final Flower kind')
   item={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i)}
  end
 end
 if item then
  if item.state<128 then return{}end
  if phase~='side-jump'and phase~='jumping'then phase='retreat'end
  if phase=='retreat'then
   if c.x<=1216 and c.grounded then phase='side-jump';age=0;return{}end
   return{left=true}
  elseif phase=='side-jump'then
   if c.grounded and not c.lastA then phase='jumping';age=0;return{right=true,a=true}end
   return{}
  else
   age=age+1
   if age>100 and c.grounded then phase='retreat'end
   return{right=c.x<item.x+2,left=c.x>item.x+10,a=age<40}
  end
 end
 if phase=='travel'then
  if c.x>=1212 then phase='align'else return travel(c)end
 end
 if phase=='align'then
  local v=c.r('GmRam00CC');if v>=128 then v=v-256 end
  local stopping=c.x+v*math.abs(v)/32
  if c.grounded and c.x>=1241 and c.x<=1246 and math.abs(v)<=2 and not c.lastA then phase='head';age=0;return{a=true}end
  return{right=stopping<1242,left=stopping>1246}
 end
 age=age+1;return{a=age<25}
end
'''


@lru_cache(maxsize=1)
def controller(raw,key='mr_gimmick'):
    text=Previous.controller(raw,key)
    assert sha256(text.encode()).hexdigest()=='87ecd7d56e4e29f16a8e1e1bf9f8f2add1719ec5f0f226adf2ad755143341e84'
    prefix,body=text.split('\n',1)
    text=prefix+"\nlocal firstMReady\nlocal flower={resume=0}\n"+body
    text=once(text,Previous.Previous.POLICY,policy())
    for name in('NrPickup','GmPickup'):
        start="hook('"+name+"',function()\n if not first or not active()or not identity()then return end"
        text=once(text,start,start.replace('if not first','if firstMReady or not first'))
    text=once(text,'  if afterPickup then','  if afterPickup and not firstMReady then')
    text=once(text,"if resume==25 then finish('natural-mushroom-capacity-and25-resume');return end",
        "if resume==25 then assert(queued and eraseAt and score()>=beforePickup.score+1000,'Real first mushroom prefix complete');firstMReady={state=state(),score=score(),inventory=r('GmRam0039')}end")
    start=text.index(' local ok=reason==');end=text.index('\n print(',start)
    text=text[:start]+" local ok=reason=='natural-flower-inventory-and25-resume'and firstMReady and flower.born and flower.mature and flower.before and flower.after and flower.cue and flower.erase and flower.resume==25 and identity()and r('NumberofLives')==2 and r('GmRam0346')>0 and r('GmRam0039')==1 and r('GmRam0036')==2 and r('GmNextSpecial')==2 and score()>=flower.before.score+1000\n"+text[end:]
    text=once(text,'natural_birth=born,','natural_flower=flower,first_mushroom_ready=firstMReady,natural_birth=born,')
    extra=r'''
hook('NrPickup',function()
 if not firstMReady then return end
 local slot=emu.getState()['cpu.x'];assert(slot>=0 and slot<6)
 local a=item(slot);assert(a.flag==1 and a.id==46 and a.kind==1 and a.state>=128,'Physical mature Flower at native collector')
 assert(not flower.native,'Exactly one real Flower collector')
 flower.native={state=state(),actor=a,score=score()}
end)
hook('GmPickup',function()
 if not firstMReady then return end
 assert(emu.getState()['cpu.a']==1 and not flower.before,'Real Flower collector callback')
 assert(flower.native and flower.mature and r('GmRam0039')==0 and r('GmNextSpecial')==1,'Genuine initial special inventory')
 local sp,ret=stackReturn();flower.pending={sp=sp,ret=ret}
 flower.before={state=state(),score=flower.native.score,hp=r('GmRam0346'),capacity=r('GmRam002B'),actor=flower.native.actor}
end)
hook('GmQueueSound',function()
 if flower.pending and emu.getState()['cpu.a']==28 then local sp,ret=stackReturn();flower.pendingCue={sp=sp,ret=ret,index=r('GmCueCount')}end
end)
for name in pairs(C.hooks)do
 if name:match('^GmQueueSoundExit')then hook(name,function()
  if not flower.pendingCue then return end
  local sp,ret=stackReturn();assert(sp==flower.pendingCue.sp and ret==flower.pendingCue.ret)
  assert(r('GmCues',flower.pendingCue.index)==28,'Original Flower cue1c queued')
  flower.cue={Main=updates,code=28,index=flower.pendingCue.index};flower.pendingCue=nil
 end)
 elseif name:match('^GmPickupExit')then hook(name,function()
  if not flower.pending then return end
  local sp,ret=stackReturn();assert(sp==flower.pending.sp and ret==flower.pending.ret)
  assert(emu.getState()['cpu.ps']&1~=0 and flower.cue,'Real accepted Flower return')
  assert(r('GmRam0039')==1 and r('GmRam0036')==2 and r('GmNextSpecial')==2,'Original inventory code2/next special2')
  assert(r('GmRam0346')==flower.before.hp and r('GmRam002B')==flower.before.capacity,'Flower preserves health/capacity')
  flower.after={state=state(),inventory=r('GmRam0036'),next=r('GmNextSpecial')};flower.lastMoves=gmMoves;flower.pending=nil
 end)end
end
'''
    text=once(text,"hook('GmMovement',function()",extra+"hook('GmMovement',function()")
    point=' pendingReturn=nil;updates=updates+1'
    text=once(text,point,point+r'''
 if firstMReady and active()and identity()then
  for i=0,5 do local a=item(i);if a.flag==1 and a.id==46 and a.kind==1 then
   flower.born=flower.born or{state=state(),actor=a}
   if a.state>=128 then flower.mature=flower.mature or{state=state(),actor=a}end
  end end
  if flower.after then
   if r('Enemy_Flag',flower.mature.actor.slot)==0 then flower.erase=flower.erase or updates end
   if gmMoves~=flower.lastMoves then flower.resume=flower.resume+1;flower.lastMoves=gmMoves end
   if flower.resume==25 then finish('natural-flower-inventory-and25-resume');return end
  end
 end''')
    text=once(text,'if frame>=5000 or updates>=2400','if frame>=9000 or updates>=5000')
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='mr_gimmick'):
    q=Previous.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        scope='Real first mushroom plus second Flower/inventory/cue/erase/score and25 resumed calls; no full-stage/audio-output claim')
    return q


def cold(raw,key='mr_gimmick'):
    with patch.object(Original,'Factory',sys.modules[__name__]):return Original.cold(raw,key)


def run(raw,metadata_only=False):
    with patch.object(Runner,'Factory',sys.modules[__name__]),patch.object(Runner,'cold',cold):
        return Runner.strict_metadata(raw,'mr_gimmick')if metadata_only else Runner.run(raw,'mr_gimmick',5000)
