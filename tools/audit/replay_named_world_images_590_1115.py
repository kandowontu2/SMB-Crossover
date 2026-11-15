"""Exact590 facade of frozen DK and six WWF opening image controllers."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import compose_prince_window567_1115 as Current
import compose_battletoads_native_service_1114 as Service
import compose_native_floatey_score_1114 as Score
import compose_battletoads_camera_handoff_1114 as Camera
import compose_gimmick_private_window7_1114 as Gimmick
import compose_dk_private_sprite_window7_1114 as Donkey
import replay_dk_private_sprite_window7_1114 as DK
import replay_shared_world_chr_reset_1114 as WWF

R,ROM,PIN=DK.R,DK.ROM,Current.CANDIDATE
IDENTITIES={k:v for k,v in WWF.IDENTITIES.items()if k!='prince'}
PINS={DK:'693f3d005217112563435604dafa423af7cf3f22d94450a229672f71efef9402',
      WWF:'0fb4e745e0ec7e47a27f43d3f8b7015e8fbc80f87225fec08751d20f444424c0'}


@lru_cache(maxsize=1)
def owning(raw):
    assert isinstance(raw,bytes)and sha256(raw).hexdigest()==PIN
    old=Current.inverse(raw)
    for component in(Service,Score,Camera,Gimmick):old=component.inverse(old)
    assert sha256(old).hexdigest()==DK.PIN
    older=Donkey.inverse(old);assert sha256(older).hexdigest()==WWF.PIN
    for page in(16,17):
        at=1048592+page*1024
        assert raw[at:at+1024]==old[at:at+1024]==older[at:at+1024]
    return old,older


@lru_cache(maxsize=7)
def controller(raw,key):
    assert key in IDENTITIES
    old,older=owning(raw);factory,parent=(DK,old)if key=='donkey_kong'else(WWF,older)
    assert sha256(Path(factory.__file__).read_bytes()).hexdigest()==PINS[factory]
    config=factory.bindings(parent,key);text=factory.controller(parent,key)
    to_lua=WWF.Previous.Frozen.lua
    prefix='local C='+to_lua(config)+'\n';assert text.startswith(prefix)
    current=deepcopy(config);current['sha']=PIN
    for h in current['hooks'].values():
        at=16+h['offset'];assert raw[at:at+len(h['bytes'])]==bytes(h['bytes'])
        if 'bank'in h:
            at=16+h['bank']*8192;current_hash=sha256(raw[at:at+8192]).hexdigest()
            h['bank_SHA256']=current_hash
    result='local C='+to_lua(current)+'\n'+text[len(prefix):]
    assert result.split('\n',1)[1]==text.split('\n',1)[1]
    factory.Frozen.LuaRuntime().compile(result)
    assert not any(s in result for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    return result


def metadata(raw,key):
    text=controller(raw,key)
    return dict(ROM_SHA256=PIN,identity=key,menu=IDENTITIES[key],
        controller_SHA256=sha256(text.encode()).hexdigest(),
        maximum_images=3 if key=='donkey_kong'else 2,
        controls_and_observers_unchanged=True,outputs=0,gameplay_seeds=0)


if __name__=='__main__':
    import json
    raw=ROM.read_bytes()
    for key in IDENTITIES:print(json.dumps(metadata(raw,key),separators=(',',':')),flush=True)
