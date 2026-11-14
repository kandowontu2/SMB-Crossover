"""Explicit private82ec rebound of frozen421 image probes; defaults unchanged."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import compose_shared_world_chr_reset_1114 as Compose
import replay_shared_world_sprite_images_1114 as Previous

R,ROM,PIN,W,N=Previous.R,Previous.ROM,Compose.CANDIDATE,Previous.W,Previous.N
IDENTITIES=Previous.IDENTITIES
PREVIOUS_SOURCE='eaec9ad2d54d6d9d0230a287f814c03c33ed4ed4ad95b088efcd63bd24a10440'


class Frozen:
    LuaRuntime=Previous.Frozen.LuaRuntime
    @staticmethod
    def normalize(raw):return Previous.Frozen.normalize(Compose.inverse(raw))


@lru_cache(maxsize=8)
def bindings(raw,key):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PREVIOUS_SOURCE
    parent=Compose.inverse(raw);c=deepcopy(Previous.bindings(parent,key));c['sha']=PIN
    for hook in c['hooks'].values():
        if 'bank'not in hook:continue
        bank=hook['bank'];lo=16+bank*8192
        hook['bank_SHA256']=sha256(raw[lo:lo+8192]).hexdigest()
        at=16+hook['offset'];assert raw[at:at+len(hook['bytes'])]==bytes(hook['bytes'])
    return c


@lru_cache(maxsize=8)
def controller(raw,key):
    c=bindings(raw,key)
    assert sha256(Previous.TEMPLATE.read_bytes()).hexdigest()==Previous.TEMPLATE_SHA
    template=Previous.TEMPLATE.read_text(encoding='utf-8')
    old='Two ordinary current421 world-sprite observations'
    assert template.count(old)==1
    template=template.replace(old,'Two ordinary private82ec world-sprite observations')
    text='local C='+Previous.Frozen.lua(c)+'\n'+template
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    return text


def metadata(raw,key):
    parent=Compose.inverse(raw);_,q=Compose.proposal(parent);c=bindings(raw,key)
    return dict(ROM_SHA256=PIN,identity=key,compiled_menu={k:c[k]for k in('name','slot','cycle','owner','role')},
        controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        frozen421_factory_SHA256=PREVIOUS_SOURCE,frozen421_template_SHA256=Previous.TEMPLATE_SHA,
        rebound='Only exact granted29B image provenance, actual changed-bank SHA256, and private observation label',
        composition=q,gameplay_seeds=0,outputs=0,Mesen_run=False)


@lru_cache(maxsize=1)
def stage_bindings(raw,key='toad'):
    assert key=='toad'
    parent=Compose.inverse(raw);c=deepcopy(Previous.Frozen.bindings(parent,key));c['sha']=PIN
    for h in c['hooks'].values():
        if'bank'in h:
            lo=16+h['bank']*8192;h['bank_SHA256']=sha256(raw[lo:lo+8192]).hexdigest()
    return c


@lru_cache(maxsize=1)
def stage_controller(raw,key='toad'):
    parent=Compose.inverse(raw);text=Previous.Frozen.controller(parent,key)
    prefix='local C='+Previous.Frozen.lua(Previous.Frozen.bindings(parent,key))+'\n'
    assert text.startswith(prefix)
    text='local C='+Previous.Frozen.lua(stage_bindings(raw,key))+'\n'+text[len(prefix):]
    Frozen.LuaRuntime().compile(text)
    return text
