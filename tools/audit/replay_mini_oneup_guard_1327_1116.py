"""Ordinary fresh-A enemy guard during genuine grounded fixed-lift waits."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_mini_oneup_retained_lifts_1327_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,H,Current=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.H,Previous.Current
BASE_SHA='712f91248acb98a446f6565fd69886300bf27a4e2d2ad8bd3fff79a8a58a122e'


@lru_cache(maxsize=1)
def controller(raw,key='oneup'):
    assert key=='oneup'and H(Path(Previous.__file__).read_bytes())==BASE_SHA
    c=deepcopy(Previous.bindings(raw));b=Current.bindings(raw)['bundle']
    for n in('Enemy_X_Speed','Enemy_MovingDir','Player_Y_Speed'):c['ram'][n]=W.address(b,n)
    at=16+89*8192+(0xbfb0&8191);c['hooks']['NativeMiniHead']=dict(pc=0xbfb0,offset=at-16,work=False,bytes=list(raw[at:at+8]),bank_SHA256=H(raw[16+89*8192:16+90*8192]))
    _,body=Previous.controller(raw).split('\n',1)
    body=Previous.Previous.once(body,' if M.scope_passed then\n  local s=state();'," if M.scope_passed then\n  assert(r('PlayerStatus')==1 and work(0xc244)==1,'Retain genuinely earned M tier before hidden1UP')\n  local s=state();")
    old='   local lift=mini_lift_inputs(s,ob,x);if lift then buttons=lift;return end'
    new="""   route.guards=route.guards or{}
   if route.active_guard then
    local g=route.active_guard;local n=steps-g.since;assert(n<160,'Bounded original enemy guard jump')
    if not g.admitted and(s.queued==12 or s.current==12 or s.current==13 or s.vy<0)then g.admitted=state()end
    if supported(s)and n>6 then g.landed=state();route.active_guard=nil;buttons={};return end
    buttons={a=n<36};return
   end
   if ob and supported(s)and s.y>=160 and work(0xc30d)==0 and s.held&128==0 then
    for i=0,5 do local e=actor(i);local dx=e.x-s.x;local vx=r('Enemy_X_Speed',i)
     if e.flag==1 and e.id==6 and e.state==0 and math.abs(e.y-(s.y+8))<=12 and math.abs(dx)<=48 and((dx<0 and vx>0 and vx<128)or(dx>=0 and vx>=128))then
      assert(#route.guards<8,'Bounded real Goomba guard episodes');local g={since=steps,request=state(),actor=e,vx=vx,direction=r('Enemy_MovingDir',i)};route.guards[#route.guards+1]=g;route.active_guard=g;buttons={a=true};return
     end
    end
   end
   local lift=mini_lift_inputs(s,ob,x);if lift then buttons=lift;return end"""
    body=Previous.Previous.once(body,old,new)
    observer="""hook('NativeMiniHead',function()
 if not M.scope_passed or work(0xc25c)==0 or word(0xc25d)<1008 or word(0xc25d)>=1056 then return end
 item.head_queries=item.head_queries or{};if#item.head_queries>=8 then return end
 local z=emu.getState();local q={PC=z['cpu.pc'],SP=z['cpu.sp'],state=state(),pending=work(0xc25c),world_x=word(0xc25d),world_y=word(0xc25f),raw_tile=work(0xc261),cell=word(0xc262),native_vy=r('Player_Y_Speed')};item.head_queries[#item.head_queries+1]=q
 returning(function(t)local a=emu.getState();q.returned={PC=t.pc,SP=t.sp,A=a['cpu.a'],P=a['cpu.ps']}end)
end)
"""
    body=Previous.Previous.once(body,"hook('GameLoop',function()",observer+"hook('GameLoop',function()")
    text='local C='+Text.lua(c)+'\n'+body;LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'));return text


def metadata(raw,key='oneup'):
    q=Previous.metadata(raw);q.update(factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(controller(raw).encode()),parent_L_factory_SHA256=BASE_SHA,
        scope='Same current M/retained fixed-lift/hiddenL transaction; ordinary fresh-A guard only for real approaching ground Goomba during lift wait; earned tier retained, real head point/cell/native VY observed')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
