"""Strict7a80 four-span persistence successor; in-memory source scope only."""
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import json,struct,zlib
import plan_prince_sword_tier2_fresh_1115 as Plan

R,Packet,PIN,digest=Plan.R,Plan.Packet,Plan.PIN,Plan.digest
GRANT=R/'docs/qa/allocations/prince-sword-tier2-fresh-source-1115.json'
GRANT_SHA='83d9411c7a60dcf17f272dc8d4ae5fea090e867ed8241908b7682041c1a4d477'
PLAN_SHA='2d4f2be9e9a49d0f72693f12018165ed5165d2bf915c39ceb12bd360254cf6b8'
CANDIDATE='40a11ffb8452c3b54caef56ddd5912e2bdda2c276545f20a589baa053de4d20e'
ORIGINAL_ZLIB_HEX='78da5bc4bbf7e1e6b97cc74e097c5fc9da7bfe58efc5632b197a971d58c9dcdb7160a56f6fe781a57b2d5e1af40a1eebed3eb074c94bc6deae030a17372b081d5edb72a0b7edc0dad603bded072c1218a060edf9631f0cb69a9c64da60b0555e406dabc9051ea0d049d60d6aefce1fbba0d8e5b192b1f7ddb195d10a81ab325629e8f7ae6453d83ac3226101f305a6054c3ed2b780d2d1ec3e0f8e830d7bb5887dee8f03a7047e010057644f11'
ORIGINAL_SHA='91cbb1ca40aca7573ec944bcf8d849ded4aa11cf756a1cce804ef126f60995ed'

@lru_cache(maxsize=1)
def allocation():
    data=GRANT.read_bytes();assert digest(data)==GRANT_SHA
    q=json.loads(data);assert digest(Path(Plan.__file__).read_bytes())==PLAN_SHA
    return q

@lru_cache(maxsize=1)
def proposal(parent):
    assert isinstance(parent,bytes)and digest(parent)==PIN,'Expected exact current7a80'
    allocation();head,before,old_sizes,rows,_=Plan.arrays(parent);originals=b''.join(row['old']for row in rows)
    def change(*parts):
        for row in rows:
            stream=row['stream'];lo,hi=row['decoded_half_open'];assert bytes(parts[stream][lo:hi])==row['old']
            parts[stream][lo:hi]=row['new']
        return parts
    raw,codec=Packet.rebuild(parent,change);newhead,after,sizes=Packet.extract(raw)
    assert sizes==(6461,5995,1263)and codec['cookie']=='a7260209e6eb04c8dbe70c3197b0cb4b'and codec['spare']==585
    changed_decoded=0
    for stream,(old,new)in enumerate(zip(before,after,strict=True)):
        owned={at for row in rows if row['stream']==stream for at in range(*row['decoded_half_open'])}
        assert len(old)==len(new)and all(a==b for at,(a,b)in enumerate(zip(old,new,strict=True))if at not in owned)
        changed_decoded+=sum(a!=b for a,b in zip(old,new,strict=True))
    assert changed_decoded==87
    config=len(head)-54;oldwords=struct.unpack_from('<12H',head,config);newwords=struct.unpack_from('<12H',newhead,config)
    edits=[(i,a,b)for i,(a,b)in enumerate(zip(oldwords,newwords,strict=True))if a!=b]
    assert edits==[(2,6469,6461),(10,1259,1263)]
    allowedhead={config+2*i+j for i,_,_ in edits for j in(0,1)}
    assert all(a==b for i,(a,b)in enumerate(zip(head,newhead,strict=True))if i not in allowedhead)
    allowed={*range(Packet.COOKIE,Packet.COOKIE+16),*(at for page in Packet.PAGES for at in range(Packet.CHR+page*1024,Packet.CHR+(page+1)*1024))}
    changed={at for at,(a,b)in enumerate(zip(parent,raw,strict=True))if a!=b};assert changed<=allowed
    if CANDIDATE is not None:assert digest(raw)==CANDIDATE
    if ORIGINAL_SHA is not None:assert digest(originals)==ORIGINAL_SHA and originals==zlib.decompress(bytes.fromhex(ORIGINAL_ZLIB_HEX))
    q=dict(passed=True,parent_SHA256=PIN,candidate_SHA256=digest(raw),grant_SHA256=GRANT_SHA,
        owned_decoded_bytes=166,changed_decoded_bytes=87,changed_physical_bytes=len(changed),
        new_packed_stream_bytes=sizes,cookie=codec['cookie'],carrier_spare_bytes=codec['spare'],
        original_preimages_SHA256=digest(originals),compact_preimages_zlib_hex=zlib.compress(originals,9).hex()if ORIGINAL_ZLIB_HEX is None else None,
        all_other_decoded_and_physical_bytes_exact=True,loader_art_tables_current_graphics_and_all_other_characters_exact=True,
        old5cfa_cold_negative_retained=True,source_only=True,native_qualified=False,installed=False,outputs=0,Mesen=False)
    return raw,q

@lru_cache(maxsize=1)
def inverse(raw):
    assert CANDIDATE is not None and isinstance(raw,bytes)and digest(raw)==CANDIDATE,'Expected exact Fresh persistence successor'
    allocation();old=zlib.decompress(bytes.fromhex(ORIGINAL_ZLIB_HEX));assert len(old)==166 and digest(old)==ORIGINAL_SHA
    # Coordinates are frozen directly; no parent or mutable nightly read is needed.
    coordinates=((2,0,80),(2,1452,1529),(1,6012,6013),(0,5105,5113));cursor=0
    def restore(*parts):
        nonlocal cursor
        for stream,lo,hi in coordinates:
            size=hi-lo;parts[stream][lo:hi]=old[cursor:cursor+size];cursor+=size
        assert cursor==len(old);return parts
    parent,_=Packet.rebuild(raw,restore);assert digest(parent)==PIN and proposal(parent)[0]==raw
    return parent

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Fresh persistence composer attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        raw,q=proposal(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
        if CANDIDATE is not None:q['portable_inverse_exact_parent']=digest(inverse(raw))==PIN
    print(json.dumps(q,separators=(',',':')),flush=True)
