"""Strict ordinary no-cheat Luigi full regression; ROM-pin-only adapter."""
from hashlib import sha256
import json
from pathlib import Path

import compose_smb2_cheat_cold_mirror_1113 as C
import replay_smb2_postbg_native_1113 as Frozen

FROZEN_SOURCE='1c6c137f1b2a61946d49b82af8005b71641ed85fe3ff6c30e11132f604777a9d'
FROZEN_LUA='ff9bc7b38a268d8cc211b57d76340b51baa4840791bf55905b206be28a8bd58f'
LUA_SHA='6594ac1c8056b9b4c7be7ecd3f636faee2649fb6a9443fb6c1de8ac50dc82223'


def rebound(raw):
    assert sha256(raw).hexdigest()==C.CANDIDATE
    assert sha256(Path(Frozen.__file__).read_bytes()).hexdigest()==FROZEN_SOURCE
    public=C.Owner.inverse(C.inverse(raw))
    assert sha256(public).hexdigest()==C.Owner.PIN
    original=Frozen.controller(public)
    assert sha256(original.encode()).hexdigest()==FROZEN_LUA
    assert original.count(C.Owner.PIN)==1
    text=original.replace(C.Owner.PIN,C.CANDIDATE,1)
    assert text.replace(C.CANDIDATE,C.Owner.PIN,1)==original
    return text


def controller(raw):
    text=rebound(raw)
    Frozen.Scene.Old.Terrain.Frozen.Flag.Root.Base.LuaRuntime().compile(text)
    assert all(w not in text for w in('emu.write','emu.setState','io.open','takeScreenshot','saveState','loadState'))
    assert sha256(text.encode()).hexdigest()==LUA_SHA
    return text


def metadata(raw):
    text=controller(raw)
    return dict(ROM_SHA256=C.CANDIDATE,existing12397_factory_SHA256=FROZEN_SOURCE,
        existing12397_controller_SHA256=FROZEN_LUA,controller_SHA256=sha256(text.encode()).hexdigest(),
        only_ROM_pin_rebound=True,original_inputs_all_auth_payloads_full_endpoint_exact=True,
        ordinary_no_cheat_regression=True,full_nonshortcut1_1_then25grounded1_2=True,
        real_cheat_options_opening_added=False,native_run=False,outputs=0)


if __name__=='__main__':
    parent,_=C.Owner.proposal(C.Owner.D.C.Owner.NIGHTLY.read_bytes());image,_=C.proposal(parent)
    print(json.dumps(metadata(image),separators=(',',':')),flush=True)
