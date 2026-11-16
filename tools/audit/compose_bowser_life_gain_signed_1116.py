"""Leased strict72-byte Bowser life join, memory only and portable inverse."""
from functools import lru_cache
from pathlib import Path
import json
import plan_bowser_life_gain_signed_bc5_1115 as Plan

R,ROM,PIN,Current,digest=Plan.R,Plan.Current.ROM,Plan.PIN,Plan.Current,Plan.digest
GRANT=R/'docs/qa/allocations/bowser-life-gain-signed-source-1116.json'
GRANT_SHA='e31a50f36dc2949039ccd34a4f3f1528b1b4d4998068c887b1f452cf8b08f2a6'
PLAN_SHA='c1308b6f81629def6d2f0b579b17b3196e188861fdf8c4ded9f6f493294e497d'
CHECK_SHA='5b1cfcdda5bc78ad1b30539d617a6edc640e94b50f8da127ff031c6b2d653a98'
CANDIDATE='6a3ff7c9a60b5ff5906d38f7815f021062006e0817d43e7ed139f47589c4eee2'

@lru_cache(maxsize=1)
def lease():
    assert digest(GRANT.read_bytes())==GRANT_SHA
    assert digest(Path(Plan.__file__).read_bytes())==PLAN_SHA
    assert digest((R/'tools/audit/check_bowser_life_gain_signed_detached_bc5_1115.py').read_bytes())==CHECK_SHA
    q=json.loads(GRANT.read_text());assert q['owning_parent_SHA256']==PIN
    assert(q['owned_bytes'],q['changed_bytes'])==(72,56)
    assert q['source_in_memory_composition_and_mounts_authorized']
    assert not any(q[k]for k in('physical_ROM_file_writes_authorized','native_Mesen_authorized','Downloads_delivery_authorized'))
    assert(q['envelope']['CPU_half_open'],q['envelope']['file_half_open'])==([0xa133,0xa15b],[1998147,1998187])
    assert q['envelope']['new_hex'][56:58]=='30','Unsigned proposal is never mountable'
    return q

def spans():
    q=lease();e=q['envelope'];c=q['cookie_views']
    return [(e['file_half_open'][0],bytes.fromhex(e['old_hex']),bytes.fromhex(e['new_hex']))]+[
        (at,bytes.fromhex(c['old_hex']),bytes.fromhex(c['new_hex']))for at in c['files']]

@lru_cache(maxsize=1)
def proposal(parent):
    assert isinstance(parent,bytes)and digest(parent)==PIN,'Exact owning bc5 parent required'
    q=lease();_,before,after,row=Plan.proposal(parent)
    lo,hi=q['payload']['file_half_open'];assert parent[lo:hi]==before
    result=bytearray(parent);owned=set()
    for at,old,new in spans():
        assert len(old)==len(new)and parent[at:at+len(old)]==old
        assert not owned.intersection(range(at,at+len(old)));owned.update(range(at,at+len(old)))
        result[at:at+len(old)]=new
    result=bytes(result);changed={i for i,(a,b)in enumerate(zip(parent,result,strict=True))if a!=b}
    assert len(owned)==72 and len(changed)==56 and changed<=owned
    assert result[lo:hi]==after and digest(after)==q['payload']['proposed_SHA256']
    if CANDIDATE is not None:assert digest(result)==CANDIDATE
    receipt=dict(parent_SHA256=PIN,candidate_SHA256=digest(result),grant_SHA256=GRANT_SHA,owned_bytes=72,changed_bytes=56,
        payload_SHA256=digest(after),cookie=q['cookie_views']['new_hex'],all_unowned_bytes_exact=True,
        new_RAM_CHR_art_physics_helper_capacity=0,source_only=True,ROM_file_writes_native_delivery_authorized=False,outputs=0)
    return result,receipt

def inverse(raw):
    assert CANDIDATE is not None and isinstance(raw,bytes)and digest(raw)==CANDIDATE,'Exact life-gain candidate required'
    parent=bytearray(raw)
    for at,old,new in spans():
        assert raw[at:at+len(new)]==new;parent[at:at+len(old)]=old
    parent=bytes(parent);assert digest(parent)==PIN
    assert proposal(parent)[0]==raw
    return parent

if __name__=='__main__':
    from unittest.mock import patch
    parent=ROM.read_bytes()
    def deny(*a,**kw):raise AssertionError('In-memory Bowser composer attempted files/native')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):raw,q=proposal(parent)
    q['receipt_SHA256']=digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
