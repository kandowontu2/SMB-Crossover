"""New currenta3fb metadata facade; frozen f544/ed3e controls remain exact."""
from hashlib import sha256

import compose_dkjr_footer_bt91dc_current_1116 as C
import replay_dkjr_platform_footer_current_1116 as Frozen

H=lambda value:sha256(value).hexdigest()


def from_text(base,candidate,*,source=False):
    assert H(candidate)==C.CANDIDATE
    historical=C.historical_reference(candidate)
    expected=Frozen.source_controller(historical)if source else Frozen.controller(historical)
    assert base==expected
    count=2 if source else 1
    assert base.count(C.Footer.CANDIDATE)==count
    text=base.replace(C.Footer.CANDIDATE,C.CANDIDATE)
    assert text.replace(C.CANDIDATE,C.Footer.CANDIDATE)==base
    Frozen.Frozen.Frozen.Prior.Ground.LuaRuntime().compile(text)
    return text


def controller(candidate):
    return from_text(Frozen.controller(C.historical_reference(candidate)),candidate)


def source_controller(candidate):
    return from_text(Frozen.source_controller(C.historical_reference(candidate)),candidate,source=True)
