"""Exact two-span Prince proposal under root's fitted grant, memory only."""
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
import json
import build_prince_worldmaterial_research_1114 as Build
import prince_prepare_funding_research_1114 as Funding
import compose_shared_world_chr_reset_1114 as Common
import compose_dk_private_sprite_window7_1114 as DK

R=Build.R
GRANT=R/'docs/qa/allocations/prince-fitted-worldmaterial-1114.json'
GRANT_SHA='971704b0a8fea8a99717f2716736e6576c81e5059574797c17f5a832bb55cbc3'
PARENTS={'common82':Common.CANDIDATE,'dk-window7-1daca':DK.CANDIDATE}
# Filled only from the first bounded exact composition; unknown images reject.
CANDIDATES={
    '2abe4014f94f9fa61d3600ae989930d6d76f01d58d08a47d5ca5bf4dd86d5ba1':'common82',
    'e4185311a7031c88570467dc99225ee42baad7c4931b5cfa1d57d37e7720dd08':'dk-window7-1daca',
}


def digest(raw):return sha256(raw).hexdigest()


@lru_cache(maxsize=1)
def allocation():
    data=GRANT.read_bytes();assert digest(data)==GRANT_SHA;q=json.loads(data)
    assert set(q['eligible_input_SHA256'])==set(PARENTS.values())
    for path,pin in q['frozen_sources'].items():assert digest((R/path).read_bytes())==pin
    return q


@dataclass(frozen=True)
class ParentInput:
    kind:str
    original:bytes
    reference421:bytes


@lru_cache(maxsize=2)
def normalize_parent(raw,*,kind):
    assert isinstance(raw,bytes)and kind in PARENTS and digest(raw)==PARENTS[kind]
    allocation();common=DK.inverse(raw)if kind=='dk-window7-1daca'else raw
    reference=Common.inverse(common)
    assert digest(reference)==Build.Old.F.PIN
    assert Build.Old.Packet.extract(raw)==Build.Old.Packet.extract(reference)
    return ParentInput(kind,raw,reference)


def parent_kind(raw):
    matches=[k for k,v in PARENTS.items()if digest(raw)==v]
    assert len(matches)==1,'Expected exact common82 or DK-window7-1daca'
    return matches[0]


@lru_cache(maxsize=1)
def original_spans():
    allocation()
    assert digest(Build.Old.SOURCE.read_bytes())=='b696f076030f1be21ad85152fe3c86ecfc6d0c204cc65523ab73afcb301614e6'
    text,symbols=Build.Old.source();world,_=Build.Old.assemble(text,symbols)
    text=Build.Old.SOURCE.read_text().split('.segment "WORLD_GEOMETRY"',1)[1].split('.segment "WORLD_MATERIAL"',1)[0]
    text='Prepare:'+text.split('Prepare:',1)[1]
    symbols.update(Cell=0xc4ff,PpWorldPhysicalFoot=0xc312)
    prepare,_,_=Build.assemble(text,symbols,origin=0xc552,check_entries=False)
    assert digest(world)==allocation()['decoded_spans'][0]['preimage_SHA256']
    assert digest(prepare)==allocation()['decoded_spans'][1]['preimage_SHA256']
    return world,prepare


@lru_cache(maxsize=2)
def proposal(raw):
    typed=normalize_parent(raw,kind=parent_kind(raw));plan=Funding.plan(typed.reference421)
    q=allocation();old=Build.Old.Packet.extract(raw);old_parts=old[1]
    replacements=(plan['world']+b'\xea'*3,plan['prepare']+plan['helper'])
    assert tuple(map(digest,replacements))==tuple(s['proposed_SHA256']for s in q['decoded_spans'])
    def change(*parts):
        for s,replacement in zip(q['decoded_spans'],replacements):
            part=parts[s['decoded_stream']];lo,hi=s['decoded_half_open']
            assert digest(part[lo:hi])==s['preimage_SHA256']and len(replacement)==hi-lo
            part[lo:hi]=replacement
        return parts
    result,codec=Build.Old.Packet.rebuild(raw,change)
    assert digest(result)in CANDIDATES and CANDIDATES[digest(result)]==typed.kind
    new=Build.Old.Packet.extract(result)
    for i,(a,b)in enumerate(zip(old_parts,new[1],strict=True)):
        allowed={k for s in q['decoded_spans']if s['decoded_stream']==i for k in range(*s['decoded_half_open'])}
        assert len(a)==len(b)and all(x==y for k,(x,y)in enumerate(zip(a,b,strict=True))if k not in allowed)
    packet=Build.Old.Packet
    allowed={*range(packet.COOKIE,packet.COOKIE+16),*(k for page in packet.PAGES for k in range(packet.CHR+page*1024,packet.CHR+(page+1)*1024))}
    changed={i for i,(a,b)in enumerate(zip(raw,result,strict=True))if a!=b}
    assert changed<=allowed
    assert old[0][:packet.LOADER]==new[0][:packet.LOADER]
    assert result[packet.CHR+823*1024:packet.CHR+824*1024]==raw[packet.CHR+823*1024:packet.CHR+824*1024]
    assert new[1][0][0x1400:0x1ae5]==old_parts[0][0x1400:0x1ae5]
    for at,oldbyte,newbyte in DK.SPANS:assert result[at]==raw[at]==(newbyte if typed.kind=='dk-window7-1daca'else oldbyte)
    return result,dict(parent_kind=typed.kind,parent_SHA256=digest(raw),candidate_SHA256=digest(result),
        allocation_SHA256=GRANT_SHA,cookie=result[packet.COOKIE:packet.COOKIE+16].hex(),
        old_packed_bytes=old[2],new_packed_bytes=new[2],codec=codec,
        exact_decoded_change_envelopes=[s['decoded_half_open']for s in q['decoded_spans']],
        metadata_scripts_art_and_unowned_bytes_exact=True,DK_operands_preserved=True,DK_sprite_page823_exact=True,
        common_reset_and_prior176_fix_bytes_preserved=True,changed_physical_bytes=len(changed),
        portable_inverse_no_Downloads_dependency=True,source_qualification_complete=False,
        native_qualified=False,installed=False,outputs=0,Mesen=False)


@lru_cache(maxsize=2)
def inverse(raw):
    assert isinstance(raw,bytes)and digest(raw)in CANDIDATES,'Expected exact Prince body-world candidate'
    kind=CANDIDATES[digest(raw)];q=allocation();before=original_spans()
    def restore(*parts):
        for s,old in zip(q['decoded_spans'],before):
            part=parts[s['decoded_stream']];lo,hi=s['decoded_half_open']
            assert digest(part[lo:hi])==s['proposed_SHA256'];part[lo:hi]=old
        return parts
    parent,_=Build.Old.Packet.rebuild(raw,restore)
    assert digest(parent)==PARENTS[kind]
    assert proposal(parent)[0]==raw
    return parent


if __name__=='__main__':
    raw=Build.Old.F.ROM.read_bytes();kind=parent_kind(raw)
    if kind=='dk-window7-1daca':raw=DK.inverse(raw)
    for parent in(raw,DK.proposal(raw)[0]):
        candidate,info=proposal(parent)
        if CANDIDATES:assert inverse(candidate)==parent
        print(json.dumps(info,separators=(',',':')),flush=True)
