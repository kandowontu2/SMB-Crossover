"""Actual91dc food: reuse authenticated native DEC credit boundary."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import replay_battletoads_mature8_food_1116 as Previous

C,Current,R,ROM,PIN,W,N=Previous.C,Previous.Current,Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N
PARENT_SHA='969a010bb1151af4e872f508ba1b22a760cfd621693e19cc7b8fa4d31e528b8f'

@lru_cache(maxsize=4)
def bindings(raw,key='rash',kind='mushroom'):
    assert C.digest(Path(Previous.__file__).read_bytes())==PARENT_SHA
    q=deepcopy(Previous.bindings(raw,key,kind));b=Current.bundle(raw)
    pc,at=W.address(b,'FloateyNumbersCore'),W.location(b,'FloateyNumbersCore');timer=W.address(b,'FloateyNum_Timer')
    pattern=bytes((0xde,timer&255,timer>>8,0xc9,43,0xd0));hits=[i for i in range(120-len(pattern))if raw[at+i:at+i+len(pattern)]==pattern]
    assert len(hits)==1;delta=hits[0];assert pc+delta==0x897c;bank=(at-16)//8192
    q['hooks']['StockTimerDEC']=dict(pc=pc+delta,offset=at+delta-16,bytes=list(raw[at+delta:at+delta+8]),bank=bank,
        bank_SHA256=C.digest(raw[16+bank*8192:16+(bank+1)*8192]))
    return q

@lru_cache(maxsize=4)
def controller(raw,key='rash',kind='mushroom'):
    text=Previous.controller(raw,key,kind);prefix='local C='+Previous.Text.lua(Previous.bindings(raw,key,kind))+'\n'
    assert text.startswith(prefix);body=text[len(prefix):]
    old="hook('FloateyNumbersCore',function()";assert body.count(old)==1;body=body.replace(old,"hook('StockTimerDEC',function()",1)
    old=' local before=score();pendingScore=returning(function(t)';assert body.count(old)==1
    body=body.replace(old,""" local cpu=emu.getState();assert(cpu['cpu.a']==43 and cpu['cpu.y']==6,'Actual timer43/control6 credit branch')
 q.credit_writer={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],slot=i,timer=r('FloateyNum_Timer',i),control=r('FloateyNum_Control',i),state=state()}
 local before=score();pendingScore=returning(function(t)""",1)
    text='local C='+Previous.Text.lua(bindings(raw,key,kind))+'\n'+body
    Previous.Previous.Previous.Previous.LuaRuntime().compile(text)
    return text

def metadata(raw,key='rash',kind='mushroom'):
    q=Previous.metadata(raw,key,kind);q.update(controller_SHA256=C.digest(controller(raw,key,kind).encode()),
        credit_factory_SHA256=C.digest(Path(__file__).read_bytes()),controls_identical=True,
        retained_entry_only_observer_negative='f392f299bcd05eadb3e34536527059d4a394e0e3a577d6ee296994ef52e5676f',
        credit_observer='Actual897C DEC A43/Y6 and authenticated caller return, real +1000 then25 original returns')
    return q

def family(kind='mushroom'):
    from types import SimpleNamespace
    return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,key,kind),metadata=lambda raw,key:metadata(raw,key,kind))
