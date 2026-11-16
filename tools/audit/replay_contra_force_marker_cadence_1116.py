"""Explicit6a3/ffbb Burns cadence prefix; frozen8752 observer body unchanged."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import replay_contra_force_current_idle_1115 as Frozen
import contra_force_p1_work_marker_model_1116 as M

C=M.C
R,ROM=C.R,C.ROM
FROZEN_SHA='f8d7dc9a9c3a85cee4c3d142f590fb460f35d68c972c5d7c80003eb9c99be875'
BODY_SHA='6e1bababb077ad935556b7b2202f001c76c40a1119e8add52d2a9b41086e1a31'
LUA_SHA={C.PIN:'94012d8bfb38eae43a19ee49e7e684bbcceef7a94871a701c6944711440d89f3',
    C.CANDIDATE:'564fcbee9e3f9f34c0b5b506e373c13dd1a6119be1c4c8daa3aaa010a729771f'}


@lru_cache(maxsize=2)
def bindings(raw,key='burns'):
    assert key=='burns','This timing facade admits only the qualified Burns empty opening'
    assert C.H(Path(Frozen.__file__).read_bytes())==FROZEN_SHA
    parent=M.parent(raw);z,_=C.Plan.inputs(parent)
    q=deepcopy(Frozen.bindings(z['reference'],key));q['sha']=C.H(raw)
    assert q['key']=='burns'and q['variant']==0
    for h in q['hooks'].values():
        at=16+h['offset'];assert raw[at:at+len(h['bytes'])]==bytes(h['bytes'])
        bank=16+h['bank']*8192;h['bank_SHA256']=C.H(raw[bank:bank+8192])
    carrier=raw[C.Plan.Audit.P.CHR+935*1024:C.Plan.Audit.P.CHR+959*1024]
    for h in q['cf']['hooks'].values():
        tag=h['physical_RAM'];pc=h['pc'];at=(tag-1)*8192+(pc&8191)
        assert carrier[at:at+len(h['bytes'])]==bytes(h['bytes'])
    assert raw[573373:573389]==raw[642966:642982]
    q['cf']['cookie']=list(raw[573373:573389]);q['cf']['carrier_SHA256']=C.H(carrier)
    return q


@lru_cache(maxsize=2)
def controller(raw,key='burns'):
    q=bindings(raw,key);body=Frozen.body();assert C.H(body.encode())==BODY_SHA
    text='local C='+Frozen.Clock.Frozen.lua(q)+'\n'+body
    Frozen.Clock.Frozen.LuaRuntime().compile(text)
    assert '\r'not in text and text.split('\n',1)[1]==body
    assert not any(word in text for word in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    if C.H(raw)in LUA_SHA:assert C.H(text.encode())==LUA_SHA[C.H(raw)]
    return text


def metadata(raw):
    q=bindings(raw);parent=M.parent(raw);d=C.Plan.descriptor(parent)
    return dict(actual_ROM_SHA256=C.H(raw),owning_parent_SHA256=C.PIN,candidate_SHA256=C.CANDIDATE,
        controller_SHA256=C.H(controller(raw).encode()),body_SHA256=BODY_SHA,frozen_body_byte_identical=True,
        identity='burns',compiled_name='BURNS',slot=30,Select_cycles=0,
        ordinary_controls='idle48/Right16 completed Main; no A/B, zero native actors/12 shots required',
        complete_cookie=q['cf']['cookie'],actual_payload_SHA256=q['cf']['carrier_SHA256'],
        private_unchanged_hook_PC_and_readbacks=q['cf']['hooks'],actual_PRG_hooks=q['hooks'],
        NmiSkipped_RAM=q['ram']['NmiSkipped'],
        leased5_ROM_readback_spans=[dict(file=f['file'],bytes=f['bytes'],SHA256=f['new_SHA256']if C.H(raw)==C.CANDIDATE else f['old_SHA256'])for f in d['fragments']],
        callback_body_does_not_add_new_private_code_callbacks=True,
        source_cold_full_RAM1_RAM3_readback_qualified_separately=True,
        physical_controller_read_histogram_and_dynamic_return_PC_SP_mapping_ack_body_unchanged=True,
        no_native_Mesen_or_ROM_file_or_delivery_authorized=True,outputs=0)
