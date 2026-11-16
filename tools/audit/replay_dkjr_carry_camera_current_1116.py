"""Candidate-bound unchanged ed3e ordinary replay with25 grounded motor returns."""
from hashlib import sha256
import compose_dkjr_carry_camera_current_1116 as C
import replay_dkjr_public_fourth_carried_bc5_1115 as Frozen

H = lambda value: sha256(value).hexdigest()
BASE = 'ed3e7206e7e2cd29f403048d4816de5c01f58768b53113eba5021f24ade6d4b1'


def one(text, before, after):
    assert text.count(before) == 1
    return text.replace(before, after, 1)


def from_text(base, candidate):
    assert H(candidate) == C.CANDIDATE and H(base.encode()) == BASE
    parent = C.inverse(candidate)
    reference = C.reference(parent)
    assert H(reference) == Frozen.Prior.PIN
    old_cookie = reference[534485:534501].hex()
    new_cookie = candidate[534485:534501].hex()
    text = one(base, Frozen.Prior.PIN, C.CANDIDATE)
    text = one(text, "cookie=='"+old_cookie+"'", "cookie=='"+new_cookie+"'")
    restored = one(text, C.CANDIDATE, Frozen.Prior.PIN)
    restored = one(restored, "cookie=='"+new_cookie+"'", "cookie=='"+old_cookie+"'")
    assert restored == base
    Frozen.Prior.Ground.LuaRuntime().compile(text)
    return text


def controller(candidate):
    parent = C.inverse(candidate)
    reference = C.reference(parent)
    base = Frozen.controller(reference)
    return from_text(base, candidate)


def source_controller(candidate):
    text = controller(candidate)
    text = one(text, "local rom=os.getenv('SMB_STDOUT_ROM_SHA')or''", f'local rom="{C.CANDIDATE}"')
    text = one(text, "os.getenv('SMB_TEST_VARIANT')=='0'", 'true')
    assert text.count("os.getenv('SMB_DKJR_FAST_ROUTE')=='1'") == 2
    text = text.replace("os.getenv('SMB_DKJR_FAST_ROUTE')=='1'", 'true')
    return one(text, "emu.addEventCallback(guarded('input',function()",
        "if CPU_CONTROLLER_OPENING then frame=541;playing=true end\n"
        "emu.addEventCallback(guarded('input',function()")
