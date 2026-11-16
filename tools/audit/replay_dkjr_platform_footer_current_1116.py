"""Strict f544 metadata rebind of the frozen camera/ed3e ordinary control."""
from hashlib import sha256

import compose_dkjr_platform_footer_current_1116 as C
import replay_dkjr_carry_camera_current_1116 as Frozen

H=lambda value:sha256(value).hexdigest()
BASE='cae70c1332a3b7451cd37597f3da4713dc1903a415ecb23debc22b6567afb82a'
SOURCE_BASE='9afeb6348e4721bbdf1ec67544cace4d67158d34486459ba06c6e130b0c3fa49'


def from_text(base,candidate,*,source=False):
    assert H(candidate)==C.CANDIDATE
    assert H(base.encode())==(SOURCE_BASE if source else BASE)
    C.inverse(candidate)
    count=2 if source else 1
    assert base.count(C.PIN)==count
    text=base.replace(C.PIN,C.CANDIDATE)
    assert text.replace(C.CANDIDATE,C.PIN)==base
    Frozen.Frozen.Prior.Ground.LuaRuntime().compile(text)
    return text


def controller(candidate):
    parent=C.inverse(candidate)
    return from_text(Frozen.controller(parent),candidate)


def source_controller(candidate):
    parent=C.inverse(candidate)
    return from_text(Frozen.source_controller(parent),candidate,source=True)
