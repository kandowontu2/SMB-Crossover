"""Strictae66 WWF image probes; frozen82/421 factories remain unchanged."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import compose_battletoads_native_service_1114 as Service
import compose_native_floatey_score_1114 as Score
import compose_battletoads_camera_handoff_1114 as Camera
import compose_gimmick_private_window7_1114 as Gimmick
import compose_dk_private_sprite_window7_1114 as Donkey
import replay_shared_world_chr_reset_1114 as Previous

R,ROM,PIN,W,N=Previous.R,Previous.ROM,Service.CANDIDATE,Previous.W,Previous.N
IDENTITIES={key:Previous.IDENTITIES[key]for key in('hogan','andre')}
PREVIOUS_SHA='0fb4e745e0ec7e47a27f43d3f8b7015e8fbc80f87225fec08751d20f444424c0'


@lru_cache(maxsize=1)
def owning82(raw):
    assert isinstance(raw,bytes)and sha256(raw).hexdigest()==PIN,'Expected exact deliveredae66'
    old=Service.inverse(raw)
    for component in(Score,Camera,Gimmick,Donkey):old=component.inverse(old)
    assert sha256(old).hexdigest()==Previous.PIN
    for page in(16,17):
        at=1048592+page*1024;assert raw[at:at+1024]==old[at:at+1024]
    return old


class Frozen:
    LuaRuntime=Previous.Frozen.LuaRuntime
    @staticmethod
    def normalize(raw):return Previous.Frozen.normalize(owning82(raw))


@lru_cache(maxsize=2)
def bindings(raw,key):
    assert key in IDENTITIES
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PREVIOUS_SHA
    old=owning82(raw);q=deepcopy(Previous.bindings(old,key));q['sha']=PIN
    for hook in q['hooks'].values():
        at=16+hook['offset'];assert raw[at:at+len(hook['bytes'])]==bytes(hook['bytes'])
        if'bank'in hook:
            at=16+hook['bank']*8192;hook['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
    return q


@lru_cache(maxsize=2)
def controller(raw,key):
    old=owning82(raw);text=Previous.controller(old,key)
    prefix='local C='+Previous.Previous.Frozen.lua(Previous.bindings(old,key))+'\n'
    assert text.startswith(prefix)
    result='local C='+Previous.Previous.Frozen.lua(bindings(raw,key))+'\n'+text[len(prefix):]
    assert result.split('\n',1)[1]==text.split('\n',1)[1],'Frozen ordinary two-spot body'
    Frozen.LuaRuntime().compile(result)
    return result


def metadata(raw,key):
    c=bindings(raw,key)
    return dict(ROM_SHA256=PIN,identity=key,compiled_menu={k:c[k]for k in('name','slot','cycle','owner','role')},
        controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        exact_typed_chain='ae66→571→F11→cf7→1daca→82',maximum_images=2,maximum_PNG_bytes=65536,
        frozen82_factory_SHA256=PREVIOUS_SHA,frozen_control_body_unchanged=True,
        natural_Goomba_and_mature_Mushroom_only=True,gameplay_seeds=0,outputs=0,Mesen_run=False)
