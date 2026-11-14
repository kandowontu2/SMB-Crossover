"""Exact root-granted three-operand DK window7 delta, memory only."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import compose_shared_world_chr_reset_1114 as Common

R=Path(__file__).resolve().parents[2]
PIN=Common.CANDIDATE
CANDIDATE='1daca93f837e894a3ee5b3d8cef54622336726f4df243c6bfb997130323f3baa'
GRANT=R/'docs/qa/allocations/dk-private-sprite-window7-1114.json'
GRANT_SHA='377cc14cab33512bcd5fb535aa0a8ab9ab7d2a9ba4fd789c5e537843ee48f79a'
SPANS=((105706,1,7),(105772,64,193),(105780,64,193))


def digest(raw):return sha256(raw).hexdigest()


@lru_cache(maxsize=1)
def allocation():
    data=GRANT.read_bytes();assert digest(data)==GRANT_SHA
    q=json.loads(data);assert q['parent_SHA256']==PIN and q['conditional_selected_owner']==28
    assert [(s['file_offset'],int(s['preimage_hex'],16),int(s['proposed_hex'],16))for s in q['operand_spans']]==list(SPANS)
    assert all(s['bytes']==1 for s in q['operand_spans'])
    lease=q['temporal_sprite_window_lease'];assert lease['window']==7 and lease['physical_CHR_page']==823
    return q


@lru_cache(maxsize=1)
def proposal(raw):
    assert isinstance(raw,bytes)and digest(raw)==PIN,'Expected exact delivered82ec'
    q=allocation();assert Common.proposal(Common.inverse(raw))[0]==raw
    routine=q['current_routine'];lo,hi=routine['file_half_open']
    assert digest(raw[lo:hi])==routine['preimage_SHA256']
    result=bytearray(raw)
    for at,old,new in SPANS:assert result[at]==old;result[at]=new
    result=bytes(result);assert digest(result)==CANDIDATE
    changed={i for i,(a,b)in enumerate(zip(raw,result,strict=True))if a!=b}
    assert changed=={at for at,_,_ in SPANS}
    assert all(result[i]==raw[i]for i in range(len(raw))if i not in changed)
    return result,dict(owning_parent_SHA256=PIN,candidate_SHA256=CANDIDATE,
        allocation_SHA256=GRANT_SHA,changed_bytes=3,temporal_owner=28,window=7,
        physical_CHR_page=823,all_other_bytes_exact=True,common_reset_and176_previous_fix_bytes_preserved=True,
        source_qualification_complete=False,native_qualified=False,installed=False,outputs=0)


def inverse(raw):
    assert isinstance(raw,bytes)and digest(raw)==CANDIDATE,'Expected exact DK-window7 image'
    allocation();parent=bytearray(raw)
    for at,old,new in SPANS:assert parent[at]==new;parent[at]=old
    parent=bytes(parent);assert digest(parent)==PIN
    assert proposal(parent)[0]==raw
    return parent


def load_current_image(path=None):
    raw=(Common.Measure.C.ROM if path is None else Path(path)).read_bytes()
    if digest(raw)==PIN:return proposal(raw)[0]
    assert digest(raw)==CANDIDATE,'Expected exact82ec or exact DK-window7 image'
    assert proposal(inverse(raw))[0]==raw
    return raw


if __name__=='__main__':
    raw=load_current_image();print(json.dumps(proposal(inverse(raw))[1],separators=(',',':')),flush=True)
