"""Ordinary fresh-A rearm after an actual powered supported landing."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse,inspect,json
import explore_bub_flower_7a80_1115 as Previous

ROM,PIN,Base=Previous.ROM,Previous.PIN,Previous.Base
PARENT='5ac94fc68a9478332fdd75a7152d23a2561189b46981cfdf9b5f63cb7f639638'

REARM=r'''
local groundRearm=nil
local function poweredGround(q)
 if not groundRearm or groundRearm.generation~=full_ride_base.completed_Main then
  groundRearm={generation=full_ride_base.completed_Main,release=sourceUpdates,jumps=q.source_total_jump_starts}
 end
 local g=groundRearm
 if g.press and q.source_total_jump_starts>g.jumps then
  flower.rearm_admissions=flower.rearm_admissions+1;groundRearm=nil
  return{right=true,a=true}
 end
 if not g.press then
  if sourceUpdates-g.release>=2 and full_state(0x301)&128==0 then
   g.press=sourceUpdates;flower.rearm_requests=flower.rearm_requests+1
   assert(flower.rearm_requests<24,'Bounded genuine supported retry requests')
  else return{right=true}end
 end
 assert(sourceUpdates-g.press<12,'Supported fresh A must reach actual original jump entry')
 return{right=true,a=true}
end
'''

@lru_cache(maxsize=2)
def controller(raw,identity=0,mode='mushroom'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT
    text=Previous.controller(raw,identity,mode);once=Previous.once
    text=once(text,"trajectory={}}","trajectory={},pipe_events={},rearm_requests=0,rearm_admissions=0}")
    text=once(text,'local function poweredAir(q,base)',REARM+'\nlocal function poweredAir(q,base)')
    text=once(text,"  if full_part=='jump'then\n   if not grounded then full_pad=poweredAir(q,full_ride_base)or full_pad\n   elseif full_step>5 then full_pad={right=true,a=full_normal_jump_ready(actor)and full_step%6<3}end\n  end",'''  if full_part=='jump'or full_part=='cross'then
   if not grounded then
    if groundRearm and groundRearm.press and q.source_total_jump_starts>groundRearm.jumps then
     flower.rearm_admissions=flower.rearm_admissions+1;groundRearm=nil
    end
    full_pad=poweredAir(q,full_ride_base)or full_pad
   elseif full_step>5 then
    full_pad=full_normal_jump_ready(actor)and poweredGround(q)or{right=true}
   end
  end''')
    text=once(text,"flower.mushroom=routeResult;routeResult=nil",'''flower.mushroom={source_flags=routeResult.source_flags,native_status=routeResult.native_status,
    observed_immature=routeResult.observed_immature,observed_mature=routeResult.observed_mature,
    captures=routeResult.captures,pops=routeResult.pops,bump_attempts=routeResult.bump_attempts};routeResult=nil''')
    text=once(text,'  flower.last=q.completed_Main;flower.age=flower.age+1',r'''  flower.last=q.completed_Main;flower.age=flower.age+1
  if flower.phase=='travel'and(flower.last_jumps~=q.source_total_jump_starts or flower.last_rides~=q.source_bubble_ride_restarts or flower.last_ground~=r('Player_State'))then
   local t=flower.pipe_events;t[#t+1]={Main=q.completed_Main,x=x,y=y,part=full_part,native=r('Player_State'),selector=full_state(actor+3),dy=ram(142),held=full_state(0x301),jumps=q.source_total_jump_starts,rides=q.source_bubble_ride_restarts,support=full_support_probe()}
   if#t>24 then table.remove(t,9)end
   flower.last_jumps=q.source_total_jump_starts;flower.last_rides=q.source_bubble_ride_restarts;flower.last_ground=r('Player_State')
  end''')
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    return text


def run(raw,identity=0):
    ns=dict(Previous.__dict__,controller=controller)
    exec(compile(inspect.getsource(Previous.run),str(Path(__file__))+':source-driver','exec'),ns)
    return ns['run'](raw,identity)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--identity',type=int,choices=(0,1),default=0);a=p.parse_args()
    raw=ROM.read_bytes()
    def forbid(*args,**kwargs):raise AssertionError('Bub Flower rearm attempted output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid):q=run(raw,a.identity)
    r=q.get('receipt')or{};receipt=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(dict(passed=q['passed'],ROM_SHA256=PIN,identity=a.identity,
        controller_SHA256=q['controller_SHA256'],source_receipt_SHA256=receipt,
        Main=r.get('Main_updates'),source_moves=r.get('source_updates'),reason=r.get('reason'),
        flower=r.get('natural_flower'),terminal=r.get('terminal'),output_files=0),separators=(',',':')),flush=True)
