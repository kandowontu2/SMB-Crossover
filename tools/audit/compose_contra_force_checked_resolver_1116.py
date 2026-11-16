"""Strict leased current91dc CF checked-resolver join; memory only."""
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import json
import plan_contra_force_checked_resolver_fit_1116 as Plan

C, BT=Plan.C,Plan.Rejected.Source.BT
R,ROM,H=C.R,C.ROM,C.H
PIN=BT.CANDIDATE
REFERENCE=BT.PIN
CANDIDATE='44b6388e3d6f30698dfb74016544a4fbb26b5373fc66aa30afa2f8671e347bf2'
PLAN_SHA='4cf5328ff33d1e68aa28cde924c3ad024447ed76b75fc7d20402008bf90e29a1'
GRANT=R/'docs/qa/allocations/cf-checked-resolver-source-root-1116.json'
GRANT_SHA='5746294b21468d99856a883b9cd5fbe39aba6125d834ff1ebb0a04a12d141d1b'
PREIMAGES=(
    (716848, '4c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb0186008488a489848ad026038e91bc907b0454ab042a8ad6c0138e920aa8a8d6a01c003d0128a29b3c913f02be033f032e04ef032a2ad38a9998d6c01a9b78d6d01a9e0205a01900f8d620168a868aa688d6a01284c5d0168a868aa688d6a01281860a911d002a9918d6c01a9b08d6d01a9c8d0d4'),
    (573271, '0848ad0260c91ff01468288d6a01a9c08d6c01a9ad8d6d01a9dd4c5a018a48ada17d48a9028da17d8d1651a20fe002f008bde0dfddadbfd018ca10f1ade85f4a4a4a2903cde2dfd008babd04010901d006babd040129fe9d0401688da17d8d165168aa682860a71f00053a7d2d9a77d5accd30e797660848ada17d48a9028da17d8d1651ade1dfc91fd005a9008de0df688da17d8d16516828600848ad0260c91ff00568284cbdbf682860ffffffffffffffffffffffffffff'),
    (792486, 'a90060b02888f00fa92b8d6c01a9b28d6d01a9c34c5a01a82039b6900fb9dcb78d6c01b9ddb78d6d01b9deb760a9c08d6c018e6d01a9dd205a0190cc8d6c01a9a08d6d019860e6b2e0f1b3e047b5e0cdb2e0cdb2e013a1bbdba686cdb2e03aaf88cbb2e08795fecdb2e0cdb2e0cdb2e08b95fee8b6e0c3b6c246b6e0a0bbccefa6e0cdb2e0cdb2e0cdb2e0dba7fc71af83cdb2e081b6e0cdb2e0f0e1ffcdb2e033b7e0cdb2e0e7bacf99b28acdb2e0cdb2e0'),
)


@lru_cache(maxsize=1)
def lease():
    assert H(GRANT.read_bytes())==GRANT_SHA
    assert H(Path(Plan.__file__).read_bytes())==PLAN_SHA
    q=json.loads(GRANT.read_text())
    assert q['owning_parent_SHA256']==PIN and q['plan_reference_only_SHA256']==REFERENCE
    assert q['owned_bytes']==587 and q['changed_bytes']==203 and q['source_in_memory_composition_and_mounts_authorized']
    assert not any(q[k]for k in('physical_ROM_file_writes_authorized','native_Mesen_authorized','Downloads_delivery_authorized'))
    assert [(at,at+len(bytes.fromhex(h)))for at,h in PREIMAGES]==[tuple(r['file_half_open'])for r in q['spans']]
    return q


@lru_cache(maxsize=2)
def reference(parent):
    lease();assert isinstance(parent,bytes)and H(parent)==PIN,'Exact owning current91dc required'
    old=BT.inverse(parent);assert H(old)==REFERENCE and BT.proposal(old)[0]==parent
    for at,h in PREIMAGES:
        before=bytes.fromhex(h);assert parent[at:at+len(before)]==old[at:at+len(before)]==before
    return old


@lru_cache(maxsize=2)
def proposal(parent):
    q=lease();oldref=reference(parent);d=Plan.descriptor(oldref);out=bytearray(parent);owned=set()
    for r,g,(at,h)in zip(d['detached_fragments'],q['spans'],PREIMAGES,strict=True):
        old,new=bytes.fromhex(h),bytes.fromhex(r['new_hex'])
        assert r['file_half_open']==g['file_half_open']==[at,at+len(old)]
        assert len(new)==len(old)==g['bytes']and H(old)==g['old_SHA256']and H(new)==g['new_SHA256']
        assert not owned.intersection(range(at,at+len(old)));owned.update(range(at,at+len(old)))
        assert parent[at:at+len(old)]==old;out[at:at+len(new)]=new
    out=bytes(out);changed={i for i,(a,b)in enumerate(zip(parent,out,strict=True))if a!=b}
    assert len(owned)==587 and len(changed)==203 and changed<=owned
    assert out[2006032:2030608]==parent[2006032:2030608]
    assert out[573373:573389]==parent[573373:573389]
    assert out[573389:573425]==parent[573389:573425]
    assert out[792556:792664]==parent[792556:792664]
    assert out[BT.CACHE:BT.CACHE+8192]==parent[BT.CACHE:BT.CACHE+8192]
    assert out[BT.HEADER:BT.HEADER+487]==parent[BT.HEADER:BT.HEADER+487]
    assert out[BT.COOKIE:BT.COOKIE+16]==parent[BT.COOKIE:BT.COOKIE+16]
    if CANDIDATE is not None:assert H(out)==CANDIDATE
    return out,dict(owning_parent_SHA256=PIN,candidate_SHA256=H(out),metadata_reference_only_SHA256=REFERENCE,
        lease_SHA256=GRANT_SHA,plan_SHA256=PLAN_SHA,owned_bytes=587,changed_bytes=203,
        all_unowned_current91dc_bytes_exact=True,fullCFpayload_cookie_Retire36_BTpayload_native487_cookie_exact=True,
        Wf108table_exact=True,portable_preimages_bytes=587,outputs=0,
        first_public_CPU_contracts_pending=True,native_or_physical_delivery_authorized=False)


def inverse(raw):
    lease();assert CANDIDATE is not None and isinstance(raw,bytes)and H(raw)==CANDIDATE,'Exact checked-resolver candidate required'
    parent=bytearray(raw)
    for at,h in PREIMAGES:parent[at:at+len(bytes.fromhex(h))]=bytes.fromhex(h)
    parent=bytes(parent);assert H(parent)==PIN and proposal(parent)[0]==raw
    return parent


def load_current_image():
    raw=ROM.read_bytes()
    if H(raw)==PIN:reference(raw)
    else:inverse(raw)
    return raw


if __name__=='__main__':
    parent=load_current_image();assert H(parent)==PIN
    reader=Path.read_bytes
    def read(path):
        assert path.resolve()!=ROM.resolve(),'Composer/inverse reread mutable Nightly'
        return reader(path)
    def deny(*a,**kw):raise AssertionError('Source composer attempted output/native')
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        raw,q=proposal(parent)
        if CANDIDATE is not None:assert inverse(raw)==parent
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
