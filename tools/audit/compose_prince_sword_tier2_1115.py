"""Strict current7a80 Prince earned-sword persistence; memory only."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json,struct,zlib
import plan_prince_sword_tier2_1115 as Plan

R,Packet,PIN=Plan.R,Plan.Packet,Plan.PIN
GRANT=R/'docs/qa/allocations/prince-sword-tier2-source-1115.json'
GRANT_SHA='c787391be64b6118f6d8183f405fd114ba82fd397adf75320be326a33af6bd51'
PLAN_SHA='4d515e094bf7a70f05fbec34224e41b48af6105ac91691b4ca0c5580ded7674a'
CANDIDATE='5cfa2a0f1e98fc74d616a922f0f7273396dc98ff20c5afe04441ca04e7f914df'
ORIGINAL_ZLIB_HEX='78da5bc4bbf7e1e6b97cc74e097c5fc9da7bfe58efc5632b197a971d58c9dcdb7160a56f6fe781a57b2d5e1af40a1eebed3eb074c94bc6deae030a17372b081d5edb72a0b7edc0dad603bded072c1218a060edf9631f0cb69a9c64da60b0555e406dabc9051ea0d049d60d6aefce1fbba0d8e5b192b1f7ddb195d10a81ab325629e8f7ae6453d83ac3226101f305a6054c3ed2b780d2d1ec3e0f8e830d7b0500f1004a3f'
ORIGINAL_SHA='b996bf9805cbf7fc4b1d5927bbe2a30d5e07f534210be9d72fa390ec6a441a2a'

def digest(data):return sha256(data).hexdigest()

@lru_cache(maxsize=1)
def allocation():
    data=GRANT.read_bytes();assert digest(data)==GRANT_SHA
    q=json.loads(data);assert q['parent_SHA256']==PIN and q['source_in_memory_composition_and_mounts_authorized']
    assert digest(Path(Plan.__file__).read_bytes())==PLAN_SHA
    assert q['detached_plan_SHA256']==PLAN_SHA and q['owned_decoded_bytes']==158
    return q

@lru_cache(maxsize=1)
def proposal(parent):
    assert isinstance(parent,bytes)and digest(parent)==PIN,'Expected exact current7a80 parent'
    grant=allocation();head,before,old_sizes,rows,_=Plan.arrays(parent)
    originals=b''.join(row['old']for row in rows)
    def change(*parts):
        for row,allowed in zip(rows,grant['decoded_spans'],strict=True):
            stream=row['stream'];lo,hi=row['decoded_half_open']
            assert stream==allowed['stream']and[lo,hi]==allowed['half_open']
            assert bytes(parts[stream][lo:hi])==row['old'];parts[stream][lo:hi]=row['new']
        return parts
    raw,codec=Packet.rebuild(parent,change);newhead,after,sizes=Packet.extract(raw)
    assert list(sizes)==grant['expected_packed_bytes']and codec['cookie']==grant['expected_cookie']
    assert codec['spare']==577
    changed_decoded=0
    for stream,(old,new)in enumerate(zip(before,after,strict=True)):
        owned={at for row in rows if row['stream']==stream for at in range(*row['decoded_half_open'])}
        assert len(old)==len(new)and all(a==b for at,(a,b)in enumerate(zip(old,new,strict=True))if at not in owned)
        changed_decoded+=sum(a!=b for a,b in zip(old,new,strict=True))
    assert changed_decoded==79
    config=len(head)-54;oldwords=struct.unpack_from('<12H',head,config);newwords=struct.unpack_from('<12H',newhead,config)
    assert[(i,a,b)for i,(a,b)in enumerate(zip(oldwords,newwords,strict=True))if a!=b]==[(10,1259,1263)]
    assert head[:config+20]==newhead[:config+20]and head[config+22:]==newhead[config+22:]
    allowed={*range(Packet.COOKIE,Packet.COOKIE+16),*(at for page in Packet.PAGES for at in range(Packet.CHR+page*1024,Packet.CHR+(page+1)*1024))}
    changed={at for at,(a,b)in enumerate(zip(parent,raw,strict=True))if a!=b};assert changed<=allowed
    if CANDIDATE is not None:assert digest(raw)==CANDIDATE
    if ORIGINAL_SHA is not None:assert digest(originals)==ORIGINAL_SHA and originals==zlib.decompress(bytes.fromhex(ORIGINAL_ZLIB_HEX))
    q=dict(passed=True,parent_SHA256=PIN,candidate_SHA256=digest(raw),grant_SHA256=GRANT_SHA,
        owned_decoded_bytes=158,changed_decoded_bytes=changed_decoded,changed_physical_bytes=len(changed),
        new_packed_stream_bytes=sizes,cookie=codec['cookie'],carrier_spare_bytes=codec['spare'],
        original_preimages_SHA256=digest(originals),compact_preimages_zlib_hex=zlib.compress(originals,9).hex()if ORIGINAL_ZLIB_HEX is None else None,
        all_other_decoded_and_physical_bytes_exact=True,loader_art_tables_and_current_graphics_exact=True,
        scope='Source-authorized in-memory candidate only; no native or delivery qualification',outputs=0,Mesen=False)
    return raw,q

@lru_cache(maxsize=1)
def inverse(raw):
    assert CANDIDATE is not None and isinstance(raw,bytes)and digest(raw)==CANDIDATE,'Expected exact Prince tier2 candidate'
    grant=allocation();old=zlib.decompress(bytes.fromhex(ORIGINAL_ZLIB_HEX));assert len(old)==158 and digest(old)==ORIGINAL_SHA
    cursor=0
    def restore(*parts):
        nonlocal cursor
        for row in grant['decoded_spans']:
            stream=row['stream'];lo,hi=row['half_open'];size=hi-lo
            parts[stream][lo:hi]=old[cursor:cursor+size];cursor+=size
        assert cursor==len(old);return parts
    parent,_=Packet.rebuild(raw,restore);assert digest(parent)==PIN
    # Validate every proposed span without reading mutable Downloads.
    assert proposal(parent)[0]==raw
    return parent

if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Tier2 composer attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        raw,q=proposal(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
        if CANDIDATE is not None:q['portable_inverse_exact_parent']=digest(inverse(raw))==PIN
    print(json.dumps(q,separators=(',',':')),flush=True)
