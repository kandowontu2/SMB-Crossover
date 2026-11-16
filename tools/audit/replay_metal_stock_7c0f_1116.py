"""Typed7c0f config facade; exact old control body and actual current bytes."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import current_metal_stock_7c0f_1116 as Current
import replay_metal_natural_stock_91dc_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,digest=Current.R,Current.ROM,Current.PIN,Current.W,Current.N,Current.digest
BASE_SHA='855c8ca26e19180a6e6050c4f2565265a01d89d0d0c86279ea86e60dd12ac47a'
TEMPLATE_SHA='f7709d90e084f276bbf22b5c38b6a3e861d5e51aefe1681c70d0c10ec2123727'
KINDS=Previous.KINDS


@lru_cache(maxsize=2)
def bindings(raw,key='oneup'):
    assert key in KINDS and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    assert digest(Previous.TEMPLATE.read_bytes())==TEMPLATE_SHA
    old=Current.reference(raw);Current.payload(raw);c=deepcopy(Previous.bindings(old,key));c['sha']=PIN
    for name,h in c['hooks'].items():
        if h['space']=='prg':
            at=h['offset']+16;assert raw[at:at+len(h['bytes'])]==old[at:at+len(h['bytes'])]==bytes(h['bytes']),name
            lo=16+h['bank']*8192;h['bank_SHA256']=digest(raw[lo:lo+8192])
    return c


@lru_cache(maxsize=2)
def controller(raw,key='oneup'):
    old=Current.reference(raw);_,body=Previous.controller(old,key).split('\n',1)
    text='local C='+Text.lua(bindings(raw,key))+'\n'+body;LuaRuntime().compile(text);return text


def metadata(raw,key='oneup'):
    return dict(ROM_SHA256=PIN,reference91dc_SHA256=Current.REFERENCE,factory_SHA256=digest(Path(__file__).read_bytes()),
        controller_SHA256=digest(controller(raw,key).encode()),cold_facade_SHA256=digest(Path(Current.__file__).read_bytes()),
        previous_factory_SHA256=BASE_SHA,old91dc_APIs_frozen=True,actual7c0f_execution_required=True,
        owning_Metal_payload_headers_exact=True,current_native_hooks=bindings(raw,key)['hooks'],
        scope='Typed current config only; unchanged initial controls retain empty-bound negative, not native-ready item proof',
        outputs=0,Mesen=False,gameplay_seeds=0,game_bytes_changed=0)


def family(kind='oneup'):return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,kind),metadata=lambda raw,key:metadata(raw,kind))
