"""Sunny Star successor: authenticate the reached native DEC/credit boundary.

Controls are byte-identical to the frozen first Star policy. The old entry-only
Floatey observer is retained as a negative; this observer uses the real writer.
"""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import replay_sunny_natural_stock_bc5_1115 as Previous

R,ROM,PIN,W,N,Current=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current
PARENT_SHA='391f5303adea769e9447f29907f55e9893f053d6340df00c0565ea8e11c9be70'

@lru_cache(maxsize=1)
def bindings(raw,key='star'):
    assert key=='star' and sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT_SHA
    q=deepcopy(Previous.bindings(raw,key));b=Current.bundle(raw)
    pc,at=W.address(b,'FloateyNumbersCore'),W.location(b,'FloateyNumbersCore');timer=W.address(b,'FloateyNum_Timer')
    pattern=bytes((0xde,timer&255,timer>>8,0xc9,43,0xd0))
    hits=[i for i in range(120-len(pattern))if raw[at+i:at+i+len(pattern)]==pattern];assert len(hits)==1
    delta=hits[0];bank=(at-16)//8192
    q['hooks']['StockTimerDEC']=dict(pc=pc+delta,offset=at+delta-16,bytes=list(raw[at+delta:at+delta+8]),bank=bank,
        bank_SHA256=sha256(raw[16+bank*8192:16+(bank+1)*8192]).hexdigest())
    return q

@lru_cache(maxsize=1)
def controller(raw,key='star'):
    text=Previous.controller(raw,key);prefix='local C='+Previous.Text.lua(Previous.bindings(raw,key))+'\n'
    assert text.startswith(prefix);body=text[len(prefix):]
    old="hook('FloateyNumbersCore',function()";assert body.count(old)==1
    body=body.replace(old,"hook('StockTimerDEC',function()",1)
    old=" local before=score();pendingScore=returning(function(t)";assert body.count(old)==1
    body=body.replace(old,""" local cpu=emu.getState();assert(cpu['cpu.a']==43 and cpu['cpu.y']==6,'Actual timer43/control6 credit branch')
 stock.credit_writer={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],slot=i,timer=r('FloateyNum_Timer',i),control=r('FloateyNum_Control',i),state=state()}
 local before=score();pendingScore=returning(function(t)""",1)
    text='local C='+Previous.Text.lua(bindings(raw,key))+'\n'+body
    Previous.LuaRuntime().compile(text);return text

def metadata(raw,key='star'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        observer_factory_SHA256=sha256(Path(__file__).read_bytes()).hexdigest(),bindings=bindings(raw,key),
        controls_identical_to_frozen_first_Star=True,credit_observer='Reached native DEC, authenticated A43/Y6/timer/control and same PC/SP return, +1000')
    return q
