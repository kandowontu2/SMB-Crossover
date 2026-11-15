"""Ordinary earned-M to F exploration on actual current CPU; no game seeds."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse,inspect,json
import replay_bub_stock_7a80_1115 as Base

ROM,PIN,B=Base.ROM,Base.PIN,Base.B

def once(text,old,new):
    assert text.count(old)==1,old[:100]
    return text.replace(old,new,1)

POWERED=r'''
local poweredGeneration,poweredSlot=nil,nil
local function poweredSample(slot)
 local oy=identity==1 and 8 or 0;local bo=0x188+8*slot
 return {slot=slot,kind=full_state(0x88+4*slot),
  dx=((full_state(bo+3)-full_state(0x103+oy)+128)%256)-128,
  dy=((full_state(bo)-full_state(0x100+oy)+128)%256)-128}
end
local function poweredGrowth(q,base,step)
 if poweredGeneration~=base.completed_Main then poweredGeneration=base.completed_Main;poweredSlot=nil end
 if q.launches>base.launches and poweredSlot==nil then
  local best=nil
  for i=0,14 do local s=poweredSample(i)
   if(s.kind==1 or s.kind==2)and s.dx>=0 and s.dx<96 and(not best or math.abs(s.dx-34)<math.abs(best.dx-34))then best=s end
  end
  if best then poweredSlot=best.slot end
 end
 local pad={right=step<4,b=step<4};local s=poweredSlot and poweredSample(poweredSlot)or nil
 if s and step>=4 then pad.right=s.dx>34 end
 local actor=identity==1 and 0x42 or 0x2e
 if s and s.kind==2 and s.dx>=30 and s.dx<=36 and s.dy>=-20 and s.dy<=-16
  and full_normal_jump_ready(actor)and full_state(0x301)&128==0 then
  local row={Main=q.completed_Main,x=full_x(),y=r('Player_Y_Position'),bubble=s,support=full_support_probe()}
  assert(#flower.takeoffs<8,'Bounded actual powered bubble takeoffs');flower.takeoffs[#flower.takeoffs+1]=row
  return{right=true,a=true},true
 end
 if q.completed_Main%8==0 then
  local t=flower.growth;t[#t+1]={Main=q.completed_Main,x=full_x(),y=r('Player_Y_Position'),step=step,bubble=s,selector=full_state(actor+3),held=full_state(0x301)}
  if#t>24 then table.remove(t,9)end
 end
 return pad,false
end
local function poweredAir(q,base)
 if q.source_bubble_ride_restarts>base.source_bubble_ride_restarts then return nil end
 local best=nil
 for i=0,14 do local s=poweredSample(i)
  if s.kind==2 and s.dx>-40 and s.dx<48 and(not best or math.abs(s.dx-8)<math.abs(best.dx-8))then best=s end
 end
 if best then return{right=best.dx>12,left=best.dx<4,a=true}end
end
'''

FLOWER=r'''
local function flowerPhase(p)flower.phase=p;flower.age=0;flower.phaseMain=updates end
local function full_tick(finish)
 if flower.phase=='mushroom'then
  return mushroom_tick(function(ok,why)
   assert(ok,'Genuine frozen Mushroom prefix');flower.mushroom=routeResult;routeResult=nil
   flower.M_moves=sourceUpdates;flowerPhase('M-resume');full_pad={}
  end)
 end
 local q=BUB_OBSERVER.summary();local x,y=full_x(),r('Player_Y_Position');local engine=r('GameEngineSubroutine')
 local actor=identity==1 and 0x42 or 0x2e;local flags=full_state(actor+2);local item=upgrade_item()
 assert(r('NumberofLives')==2 and engine~=11,'Living natural Bub Flower continuation')
 assert(r('WorldNumber')==0 and r('LevelNumber')==0,'Flower continuation actual1-1')
 if q.completed_Main~=flower.last then
  flower.last=q.completed_Main;flower.age=flower.age+1
  if q.completed_Main%8==0 then
   local t=flower.trajectory;t[#t+1]={Main=q.completed_Main,phase=flower.phase,part=full_part,x=x,y=y,selector=full_state(actor+3),flags=flags,held=full_state(0x301),native=r('Player_State'),dy=ram(142),rides=q.source_bubble_ride_restarts,item=item}
   if#t>32 then table.remove(t,9)end
  end
 end
 assert(flower.age<1400,'Bounded real Flower phase '..flower.phase)
 if flower.phase=='M-resume'then
  full_pad={}
  if sourceUpdates-flower.M_moves>=25 then
   assert(sourceUpdates-flower.M_moves==25,'Exactly25 source movements after real M')
   flower.M_resume=25;full_part='approach';full_step=0;full_last=q.completed_Main-1;flowerPhase('travel')
  else return end
 end
 if item then
  assert(ram(L.PowerUpType+item.slot)==1,'Actual complete spawn chain chose Flower')
  flower.born=flower.born or{Main=q.completed_Main,item=item,x=x,y=y}
  if item.state>=128 then flower.mature=flower.mature or{Main=q.completed_Main,item=item,x=x,y=y}end
 end
 if engine==9 then full_pad={};return end
 if flags==7 and engine==8 and r('GuestPowerupActive')==0 then
  assert(r('PlayerStatus')==2 and flower.born and flower.mature,'Mature real Flower and original flags7')
  flower.F_moves=flower.F_moves or sourceUpdates;flower.resume=sourceUpdates-flower.F_moves;full_pad={}
  if flower.resume==25 then
   flower.final={x=x,y=y,flags=flags,status=r('PlayerStatus'),lives=r('NumberofLives'),moves=sourceUpdates}
   finish(true,'Genuine earned Mushroom then Flower and25 source movement calls');return
  end
  return
 end
 if flower.phase=='travel'then
  if not flower.target then
   local camera=r('ScreenLeft_PageLoc')*256+r('ScreenLeft_X_Pos')
   for wx=math.floor(math.max(camera,1104)/16)*16,math.min(camera+224,x+160,1376),16 do
    for yy=80,160,16 do local _,tile=full_solid(wx+4,yy)
     if tile==0xc1 and(not flower.target or wx<flower.target.x)then flower.target={x=wx,y=yy}end
    end
   end
  end
  assert(x<1376,'Actual first Flower block before next pit')
  if flower.target and x>=flower.target.x-32 and y>=flower.target.y+16 and r('Player_State')==0 then
   flowerPhase('align');full_pad={}
  else return full_tick_base(finish)end
 end
 if flower.phase=='align'then
  full_pad={right=x<flower.target.x+1,left=x>flower.target.x+3}
  if x>=flower.target.x+1 and x<=flower.target.x+3 and full_normal_jump_ready(actor)and full_state(0x301)&128==0 then
   flowerPhase('bump');full_pad={a=true}
  end
 elseif flower.phase=='bump'then
  full_pad={a=flower.age<25}
  if item then
   local left=flower.target.x
   for _=1,8 do if full_solid(left-12,flower.target.y)then left=left-16 else break end end
   flower.runup=math.max(left-96,1144);flowerPhase('mount');full_pad={}
  elseif flower.age>80 then error('Real source head did not release Flower')end
 elseif flower.phase=='mount'then
  if not full_normal_jump_ready(actor)then full_pad={};return end
  if x>flower.runup+2 then full_pad={left=true}
  elseif x<flower.runup-2 then full_pad={right=true}
  elseif full_state(0x102+(identity==1 and 8 or 0))&64==0 then full_pad={right=true}
  elseif full_launch_ready(actor)and full_state(0x301)&128==0 and flower.mature then
   flower.base=q;flowerPhase('grow');full_pad={right=true,b=true}
  else full_pad={}end
 elseif flower.phase=='grow'then
  local takeoff;full_pad,takeoff=poweredGrowth(q,flower.base,flower.age)
  if flower.age>=5 then assert(q.launches>flower.base.launches,'Actual earned Flower-mount bubble launch')end
  if takeoff then flowerPhase('ride')end
  assert(flower.age<180,'Measured grown bubble window')
 elseif flower.phase=='ride'then
  local tx=item and item.x or flower.target.x
  full_pad={right=x<tx-2,left=x>tx+3,a=true}
  full_pad=poweredAir(q,flower.base)or full_pad
  if y<=flower.target.y-32 and r('Player_State')==0 then full_pad.a=false end
 end
end
'''


@lru_cache(maxsize=2)
def controller(raw,identity=0,mode='mushroom'):
    assert mode=='mushroom'
    text=Base.controller(raw,identity,mode)
    text=once(text,'local function finish(',"local flower={phase='mushroom',age=0,last=-1,takeoffs={},growth={},trajectory={}}\nlocal function finish(")
    text=once(text,'route=routeResult','route=routeResult,natural_flower=flower')
    text=once(text,'local function full_tick(finish)','local function mushroom_tick(finish)')
    text=once(text,'local function full_tick_base(finish)',POWERED+'\nlocal function full_tick_base(finish)')
    lo=text.index(" elseif full_part=='grow'then");hi=text.index(" elseif full_part=='jump'or full_part=='cross'then",lo)
    text=text[:lo]+''' elseif full_part=='grow'then
  local takeoff;full_pad,takeoff=poweredGrowth(q,full_ride_base,full_step)
  if full_step>=5 then assert(q.launches>full_ride_base.launches,'Real powered route bubble launch')end
  if takeoff then full_part='jump';full_step=0;full_event('actual-measured-powered-bubble-takeoff')end
  assert(full_step<180,'Measured source powered growth bound')
'''+text[hi:]
    text=once(text,'  full_pad={right=true,a=true};full_min_y=math.min(full_min_y,y)',
        '''  full_pad={right=true,a=true};full_min_y=math.min(full_min_y,y)
  if full_part=='jump'then
   if not grounded then full_pad=poweredAir(q,full_ride_base)or full_pad
   elseif full_step>5 then full_pad={right=true,a=full_normal_jump_ready(actor)and full_step%6<3}end
  end''')
    text=once(text,'local routeStarted=false',FLOWER+'\nlocal routeStarted=false')
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    assert not any(x in text for x in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    return text


def run(raw,identity=0):
    Base.reference(raw)
    namespace=dict(Base.Previous.__dict__,PIN=PIN,controller=controller)
    source=inspect.getsource(Base.Previous.source_check)
    exec(compile(source,str(Path(__file__))+':source-driver','exec'),namespace)
    try:q=namespace['source_check'](raw,identity,'mushroom',4200)
    except AssertionError as e:
        assert len(e.args)==1 and isinstance(e.args[0],dict)and'receipt'in e.args[0]
        q=e.args[0]
    return q


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--identity',type=int,choices=(0,1),default=0);a=p.parse_args()
    raw=ROM.read_bytes()
    def forbid(*args,**kwargs):raise AssertionError('Bub Flower exploration attempted output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid):q=run(raw,a.identity)
    r=q.get('receipt')or{}
    receipt=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(dict(passed=q['passed'],ROM_SHA256=PIN,identity=a.identity,
        controller_SHA256=q['controller_SHA256'],source_receipt_SHA256=receipt,
        Main=r.get('Main_updates'),source_moves=r.get('source_updates'),reason=r.get('reason'),
        flower=r.get('natural_flower'),terminal=r.get('terminal'),output_files=0),separators=(',',':')),flush=True)
