"""Strict72-byte selected-Star rebase over exact Prince7fb3, memory only."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import compose_prince_hidden_point67_ace_1115 as Prince
import compose_bub_selected_star_palette_ace_1115 as Bub

R,ROM,B,W,N=Bub.R,Bub.ROM,Bub.B,Bub.W,Bub.N
PIN='7fb328a6dcf6b50fd000e81eced4fd4b7390bedec56085d33130434003cc76d0'
CANDIDATE='67e3b8e7d4b01ea549fe9dc15c09b5a0b5f7085ee396d672a9c963d24287d0b5'
GRANT=R/'docs/qa/allocations/bub-selected-star-palette-prince-source-1115.json'
GRANT_SHA='a5580011bc6489fa8c9200dd1ca9fee45c1fccc8e75bafd33ef2eaa2b43885ee'
PINS=((Prince,'1fce2b546003860e31da49723c3ac185a25b5420e2ba88143434516c59a4ee27'),
    (Bub,'1b965068ca15fa588c6d77b18b7d7a49fd1c31313a10d274c2ac6db7c8a79943'))
FILE,COOKIE,OLD,NEW,OLD_COOKIE=Bub.FILE,Bub.COOKIE,Bub.OLD,Bub.NEW,Bub.OLD_COOKIE
code,cookie,H=Bub.code,Bub.cookie,Bub.H


@lru_cache(maxsize=1)
def lease():
    assert H(GRANT.read_bytes())==GRANT_SHA
    for module,pin in PINS:assert H(Path(module.__file__).read_bytes())==pin
    q=json.loads(GRANT.read_text())
    assert q['owning_parent_SHA256']==PIN and q['owned_bytes']==72
    assert q['envelopes']==[[FILE,56],[COOKIE,16]]
    assert q['source_in_memory_composition_and_mounts_authorized']
    assert not any(q[k]for k in('physical_ROM_file_writes_authorized','native_Mesen_authorized','Downloads_delivery_authorized'))
    assert q['prior_mapper_grant_SHA256']==Bub.GRANT_SHA
    Bub.lease();return q


@lru_cache(maxsize=1)
def reference(parent):
    lease();assert isinstance(parent,bytes)and H(parent)==PIN,'Exact owning Prince7fb3 only'
    ace=Prince.inverse(parent);assert H(ace)==Bub.PIN
    e9,_=Bub.proposal(ace);assert Bub.inverse(e9)==ace
    return e9


@lru_cache(maxsize=1)
def proposal(parent):
    e9=reference(parent);ace=Prince.inverse(parent)
    assert parent[FILE:FILE+56]==OLD and parent[COOKIE:COOKIE+16]==OLD_COOKIE
    assert e9[FILE:FILE+56]==NEW and e9[COOKIE:COOKIE+16]==Bub.cookie(e9)
    out=bytearray(parent);out[FILE:FILE+56]=NEW;out[COOKIE:COOKIE+16]=e9[COOKIE:COOKIE+16];out=bytes(out)
    owned=set(range(FILE,FILE+56))|set(range(COOKIE,COOKIE+16))
    prince_changes={i for i,(a,b)in enumerate(zip(ace,parent,strict=True))if a!=b}
    changes={i for i,(a,b)in enumerate(zip(parent,out,strict=True))if a!=b}
    assert len(prince_changes)==9907 and not owned.intersection(prince_changes)
    assert changes<=owned and len(changes)==57
    # Commutative physical join: the only differences from e9 are exactly
    # the already qualified Prince changes, not a normalized CPU candidate.
    assert {i for i,(a,b)in enumerate(zip(e9,out,strict=True))if a!=b}==prince_changes
    assert code(out)==code(e9)
    ch=Bub.Palette.A.CH
    assert out[ch+441*1024:ch+442*1024]==e9[ch+441*1024:ch+442*1024]
    native_differences={i for i in prince_changes if 16<=i<ch}
    assert native_differences<=set(range(Prince.Packet.COOKIE,Prince.Packet.COOKIE+16))
    for at,h in Bub.Carry.PREIMAGES:
        size=len(bytes.fromhex(h));assert out[at:at+size]==ace[at:at+size]
    for at,before,after in Bub.Palette.EDITS:
        for index,value in enumerate(bytes.fromhex(after)):
            if at+index not in owned:assert out[at+index]==value
    if CANDIDATE is not None:assert H(out)==CANDIDATE
    return out,dict(parent_SHA256=PIN,candidate_SHA256=H(out),grant_SHA256=GRANT_SHA,
        owned_bytes=72,changed_bytes=57,cookie=out[COOKIE:COOKIE+16].hex(),
        all_unowned7fb3_bytes_exact=True,all9907_Prince_and714_carry_changes_preserved=True,
        transferred_e9_complete_Bub_code_SHA256=H(code(out)),
        transferred_art_helper441_SHA256=H(out[ch+441*1024:ch+442*1024]),
        native_PRG_code_exact_e9_except_other_owner_Prince_cookie=True,
        Prince_only_PRG_changed_file_offsets=sorted(native_differences),
        prior_e9_finite_Pair_ISR_lifecycle_receipts_transferred_not_rerun=True,
        source_only=True,output_files=0)


@lru_cache(maxsize=1)
def inverse(raw):
    lease();assert CANDIDATE is not None and isinstance(raw,bytes)and H(raw)==CANDIDATE
    assert raw[FILE:FILE+56]==NEW and raw[COOKIE:COOKIE+16]==cookie(raw)
    parent=bytearray(raw);parent[FILE:FILE+56]=OLD;parent[COOKIE:COOKIE+16]=OLD_COOKIE
    parent=bytes(parent);assert H(parent)==PIN and proposal(parent)[0]==raw
    return parent


def load_current():
    raw=ROM.read_bytes();assert H(raw)==PIN,'Expected exact installed Prince7fb3'
    return raw


if __name__=='__main__':
    parent=load_current();raw,q=proposal(parent)
    if CANDIDATE is not None:assert inverse(raw)==parent
    print('RESULT '+json.dumps(q,sort_keys=True,separators=(',',':')),flush=True)
