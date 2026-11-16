"""Exact leased20B native owner repair; memory only, portable strict inverse."""
from functools import lru_cache
from pathlib import Path
import json
import plan_mini_weapon_owner_fit_1327_1116 as Plan

R,ROM,H,N=Plan.R,Plan.ROM,Plan.H,Plan.N
PARENT=Plan.PIN
CANDIDATE='e32f9036ef79287d2fb41259ce510d86679006331618ed3b73b5e3a17a1eba7f'
PLAN_SHA='9226fbaa7c21317110e6d9a3da1291a3b09cd8c25d102af3e636957d63b9fce2'
GRANT=R/'docs/qa/allocations/mini-weapon-owner-source-root-1116.json'
GRANT_SHA='fd698e423700804227d8a860a8337ad8fe399a3bf55fb3fa3e73bd692d6d6acd'
SPANS=((649979,bytes.fromhex('3d'),bytes.fromhex('3c')),(649998,bytes.fromhex('42'),bytes.fromhex('44')),(652618,bytes.fromhex('4c4cb5c9224c7ebf68a828ad6a013860eaea'),bytes.fromhex('3010ad0260c9224c7ebf68a828ad6a013860')))

@lru_cache(maxsize=1)
def lease():
    assert H(Path(Plan.__file__).read_bytes())==PLAN_SHA and H(GRANT.read_bytes())==GRANT_SHA
    g=json.loads(GRANT.read_bytes());assert g['parent_SHA256']==PARENT and g['candidate_SHA256']==CANDIDATE
    assert g['source_composition_in_memory_and_actual_CPU_authorized']and not g['physical_ROM_files_Mesen_Downloads_delivery_authorized']
    assert[(q['file'],bytes.fromhex(q['old_hex']),bytes.fromhex(q['new_hex']))for q in g['owned_spans']]==list(SPANS)
    return g

def inverse(raw):
    lease();assert isinstance(raw,bytes)and H(raw)==CANDIDATE,'Exact e32f Mini owner image only'
    out=bytearray(raw)
    for at,old,new in SPANS:assert raw[at:at+len(new)]==new;out[at:at+len(old)]=old
    restored=bytes(out);assert H(restored)==PARENT;return restored

@lru_cache(maxsize=1)
def proposal(parent):
    lease();assert isinstance(parent,bytes)and H(parent)==PARENT,'Exact1327 owning input only'
    rows=Plan.patch_descriptor(parent);assert Plan.predicted_hash(parent,rows)==CANDIDATE
    out=bytearray(parent)
    for at,old,new in SPANS:assert parent[at:at+len(old)]==old;out[at:at+len(new)]=new
    raw=bytes(out);assert H(raw)==CANDIDATE and inverse(raw)==parent
    owned={j for at,old,_ in SPANS for j in range(at,at+len(old))}
    assert{i for i,(a,b)in enumerate(zip(parent,raw,strict=True))if a!=b}==owned and len(owned)==20
    at=Plan.Previous.Current.CODE_AT;assert raw[at:at+7168]==parent[at:at+7168]
    q=dict(passed=True,parent_SHA256=PARENT,candidate_SHA256=CANDIDATE,grant_SHA256=GRANT_SHA,plan_SHA256=PLAN_SHA,
        owned_bytes=20,changed_bytes=20,spans=rows,strict_portable_inverse=True,all_unowned_bytes_exact=True,
        Mini7168_cookie_headers_exact=True,new_resources=0,files=0,Mesen=False)
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return raw,q

def current(raw):
    if H(raw)==PARENT:return proposal(raw)[0]
    assert H(raw)==CANDIDATE;inverse(raw);return raw
