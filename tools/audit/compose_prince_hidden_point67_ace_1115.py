"""Strict owning-ACE Prince point repair; source-only, entirely in memory."""
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import json,struct
import compose_battletoads_carry_current_1115 as Carry
import plan_prince_hidden_point67_174fa_1115 as Plan

R,Packet,digest=Plan.R,Plan.C.Packet,Plan.H
PIN='aceedaf2151fdf673b489a742831a0844abbb3837e0bcba68408d3ba5c3a4cfe'
CANDIDATE='7fb328a6dcf6b50fd000e81eced4fd4b7390bedec56085d33130434003cc76d0'
GRANT=R/'docs/qa/allocations/prince-hidden-point67-ace-source-1115.json'
GRANT_SHA='8bf7fb86cdbc77956ee452f4a8b34bc66fda49ea883100641f837e12e459ceb0'
PLAN_SHA='8e583fdf06ff2f3bc0f83876e6a3c416088cb5bcabf0fb19146d7c9d50741f62'
CARRY_SHA='6b87663ae0de5a1bb8b58ab73fa5313dcc8b80def75b09102fd2b66669fd604d'
OLD=bytes.fromhex('8a489848ad6cb3d02cad6bb338e920c9d0b02229f0a8ad6ab32901aaad69b34a4a4a4a187dd8958d3bb3b90003aabd36ef4a8ab003a900188d6db368a868aaad6db360')
NEW=bytes.fromhex('9848ad6cb3d030ad6bb338e920c9d0b02629f0a8ad6ab34aad69b36a4ac9406ac9806ab88d38b3b9000320ca9ef008a8b936ef4a98b003a900188d6db368a8ad6db360')
LO,HI=4880,4947

@lru_cache(maxsize=1)
def allocation():
    assert digest(GRANT.read_bytes())==GRANT_SHA
    assert digest(Path(Plan.__file__).read_bytes())==PLAN_SHA
    assert digest(Path(Carry.__file__).read_bytes())==CARRY_SHA
    q=json.loads(GRANT.read_bytes());assert q['owning_parent_SHA256']==PIN
    assert q['source_in_memory_composition_and_mounts_authorized']
    assert not any(q[k]for k in('physical_ROM_file_writes_authorized','native_Mesen_authorized','Downloads_delivery_authorized'))
    row=q['decoded_envelope'];assert row['half_open']==[LO,HI]and bytes.fromhex(row['new_hex'])==NEW
    assert len(OLD)==len(NEW)==67 and digest(OLD)==row['old_SHA256']and digest(NEW)==row['new_SHA256']
    return q

@lru_cache(maxsize=1)
def reference(raw):
    allocation();assert isinstance(raw,bytes)and digest(raw)==PIN,'Exact owning ACE image required'
    prior=Carry.inverse(raw);assert digest(prior)==Plan.Current.PIN
    assert Packet.extract(raw)==Packet.extract(prior),'Carry must preserve every Prince packet byte'
    return prior

def spans(changes):
    rows=[]
    for at in sorted(changes):
        if rows and rows[-1][1]==at:rows[-1][1]+=1
        else:rows.append([at,at+1])
    return rows

@lru_cache(maxsize=1)
def proposal(parent):
    prior=reference(parent);old,new,*_=Plan.arrays(prior);assert old==OLD and new==NEW
    head,before,old_sizes=Packet.extract(parent)
    def change(*parts):
        assert parts[0][LO:HI]==OLD;parts[0][LO:HI]=NEW;return parts
    raw,codec=Packet.rebuild(parent,change);newhead,after,sizes=Packet.extract(raw)
    assert sizes==(6467,5995,1263)and codec['cookie']=='a72602350cd97981c60cc7748ecae33b'and codec['spare']==579
    assert before[1:]==after[1:]and before[0][:LO]==after[0][:LO]and before[0][HI:]==after[0][HI:]
    config=len(head)-54;a=struct.unpack_from('<12H',head,config);b=struct.unpack_from('<12H',newhead,config)
    assert [(i,x,y)for i,(x,y)in enumerate(zip(a,b))if x!=y]==[(2,6461,6467)]
    assert all(x==y for i,(x,y)in enumerate(zip(head,newhead))if i not in(config+4,config+5))
    allowed={*range(Packet.COOKIE,Packet.COOKIE+16),*(at for page in Packet.PAGES for at in range(Packet.CHR+page*1024,Packet.CHR+(page+1)*1024))}
    changed={at for at,(x,y)in enumerate(zip(parent,raw,strict=True))if x!=y};assert changed<=allowed
    # All carry-owned physical envelopes and the entire remaining image are exact.
    for at,h in Carry.PREIMAGES:assert raw[at:at+len(bytes.fromhex(h))]==parent[at:at+len(bytes.fromhex(h))]
    assert raw[Plan.Current.Palette.COOKIE:Plan.Current.Palette.COOKIE+16]==parent[Plan.Current.Palette.COOKIE:Plan.Current.Palette.COOKIE+16]
    if CANDIDATE is not None:assert digest(raw)==CANDIDATE
    q=dict(passed=True,parent_SHA256=PIN,candidate_SHA256=digest(raw),grant_SHA256=GRANT_SHA,
        old_code_SHA256=digest(OLD),new_code_SHA256=digest(NEW),owned_decoded_bytes=67,changed_decoded_bytes=61,
        packed_sizes=sizes,cookie=codec['cookie'],spare=codec['spare'],changed_header_words=[2],
        changed_physical_bytes=len(changed),changed_physical_half_open=spans(changed),
        all_other_decoded_and_unowned_physical_bytes_exact=True,carry714_and_Bub52_preserved=True,
        public_entry=0xb310,shared_RTS=0xb352,probe_entry=0xb353,old_SMC_low=0xb33b,new_SMC_low=0xb338,
        source_only=True,outputs=0,Mesen=False,installed=False)
    return raw,q

@lru_cache(maxsize=1)
def inverse(raw):
    allocation();assert CANDIDATE is not None and isinstance(raw,bytes)and digest(raw)==CANDIDATE,'Exact new Prince point candidate required'
    def restore(*parts):
        assert parts[0][LO:HI]==NEW;parts[0][LO:HI]=OLD;return parts
    parent,_=Packet.rebuild(raw,restore);assert digest(parent)==PIN and proposal(parent)[0]==raw
    return parent

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Point composer attempted output/native launch')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        raw,q=proposal(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
        if CANDIDATE is not None:q['portable_inverse_exact_ACE']=inverse(raw)==Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    q['receipt_SHA256']=digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());print(json.dumps(q,separators=(',',':')),flush=True)
