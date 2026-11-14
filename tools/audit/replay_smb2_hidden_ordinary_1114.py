"""Separate strict421 ordinary adapter; frozen6594 changes only its ROM pin."""
from hashlib import sha256
import json
from pathlib import Path

import compose_smb2_hidden_response_1114 as C
import replay_smb2_cheat_cold_regress_1113 as Frozen
from check_ff_stdout_controller_source_1110 import LuaRuntime

COMPOSER_SOURCE='7d8e2210a38952902694efcbb5334ae9b704902679b6353e43834f361bbee71a'
FROZEN_SOURCE='e7ab69df1a20981d854bcb676ffcc816930aac4f53510ac5da6080216542d2e6'
FROZEN_LUA='6594ac1c8056b9b4c7be7ecd3f636faee2649fb6a9443fb6c1de8ac50dc82223'
LUA_SHA='0705cb62eb0ee787071d466b8019aa632cea516eee65ee8c0857b0ac2c01cf15'


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
        only_ROM_pin_rebound=True,original_inputs_authentication_and_assertions_exact=True,
        ordinary_no_cheat=True,full_1_1_then25grounded1_2=True,
        native_run=False,installed=False,outputs=0)


if __name__=='__main__':
    print(json.dumps(metadata(C.load_current_image()),separators=(',',':')),flush=True)
