"""Pure private movement-only adapter; root owns the actual Mesen queue.

Inputs, real cheat-option opening and all diagnostic/route assertions are
frozeneb9. Only the exact ROM pin changes. E037 alias debt remains observable
and blocks delivery; this is not an ordinary no-cheat stage qualification.
"""
from hashlib import sha256
import json
from pathlib import Path

import compose_smb2_cheat_owner_1113 as C
import replay_smb2_cold_gate_native_1113 as Frozen

FROZEN_SOURCE='6e1a95017100d08193b5c7298d89125066eaa6e6832bd55cde7bbd0fe4c042d1'
FROZEN_LUA='eb9ae28a623d58d75b5795e3620643c7e2b945a047e75df46ae3fbd9bec6102b'
LUA_SHA='53055897759c775a4f27c7a27d1b9af437bf4c566b3e1a6058bf8d34a98f4755'


def controller(raw):
    assert sha256(raw).hexdigest()==C.CANDIDATE
    assert sha256(Path(Frozen.__file__).read_bytes()).hexdigest()==FROZEN_SOURCE
    parent=C.inverse(raw)
    original=Frozen.controller(parent)
    assert sha256(original.encode()).hexdigest()==FROZEN_LUA
    assert original.count(C.PIN)==1 and C.CANDIDATE not in original
    text=original.replace(C.PIN,C.CANDIDATE,1)
    assert text.replace(C.CANDIDATE,C.PIN,1)==original
    assert text.count(C.CANDIDATE)==1
    C.D.C.Owner.Terrain.Frozen.Flag.Root.Base.LuaRuntime().compile(text)
    assert all(word not in text for word in('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    assert sha256(text.encode()).hexdigest()==LUA_SHA
    return text


def metadata(raw):
    text=controller(raw)
    return dict(ROM_SHA256=C.CANDIDATE,parent_SHA256=C.PIN,
        controller_SHA256=sha256(text.encode()).hexdigest(),frozen_controller_SHA256=FROZEN_LUA,
        frozen_factory_SHA256=FROZEN_SOURCE,only_exact_ROM_pin_rebound=True,
        real_UI_earned_Invincible_inputs_and_full_assertions_unchanged=True,
        cheat_option_diagnostic=True,standard_stage_qualification=False,
        movement_only_private=True,E037_alias_debt_untouched=True,delivery_blocked=True,
        passive_event_cap=64,native_run=False,outputs=0)


if __name__=='__main__':
    image,_=C.proposal(C.D.C.Owner.NIGHTLY.read_bytes())
    print(json.dumps(metadata(image),separators=(',',':')),flush=True)
