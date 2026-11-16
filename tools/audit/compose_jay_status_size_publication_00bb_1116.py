"""Strict leased116-byte Jay status+size composer/inverse; memory only."""
from functools import lru_cache
from pathlib import Path
import json
import plan_jay_status_size_publication_00bb_1116 as Plan

R,H,PIN=Plan.R,Plan.H,Plan.PIN
CANDIDATE='13272464e34237f09c7fce87ac276b20da299f8028640cc51155759d6c642a4d'
GRANT=R/'docs/qa/allocations/jay-status-size-source-root-1116.json'
GRANT_SHA='a5039ccaed13fcf21b01914f8d9d120be10251516b6b35ccbbd10cc55a8d05f7'
PLAN_SHA='6ece60af99ca5d56cd31768c895067a88719fef2ad5d098c35154a86d0aa407d'
PLAN_RECEIPT='428e0f3b12cbde2eff093a7c3dd04be37c381bedb269374ebf9f87a6c5e24a1f'
REVIEW_SHA='50f8f78557d9b3f40cb584973d1c087eaab71ce4ed14beb4bdb142aa061c99f6'
OLD_COOKIE=bytes.fromhex('aa10200c3c8114b6f52cd1db4b8564a0')
COOKIE=bytes.fromhex('aa10200ea90dc687ba45c39a3923ed6f')
OLD_MAIN=bytes.fromhex('ad7107c901d029ad7307c903d022a50fc908d01cad77074ab016ad39011011adff5f4a900b20e6a7eaeaeaeaeaea90021860')
NEW_MAIN=bytes.fromhex('ad7107c901d023ad7307c903d01ca50fc908d016ad77074ab010ad3901100badff5f4a900520e6a79002186020f6b74c32b8')
TAIL=bytes.fromhex('ad3e5f0aa9004cd7beea')
LEAF=bytes.fromhex('8d59072a8d5b0760')


@lru_cache(maxsize=1)
def lease():
    assert H(GRANT.read_bytes())==GRANT_SHA and H(Path(Plan.__file__).read_bytes())==PLAN_SHA
    assert H((R/'tools/audit/audit_jay_size_tail_consumers_00bb_1116.py').read_bytes())==REVIEW_SHA
    g=json.loads(GRANT.read_text())
    assert(g['parent_SHA256'],g['candidate_SHA256'],g['plan_receipt_SHA256'])==(PIN,CANDIDATE,PLAN_RECEIPT)
    assert g['source_in_memory_composition_and_execution_authorized']and not g['physical_candidate_native_Downloads_release_authorized']
    return g


def spans():
    lease()
    return((1286160,OLD_MAIN,NEW_MAIN),(1276934,b'\xea'*10,TAIL),(1288935,b'\xea'*8,LEAF))+tuple(
        (at,OLD_COOKIE,COOKIE)for at in(534328,774911,1429421))


@lru_cache(maxsize=1)
def proposal(parent):
    assert isinstance(parent,bytes)and H(parent)==PIN,'Exact public00bb only'
    lease();fit=Plan.descriptor(parent)
    assert fit['receipt_SHA256']==PLAN_RECEIPT and fit['predicted_candidate_SHA256']==CANDIDATE and fit['proposed_cookie']==COOKIE.hex()
    assert[(r['file'],bytes.fromhex(r['old_hex']),bytes.fromhex(r['new_hex']))for r in fit['physical_spans']]==list(spans())
    out=bytearray(parent);owned=set()
    for at,old,new in spans():
        assert len(old)==len(new)and parent[at:at+len(old)]==old
        domain=set(range(at,at+len(old)));assert not domain&owned;owned|=domain
        out[at:at+len(new)]=new
    raw=bytes(out);changed={i for i,(a,b)in enumerate(zip(parent,raw,strict=True))if a!=b}
    assert len(owned)==116 and len(changed)==72 and changed<=owned and H(raw)==CANDIDATE
    assert all(a==b for i,(a,b)in enumerate(zip(parent,raw,strict=True))if i not in owned)
    assert fit['primary331_332_and_all34Metal_bytes_preserved']
    return raw,dict(parent_SHA256=PIN,candidate_SHA256=CANDIDATE,owned_bytes=116,changed_bytes=72,
        main50=H(NEW_MAIN),tail10=H(TAIL),leaf8=H(LEAF),cookie=COOKIE.hex(),cookie_views=3,
        all_unowned_00bb_and34Metal_bytes_exact=True,all54_transfer_and_packed_primary_bytes_exact=True,
        grant_SHA256=GRANT_SHA,plan_SHA256=PLAN_SHA,independent_review_SHA256=REVIEW_SHA,
        no_added_RAM_carriers_platform_actors=True,proposed_CPU_executed=False,ROM_written=False,outputs=0)


def inverse(raw):
    assert isinstance(raw,bytes)and H(raw)==CANDIDATE,'Exact leased1327 only'
    out=bytearray(raw)
    for at,old,new in spans():
        assert raw[at:at+len(new)]==new;out[at:at+len(old)]=old
    parent=bytes(out);assert H(parent)==PIN;return parent


if __name__=='__main__':
    parent=Plan.ROM.read_bytes();raw,q=proposal(parent)
    assert inverse(raw)==parent and proposal(inverse(raw))[0]==raw
    wrong=0
    for image,fn in((parent,inverse),(raw,proposal),(raw[:-1],inverse),(parent[:-1],proposal)):
        try:fn(image)
        except AssertionError:wrong+=1
        else:raise AssertionError('Wrong role accepted')
    q.update(strict_roundtrip=True,wrong_role_rejections=wrong,composer_SHA256=H(Path(__file__).read_bytes()))
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
