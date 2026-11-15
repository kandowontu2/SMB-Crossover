"""Strict current40a ordinary Bub Flower, defend a real return run-up."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import inspect
import compose_prince_sword_tier2_fresh_1115 as Current
import replay_bub_flower_7a80_1115 as Previous

ROM,B=Previous.ROM,Previous.B
R,W,N=B.R,B.W,B.N
PIN=Current.CANDIDATE
CURRENT_SOURCE='6d2cbeb8bcf6b9a32d85c08ef158bb4dbe67e890831bbdb8dd203359e61b1afc'

@lru_cache(maxsize=1)
def reference(raw):
    assert isinstance(raw,bytes)and sha256(raw).hexdigest()==PIN,'Expected exact current40a'
    assert sha256(Path(Current.__file__).read_bytes()).hexdigest()==CURRENT_SOURCE
    old=Current.inverse(raw);assert sha256(old).hexdigest()==Previous.PIN
    Previous.Base.reference(old)
    spans=[(1048592+p*1024,1024)for p in(*B.PAGES,441)]
    spans.append((16+65*8192+0xfea,16))
    spans.extend((Previous.Base.Previous.U.at(pc),len(new))for pc,before,new in Previous.Base.Previous.U.changes())
    for at,size in spans:assert raw[at:at+size]==old[at:at+size],(at,size)
    for h in Previous.bindings(old)['hooks'].values():
        if h['kind']==2:
            at=16+h['offset'];assert raw[at:at+len(h['data'])//2]==bytes.fromhex(h['data'])
    return old

DEFENCE=r'''
local mountCombat=nil
local function mountDefence(q,actor,x,y)
 local enemies={};local nearest=nil
 for i=0,5 do
  local flag=read(L.Enemy_Flag+i);local id=read(L.Enemy_ID+i);local st=read(L.Enemy_State+i)
  if flag>0 and flag<128 and(id==6 or id==0)and st&32==0 then
   local a={slot=i,id=id,flag=flag,state=st,x=full_x(i),y=read(L.Enemy_Y_Position+i),direction=read(L.Enemy_MovingDir+i)}
   a.dx=a.x-x;enemies[#enemies+1]=a
   if math.abs(a.dx)<80 and math.abs(a.y-y)<=32 and(not nearest or math.abs(a.dx)<math.abs(nearest.dx))then nearest=a end
  end
 end
 if q.completed_Main~=flower.defenceLast then
  flower.defenceLast=q.completed_Main;flower.defence=flower.defence or{}
  local t=flower.defence
  if nearest or full_state(actor+3)&128~=0 then
   t[#t+1]={Main=q.completed_Main,x=x,y=y,selector=full_state(actor+3),enemies=enemies,pops=q.pops,captures=q.captures}
   if#t>20 then table.remove(t,7)end
  end
 end
 if mountCombat then
  local c=mountCombat;local age=q.completed_Main-c.Main
  if q.captures>c.captures and q.pops>c.pops then
   flower.retirements=flower.retirements or{}
   flower.retirements[#flower.retirements+1]={Main=q.completed_Main,x=x,y=y,target=c.target,captures=q.captures-c.captures,pops=q.pops-c.pops}
   mountCombat=nil;full_pad={};return true
  end
  assert(age<45,'Actual return-path bubble must trap/pop the real threat')
  full_pad={right=c.direction>0,left=c.direction<0,b=age<4};return true
 end
 if not nearest or not full_normal_jump_ready(actor)then return false end
 local dir=nearest.dx>=0 and 1 or-1;local gap=math.abs(nearest.dx)
 local function retreat()
  local safe=full_solid(x-dir*2,y+32)and full_solid(x+7,y+32)
  full_pad={right=safe and dir<0,left=safe and dir>0}
 end
 if math.abs(nearest.y-(y+8))>8 then retreat();return true end
 if full_state(actor+8)~=0 or full_state(0x301)&64~=0 then retreat();return true end
 local right=full_state(0x102+(identity==1 and 8 or 0))&64~=0
 if right~=(dir>0)then full_pad={right=dir>0,left=dir<0};return true end
 local away=nearest.direction==(dir>0 and 1 or 2);local fireGap=away and 20 or 24
 full_pad={right=dir>0,left=dir<0}
 if gap<=fireGap then
  assert(gap>=16,'Real threat stays outside body before fresh close shot')
  mountCombat={Main=q.completed_Main,direction=dir,target=nearest,captures=q.captures,pops=q.pops}
  full_pad.b=true
 end
 return true
end
'''

@lru_cache(maxsize=2)
def controller(raw,identity=0,mode='mushroom'):
    old=reference(raw);text=Previous.controller(old,identity,mode)
    assert text.count(Previous.PIN)==2,'Only explicit Stock metadata and actual ROM pin'
    text=text.replace(Previous.PIN,PIN)
    once=Previous.Previous.Previous.Previous.once
    text=once(text,'local function full_tick(finish)',DEFENCE+'\nlocal function full_tick(finish)')
    text=once(text," elseif flower.phase=='mount'then\n  if not full_normal_jump_ready(actor)"," elseif flower.phase=='mount'then\n  if mountDefence(q,actor,x,y)then return end\n  if not full_normal_jump_ready(actor)")
    text=once(text,'local function drive()\n if not game or done then return end','local function drive()\n if not game or done or pending then return end')
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    return text


def source_check(raw,identity=0):
    base=SimpleNamespace(reference=reference,Previous=Previous.Base.Previous)
    ns=dict(Previous.__dict__,Base=base,PIN=PIN,controller=controller)
    exec(compile(inspect.getsource(Previous.source_check),str(Path(__file__))+':actual-current-driver','exec'),ns)
    return ns['source_check'](raw,identity)
