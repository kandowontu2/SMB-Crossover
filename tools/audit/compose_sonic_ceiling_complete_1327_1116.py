"""Strict leased94-byte complete Sonic ceiling composer/inverse; RAM only."""
from functools import lru_cache
from pathlib import Path
import json
import plan_sonic_ceiling_hold_cancel_1327_1116 as Plan

R,ROM,H,PIN=Plan.R,Plan.ROM,Plan.H,Plan.PIN
CANDIDATE='a2d9d1218504dedf186cfe352ee4c927160529af4f8d09fe6e2aafccfae477c7'
GRANT=R/'docs/qa/allocations/sonic-ceiling-source-root-1116.json'
GRANT_SHA='c4d913a20300f419ae9267b557d49d9dbd26f0019da587490df522454c1bbe79'
PLAN_SHA='dcd6c04b09fc5e5052088d67fd12273788bde250a91a0367d6aed6ce0f381aa3'
PLAN_RECEIPT='94bbe428efd3ee02efd10a688cdcaf30e93392798524a0b0e6dc3f03fc261e89'
OLD=bytes.fromhex('ad04c1c95ff070c960f06cc967f068c968f064')
NEW=bytes.fromhex('4c44d3')+b'\xea'*16
CLASSIFIER=bytes.fromhex('ad04c1c95ff00fc960f00bc967f01bc968f0174c39bbadb7c0c901d00aadb8c0c901d0034c39bb4c5fbb4c9dbb')
TIMER=bytes.fromhex('8d22c1a9008d58c0a90160')
HELPER=CLASSIFIER+TIMER
OLD_HOOK=bytes.fromhex('8d22c1')
HOOK=bytes.fromhex('2071d3')
OLD_COOKIE=bytes.fromhex('a72b0124b3a071484566f32036ec45cb')
COOKIE=bytes.fromhex('a72b017f365cb0a90a5f71d011b56294')


@lru_cache(maxsize=1)
def lease():
    assert H(GRANT.read_bytes())==GRANT_SHA and H(Path(Plan.__file__).read_bytes())==PLAN_SHA
    g=json.loads(GRANT.read_text())
    assert(g['parent_SHA256'],g['candidate_SHA256'],g['descriptor_receipt_SHA256'])==(PIN,CANDIDATE,PLAN_RECEIPT)
    assert g['source_composition_in_memory_and_actual_CPU_authorized']and not g['physical_ROM_files_Mesen_Downloads_delivery_authorized']
    assert [(r['file'],r['bytes'])for r in g['owned_spans']]==[(1384246,19),(1384607,3),(1385300,56),(1034472,16)]
    return g


def spans():
    lease();return((1384246,OLD,NEW),(1384607,OLD_HOOK,HOOK),(1385300,b'\xff'*56,HELPER),(1034472,OLD_COOKIE,COOKIE))


@lru_cache(maxsize=1)
def proposal(parent):
    assert isinstance(parent,bytes)and H(parent)==PIN,'Exact public1327 only'
    d=Plan.descriptor(parent);assert d['receipt_SHA256']==PLAN_RECEIPT
    assert [(s['file'],bytes.fromhex(s['old_hex']),bytes.fromhex(s['new_hex']))for s in d['physical_spans']]==list(spans())
    out=bytearray(parent);owned=set()
    for at,old,new in spans():
        assert len(old)==len(new)and parent[at:at+len(old)]==old
        domain=set(range(at,at+len(old)));assert not owned&domain;owned|=domain;out[at:at+len(new)]=new
    raw=bytes(out);changed={i for i,(a,b)in enumerate(zip(parent,raw,strict=True))if a!=b}
    assert len(owned)==94 and len(changed)==91 and changed<=owned and H(raw)==CANDIDATE
    assert all(a==b for i,(a,b)in enumerate(zip(parent,raw,strict=True))if i not in owned)
    return raw,dict(parent_SHA256=PIN,candidate_SHA256=CANDIDATE,owned_bytes=94,changed_bytes=91,
        all_unowned_bytes_exact=True,cookie=COOKIE.hex(),grant_SHA256=GRANT_SHA,plan_SHA256=PLAN_SHA,
        original_motor5526_exact=True,proposed_CPU_executed=False,physical_ROM_native_Downloads=False,outputs=0)


def inverse(raw):
    assert isinstance(raw,bytes)and H(raw)==CANDIDATE,'Exact leaseda2d9 only'
    out=bytearray(raw)
    for at,old,new in spans():assert raw[at:at+len(new)]==new;out[at:at+len(old)]=old
    parent=bytes(out);assert H(parent)==PIN;return parent


if __name__=='__main__':
    parent=ROM.read_bytes();raw,q=proposal(parent);assert inverse(raw)==parent and proposal(inverse(raw))[0]==raw
    wrong=0
    for image,fn in((parent,inverse),(raw,proposal),(parent[:-1],proposal),(raw[:-1],inverse),(raw[:500]+bytes([raw[500]^1])+raw[501:],inverse)):
        try:fn(image)
        except AssertionError:wrong+=1
        else:raise AssertionError('Wrong or dirty role accepted')
    q.update(strict_roundtrip=True,wrong_roles_rejected=wrong,source_SHA256=H(Path(__file__).read_bytes()))
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
