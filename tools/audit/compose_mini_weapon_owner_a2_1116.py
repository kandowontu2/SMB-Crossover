"""Exact leased Mini20 over owning Sonic a2; memory only, strict inverse."""
from functools import lru_cache
from pathlib import Path
import json
import plan_mini_weapon_owner_a2_1116 as Plan

R,ROM,H=Plan.R,Plan.ROM,Plan.H
PARENT='a2d9d1218504dedf186cfe352ee4c927160529af4f8d09fe6e2aafccfae477c7'
CANDIDATE='98261effbc214d24a00b2f8bd2950eca8ea3bf3675b331956a2ad42a7ab819e6'
PLAN_SHA='4b2e564c416b5935a46e4ed635adf10efa712076c4e2db6429d11b0529529eec'
GRANT=R/'docs/qa/allocations/mini-weapon-owner-a2-source-root-1116.json'
GRANT_SHA='53e9937b5a62346d1b7329443c7e1d054275230457fc718a6c8a0c5cac9cb715'
SPANS=Plan.Mini.SPANS

@lru_cache(maxsize=1)
def lease():
    assert H(Path(Plan.__file__).read_bytes())==PLAN_SHA and H(GRANT.read_bytes())==GRANT_SHA
    g=json.loads(GRANT.read_bytes());assert(g['parent_SHA256'],g['candidate_SHA256'])==(PARENT,CANDIDATE)
    assert g['source_composition_in_memory_and_actual_CPU_authorized']and not g['physical_ROM_files_Mesen_Downloads_delivery_authorized']
    assert[(q['file'],bytes.fromhex(q['old_hex']),bytes.fromhex(q['new_hex']))for q in g['owned_spans']]==list(SPANS)
    return g

def inverse(raw):
    lease();assert isinstance(raw,bytes)and H(raw)==CANDIDATE,'Exact owning 9826 only'
    out=bytearray(raw)
    for at,old,new in SPANS:assert raw[at:at+len(new)]==new;out[at:at+len(old)]=old
    restored=bytes(out);assert H(restored)==PARENT;return restored

@lru_cache(maxsize=1)
def proposal(parent):
    lease();assert isinstance(parent,bytes)and H(parent)==PARENT,'Exact owning a2 input only'
    assert Plan.streaming(parent,SPANS)==CANDIDATE
    out=bytearray(parent)
    for at,old,new in SPANS:assert parent[at:at+len(old)]==old;out[at:at+len(new)]=new
    raw=bytes(out);assert H(raw)==CANDIDATE and inverse(raw)==parent
    owned={i for at,old,_ in SPANS for i in range(at,at+len(old))}
    assert{i for i,(a,b)in enumerate(zip(parent,raw,strict=True))if a!=b}==owned and len(owned)==20
    for at,old,new in Plan.Reader.Sonic.spans():assert raw[at:at+len(new)]==parent[at:at+len(new)]==new
    q=dict(passed=True,parent_SHA256=PARENT,candidate_SHA256=CANDIDATE,grant_SHA256=GRANT_SHA,plan_SHA256=PLAN_SHA,
        owned_bytes=20,changed_bytes=20,Sonic94_preserved=True,all_unowned_bytes_exact=True,strict_portable_inverse=True,
        spans=[dict(file=at,bytes=len(old),old_hex=old.hex(),new_hex=new.hex())for at,old,new in SPANS],outputs=0,Mesen=False)
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return raw,q

def current(raw):
    if H(raw)==PARENT:return proposal(raw)[0]
    assert H(raw)==CANDIDATE;inverse(raw);return raw
