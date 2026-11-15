"""Strictae66 ordinary earned-M/real-star-boarding/Flower production replay."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import compose_battletoads_native_service_1114 as Current
import replay_gimmick_natural_flower_1114 as Previous

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Current.CANDIDATE
IDENTITIES=Previous.IDENTITIES
PARENT_SOURCE='0a665cec0ccb5f021823881a4c538a1c6328ff3767400f0c3f7d7bb9cac3c261'
PARENT_LUA='30ba432109dfe4b734ce4ebb523b74b957cd242fb855b63b722dbf0445f24cc8'
once=Previous.once


@lru_cache(maxsize=1)
def owning571(raw):
    assert isinstance(raw,bytes)and sha256(raw).hexdigest()==PIN,'Expected exact deliveredae66'
    old=Current.inverse(raw);assert sha256(old).hexdigest()==Previous.PIN
    return old


def normalize(raw):return Previous.normalize(owning571(raw))


class Frozen:
    LuaRuntime=Previous.Frozen.LuaRuntime
    normalize=staticmethod(normalize)


def policy():
    return 'local oldPolicy=(function()\n'+Previous.policy()+'\nend)()\n'+r'''
local phase,age='align',0
local function nativeStar(c)return c.r('GmRam0091')end
return function(c)
 if not firstMReady then return oldPolicy(c)end
 if flower.after then return{}end
 local mature=false
 for i=0,5 do if c.r('Enemy_Flag',i)==1 and c.r('Enemy_ID',i)==46 then
  assert(c.r('PowerUpType',i)==1,'Ordinary final Flower kind')
  mature=c.r('Enemy_State',i)>=128
 end end
 if not mature then return oldPolicy(c)end
 local v=c.r('GmRam00CC');if v>=128 then v=v-256 end
 local stopping=c.x+v*math.abs(v)/32
 if phase=='align'then
  if not(c.grounded and c.x>=1242 and c.x<=1246 and math.abs(v)<=2)then return{right=stopping<1243,left=stopping>1245}end
  if nativeStar(c)~=0 then return{}end
  phase='charge';age=0;flower.boarding_policy_start=state()
 end
 if phase=='charge'then
  age=age+1;assert(age<160,'Bounded ordinary charge')
  if nativeStar(c)>=169 then phase='right-runup'else return{b=true}end
 end
 if phase=='right-runup'then
  if c.x<1270 then return{right=true,b=true}end
  phase='left-runup'
 end
 if phase=='left-runup'then
  if c.x>1244 or v>=0 then return{left=true,b=true}end
  phase='left-air-charge';age=0;flower.boarding_takeoff=state()
  return{left=true,a=true,b=true}
 elseif phase=='left-air-charge'then
  age=age+1
  if age<8 then return{left=true,a=true,b=true}end
  assert(c.r('GmRam00C2')>=128,'Actual original rising jump before release')
  phase='left-chase';age=0;flower.support_baseline=flower.support_count or 0
  return{right=true,a=true}
 elseif phase=='left-chase'then
  age=age+1;assert(age<100,'Bounded reflected-star support')
  if(flower.support_count or 0)>flower.support_baseline then
   phase='ride-release';return{}
  end
  assert(nativeStar(c)~=0 and c.x>=1152,'Real star remains active before support')
  return{left=true,a=true}
 elseif phase=='ride-release'then
  assert(flower.real_support,'Actual original flagged support before fresh jump')
  phase='flower-jump';age=0;return{right=true,a=true}
 elseif phase=='flower-jump'then
  age=age+1;assert(age<100,'Bounded ordinary post-support Flower jump')
  return{right=c.x<1243,left=c.x>1247,a=age<=25}
 end
 error('Unknown measured Flower boarding phase '..phase)
end
'''


@lru_cache(maxsize=1)
def parent571_bindings(raw,key='mr_gimmick'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT_SOURCE
    assert sha256(Previous.controller(raw,key).encode()).hexdigest()==PARENT_LUA
    q=deepcopy(Previous.bindings(raw,key));b=dict(W.Symbols.bundle(),raw=raw)
    for name in('GmRam0379','GmRam00D7','GmRam00CC','GmRam00C2'):
        q['ram'][name]=W.address(b,name)
    for alias,name in(('BoardStarLaunchVX','GmN30_829C'),('BoardStarReflectVX','GmN29_8114'),('BoardFreshJump','GmN30_81A2')):
        at=W.location(b,name);q['hooks'][alias]=dict(pc=W.address(b,name),offset=at-16,
            bytes=list(raw[at:at+8]),bank=(at-16)//8192)
    for h in q['hooks'].values():
        if'bank'in h:
            at=16+h['bank']*8192;h['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
    return q


@lru_cache(maxsize=1)
def parent571_controller(raw,key='mr_gimmick'):
    q=parent571_bindings(raw,key);text=Previous.controller(raw,key)
    lua=Previous.Previous.Previous.Base.Stage.Frozen.lua
    old='local C='+lua(Previous.bindings(raw,key))+'\n';assert text.startswith(old)
    text='local C='+lua(q)+'\n'+text[len(old):]
    text=once(text,Previous.policy(),policy())
    text=once(text,'and flower.resume==25 and identity()',
        'and flower.resume==25 and flower.opposite_launch and flower.wall_reflection and flower.real_support and flower.support_jump and identity()')
    insert=r'''
hook('BoardStarLaunchVX',function()
 if not firstMReady or not flower.boarding_takeoff then return end
 local a=emu.getState()['cpu.a'];assert(a>0 and a<128 and r('GmRam00CC')>=128,'Real right star launch with left hero momentum')
 flower.opposite_launch={state=state(),A=a,heroVX=r('GmRam00CC')}
end)
hook('BoardStarReflectVX',function()
 if not flower.opposite_launch then return end
 local a=emu.getState()['cpu.a'];assert(a>=128 and r('GmRam0379')==128,'Actual original side-wall star reflection')
 flower.wall_reflection={state=state(),A=a,wall=r('GmRam0379')}
end)
hook('BoardFreshJump',function()
 if not flower.real_support then return end
 assert(emu.getState()['cpu.a']==172,'Actual original fresh post-support jump velocity')
 flower.support_jump={state=state(),A=172}
end)
'''
    text=once(text,"hook('GmMovement',function()",insert+"hook('GmMovement',function()")
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


@lru_cache(maxsize=1)
def bindings(raw,key='mr_gimmick'):
    old=owning571(raw);q=deepcopy(parent571_bindings(old,key));q['sha']=PIN
    for h in q['hooks'].values():
        at=16+h['offset'];assert raw[at:at+len(h['bytes'])]==bytes(h['bytes'])
        if'bank'in h:
            at=16+h['bank']*8192;h['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
    return q


@lru_cache(maxsize=1)
def controller(raw,key='mr_gimmick'):
    old=owning571(raw);text=parent571_controller(old,key)
    lua=Previous.Previous.Previous.Base.Stage.Frozen.lua
    prefix='local C='+lua(parent571_bindings(old,key))+'\n';assert text.startswith(prefix)
    result='local C='+lua(bindings(raw,key))+'\n'+text[len(prefix):]
    assert result.split('\n',1)[1]==text.split('\n',1)[1]
    Frozen.LuaRuntime().compile(result);return result


def metadata(raw,key='mr_gimmick'):
    old=owning571(raw);q=Previous.metadata(old,key)
    q.update(ROM_SHA256=PIN,controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        old571_default_controller_SHA256=PARENT_LUA,old571_factory_SHA256=PARENT_SOURCE,
        source_only_parent571_controller_SHA256=sha256(parent571_controller(old,key).encode()).hexdigest(),
        strict_typed_inverse='compose_battletoads_native_service_1114.inverse',
        scope='Genuine M then mature Flower via observed original wall reflection/real flagged star support/fresh jump; actual inventory2,next2,cue1c,erase,1000score and25 movement entries; no native/audio/fullstage claim')
    return q
