"""Explicit Gimmick7 stage/image adapters; frozen parent Lua recipes intact."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256

import compose_gimmick_private_window7_1114 as Compose
import replay_mr_gimmick_full11_current_1114 as Stage
import replay_gimmick_world_sprite_images_1114 as Images

R,ROM,W,N,PIN=Stage.R,Stage.ROM,Stage.W,Stage.N,Compose.CANDIDATE
IDENTITIES=Stage.IDENTITIES


class Frozen:
    LuaRuntime=Stage.Frozen.LuaRuntime
    @staticmethod
    def normalize(raw):return Stage.normalize(Compose.inverse(raw))


normalize=Frozen.normalize


def rebound_bindings(raw,key,factory):
    parent=Compose.inverse(raw);q=deepcopy(factory.bindings(parent,key));q['sha']=PIN
    for h in q['hooks'].values():
        if'bank'in h:
            at=16+h['bank']*8192;h['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
    return q


@lru_cache(maxsize=1)
def bindings(raw,key='mr_gimmick'):return rebound_bindings(raw,key,Stage)


@lru_cache(maxsize=1)
def image_bindings(raw,key='mr_gimmick'):return rebound_bindings(raw,key,Images)


def rebound(raw,key,factory,config):
    parent=Compose.inverse(raw);text=factory.controller(parent,key)
    prefix='local C='+Stage.Frozen.lua(factory.bindings(parent,key))+'\n'
    assert text.startswith(prefix)
    result='local C='+Stage.Frozen.lua(config)+'\n'+text[len(prefix):]
    Frozen.LuaRuntime().compile(result)
    return result


@lru_cache(maxsize=1)
def controller(raw,key='mr_gimmick'):return rebound(raw,key,Stage,bindings(raw,key))


stage_controller=controller


@lru_cache(maxsize=1)
def image_controller(raw,key='mr_gimmick'):return rebound(raw,key,Images,image_bindings(raw,key))


def metadata(raw,key='mr_gimmick'):
    parent=Compose.inverse(raw);old=Stage.metadata(parent,key);old.update(ROM_SHA256=PIN,
        controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),typed_rebound='Only candidate ROM provenance/changed-bank hashes; parent route text unchanged',
        parent_controller_SHA256=sha256(Stage.controller(parent,key).encode()).hexdigest())
    return old


def image_metadata(raw,key='mr_gimmick'):
    parent=Compose.inverse(raw);old=Images.metadata(parent,key);old.update(ROM_SHA256=PIN,
        controller_SHA256=sha256(image_controller(raw,key).encode()).hexdigest(),typed_rebound='Only candidate ROM provenance/changed-bank hashes; parent image route text unchanged',
        parent_controller_SHA256=sha256(Images.controller(parent,key).encode()).hexdigest())
    return old


class ImageFactory:
    R,ROM,W,N,PIN=R,ROM,W,N,PIN
    IDENTITIES=IDENTITIES
    Frozen=Frozen
    bindings=staticmethod(image_bindings)
    controller=staticmethod(image_controller)
    metadata=staticmethod(image_metadata)
