"""Root-only ordinary controllers for the funded source image; no file runner."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256

import compose_battletoads_idle_funded_1115 as C
import replay_battletoads_native_service_1114 as Previous

R,ROM,W,N=Previous.R,Previous.ROM,Previous.W,Previous.N
IDENTITIES=Previous.IDENTITIES


@lru_cache(maxsize=2)
def reference(raw):return C.Packet.reference(C.inverse(raw))


class Frozen:
    LuaRuntime=Previous.Frozen.LuaRuntime
    @staticmethod
    def normalize(raw):return Previous.normalize(reference(raw))


normalize=Frozen.normalize


@lru_cache(maxsize=4)
def bindings(raw,key):
    q=deepcopy(Previous.bindings(reference(raw),key));q['sha']=C.CANDIDATE
    for hook in q['hooks'].values():
        at=16+hook['offset'];assert raw[at:at+len(hook['bytes'])]==bytes(hook['bytes'])
        if 'bank'in hook:
            at=16+hook['bank']*8192;hook['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
    return q


def rebound(raw,text,q):
    prefix,body=text.split('\n',1)
    assert prefix.startswith('local C=')
    result='local C='+Previous.Stage.Previous.Parent.Frozen.lua(q)+'\n'+body
    assert result.split('\n',1)[1]==body
    Frozen.LuaRuntime().compile(result)
    assert not any(s in result for s in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    return result


@lru_cache(maxsize=4)
def controller(raw,key='rash'):
    return rebound(raw,Previous.controller(reference(raw),key),bindings(raw,key))


@lru_cache(maxsize=2)
def cadence_reads(raw):
    parent=reference(raw);q=deepcopy(bindings(raw,'rash'))
    q['ram']['NmiSkipped']=Previous.Idle.config(Previous.parent(parent))['ram']['NmiSkipped']
    return rebound(raw,Previous.cadence_reads(parent),q)


def metadata(raw,key=None):
    C.inverse(raw)
    if key is not None:
        return dict(ROM_SHA256=C.CANDIDATE,parent_SHA256=C.PIN,identity=key,
            controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
            frozen_stage_body_unchanged=True,normal_controls_only=True,gameplay_seeds=0,outputs=0)
    return dict(ROM_SHA256=C.CANDIDATE,parent_SHA256=C.PIN,
        stage_controllers={key:sha256(controller(raw,key).encode()).hexdigest()for key in('rash','zitz')},
        literal_read_idle48_Right32_controller_SHA256=sha256(cadence_reads(raw).encode()).hexdigest(),
        LF_only=True,ordinary_controls_only=True,gameplay_state_seeds=0,
        frozen_route_and_read_observer_bodies_unchanged=True,native_not_run=True,outputs=0)
