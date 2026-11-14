"""Strict in-memory DK769 merge over delivered12397; old APIs stay frozen."""
from hashlib import sha256
from functools import lru_cache
import json
from pathlib import Path

import compose_dkjr_direct_current_1113 as Old
import compose_smb2_postbg_mirror_1113 as Mirror
import replay_dkjr_odd_stair_turn_1113 as Turn
from check_ff_stdout_controller_source_1110 import LuaRuntime

PARENT=Mirror.CANDIDATE
PIN='16c71bc6fb6427ddb0c43dc41d687e768bb4f86015a23204398023fbf3856bd1'
DK=Old.DK


def mirror_envelopes():
    return [(16+bank*8192+(Mirror.BRIDGE&8191),len(Mirror.CANONICAL))
            for bank in(119,120,125,127)]


def repair_mirrors(raw):
    """Only the already source/grant-qualified six operands, on exact8623."""
    assert sha256(raw).hexdigest()==Old.PIN
    out=bytearray(raw)
    for at,before,after in Mirror.EDITS:
        assert raw[at]==before
        out[at]=after
    for at,size in mirror_envelopes():assert out[at:at+size]==Mirror.CANONICAL
    return bytes(out)


def proposal(raw):
    image,info=_proposal(raw)
    return image,dict(info)


@lru_cache(maxsize=1)
def _proposal(raw):
    assert sha256(raw).hexdigest()==PARENT
    assert PARENT=='12397b1c2557834f6a2b7e23c9915d5dc40c6cabff7a6ee844c1adebf6564c52'
    prior=Mirror.inverse(raw)
    assert sha256(prior).hexdigest()==Old.PARENT==Mirror.PIN
    mirror_info=Mirror.bindings(prior)
    historical,old_info=Old.proposal(prior)
    image=repair_mirrors(historical)
    digest=sha256(image).hexdigest()
    if PIN is not None:assert digest==PIN
    own={i for at,size in Old.dk_envelopes()for i in range(at,at+size)}
    others=Old.spans(prior)
    foreign={i for at,before,after in others for i in range(at,at+len(before))}
    mirrors={i for at,size in mirror_envelopes()for i in range(at,at+size)}
    assert not own&(foreign|mirrors),'Complete DK/current-owner envelopes overlap'
    changes={i for i,(a,b)in enumerate(zip(prior,historical,strict=True))if a!=b}
    actual={i for i,(a,b)in enumerate(zip(raw,image,strict=True))if a!=b}
    assert changes==actual and actual<=own
    assert all(image[i]==raw[i]for i in range(len(raw))if i not in actual)
    assert all(image[i]==raw[i]for i in foreign|mirrors)
    assert len(actual)==old_info['DK_changed_bytes']==846
    # Independent order: apply only the original DK source changes directly
    # to delivered12397, rather than producing8623 then repairing its aliases.
    independent=bytearray(raw)
    for i in changes:
        assert raw[i]==prior[i]
        independent[i]=historical[i]
    assert bytes(independent)==image
    sample_bytes=0
    for row in mirror_info['samples']:
        at,size=row['file'],row['bytes'];sample_bytes+=size
        assert image[at:at+size]==raw[at:at+size]
        assert sha256(image[at:at+size]).hexdigest()==row['SHA256']
    return image,dict(parent_SHA256=PARENT,candidate_SHA256=digest,
        canonical_DK_SHA256=DK.PIN,historical_merge_SHA256=Old.PIN,
        DK_changed_bytes=len(actual),complete_DK_envelope_bytes=len(own),
        complete_Bub_foreground_envelope_bytes=len(foreign),
        complete_postBG_envelope_bytes=len(mirrors),postBG_operand_bytes_preserved=6,
        complete_foreign_union_bytes=len(foreign|mirrors),
        complete_envelopes_disjoint=True,source_construction_orders_equal=True,
        eight_DMC_request_windows_unchanged=True,DMC_window_byte_sum=sample_bytes,
        all_unowned_bytes_exact=True,new_RAM_bytes=0,new_CHR_bytes=0,
        new_native_capacity_bytes=0,merged_native_qualified=False,outputs_written=0)


def previous_merge(raw):
    assert PIN is not None and sha256(raw).hexdigest()==PIN
    for at,size in mirror_envelopes():assert raw[at:at+size]==Mirror.CANONICAL
    out=bytearray(raw)
    for at,before,after in Mirror.EDITS:
        assert raw[at]==after
        out[at]=before
    old=bytes(out)
    assert sha256(old).hexdigest()==Old.PIN and repair_mirrors(old)==raw
    return old


@lru_cache(maxsize=1)
def private_image(raw):
    private=Old.private_image(previous_merge(raw))
    assert sha256(private).hexdigest()==DK.PIN
    return private


@lru_cache(maxsize=1)
def inverse(raw):
    historical=previous_merge(raw)
    prior=Old.inverse(historical)
    parent,_=Mirror.proposal(prior)
    assert sha256(parent).hexdigest()==PARENT and proposal(parent)[0]==raw
    return parent


def controller(raw,*,full=False):
    private=private_image(raw)
    text=Turn.donor_ground_controller(private)if full else DK.controller(private)
    expected=Turn.DONOR_GROUND_LUA_PIN if full else'5ef1c7955010c1abebcbefdcdbe6594b76024f123a89117436b5782cde7f1d53'
    assert sha256(text.encode()).hexdigest()==expected and text.count(DK.PIN)==1
    text=text.replace(DK.PIN,PIN,1)
    LuaRuntime().compile(text)
    return text


if __name__=='__main__':
    current=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    image,info=proposal(current)
    if PIN is not None:
        assert inverse(image)==current
        info['inverse_and_forward_roundtrip']=True
        info['controller_Lua_SHA256']={name:sha256(controller(image,full=full).encode()).hexdigest()
            for name,full in(('first',False),('full',True))}
    print('DKJR_DIRECT_POSTBG_CURRENT '+json.dumps(info,separators=(',',':')),flush=True)
