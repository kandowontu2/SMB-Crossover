"""Exact cf7 classic-DK source/image input; frozen1daca APIs stay strict."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256

import compose_gimmick_private_window7_1114 as Gimmick
import replay_dk_private_sprite_window7_1114 as Previous

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Gimmick.CANDIDATE
IDENTITIES=Previous.IDENTITIES
KIND='gimmick-cf7-classic-dk'


@lru_cache(maxsize=1)
def parent(raw,*,kind=KIND):
    assert kind==KIND and isinstance(raw,bytes)and sha256(raw).hexdigest()==PIN
    result=Gimmick.inverse(raw)
    assert sha256(result).hexdigest()==Previous.PIN
    assert Gimmick.proposal(result)[0]==raw
    return result


class Frozen:
    LuaRuntime=Previous.Frozen.LuaRuntime
    @staticmethod
    def normalize(raw):return Previous.Frozen.normalize(parent(raw))


@lru_cache(maxsize=1)
def bindings(raw,key='donkey_kong'):
    old=parent(raw);q=deepcopy(Previous.bindings(old,key));q['sha']=PIN
    for h in q['hooks'].values():
        at=16+h['offset'];assert raw[at:at+len(h['bytes'])]==bytes(h['bytes'])
        if'bank'in h:
            at=16+h['bank']*8192;h['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
    return q


@lru_cache(maxsize=1)
def controller(raw,key='donkey_kong'):
    old=parent(raw);text=Previous.controller(old,key)
    encode=Previous.Previous.Previous.Frozen.lua
    prefix='local C='+encode(Previous.bindings(old,key))+'\n'
    assert text.startswith(prefix)
    result='local C='+encode(bindings(raw,key))+'\n'+text[len(prefix):]
    Frozen.LuaRuntime().compile(result)
    return result


def metadata(raw,key='donkey_kong'):
    q=Previous.metadata(parent(raw),key)
    q.update(ROM_SHA256=PIN,controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        typed_input=KIND,model_parent_SHA256=Previous.PIN,
        rebound_scope='ROM hash and exact changed bank hashes only; image controls unchanged')
    return q
