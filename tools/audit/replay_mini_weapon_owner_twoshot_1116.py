"""Frozen ordinary earnedF/two-shot body on exact leased owning e32f bytes."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_mini_flower_twoshot_1327_1116 as Previous
import current_mini_weapon_owner_1116 as Current
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,H=Current.R,Current.ROM,Current.PIN,Current.W,Current.N,Current.H
C=Current.Compose
BASE_SHA='36f8fcb93b28145a58354d400bcd8aa49a9cfeb9f66d4f87d99f905ccc078b83'

@lru_cache(maxsize=1)
def bindings(raw):
    parent=Current.reference(raw);c=deepcopy(Previous.bindings(parent));c['sha']=PIN
    for h in c['hooks'].values():
        if not h['work']:
            bank=h['offset']//8192;at=16+bank*8192;h['bank_SHA256']=H(raw[at:at+8192]);assert raw[16+h['offset']:16+h['offset']+len(h['bytes'])]==bytes(h['bytes'])
    return c

@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower'and H(Path(Previous.__file__).read_bytes())==BASE_SHA
    _,body=Previous.controller(Current.reference(raw),key).split('\n',1)
    text='local C='+Text.lua(bindings(raw))+'\n'+body;LuaRuntime().compile(text);return text

def metadata(raw,key='flower'):
    q=Previous.metadata(Current.reference(raw),key);q.update(ROM_SHA256=PIN,factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(controller(raw,key).encode()),
        parent_frozen_twoshot_SHA256=BASE_SHA,controls_and_all_body_assertions_identical=True,owning_current=Current.metadata(raw),grant_SHA256=C.GRANT_SHA,game_bytes_changed=20)
    return q

def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
