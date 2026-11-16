"""Frozen earnedF/two-shot controls, config only rebound to owning 9826."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_mini_weapon_owner_twoshot_1116 as Previous
import current_mini_weapon_owner_a2_1116 as Current
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,H=Current.R,Current.ROM,Current.PIN,Current.W,Current.N,Current.H
C=Current.Compose
BASE_SHA='9f9b72ef23488f6a72507b281ecaaa1d33db976d33518c796d383496bce89ecd'
BODY_SHA='70f4d656bd1f512c3b11c478bae13d1d4b3837ae9e5843c9ff6fcbc93f903977'

@lru_cache(maxsize=1)
def bindings(raw):
    c=deepcopy(Previous.bindings(Current.reference(raw)));c['sha']=PIN
    for h in c['hooks'].values():
        if not h['work']:
            at=16+h['offset'];bank=h['offset']//8192;assert raw[at:at+len(h['bytes'])]==bytes(h['bytes'])
            h['bank_SHA256']=H(raw[16+bank*8192:16+(bank+1)*8192])
    return c

@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower'and H(Path(Previous.__file__).read_bytes())==BASE_SHA
    body=Previous.controller(Current.reference(raw),key).split('\n',1)[1];assert H(body.encode())==BODY_SHA
    text='local C='+Text.lua(bindings(raw))+'\n'+body;LuaRuntime().compile(text);return text

def metadata(raw,key='flower'):
    q=Previous.metadata(Current.reference(raw),key);q.update(ROM_SHA256=PIN,factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(controller(raw,key).encode()),
        frozen_body_SHA256=BODY_SHA,controls_and_all_body_assertions_identical=True,owning_current=Current.metadata(raw),grant_SHA256=C.GRANT_SHA,
        facade_SHA256=H(Path(Current.__file__).read_bytes()),versioned_e32f_metadata_only=True,Sonic94_preserved=True);return q

def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
