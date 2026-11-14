"""Separate strict421 contact adapter; frozenda1f changes only its ROM pin."""
from hashlib import sha256
import json
from pathlib import Path

import compose_smb2_hidden_response_1114 as C
import replay_smb2_invincible_contact_1113 as Frozen
from check_ff_stdout_controller_source_1110 import LuaRuntime

Full=Frozen.Full
COMPOSER_SOURCE='7d8e2210a38952902694efcbb5334ae9b704902679b6353e43834f361bbee71a'
FROZEN_SOURCE='63031bae5c176ddddac76b5cb02a80720bcd40b0c10f6a875d40bbadcaae8078'
FROZEN_LUA='da1fd6ad6bb4bab273ec638d84186b50204602f59e400f659aaf1c97eb9226d9'
LUA_SHA='b27a809fc5d7011f8f050a5c7694675c8e73402ce9743578d55934d26b8078cb'


def rebound(raw):
    assert sha256(raw).hexdigest()==C.CANDIDATE
    assert sha256(Path(C.__file__).read_bytes()).hexdigest()==COMPOSER_SOURCE
    assert sha256(Path(Frozen.__file__).read_bytes()).hexdigest()==FROZEN_SOURCE
    parent=C.inverse(raw);assert sha256(parent).hexdigest()==C.PIN
    original=Frozen.controller(parent)
    assert sha256(original.encode()).hexdigest()==FROZEN_LUA and original.count(C.PIN)==1
    text=original.replace(C.PIN,C.CANDIDATE,1)
    assert text.replace(C.CANDIDATE,C.PIN,1)==original
    return text


def controller(raw):
    text=rebound(raw);LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    assert sha256(text.encode()).hexdigest()==LUA_SHA
    return text


def metadata(raw):
    text=controller(raw)
    return dict(ROM_SHA256=C.CANDIDATE,parent_SHA256=C.PIN,
        composer_SHA256=COMPOSER_SOURCE,frozen_factory_SHA256=FROZEN_SOURCE,
        frozen_controller_SHA256=FROZEN_LUA,controller_SHA256=sha256(text.encode()).hexdigest(),
        only_ROM_pin_rebound=True,real_title_options_Inv1_opening_exact=True,
        original_inputs_authentication_and_assertions_exact=True,
        positive_native_carry_and_box_overlap_health31_lives2_Star0_and30quiet_updates_required=True,
        full_stage=False,native_run=False,installed=False,outputs=0)


if __name__=='__main__':
    print(json.dumps(metadata(C.load_current_image()),separators=(',',':')),flush=True)
