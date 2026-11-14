"""Strict reversible private cheat-owner routing proposal; in-memory only.

This deliberately preserves the unresolved119/120 E037 operands. It must
not be installed as a movement-only nightly or treated as full qualification.
"""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import check_smb2_invincible_dispatch_1113 as D
from compose_metal_head_bridge_1112 import assemble_segments

W,N=D.W,D.N
R=Path(__file__).resolve().parents[2]
PIN=D.PIN
CANDIDATE='e8cd1e48bdc48412c30e31b2d0f5decf3a86c49aed85890e8452989e34cc1e17'
GRANT=R/'docs/qa/allocations/smb2-cheat-owner-1113.json'
GRANT_SHA='b13857fde91a588fc992acaf86da2a9c2da9ec171e0a055091fc896663d01d33'
DIAGNOSTIC_SHA='2da1991969af7bfa698815f4532d22df6904fc1665fb3a50f30860a719d9f03a'
SOURCE=R/'tools/reference/smb2_cheat_owner_1113.s'
SOURCE_SHA='fdc5aad5a90308a7ad752e165b7c30d7bf2f9b358b68aa949e42175ff2b72084'
SPANS=((516793,D.RESTORE,D.DRAFT_RESTORE),(518912,b'\xff'*15,D.DRAFT_TAIL))


@lru_cache(maxsize=1)
def recipe():
    assert sha256(Path(D.__file__).read_bytes()).hexdigest()==DIAGNOSTIC_SHA
    assert sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
    symbols=dict(GuestHurtKind=0x6f1c,SelectedCharacter=0x6002,SafeA=0x16a,
                 TargetLo=0x16c,TargetHi=0x16d,FarCallCommon=0x15a,ExistingSMB2Tail=0xad40)
    code,labels=assemble_segments(SOURCE.read_text(),
            dict(OWNER_RESTORE=0xa2a9,OWNER_FOREIGN=0xaaf0),symbols)
    assert code==dict(OWNER_RESTORE=D.DRAFT_RESTORE,OWNER_FOREIGN=D.DRAFT_TAIL)
    assert labels['OwnerRestore']==0xa2a9 and labels['OwnerNative']==0xa2ce
    assert labels['OwnerSMB2']==0xa2dd and labels['OwnerForeignTail']==0xaaf0
    return code,labels


def bindings(raw):
    assert sha256(raw).hexdigest()==PIN
    assert sha256(Path(D.__file__).read_bytes()).hexdigest()==DIAGNOSTIC_SHA
    assert sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
    manifest=GRANT.read_bytes();assert sha256(manifest).hexdigest()==GRANT_SHA
    g=json.loads(manifest)
    assert g['parent_ROM_SHA256']==PIN and g['checker_SHA256']==DIAGNOSTIC_SHA
    assert g['required_semantics']['route_only_raw_owner']==25
    for q,(at,old,new)in zip(g['spans'],SPANS,strict=True):
        assert q['physical_bank']==63 and q['file_half_open']==[at,at+len(old)]
        assert q['bytes']==len(old)==len(new) and raw[at:at+len(old)]==old
        if 'preimage_SHA256'in q:assert sha256(old).hexdigest()==q['preimage_SHA256']
        else:assert old.hex()==q['preimage_hex'] and new.hex()==q['allowed_replacement_hex']
    assert raw[518927]==255
    funding=dict(D.funding(raw),formal_grant=True,grant_SHA256=GRANT_SHA)
    code,labels=recipe()
    return dict(grant_SHA256=GRANT_SHA,source_SHA256=SOURCE_SHA,
                source_labels=labels,funding=funding,
                ROM_image_not_native_qualified=True,E037_debt_untouched=True)


def proposal(raw):
    info=bindings(raw);out=bytearray(raw)
    for at,old,new in SPANS:out[at:at+len(old)]=new
    image=bytes(out)
    assert sha256(image).hexdigest()==CANDIDATE and len(image)==len(raw)
    changed={i for i,(a,b)in enumerate(zip(raw,image,strict=True))if a!=b}
    expected={at+i for at,old,new in SPANS for i,(a,b)in enumerate(zip(old,new,strict=True))if a!=b}
    assert changed==expected
    # Complete DMC resident/sample banks, not merely the six prior operands.
    for bank in(119,120,125,127):
        at=16+bank*8192;assert image[at:at+8192]==raw[at:at+8192]
    return image,dict(**info,parent_SHA256=PIN,ROM_SHA256=CANDIDATE,
        owned_spans=[dict(file=at,bytes=len(old),before=old.hex(),after=new.hex())for at,old,new in SPANS],
        changed_bytes=len(changed),all_unowned_bytes_exact=True,all_resident_sample_banks_exact=True,
        new_RAM_CHR_stack_bytes=0,movement_only_private=True,outputs=0)


def inverse(raw):
    assert sha256(raw).hexdigest()==CANDIDATE
    out=bytearray(raw)
    for at,old,new in SPANS:
        assert raw[at:at+len(new)]==new
        out[at:at+len(old)]=old
    parent=bytes(out)
    assert sha256(parent).hexdigest()==PIN and proposal(parent)[0]==raw
    return parent


reverse=inverse


if __name__=='__main__':
    raw=D.C.Owner.NIGHTLY.read_bytes();image,q=proposal(raw)
    assert inverse(image)==raw
    print(json.dumps(q,separators=(',',':')),flush=True)
