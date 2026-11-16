"""Strict leased106-byte Jay publication composer/portable inverse; RAM only."""
from functools import lru_cache
from pathlib import Path
import json
import plan_jay_status_publication_00bb_1116 as Plan

R,H,PIN=Plan.R,Plan.H,Plan.PIN
CANDIDATE='df0e009bad3240122629da681dfd20e559b1fdba2b235b6a00c3ffeefda88afe'
GRANT=R/'docs/qa/allocations/jay-status-source-root-1116.json'
GRANT_SHA='812f8e8f040cf6cd79d65e7861c331003d7925340b2187f37641206d0305b460'
PLAN_SHA='0ae3ac71e6fa8f7e0f40fe0da13ce33af9ad79dec18367f01b0ae9698bbb0295'
PLAN_RECEIPT='7700b0a40d77f97a4264d6e8aceed97460d795e7bd1887d3a1b4ed9cfb7b8e0c'
OLD_COOKIE=Plan.COOKIE
COOKIE=bytes.fromhex('aa10200deffb68f830e7c4bb7fe4b68a')
OLD_MAIN=bytes.fromhex('ad7107c901d029ad7307c903d022a50fc908d01cad77074ab016ad39011011adff5f4a900b20e6a7eaeaeaeaeaea90021860')
NEW_MAIN=bytes.fromhex('ad7107c901d023ad7307c903d01ca50fc908d016ad77074ab010ad3901100badff5f4a900520e6a790021860ad3e5f20d7be')
LEAF=bytes.fromhex('0aa9002a8d5b0760')


@lru_cache(maxsize=1)
def lease():
    assert H(GRANT.read_bytes())==GRANT_SHA and H(Path(Plan.__file__).read_bytes())==PLAN_SHA
    g=json.loads(GRANT.read_text())
    assert(g['parent_SHA256'],g['candidate_SHA256'],g['plan_receipt_SHA256'])==(PIN,CANDIDATE,PLAN_RECEIPT)
    assert g['source_in_memory_composition_and_execution_authorized']and not g['physical_candidate_native_Downloads_or_release_authorized']
    return g


def spans():
    lease()
    rows=((1286160,OLD_MAIN,NEW_MAIN),(1288935,b'\xea'*8,LEAF))
    return rows+tuple((at,OLD_COOKIE,COOKIE)for at in(534328,774911,1429421))


@lru_cache(maxsize=1)
def proposal(parent):
    assert isinstance(parent,bytes)and H(parent)==PIN,'Exact owning00bb parent required'
    lease();fit=Plan.descriptor(parent)
    assert fit['receipt_SHA256']==PLAN_RECEIPT and fit['streamed_conditional_digest']==CANDIDATE
    assert fit['proposed_cookie']==COOKIE.hex()
    assert [(r['file'],bytes.fromhex(r['old_hex']),bytes.fromhex(r['new_hex']))for r in fit['exact_spans']]==list(spans())
    out=bytearray(parent);owned=set()
    for at,old,new in spans():
        assert len(old)==len(new)and parent[at:at+len(old)]==old
        domain=set(range(at,at+len(old)));assert not owned&domain;owned|=domain
        out[at:at+len(new)]=new
    raw=bytes(out);changed={i for i,(a,b)in enumerate(zip(parent,raw,strict=True))if a!=b}
    assert len(owned)==106 and len(changed)==63 and changed<=owned and H(raw)==CANDIDATE
    assert all(a==b for i,(a,b)in enumerate(zip(parent,raw,strict=True))if i not in owned)
    assert fit['all34_Metal_owned_bytes_preserved']
    return raw,dict(parent_SHA256=PIN,candidate_SHA256=CANDIDATE,owned_bytes=106,changed_bytes=63,
        main_bytes=50,retired_producer_pad_bytes=8,cookie_views=3,cookie=COOKIE.hex(),
        all_unowned_00bb_bytes_exact=True,all34_Metal_bytes_preserved=True,new_RAM_carriers_helpers=0,
        grant_SHA256=GRANT_SHA,plan_SHA256=PLAN_SHA,plan_receipt=PLAN_RECEIPT,
        proposed_CPU_executed=False,ROM_written=False,outputs=0)


def inverse(raw):
    assert isinstance(raw,bytes)and H(raw)==CANDIDATE,'Exact leaseddf0e candidate required'
    out=bytearray(raw)
    for at,old,new in spans():
        assert raw[at:at+len(new)]==new
        out[at:at+len(old)]=old
    parent=bytes(out);assert H(parent)==PIN
    return parent


if __name__=='__main__':
    parent=Plan.ROM.read_bytes();raw,report=proposal(parent)
    assert inverse(raw)==parent and proposal(inverse(raw))[0]==raw
    rejected=0
    for image,fn in((parent,inverse),(raw,proposal),(raw[:-1],inverse),(parent[:-1],proposal)):
        try:fn(image)
        except AssertionError:rejected+=1
        else:raise AssertionError('Wrong role accepted')
    report.update(strict_roundtrip=True,wrong_role_or_truncated_rejections=rejected,composer_SHA256=H(Path(__file__).read_bytes()))
    report['receipt_SHA256']=H(json.dumps(report,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(report,separators=(',',':')),flush=True)
