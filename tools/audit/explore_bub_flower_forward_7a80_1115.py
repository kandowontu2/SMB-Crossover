"""Preserve intended right direction at actual original bubble restart."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse,inspect,json
import explore_bub_flower_rearm_7a80_1115 as Previous

ROM,PIN,Base=Previous.ROM,Previous.PIN,Previous.Base

@lru_cache(maxsize=2)
def controller(raw,identity=0,mode='mushroom'):
    text=Previous.controller(raw,identity,mode);once=Previous.Previous.once
    text=once(text,'if best then return{right=best.dx>12,left=best.dx<4,a=true}end',r'''if best then
  local t=flower.align_trace or{};flower.align_trace=t
  t[#t+1]={Main=q.completed_Main,x=full_x(),y=r('Player_Y_Position'),bubble=best,held=full_state(0x301),cached_direction=full_state((identity==1 and 0x42 or 0x2e)+5)}
  if#t>24 then table.remove(t,9)end
  -- Actual D36B copies held&3 into the original jump-direction latch.
  -- Neutral horizontal alignment avoids a new Left-facing support bounce;
  -- when the real bubble approaches the feet, keep its restart rightward.
  return{right=best.dx>12 or best.dy>=8,a=true}
 end''')
    text=once(text,"selector=full_state(actor+3),dy=ram(142),held=full_state(0x301),jumps=", "selector=full_state(actor+3),cached_direction=full_state(actor+5),dy=ram(142),held=full_state(0x301),jumps=")
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
    def forbid(*args,**kwargs):raise AssertionError('Bub forward boarding attempted output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid):q=run(raw,a.identity)
    r=q.get('receipt')or{};receipt=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(dict(passed=q['passed'],ROM_SHA256=PIN,identity=a.identity,
        controller_SHA256=q['controller_SHA256'],source_receipt_SHA256=receipt,
        Main=r.get('Main_updates'),source_moves=r.get('source_updates'),reason=r.get('reason'),
        flower=r.get('natural_flower'),terminal=r.get('terminal'),output_files=0),separators=(',',':')),flush=True)
