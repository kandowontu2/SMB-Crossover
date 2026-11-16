"""Strict leased current91dc direct-C2 resolver; memory-only composition."""
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import json
import plan_contra_force_checked_c2_direct_v2_1116 as Plan

Base=Plan.Base
R,ROM,H=Base.R,Base.ROM,Base.H
PIN=Base.PIN
CANDIDATE='b8bd4affddb231dbc7d3b67fe5bcad51be110b120665773db80c4dab5f2d73fd'
GRANT=R/'docs/qa/allocations/cf-checked-c2-direct-source-root-1116.json'
GRANT_SHA='d1c045f81786d52f75ccc1f3d58bebb6150412b0c52e8926300207cb2d112767'
PLAN_SHA='0c2c3f37b326c6899ce261e4afca6fccab752eee8632422d74fa94080dfc5bce'
CAPACITY_SHA='e8c634a20c6a1cb9d3f1659daec9e0777f5a76ce249b932a0cc1ab0cbee381db'
ADDITIONAL_PREIMAGES=(
    (573351,'2047bf90088d6c01ce6d01a90260'),
    (2022305,'ff'*58),
    (573373,'a71f00053a7d2d9a77d5accd30e79766'),
    (642966,'a71f00053a7d2d9a77d5accd30e79766'),
)


@lru_cache(maxsize=1)
def lease():
    assert H(GRANT.read_bytes())==GRANT_SHA
    assert H(Path(Plan.__file__).read_bytes())==PLAN_SHA
    assert H((R/'tools/audit/audit_contra_force_c2_tail_capacity_1116.py').read_bytes())==CAPACITY_SHA
    q=json.loads(GRANT.read_text())
    assert q['owning_parent_SHA256']==PIN and q['reference44b_composer_SHA256']==Plan.Rejected.BASE_SHA
    assert q['source_in_memory_composition_and_mounts_authorized']
    assert not any(q[k]for k in('physical_ROM_file_writes_authorized','native_Mesen_authorized','Downloads_delivery_authorized'))
    assert(q['owning_union_bytes'],q['changed_bytes'])==(661,284)
    assert [(at,at+len(bytes.fromhex(h)))for at,h in ADDITIONAL_PREIMAGES]==[tuple(r['file_half_open'])for r in q['additional_fragments_relative_to_exact44b']]
    return q


@lru_cache(maxsize=2)
def proposal(parent):
    grant=lease();assert isinstance(parent,bytes)and H(parent)==PIN,'Exact owning current91dc required'
    old44b,_=Base.proposal(parent);d=Plan.descriptor(parent)
    assert d['receipt_SHA256']==grant['helper_plan_receipt_SHA256']
    out=bytearray(old44b);owned=set()
    for at,h in Base.PREIMAGES:owned.update(range(at,at+len(bytes.fromhex(h))))
    for row,g,(at,h)in zip(d['additional_detached_fragments'],grant['additional_fragments_relative_to_exact44b'],ADDITIONAL_PREIMAGES,strict=True):
        old,new=bytes.fromhex(h),bytes.fromhex(row['new_hex'])
        assert row['file_half_open']==g['file_half_open']==[at,at+len(old)]
        assert old44b[at:at+len(old)]==old and len(old)==len(new)==g['bytes']
        assert H(old)==g['old_SHA256']and H(new)==g['new_SHA256']
        out[at:at+len(new)]=new;owned.update(range(at,at+len(new)))
    out=bytes(out);changed={i for i,(a,b)in enumerate(zip(parent,out,strict=True))if a!=b}
    assert len(owned)==661 and len(changed)==284 and changed<=owned
    assert out[2006032:2006032+24576]!=parent[2006032:2006032+24576]
    assert H(out[2006032:2030608])==grant['new_CF_payload_SHA256']
    assert out[573373:573389]==out[642966:642982]==bytes.fromhex(grant['new_expected_cookie_hex'])
    assert out[2021904:2022305]==parent[2021904:2022305],'Old401 A2 API/full inner check'
    assert out[573389:573425]==parent[573389:573425],'Old full CfRetire36'
    assert out[792556:792664]==parent[792556:792664],'Wf108 target bytes'
    for at,n in((Base.BT.CACHE,8192),(Base.BT.HEADER,487),(Base.BT.COOKIE,16)):
        assert out[at:at+n]==parent[at:at+n],'Current BT unowned protection'
    if CANDIDATE is not None:assert H(out)==CANDIDATE
    return out,dict(owning_parent_SHA256=PIN,candidate_SHA256=H(out),reference44b_only_SHA256=Base.CANDIDATE,
        lease_SHA256=GRANT_SHA,source_plan_SHA256=PLAN_SHA,owned_bytes=661,changed_bytes=284,
        every_unowned_current91dc_byte_exact=True,old401_A2_fullcheck_Retire36_Wf108_BT_payload_native_cookie_exact=True,
        new_full_CF_payload_SHA256=grant['new_CF_payload_SHA256'],expected_cookie_hex=grant['new_expected_cookie_hex'],
        new_CPU_semantics_liveness_and_interrupt_gates_pending=True,no_native_or_delivery_authorized=True,outputs=0)


def inverse(raw):
    lease();assert CANDIDATE is not None and isinstance(raw,bytes)and H(raw)==CANDIDATE,'Exact direct-C2 candidate required'
    old44b=bytearray(raw)
    for at,h in ADDITIONAL_PREIMAGES:old44b[at:at+len(bytes.fromhex(h))]=bytes.fromhex(h)
    old44b=bytes(old44b);assert H(old44b)==Base.CANDIDATE
    parent=Base.inverse(old44b);assert H(parent)==PIN and proposal(parent)[0]==raw
    return parent


def reference(parent):
    assert isinstance(parent,bytes)and H(parent)==PIN
    return Base.reference(parent)


def load_current_image():
    raw=ROM.read_bytes()
    if H(raw)==PIN:reference(raw)
    else:inverse(raw)
    return raw


if __name__=='__main__':
    parent=load_current_image();assert H(parent)==PIN
    reader=Path.read_bytes
    def read(path):
        assert path.resolve()!=ROM.resolve(),'Portable composition reread mutable Nightly'
        return reader(path)
    def deny(*a,**kw):raise AssertionError('Direct-C2 source composer attempted files/native')
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        raw,q=proposal(parent)
        if CANDIDATE is not None:assert inverse(raw)==parent
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
