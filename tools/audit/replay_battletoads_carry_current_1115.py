"""Strict current dense stage controls and explicit40a/candidate read observer."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import compose_battletoads_carry_current_1115 as C
import replay_battletoads_idle_funded_1115 as FrozenStage
import replay_battletoads_idle_funded_benchmark_1115 as FrozenBench

R,ROM,W,N=C.R,C.ROM,FrozenStage.W,FrozenStage.N
IDENTITIES=FrozenStage.IDENTITIES
BENCH_SHA='3bee1e34d1da8ebf737d555e996286fc36198ab78e929f9540fd58c230b224c4'
STAGE_SHA='401a6b933a9fe84996a4070c92f56da2eb9c8a8f1cfd17287adc9eea9b82cb68'
BODY_SHA='f76943af78cedc9d38c6433ed438a2040ccc186c18c2dd6fb686a4fbde179f7e'


def sources():
    C.lease();assert C.digest(Path(FrozenStage.__file__).read_bytes())==STAGE_SHA
    assert C.digest(Path(FrozenBench.__file__).read_bytes())==BENCH_SHA


@lru_cache(maxsize=2)
def reference(raw):
    sources();return C.reference(C.inverse(raw))


class Frozen:
    LuaRuntime=FrozenStage.Frozen.LuaRuntime
    @staticmethod
    def normalize(raw):return FrozenStage.normalize(reference(raw))


normalize=Frozen.normalize


def refresh(raw,q):
    q=deepcopy(q);q['sha']=C.digest(raw)
    for hook in q['hooks'].values():
        at=16+hook['offset'];assert raw[at:at+len(hook['bytes'])]==bytes(hook['bytes'])
        if'bank'in hook:
            at=16+hook['bank']*8192;hook['bank_SHA256']=C.digest(raw[at:at+8192])
    return q


@lru_cache(maxsize=4)
def bindings(raw,key):return refresh(raw,FrozenStage.bindings(reference(raw),key))


def rebound(text,q):
    old_prefix,body=text.split('\n',1);assert old_prefix.startswith('local C=')
    lua=FrozenStage.Previous.Stage.Previous.Parent.Frozen.lua
    result='local C='+lua(q)+'\n'+body
    Frozen.LuaRuntime().compile(result)
    assert '\r'not in result and result.split('\n',1)[1]==body
    assert not any(x in result for x in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    return result


@lru_cache(maxsize=4)
def controller(raw,key='rash'):return rebound(FrozenStage.controller(reference(raw),key),bindings(raw,key))


@lru_cache(maxsize=2)
def observer_config(raw):
    sources();pin=C.digest(raw)
    if pin==C.PIN:old=C.reference_parent(raw)
    else:assert pin==C.CANDIDATE;old=reference(raw)
    return refresh(raw,FrozenBench.config(old))


@lru_cache(maxsize=2)
def cadence_reads(raw):
    pin=C.digest(raw)
    old=C.reference_parent(raw)if pin==C.PIN else reference(raw)
    text=rebound(FrozenBench.controller(old),observer_config(raw))
    assert C.digest(text.split('\n',1)[1].encode())==BODY_SHA
    return text


def metadata(raw,key=None):
    if key is not None:
        return dict(ROM_SHA256=C.digest(raw),identity=key,controller_SHA256=C.digest(controller(raw,key).encode()),
            frozen_route_body_unchanged=True,normal_controls_only=True,outputs=0)
    reference(raw)
    return dict(ROM_SHA256=C.digest(raw),parent_SHA256=C.PIN,
        stage_controllers={k:C.digest(controller(raw,k).encode())for k in IDENTITIES},
        cadence_controller_SHA256=C.digest(cadence_reads(raw).encode()),cadence_body_SHA256=BODY_SHA,
        parent174fa_cadence_controller_SHA256=C.digest(cadence_reads(C.inverse(raw)).encode()),
        NmiSkipped_RAM=observer_config(raw)['ram']['NmiSkipped'],ordinary_controls_only=True,
        source_only=True,native_run=False,outputs=0)
