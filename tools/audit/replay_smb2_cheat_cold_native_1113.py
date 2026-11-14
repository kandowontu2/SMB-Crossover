"""Pure exact two-alias adapter; frozen5305 UI/inputs/assertions remain exact."""
from hashlib import sha256
import json
from pathlib import Path

import compose_smb2_cheat_cold_mirror_1113 as C
import replay_smb2_cheat_owner_native_1113 as Previous

PREVIOUS_SOURCE='2f0a5f42434d161fe5250aa41862e1c37f36d1a809099f15f72d836178bf0ae6'
PREVIOUS_LUA='53055897759c775a4f27c7a27d1b9af437bf4c566b3e1a6058bf8d34a98f4755'
LUA_SHA='9f693d9f667bb92bda9f4b8ffb060a7a1b550486e5e12568f67303b00b23f625'


def rebound(raw):
    assert sha256(raw).hexdigest()==C.CANDIDATE
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PREVIOUS_SOURCE
    parent=C.inverse(raw);original=Previous.controller(parent)
    assert sha256(original.encode()).hexdigest()==PREVIOUS_LUA
    assert original.count(C.PIN)==1
    text=original.replace(C.PIN,C.CANDIDATE,1);swaps=[]
    public=C.Owner.inverse(parent)
    for w in Previous.Frozen.bindings(public)[1]:
        if w['name']not in('game_gate_119','game_gate_120'):continue
        old=bytearray(C.CANONICAL);old[0xe037-C.BRIDGE]=0xde
        assert w['hex']==old.hex()
        at=16+w['offset'];assert raw[at:at+45]==C.CANONICAL
        before=Previous.Frozen.C.Owner.lua(w)
        after=Previous.Frozen.C.Owner.lua(dict(w,hex=C.CANONICAL.hex()))
        assert text.count(before)==1;text=text.replace(before,after,1);swaps.append((before,after))
    assert len(swaps)==2
    restored=text
    for before,after in reversed(swaps):
        assert restored.count(after)==1;restored=restored.replace(after,before,1)
    assert restored.replace(C.CANDIDATE,C.PIN,1)==original
    return text


def controller(raw):
    text=rebound(raw)
    Previous.C.D.C.Owner.Terrain.Frozen.Flag.Root.Base.LuaRuntime().compile(text)
    assert all(w not in text for w in('emu.write','emu.setState','io.open','takeScreenshot','saveState','loadState'))
    assert sha256(text.encode()).hexdigest()==LUA_SHA
    return text


def metadata(raw):
    text=controller(raw)
    return dict(ROM_SHA256=C.CANDIDATE,parent_SHA256=C.PIN,controller_SHA256=sha256(text.encode()).hexdigest(),
        previous_controller_SHA256=PREVIOUS_LUA,previous_factory_SHA256=PREVIOUS_SOURCE,
        only_ROM_pin_and_two_actual_clone_auth_payloads_changed=True,
        frozen_real_UI_inputs_and_all_route_assertions_exact=True,
        cheat_option_diagnostic=True,standard_stage_qualification=False,
        expected_native_contract='zero obsolete targets, every gate canonical, every FRC and resident return, complete25grounded1-2',
        event_cap=64,private_only=True,native_run=False,outputs=0)


if __name__=='__main__':
    parent,_=C.Owner.proposal(C.Owner.D.C.Owner.NIGHTLY.read_bytes());image,_=C.proposal(parent)
    print(json.dumps(metadata(image),separators=(',',':')),flush=True)
