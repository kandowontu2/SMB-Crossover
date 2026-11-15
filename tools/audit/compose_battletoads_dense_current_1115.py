"""Strict current40a eleven-span source composition, in memory only."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
import compose_battletoads_idle_funded_1115 as Prior
import plan_battletoads_dense_resolver_1115 as Dense

R=Path(__file__).resolve().parents[2]
ROM=Prior.Packet.Frozen.ROM
PIN='40a11ffb8452c3b54caef56ddd5912e2bdda2c276545f20a589baa053de4d20e'
CANDIDATE='5b28a14cc135517a58a4dff840b4e3c6896e79547577b3c0ce083a1bc85b878d'
GRANT=R/'docs/qa/allocations/battletoads-dense-current-source-1115.json'
GRANT_SHA='368b5651844b65e930b116a3796cc654850bbe6a6965553009e6a3418e20cd03'
DENSE_SHA='04d2397ee37917ee62ecf4f8ac8b8181ddcb88bb5ca26196ec5353d45f86b7c0'
PRIOR_SHA='2ecaff26b204a7969878f18775369806a9ec3ed267d6f41c8e4fcf691f069856'
PRINCE_SHA='6d2cbeb8bcf6b9a32d85c08ef158bb4dbe67e890831bbdb8dd203359e61b1afc'
PREIMAGES=(
 (244078,'54'),(653403,'ade55f2944c940d005'),(653438,'c922b00a'),
 (653451,'3c'),(653485,'d8b8'),(653491,'68b9'),(653495,'f8b9'),(653501,'26ba'),
 (653512,
 'a9b08d6d01a9d78d6201c0249002a024988d6c010a6d6c0169208d6c014cb2b8'
 '21a5325f7ecbea04ac37c66347767919e316f9ef096537932385a40b668fe2b06f9903dbf3b4c1d48920184d61736b080b64e665671688f1cd8d8da0acd4e10b66818fb0e70489e9217158ea407e7a85ac3cc6904776792ac316c508c4f91a3b688573a966f89aa96f9903e01a1c329057fe69568e39c61d47767991f71640efae65a77d00855872669699726f9939db'
 '00010200000000030004030301010506070607080808080803090a0b0c0d040e0f1002111213131314151515151516151414161314061313170707071512130b0c15150e17181419001a1a1b1c1a1a1a001d031a0101051e1f061e1e1a1a202020091e200c1e1e200f100220212202232425212626210326010105272806290825082a2a2a092b2c0c2d292c0f102411'
 'a5b8b9a7a8aeb7a3a6a4baa1a6aaa4afb2b9babdbdbebcbabfbebcbeb1b9bfb6bdb9bbbeaebcbab8b5bcb5b7adbbe0cecee0e0dabefce0bfbed6c7cdfcc88ac2a4a4c1a4c1cfa4c1d6d69ad6d6c2d6dfdfdff9dfdfdfdff9f9dff9f9'
 '0848ad026048babd02018d6a01a9768d6c01a9be8d6d01a9d1205a01c91af008c91cf01e684cc7ba68c91af0468d6a01a9138d6c01a9be8d6d01a998205a014cc7ba68c91cd00ead0b73299ff0078d6a01a95dd0058d6a01a9fd088d6c010a9002a9b98d6d0128a9a4205a01eaeaeaeaeaeaea6828ad026060'),
 (716848,'4c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb0186008488a489848ad026038e91bc907b0572901d053ad6c0138e920aaad0260c921d0218a29b3c913f03ee033f008e04ed012a991d002a9118d6c01a9b08d6d01a9c8d0158a8d6a01a99d8d6c01a9b78d6d01a9e0205a01900f8d620168a868aa688d6a01284c5d0168a868aa688d6a01281860'),
 (792489,'1860386048ad0260c91df014688d6a01a92b8d6c01a9b28d6d01a9c3205a0160ade85f2907c906b01768c96cb013a8b9dcb78d6c01b9ddb78d6d01b9deb73860681860e6b2e0f1b3e047b5e099b7e099b7e013a1bbdba68699b7e03aaf889bb7e08795fe99b7e099b7e099b7e08b95fee8b6e0c3b6c246b6e0a0bbccefa6e099b7e099b7e099b7e0dba7fc71af8399b7e081b6e099b7e0f0e1ff99b7e033b7e099b7e0e7bacf99b28a99b7e099b7e0'),
)


def digest(raw):return sha256(raw).hexdigest()


@lru_cache(maxsize=1)
def lease():
    assert digest(GRANT.read_bytes())==GRANT_SHA
    assert digest(Path(Prior.__file__).read_bytes())==PRIOR_SHA
    assert digest(Path(Dense.__file__).read_bytes())==DENSE_SHA
    assert digest((R/'tools/audit/plan_battletoads_flat_resolver_1115.py').read_bytes())=='d27a42a2a61401c738f8ec97101cdd411d3ac34627a65dc9d6604aba40cb542e'
    q=json.loads(GRANT.read_text())
    assert q['owning_parent_SHA256']==PIN and q['source_in_memory_composition_and_mounts_authorized']
    assert not any(q[n]for n in('physical_ROM_file_writes_authorized','native_Mesen_authorized','Downloads_delivery_authorized'))
    assert [(at,len(bytes.fromhex(h)))for at,h in PREIMAGES]==[tuple(x)for x in q['envelopes']]
    assert PREIMAGES[:9]==Prior.PREIMAGES and sum(len(bytes.fromhex(h))for _,h in PREIMAGES)==955
    return q


@lru_cache(maxsize=1)
def reference_parent(raw):
    lease();assert isinstance(raw,bytes)and digest(raw)==PIN,'Expected exact official40a'
    import compose_prince_sword_tier2_fresh_1115 as Prince
    assert digest(Path(Prince.__file__).read_bytes())==PRINCE_SHA
    parent=Prince.inverse(raw);assert digest(parent)==Prior.PIN
    return parent


@lru_cache(maxsize=1)
def reference(raw):
    parent=reference_parent(raw);image,_=Prior.proposal(parent)
    assert Prior.inverse(image)==parent and digest(image)==Prior.CANDIDATE
    return image


@lru_cache(maxsize=1)
def proposal(raw):
    q=lease();oldparent=reference_parent(raw);oldref=reference(raw)
    dense=Dense.shapes(oldparent,oldref)['detached_envelopes']
    assert [(x['file'],x['old_SHA256'],x['new_SHA256'])for x in dense]==[(x['file_half_open'],x['old'],x['new'])for x in q['dense_span_hashes']]
    newrows=[oldref[at:at+len(bytes.fromhex(h))]for at,h in PREIMAGES[:9]]+[bytes.fromhex(x['new_hex'])for x in dense]
    image=bytearray(raw);owned=set();rows=[]
    for(at,h),new in zip(PREIMAGES,newrows,strict=True):
        old=bytes.fromhex(h);assert raw[at:at+len(old)]==old and len(old)==len(new)
        assert not owned.intersection(range(at,at+len(old)));owned.update(range(at,at+len(old)))
        image[at:at+len(old)]=new
        rows.append(dict(file=[at,at+len(old)],old_SHA256=digest(old),new_SHA256=digest(new),changed=sum(a!=b for a,b in zip(old,new,strict=True))))
    image=bytes(image);changes={i for i,(a,b)in enumerate(zip(raw,image,strict=True))if a!=b}
    assert len(owned)==955 and len(changes)==716 and changes<=owned
    if CANDIDATE is not None:assert digest(image)==CANDIDATE
    return image,dict(parent_SHA256=PIN,candidate_SHA256=digest(image),grant_SHA256=GRANT_SHA,eleven_spans=rows,
        owned_bytes=955,changed_bytes=716,all_unowned_bytes_exact=True,
        actual40a_Prince_carriers_cookie_Gimmick_score_BT_cache_cookie_full_Check_preserved=True,
        binding_reference_only=Prior.CANDIDATE,source_only=True,physical_ROM_written=False,native_run=False,outputs=0)


@lru_cache(maxsize=1)
def inverse(raw):
    lease();assert CANDIDATE is not None and isinstance(raw,bytes)and digest(raw)==CANDIDATE,'Expected exact current dense source candidate'
    parent=bytearray(raw)
    for at,h in PREIMAGES:
        old=bytes.fromhex(h);parent[at:at+len(old)]=old
    parent=bytes(parent);assert digest(parent)==PIN,'Dirty unowned bytes in dense source image'
    assert proposal(parent)[0]==raw,'Source-bound portable roundtrip'
    return parent


def load_current_image():
    raw=ROM.read_bytes()
    assert digest(raw)in(PIN,CANDIDATE),'Expected exact current40a or exact dense source candidate'
    if digest(raw)==CANDIDATE:inverse(raw)
    return raw


if __name__=='__main__':
    raw=load_current_image();parent=inverse(raw)if digest(raw)==CANDIDATE else raw
    image,q=proposal(parent)
    if CANDIDATE is not None:q['portable_inverse_exact40a']=inverse(image)==parent
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)

