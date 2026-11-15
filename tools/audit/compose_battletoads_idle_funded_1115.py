"""Strict source-only 7a80 funded-idle composition; bytes stay in memory."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json

import research_battletoads_idle_funding_1115 as Packet

R=Path(__file__).resolve().parents[2]
PIN='7a80f0f37e316436be0825bbd6fd9d372af6b0b7741f84ea87356282033d9b79'
CANDIDATE='a90cf06bdad6778a5b01927af5bfe175fcf5dd391f52d4f8877ce622628bdde9'
GRANT=R/'docs/qa/allocations/battletoads-idle-funded-source-1115.json'
GRANT_SHA='676a61814f6571eada48a51f3ac350702e45d7248eb7a90817354d554e8f00d0'
PACKET_SHA='c43361c1d8e0e9c2f88748686170f5b73a012df83f4fc3ee2927e82a5d3d6c47'
ARRAY_SHA='295e9408740ad58b4a36ccd558b0a72806cebf14461d3a88cc34f0317c6adb9a'
PREIMAGES=(
 (244078,'54'),(653403,'ade55f2944c940d005'),(653438,'c922b00a'),
 (653451,'3c'),(653485,'d8b8'),(653491,'68b9'),(653495,'f8b9'),(653501,'26ba'),
 (653512,
 'a9b08d6d01a9d78d6201c0249002a024988d6c010a6d6c0169208d6c014cb2b8'
 '21a5325f7ecbea04ac37c66347767919e316f9ef096537932385a40b668fe2b06f9903dbf3b4c1d48920184d61736b080b64e665671688f1cd8d8da0acd4e10b66818fb0e70489e9217158ea407e7a85ac3cc6904776792ac316c508c4f91a3b688573a966f89aa96f9903e01a1c329057fe69568e39c61d47767991f71640efae65a77d00855872669699726f9939db'
 '00010200000000030004030301010506070607080808080803090a0b0c0d040e0f1002111213131314151515151516151414161314061313170707071512130b0c15150e17181419001a1a1b1c1a1a1a001d031a0101051e1f061e1e1a1a202020091e200c1e1e200f100220212202232425212626210326010105272806290825082a2a2a092b2c0c2d292c0f102411'
 'a5b8b9a7a8aeb7a3a6a4baa1a6aaa4afb2b9babdbdbebcbabfbebcbeb1b9bfb6bdb9bbbeaebcbab8b5bcb5b7adbbe0cecee0e0dabefce0bfbed6c7cdfcc88ac2a4a4c1a4c1cfa4c1d6d69ad6d6c2d6dfdfdff9dfdfdfdff9f9dff9f9'
 '0848ad026048babd02018d6a01a9768d6c01a9be8d6d01a9d1205a01c91af008c91cf01e684cc7ba68c91af0468d6a01a9138d6c01a9be8d6d01a998205a014cc7ba68c91cd00ead0b73299ff0078d6a01a95dd0058d6a01a9fd088d6c010a9002a9b98d6d0128a9a4205a01eaeaeaeaeaeaea6828ad026060'),
)


def digest(raw):return sha256(raw).hexdigest()


@lru_cache(maxsize=1)
def lease():
    assert digest(GRANT.read_bytes())==GRANT_SHA,'Source lease changed'
    assert digest(Path(Packet.__file__).read_bytes())==PACKET_SHA,'Frozen packet changed'
    q=json.loads(GRANT.read_text())
    assert q['input_SHA256']==PIN and q['source_overlay_in_memory_authorized']
    assert not q['ROM_file_writes_authorized'] and not q['native_Mesen_authorized']
    assert [(at,len(bytes.fromhex(h)))for at,h in PREIMAGES]==[tuple(z)for z in q['exact_envelopes']]
    assert sum(len(bytes.fromhex(h))for _,h in PREIMAGES)==556
    assert len(bytes.fromhex(PREIMAGES[-1][1]))==533
    assert digest(bytes.fromhex(PREIMAGES[-1][1]))=='4eff5ba5a865ecc4e2924581b458afecd82690c5c2e929b83e07905c50c00c37'
    return q


@lru_cache(maxsize=2)
def proposal(raw):
    """Accept only exact current parent; source-model lease is not staging permission."""
    lease();assert digest(raw)==PIN,'Expected exact 7a80 parent'
    q=Packet.final_proposal(raw)
    assert q['framed_array_SHA256']==ARRAY_SHA and q['total_owned_bytes']==556 and q['actual_changed_bytes']==535
    rows=q['exact_detached_envelopes'];image=bytearray(raw);owned=set()
    for row,(at,old_hex)in zip(rows,PREIMAGES,strict=True):
        old,new=bytes.fromhex(old_hex),bytes.fromhex(row['new_hex'])
        assert row['file']==[at,at+len(old)] and row['old_hex']==old_hex and len(old)==len(new)
        assert raw[at:at+len(old)]==old
        image[at:at+len(old)]=new;owned.update(range(at,at+len(old)))
    image=bytes(image)
    changed={i for i,(a,z)in enumerate(zip(raw,image,strict=True))if a!=z}
    assert len(changed)==535 and changed<=owned and len(owned)==556
    assert digest(image)==CANDIDATE
    return image,dict(parent_SHA256=PIN,candidate_SHA256=digest(image),source_lease_SHA256=GRANT_SHA,
        packet_SHA256=PACKET_SHA,framed_array_SHA256=ARRAY_SHA,envelopes=[dict(file=row['file'],old_SHA256=row['old_SHA256'],new_SHA256=row['new_SHA256'])for row in rows],
        owned_bytes=556,actual_changes=535,all_unowned_bytes_exact=True,
        cache_cookie_full_BtCheck_score_Prince_Gimmick_bytes_preserved=True,
        source_only=True,ROM_file_written=False,native_or_delivery_authorized=False)


@lru_cache(maxsize=2)
def inverse(raw):
    """Portable exact inverse, with source preimages and no mutable-ROM read."""
    lease();assert digest(raw)==CANDIDATE,'Expected exact funded source image'
    old=bytearray(raw)
    for at,h in PREIMAGES:
        block=bytes.fromhex(h);old[at:at+len(block)]=block
    old=bytes(old);assert digest(old)==PIN,'Unowned or dirty bytes in source image'
    rebuilt,_=proposal(old);assert rebuilt==raw,'Source-bound roundtrip failed'
    return old


def load_current_image():
    raw=Packet.Frozen.ROM.read_bytes();assert digest(raw)==PIN,'Expected exact installed 7a80'
    return raw


def main():
    raw=load_current_image();image,q=proposal(raw)
    assert inverse(image)==raw
    print(json.dumps(q,sort_keys=True))


if __name__=='__main__':main()
