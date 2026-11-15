"""New strict BT-f11 classic-DK source boundary; frozencf7 stays unchanged."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256

import compose_battletoads_camera_handoff_1114 as BT
import replay_dk_full11_current_1114 as Previous

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,BT.CANDIDATE
KIND='battletoads-f11-classic-dk'


@lru_cache(maxsize=1)
def parent(raw,*,kind=KIND):
    assert kind==KIND and isinstance(raw,bytes)and sha256(raw).hexdigest()==PIN
    old=BT.inverse(raw);assert sha256(old).hexdigest()==Previous.PIN
    assert BT.proposal(old)[0]==raw
    return old


@lru_cache(maxsize=1)
def normalize(raw):return Previous.normalize(parent(raw))


@lru_cache(maxsize=1)
def bindings(raw,key='donkey_kong'):
    q=deepcopy(Previous.bindings(parent(raw),key));q['sha']=PIN
    for h in q['hooks'].values():
        at=16+h['offset'];assert raw[at:at+len(h['bytes'])]==bytes(h['bytes'])
        if'bank'in h:
            at=16+h['bank']*8192;h['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
    return q
