"""Granted hidden-head source successor over repaired fa66; memory only."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import compose_smb2_cheat_cold_mirror_1113 as Parent
import measure_smb2_hidden_head_split_1113 as Measure

R=Path(__file__).resolve().parents[2]
W,N=Parent.W,Parent.N
PIN=Parent.CANDIDATE
CANDIDATE='1dda056e8717f7168a3cb85a0f086ee8460e791773f2dbfd0562d3998a47d06e'
GRANT=R/'docs/qa/allocations/smb2-hidden-head-1113.json'
GRANT_SHA='fc69deed91f0d5c3aa09345733d8052e80dba4a4a6acd0e25e31c7a56d24b67f'
MEASURE_SHA='39ff7854976e7ed81d66042d1aeb6b35b9b547552d3ede684c342389cc45b353'
SOURCE_SHA='5302cab40bdc908174b0ae52be9f10e8f09b9940750d28d051d1e852818b12a1'
SEGMENTS=('S2_FLAG_PROBE','HIDDEN_PREDICATE','HIDDEN_VY','HIDDEN_RETURN')


@lru_cache(maxsize=1)
def parent_image(public=None):
    if public is None:public=Parent.Owner.D.C.Owner.NIGHTLY.read_bytes()
    digest=sha256(public).hexdigest()
    if digest==PIN:return public
    assert digest==Measure.Route.PIN,'Only public12397 or repairedfa66 is accepted'
    owner,_=Parent.Owner.proposal(public)
    return Parent.proposal(owner)[0]


@lru_cache(maxsize=1)
def public_image(raw):
    assert sha256(raw).hexdigest()==PIN
    public=Parent.Owner.inverse(Parent.inverse(raw))
    assert sha256(public).hexdigest()==Measure.Route.PIN
    return public


@lru_cache(maxsize=1)
def bindings(raw):
    public=public_image(raw)
    grant=GRANT.read_bytes();assert sha256(grant).hexdigest()==GRANT_SHA
    g=json.loads(grant)
    assert g['parent_ROM_SHA256']==Measure.Route.PIN
    assert sha256(Path(Measure.__file__).read_bytes()).hexdigest()==MEASURE_SHA
    b,source,old,code,labels,newlabels=Measure.recipe(public)
    assert sha256(source.encode()).hexdigest()==SOURCE_SHA
    spans=[]
    for name,q in zip(SEGMENTS,g['spans'],strict=True):
        lo,hi=q['file_half_open'];pc,end=q['CPU_half_open']
        assert pc==Measure.ORIGINS[name]and end-pc==hi-lo==len(code[name])==q['bytes']
        before=public[lo:hi]
        assert raw[lo:hi]==before
        if 'preimage_hex'in q:assert before.hex()==q['preimage_hex']
        if 'preimage_SHA256'in q:assert sha256(before).hexdigest()==q['preimage_SHA256']
        if 'replacement_hex'in q:assert code[name].hex()==q['replacement_hex']
        spans.append((lo,before,code[name]))
    assert spans[0][1]==old
    moved={n:[labels[n],newlabels[n]]for n in labels if n in newlabels and labels[n]!=newlabels[n]}
    assert moved==g['allowed_internal_relocations']
    assert newlabels['S2FlagProbe']==0xb128 and newlabels['S2FlagSharedReturn']==0xb1d5
    return b,spans,dict(grant_SHA256=GRANT_SHA,generated_source_SHA256=SOURCE_SHA,
        measurement_tool_SHA256=MEASURE_SHA,relocated_internal_labels=moved,
        parent_SHA256=PIN,reference_public_SHA256=Measure.Route.PIN,
        spans=[dict(file=at,bytes=len(old),preimage_SHA256=sha256(old).hexdigest(),
                    replacement_SHA256=sha256(new).hexdigest())for at,old,new in spans],
        source_RAM_CHR_geometry_helper_bytes=0,outputs=0,Mesen_run=False,native_qualified=False)


def proposal(raw):
    _,spans,info=bindings(raw);out=bytearray(raw)
    allowed=set()
    for at,old,new in spans:
        assert raw[at:at+len(old)]==old
        out[at:at+len(new)]=new;allowed.update(range(at,at+len(old)))
    image=bytes(out);digest=sha256(image).hexdigest()
    assert len(image)==len(raw)
    changes={i for i,(a,b)in enumerate(zip(raw,image,strict=True))if a!=b}
    assert changes<=allowed
    assert digest==CANDIDATE
    # Explicitly retain every cheat-owner and E037 correction. No composition
    # from the old public image can silently replace those bytes.
    for at,_,new in Parent.EDITS:assert image[at]==new
    for at,_,new in Parent.Owner.SPANS:assert image[at:at+len(new)]==new
    return image,dict(**info,ROM_SHA256=digest,changed_bytes=len(changes),
        granted_envelope_bytes=len(allowed),all_unowned_bytes_exact=True,
        repaired_cheat_owner_and_E037_exact=True)


def inverse(raw):
    assert sha256(raw).hexdigest()==CANDIDATE
    public_parent=parent_image();_,spans,_=bindings(public_parent)
    out=bytearray(raw)
    for at,old,new in spans:
        assert raw[at:at+len(new)]==new;out[at:at+len(old)]=old
    parent=bytes(out)
    assert sha256(parent).hexdigest()==PIN and proposal(parent)[0]==raw
    return parent


reverse=inverse


if __name__=='__main__':
    raw=parent_image();image,q=proposal(raw);assert inverse(image)==raw
    print(json.dumps(q,separators=(',',':')),flush=True)
