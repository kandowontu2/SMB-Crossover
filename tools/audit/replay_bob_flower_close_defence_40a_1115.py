"""Bob-only binding of the frozen actual-coordinate Bub danger policy."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import inspect
import replay_bub_flower_close_defence_40a_1115 as Previous

R,ROM,W,N,B,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.B,Previous.PIN
PARENT='17f9eb47e1d2aa964c154994c704c015809a6bfb051a750bb143e2908b4ba154'

@lru_cache(maxsize=2)
def controller(raw,identity=1,mode='mushroom'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT
    if identity==0:return Previous.controller(raw,identity,mode)
    assert identity==1
    old=Previous.Previous.controller(raw,identity,mode);text=old
    once=Previous.Previous.Previous.Previous.Previous.Previous.once
    declaration=Previous.DEFENCE+'\n'
    text=once(text,'local function full_tick_base(finish)',declaration+'local function full_tick_base(finish)')
    marker=" if full_state(actor+3)&128~=0 or full_state(0x307)~=0 then full_fail('Fullstage source injury/death')end"
    call='\n if closeThreat(q,actor,x,y,grounded)then return end'
    text=once(text,marker,marker+call)
    assert text.replace(declaration,'',1).replace(call,'',1)==old,'Only the exact frozen danger policy and read-only observations added to Bob'
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    return text


def source_check(raw,identity=1):
    ns=dict(Previous.__dict__,controller=controller)
    exec(compile(inspect.getsource(Previous.source_check),str(Path(__file__))+':current-Bob-source','exec'),ns)
    return ns['source_check'](raw,identity)
