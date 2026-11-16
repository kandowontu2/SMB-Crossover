"""Strict leased14B cb95->79fd HUD lifecycle repair; RAM-only composition."""
from pathlib import Path
from functools import lru_cache
import json
import plan_rogue_hud_scene_dirty_cb95_1116 as Plan

R,ROM,H=Plan.R,Plan.ROM,Plan.H
PARENT=Plan.PARENT
CANDIDATE='79fd089f80b06038e68b968d2ff80d09caba72a133735b3fef6bb86ffa3ed2df'
GRANT=R/'docs/qa/allocations/rogue-hud-scene-dirty-source-root-1116.json'
GRANT_SHA='43bfb253dca087acf657c990a88297faa354baf697cf6b163de65f880f50eabb'
PLAN_SHA='ad1b325160693fa653209b326d598b093a3159a8a41f0c1bc6075e150ca154a2'
PLAN_RECEIPT='e2d1f78e81791817d1835553eac6d35a89b75c099937d78951a44792268debe8'
AT=784287
OLD=bytes.fromhex('203daf900820c3b1a9018d7c5c60')
NEW=bytes.fromhex('900b20c3b1a9018d8e7d8d7c5c60')
SPANS=((AT,OLD,NEW),)


def lease():
    assert H(GRANT.read_bytes())==GRANT_SHA
    assert H(Path(Plan.__file__).read_bytes())==PLAN_SHA
    g=json.loads(GRANT.read_bytes())
    assert(g['parent_SHA256'],g['candidate_SHA256'])==(PARENT,CANDIDATE)
    assert(g['owned_file_offset'],g['owned_length'],g['changed_bytes'])==(AT,14,10)
    assert(g['old_hex'],g['new_hex'])==(OLD.hex(),NEW.hex())
    assert g['source_candidate_only_authorized']
    assert not g['native_ROM_files_or_Mesen_authorized']and not g['Downloads_or_release_authorized']
    return g


def inverse(raw):
    lease();assert isinstance(raw,bytes)and H(raw)==CANDIDATE
    assert raw[AT:AT+14]==NEW
    parent=raw[:AT]+OLD+raw[AT+14:]
    assert H(parent)==PARENT;return parent


@lru_cache(maxsize=1)
def proposal(parent):
    lease();assert isinstance(parent,bytes)and H(parent)==PARENT
    d=Plan.descriptor(parent);assert d['receipt_SHA256']==PLAN_RECEIPT
    assert parent[AT:AT+14]==OLD
    raw=parent[:AT]+NEW+parent[AT+14:]
    assert H(raw)==CANDIDATE and inverse(raw)==parent
    changed=[i for i,(a,z)in enumerate(zip(parent,raw,strict=True))if a!=z]
    assert len(changed)==10 and set(changed)<=set(range(AT,AT+14))
    assert raw[:AT]==parent[:AT]and raw[AT+14:]==parent[AT+14:]
    return raw,dict(passed=True,parent_SHA256=PARENT,candidate_SHA256=CANDIDATE,
        grant_SHA256=GRANT_SHA,owned_bytes=14,changed_bytes=10,code_growth=0,new_RAM=0,
        all_unowned_bytes_exact=True,strict_portable_inverse=True,
        protected_Mini20_Sonic94_Rogue2=True,no_cookie_header_art_helper_changes=True,
        candidate_CPU_executed=False,outputs=0,native=False)
