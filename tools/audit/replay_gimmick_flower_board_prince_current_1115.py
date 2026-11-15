"""Strict590 config adapter of the frozenae66 genuine Flower boarding body."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import compose_prince_window567_1115 as Current
import replay_gimmick_flower_board_current_1115 as Previous
import replay_smb1_alts_full11_1114 as Text

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Current.CANDIDATE
IDENTITIES=Previous.IDENTITIES
PARENT_SOURCE='9b875f9ea4eda6ad3d334caa6e56913be917d290ce98e1d33c18dc7202b7e49e'
PARENT_LUA='f358274e9abd17883a6e6a3280417db786aee625469f020753449c0c977b38ce'


@lru_cache(maxsize=1)
def owningAE(raw):
    assert isinstance(raw,bytes)and sha256(raw).hexdigest()==PIN,'Expected exact deliveredPrince590'
    old=Current.inverse(raw);assert sha256(old).hexdigest()==Previous.PIN
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT_SOURCE
    return old


def normalize(raw):return Previous.normalize(owningAE(raw))


class Frozen:
    LuaRuntime=Previous.Frozen.LuaRuntime
    normalize=staticmethod(normalize)


@lru_cache(maxsize=1)
def bindings(raw,key='mr_gimmick'):
    q=deepcopy(Previous.bindings(owningAE(raw),key));q['sha']=PIN
    for h in q['hooks'].values():
        at=16+h['offset'];assert raw[at:at+len(h['bytes'])]==bytes(h['bytes'])
        if'bank'in h:
            at=16+h['bank']*8192;h['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
    return q


@lru_cache(maxsize=1)
def controller(raw,key='mr_gimmick'):
    old=owningAE(raw);text=Previous.controller(old,key)
    assert sha256(text.encode()).hexdigest()==PARENT_LUA
    prefix='local C='+Text.lua(Previous.bindings(old,key))+'\n';assert text.startswith(prefix)
    body=text[len(prefix):];result='local C='+Text.lua(bindings(raw,key))+'\n'+body
    assert result.split('\n',1)[1]==text.split('\n',1)[1]
    Frozen.LuaRuntime().compile(result)
    return result


def metadata(raw,key='mr_gimmick'):
    old=owningAE(raw);q=Previous.metadata(old,key)
    q.update(ROM_SHA256=PIN,controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        parent_ae66_ROM_SHA256=Previous.PIN,parent_ae66_factory_SHA256=PARENT_SOURCE,
        parent_ae66_controller_SHA256=PARENT_LUA,strict590_inverse='compose_prince_window567_1115.inverse',
        exact_frozen_control_and_observer_body=True,current_native_hook_bytes_and_bank_SHA256=True)
    return q
