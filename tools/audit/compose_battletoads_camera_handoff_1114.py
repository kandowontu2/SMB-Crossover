"""Exact root-granted52-byte BT camera composition over deliveredcf7, memory only."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import compose_gimmick_private_window7_1114 as Parent

R=Parent.R
PIN=Parent.CANDIDATE
CANDIDATE='f11a25b892779cb0d5192457f7feff548f35019818cd75dfef5bdf3f2419b865'
GRANT=R/'docs/qa/allocations/battletoads-camera-handoff-1114.json'
GRANT_SHA='a6cf8e2291c92d03077cdf6b5172d0f2a8876ae74562fc2cccbceeadb3db92bf'
BASE=1989648


def digest(raw):return sha256(raw).hexdigest()


@lru_cache(maxsize=1)
def allocation():
    data=GRANT.read_bytes();assert digest(data)==GRANT_SHA;q=json.loads(data)
    assert(q['eligible_input_SHA256'],q['conditional_owner'],q['temporal_RAM_bank'])==(PIN,33,3)
    assert q['payload_file']==[BASE,BASE+8192]and q['maximum_changed_bytes']==52
    for name,pin in q['frozen_research'].items():assert digest((R/name).read_bytes())==pin,name
    return q


def spans():
    result=[]
    for s in allocation()['spans']:
        at=s['file']if'file'in s else s['file_half_open'][0]
        old,new=bytes.fromhex(s['old']),bytes.fromhex(s['new']);assert len(old)==len(new)
        if'file_half_open'in s:assert s['file_half_open'][1]==at+len(old)
        result.append((at,old,new))
    assert[(at,len(old))for at,old,_ in result]==[(1993448,5),(1993646,6),(1995254,29),(765863,16)]
    assert len({at+i for at,old,_ in result for i in range(len(old))})==56
    return tuple(result)


@lru_cache(maxsize=1)
def bindings(raw):
    assert isinstance(raw,bytes)and digest(raw)==PIN,'Expected exact deliveredcf7'
    assert Parent.proposal(Parent.inverse(raw))[0]==raw
    q=allocation();assert digest(raw[BASE:BASE+8192])==q['old_payload_SHA256']
    for at,old,new in spans():assert raw[at:at+len(old)]==old
    assert raw[BASE+0x1fe0:BASE+0x1ff0]==bytes(16)
    return spans()


@lru_cache(maxsize=1)
def proposal(raw):
    specs=bindings(raw);out=bytearray(raw)
    for at,old,new in specs:out[at:at+len(new)]=new
    out=bytes(out);assert digest(out)==CANDIDATE
    q=allocation();cache=out[BASE:BASE+8192]
    assert digest(cache)==q['new_payload_SHA256']
    assert out[765863:765879]==bytes((167,33,1,117))+sha256(cache).digest()[:12]
    changed={i for i,(a,z)in enumerate(zip(raw,out,strict=True))if a!=z}
    expected={at+i for at,old,new in specs for i,(a,z)in enumerate(zip(old,new,strict=True))if a!=z}
    assert changed==expected and len(changed)==52
    assert all(out[i]==raw[i]for i in range(len(raw))if i not in changed)
    return out,dict(parent_SHA256=PIN,candidate_SHA256=CANDIDATE,allocation_SHA256=GRANT_SHA,
        changed_bytes=52,cache_code_bytes=40,cookie_digest_bytes=12,all_unowned_bytes_exact=True,
        protected_Gimmick192_DK3_common29_prior176_preserved=True,payload_SHA256=digest(cache),
        cookie=out[765863:765879].hex(),source_qualification_complete=False,native_qualified=False,
        installed=False,outputs=0)


def inverse(raw):
    assert isinstance(raw,bytes)and digest(raw)==CANDIDATE,'Expected exact BT camera candidate'
    out=bytearray(raw)
    for at,old,new in spans():assert out[at:at+len(new)]==new;out[at:at+len(old)]=old
    out=bytes(out);assert digest(out)==PIN
    assert proposal(out)[0]==raw
    return out


def load_current_image(path=None):
    raw=(Parent.Census.Factory.ROM if path is None else Path(path)).read_bytes()
    if digest(raw)==PIN:return proposal(raw)[0]
    assert digest(raw)==CANDIDATE,'Expected exactcf7 or exactBT camera image'
    assert proposal(inverse(raw))[0]==raw
    return raw


if __name__=='__main__':
    raw=load_current_image();print(json.dumps(proposal(inverse(raw))[1],separators=(',',':')),flush=True)
