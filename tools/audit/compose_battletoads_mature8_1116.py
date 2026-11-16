"""Strict leased27-byte Battletoads maturity join, memory only."""
from functools import lru_cache
from pathlib import Path
from hashlib import sha256
import json

R=Path(__file__).resolve().parents[2]
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN='6a3ff7c9a60b5ff5906d38f7815f021062006e0817d43e7ed139f47589c4eee2'
CANDIDATE='91dc4ac58ae749bc81f1ef91953c7c3e5aba73dd07e4b6ea2cd3059d1cdb41cc'
GRANT=R/'docs/qa/allocations/battletoads-mature8-source-1116.json'
GRANT_SHA='432d8f7e4797a646a394756ab04af58ed56ce1f9fbe7f83ba5030e25347e08dd'
PLAN_SHA='3b1a0aaa72c1982e1ce77d082ef92b9f11cb9347a0c72c60b48ccc8cd3ea5b9a'
CHECK_SHA='915f7eace1a020d0d159fdff61d25656bf71130b245a8846e2edc0e3b774a483'
CACHE,COOKIE,HEADER=1989648,765863,765392
digest=lambda raw:sha256(raw).hexdigest()

@lru_cache(maxsize=1)
def lease():
    assert digest(GRANT.read_bytes())==GRANT_SHA
    assert digest((R/'tools/audit/plan_battletoads_mature8_6a3_1116.py').read_bytes())==PLAN_SHA
    assert digest((R/'tools/audit/check_battletoads_mature8_detached_6a3_1116.py').read_bytes())==CHECK_SHA
    q=json.loads(GRANT.read_text());assert q['owning_parent_SHA256']==PIN
    assert(q['owned_bytes'],q['changed_bytes'])==(27,22)
    assert q['source_in_memory_composition_and_mounts_authorized']
    assert not any(q[n]for n in('physical_ROM_file_writes_authorized','native_Mesen_authorized','Downloads_delivery_authorized'))
    return q

def spans():return[(r['file_half_open'][0],bytes.fromhex(r['old_hex']),bytes.fromhex(r['new_hex']))for r in lease()['spans']]

@lru_cache(maxsize=1)
def proposal(parent):
    assert isinstance(parent,bytes)and digest(parent)==PIN,'Exact current6a3 required'
    q=lease();out=bytearray(parent);owned=set()
    for at,old,new in spans():
        assert len(old)==len(new)and parent[at:at+len(old)]==old
        assert not owned.intersection(range(at,at+len(old)));owned.update(range(at,at+len(old)));out[at:at+len(old)]=new
    out=bytes(out);changed={i for i,(a,b)in enumerate(zip(parent,out,strict=True))if a!=b}
    assert len(owned)==27 and len(changed)==22 and changed<=owned
    assert digest(parent[CACHE:CACHE+8192])==q['payload']['old_SHA256']
    assert digest(out[CACHE:CACHE+8192])==q['payload']['new_SHA256']
    assert digest(out[HEADER:HEADER+487])==q['payload']['new_native_header487_SHA256']
    assert out[COOKIE+4:COOKIE+16]==bytes.fromhex(digest(out[CACHE:CACHE+8192]))[:12]
    assert out[CACHE+0x1602]==parent[CACHE+0x1602]==0x60
    if CANDIDATE is not None:assert digest(out)==CANDIDATE
    return out,dict(parent_SHA256=PIN,candidate_SHA256=digest(out),grant_SHA256=GRANT_SHA,
        owned_bytes=27,changed_bytes=22,payload_SHA256=digest(out[CACHE:CACHE+8192]),
        full16_cookie=out[COOKIE:COOKIE+16].hex(),all_unowned_bytes_exact=True,
        Bowser72_CF_Hot118_Carry714_camera29_preserved=True,outputs=0,physical_ROM_native_delivery_authorized=False)

def inverse(raw):
    assert CANDIDATE is not None and isinstance(raw,bytes)and digest(raw)==CANDIDATE,'Exact maturity candidate required'
    parent=bytearray(raw)
    for at,old,new in spans():assert raw[at:at+len(new)]==new;parent[at:at+len(old)]=old
    parent=bytes(parent);assert digest(parent)==PIN
    return parent

if __name__=='__main__':
    _,q=proposal(ROM.read_bytes());q['receipt_SHA256']=digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
