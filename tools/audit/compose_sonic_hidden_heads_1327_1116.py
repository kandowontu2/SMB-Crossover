"""Strict leased80-byte Sonic hidden-head composer, portable inverse, RAM only."""
from functools import lru_cache
from pathlib import Path
import json
import plan_sonic_hidden_heads_1327_1116 as Plan

R,ROM,H,PIN=Plan.R,Plan.ROM,Plan.H,Plan.PIN
CANDIDATE='f7c934fad98f580c854fc38065c57fec60606a58f0fb8f63c4c29ad4998769af'
GRANT=R/'docs/qa/allocations/sonic-hidden-heads-source-root-1116.json'
GRANT_SHA='3ce968bccd34ffd3f87034c5e9d661afcd42f2c9637c7c92d54e604ce9f7ecc9'
PLAN_SHA='72389119e42a6f84ef71bbfdea78c3132799cae779a2c6d99219cb549c118901'
PLAN_RECEIPT='6140b1334cc35e2c3bc258e275036e4d6a24e0f533e743b027cca60c8c2056f2'
OLD=bytes.fromhex('ad04c1c95ff070c960f06cc967f068c968f064')
NEW=bytes.fromhex('4c44d3')+b'\xea'*16
HELPER=bytes.fromhex('ad04c1c95ff00fc960f00bc967f01bc968f0174c39bbadb7c0c901d00aadb8c0c901d0034c39bb4c5fbb4c9dbb')
OLD_COOKIE=bytes.fromhex('a72b0124b3a071484566f32036ec45cb')
COOKIE=bytes.fromhex('a72b015484b4b55c20d06fff02bfa3bd')


@lru_cache(maxsize=1)
def lease():
    assert H(GRANT.read_bytes())==GRANT_SHA and H(Path(Plan.__file__).read_bytes())==PLAN_SHA
    g=json.loads(GRANT.read_text())
    assert(g['parent_SHA256'],g['candidate_SHA256'],g['descriptor_receipt_SHA256'])==(PIN,CANDIDATE,PLAN_RECEIPT)
    assert g['source_composition_in_memory_and_actual_CPU_authorized']and not g['physical_ROM_files_Mesen_Downloads_delivery_authorized']
    assert [(r['file'],r['bytes'])for r in g['owned_spans']]==[(1384246,19),(1385300,45),(1034472,16)]
    return g


def spans():
    lease();return((1384246,OLD,NEW),(1385300,b'\xff'*45,HELPER),(1034472,OLD_COOKIE,COOKIE))


@lru_cache(maxsize=1)
def proposal(parent):
    assert isinstance(parent,bytes)and H(parent)==PIN,'Exact owning1327 only'
    d=Plan.descriptor(parent);assert d['receipt_SHA256']==PLAN_RECEIPT
    assert [(s['file'],bytes.fromhex(s['old_hex']),bytes.fromhex(s['new_hex']))for s in d['physical_spans']]==list(spans())
    out=bytearray(parent);owned=set()
    for at,old,new in spans():
        assert len(old)==len(new)and parent[at:at+len(old)]==old
        domain=set(range(at,at+len(old)));assert not owned&domain;owned|=domain;out[at:at+len(new)]=new
    raw=bytes(out);changed={i for i,(a,b)in enumerate(zip(parent,raw,strict=True))if a!=b}
    assert len(owned)==80 and len(changed)==77 and changed<=owned and H(raw)==CANDIDATE
    assert all(a==b for i,(a,b)in enumerate(zip(parent,raw,strict=True))if i not in owned)
    return raw,dict(parent_SHA256=PIN,candidate_SHA256=CANDIDATE,owned_bytes=80,changed_bytes=77,
        all_unowned_bytes_exact=True,cookie=COOKIE.hex(),grant_SHA256=GRANT_SHA,plan_SHA256=PLAN_SHA,
        proposed_CPU_executed=False,physical_ROM_native_Downloads=False,outputs=0)


def inverse(raw):
    assert isinstance(raw,bytes)and H(raw)==CANDIDATE,'Exact leasedf7c9 only'
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
