"""Root-granted exact192-byte Gimmick window7 composition, memory only."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import compose_dk_private_sprite_window7_1114 as Parent
import check_gimmick_world_sprite_images_1114 as Census

R=Path(__file__).resolve().parents[2]
PIN=Parent.CANDIDATE
CANDIDATE='cf7b6d2964ae0ef18d08c726f66afe9bf5be3dc6f3ec9c7a43279121ee09d968'
GRANT=R/'docs/qa/allocations/gimmick-private-window7-1114.json'
GRANT_SHA='5135a2e27f0d71764d71a420c80e0fe5b0866b3650d543b5a9b2cabd1a85d5df'


def digest(raw):return sha256(raw).hexdigest()


@lru_cache(maxsize=1)
def allocation():
    data=GRANT.read_bytes();assert digest(data)==GRANT_SHA;q=json.loads(data)
    assert(q['eligible_input_SHA256'],q['conditional_owner'],q['private_CHR_page'],q['private_sprite_window'])==(PIN,26,818,7)
    assert [(p['file'],p['old'],p['new'])for p in q['publisher_operands']]==[(622194,1,7),(622413,1,7)]
    for path,pin in q['frozen_sources'].items():assert digest((R/path).read_bytes())==pin,path
    return q


def tile_digest(triples):return digest(json.dumps([(at,(old,new))for at,old,new in sorted(triples)]).encode())


@lru_cache(maxsize=1)
def bindings(raw):
    assert isinstance(raw,bytes)and digest(raw)==PIN,'Expected exact delivered1daca'
    q=allocation();assert Parent.proposal(Parent.inverse(raw))[0]==raw
    source=Census.census(raw);tiles=tuple(map(tuple,source['proposed_tile_offset_triples']))
    assert len(tiles)==q['tile_metadata']['deduplicated_operand_bytes']==190
    assert tile_digest(tiles)==q['tile_metadata']['exact_sorted_offset_old_new_digest']
    assert source['record_digest']==q['tile_metadata']['record_digest']
    pubs=[]
    for p in q['publisher_operands']:
        at=p['file'];assert raw[at-5:at+1]==bytes.fromhex(p['preimage'])
        pubs.append((at,p['old'],p['new']))
    spans=tuple(sorted((*tiles,*pubs)));assert len({at for at,_,_ in spans})==192
    return spans


@lru_cache(maxsize=1)
def proposal(raw):
    spans=bindings(raw);result=bytearray(raw)
    for at,old,new in spans:assert result[at]==old;result[at]=new
    result=bytes(result);assert digest(result)==CANDIDATE
    changed={i for i,(a,b)in enumerate(zip(raw,result,strict=True))if a!=b}
    assert changed=={at for at,_,_ in spans}and len(changed)==192
    assert all(result[i]==raw[i]for i in range(len(raw))if i not in changed)
    return result,dict(owning_parent_SHA256=PIN,candidate_SHA256=CANDIDATE,allocation_SHA256=GRANT_SHA,
        changed_bytes=192,metadata_bytes=190,publisher_bytes=2,temporal_owner=26,window=7,physical_CHR_page=818,
        all_other_1daca_bytes_exact=True,all_previous_fixes_and_CHR_pixels_preserved=True,
        inverse_mutable_Downloads_dependency=False,source_qualification_complete=False,native_qualified=False,installed=False,outputs=0)


def inverse(raw):
    """Recover source-proven preimages from candidate records, never Downloads."""
    assert isinstance(raw,bytes)and digest(raw)==CANDIDATE,'Expected exact Gimmick7 candidate'
    q=allocation();b=dict(Census.W.Symbols.bundle(),raw=raw);parent=bytearray(raw);tiles={}
    for name,count in q['tile_metadata']['source_tables'].items():
        table=Census.W.location(b,name);bank=(table-16)//8192
        for index in range(count):
            pointer=int.from_bytes(raw[table+2*index:table+2*index+2],'little')
            offset=16+bank*8192+(pointer&8191)
            for part in range(16):
                if raw[offset+4*part]==0:break
                at=offset+4*part+1;tile=raw[at]
                if tile&1:
                    assert tile>=193 and((tile&1)*4+(tile>>6))==7
                    old=(tile&62)|64;assert old&62==tile&62;tiles[at]=(old,tile);parent[at]=old
                else:assert tile<64
            else:raise AssertionError('Candidate source record termination')
    triples=tuple((at,*pair)for at,pair in sorted(tiles.items()))
    assert len(triples)==190 and tile_digest(triples)==q['tile_metadata']['exact_sorted_offset_old_new_digest']
    for p in q['publisher_operands']:
        at=p['file'];assert raw[at]==p['new'];parent[at]=p['old']
    parent=bytes(parent);assert digest(parent)==PIN
    assert bindings(parent)==tuple(sorted((*triples,*[(p['file'],p['old'],p['new'])for p in q['publisher_operands']])))
    assert proposal(parent)[0]==raw
    return parent


def load_current_image(path=None):
    raw=(Census.Factory.ROM if path is None else Path(path)).read_bytes()
    if digest(raw)==PIN:return proposal(raw)[0]
    assert digest(raw)==CANDIDATE,'Expected exact1daca or exact Gimmick7 image'
    assert proposal(inverse(raw))[0]==raw
    return raw


if __name__=='__main__':
    raw=load_current_image();print(json.dumps(proposal(inverse(raw))[1],separators=(',',':')),flush=True)
