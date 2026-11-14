"""Granted legitimate hidden upward ceiling response, exact fa66 successor."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import compose_smb2_hidden_head_1114 as Cache
import measure_smb2_hidden_response_1114 as Measure

W,N,R=Cache.W,Cache.N,Cache.R
PIN=Cache.PIN
CANDIDATE='421379021e775e6e03357c0aa11d4cab04008452f94bc9e8938f0662cc0c979f'
GRANT=R/'docs/qa/allocations/smb2-hidden-head-response-1114.json'
GRANT_SHA='5b881c4e1a28152ce9b4a09c61fe1877e40d86bfb1d01b1ce4795e97462e2358'
MEASURE_SHA='b23037cf06875d2107f13331b6dcf9993372af0ebb69104756311f9a75fa6ec3'
SOURCE_SHA='c3dab5f091f69b4af30b3059c08d1387eeb22e4f239816eb6f64c1252031ef16'


@lru_cache(maxsize=1)
def bindings(raw):
    b,oldspans,info=Cache.bindings(raw)
    data=GRANT.read_bytes();assert sha256(data).hexdigest()==GRANT_SHA
    grant=json.loads(data)
    assert grant['resource_grant_SHA256']==Cache.GRANT_SHA
    assert grant['owning_parent_ROM_SHA256']==PIN
    assert sha256(Path(Measure.__file__).read_bytes()).hexdigest()==MEASURE_SHA
    public=Cache.public_image(raw)
    _,source,_,code,_,labels=Measure.recipe(public)
    assert sha256(source.encode()).hexdigest()==SOURCE_SHA==grant['generated_source_SHA256']
    spans=[]
    for name,(at,old,previous)in zip(Cache.SEGMENTS,oldspans,strict=True):
        new=code[name]
        if name=='HIDDEN_RETURN':
            q=grant['replacement'];assert q['file_half_open']==[at,at+len(new)]
            assert old.hex()==q['owning_parent_preimage_hex']and previous.hex()==q['previous_unqualified_helper_hex']
            assert new.hex()==q['allowed_helper_hex']
        else:assert new==previous
        spans.append((at,old,new))
    return b,spans,dict(parent_SHA256=PIN,resource_grant_SHA256=Cache.GRANT_SHA,
        behavior_grant_SHA256=GRANT_SHA,generated_source_SHA256=SOURCE_SHA,
        measurement_tool_SHA256=MEASURE_SHA,outputs=0,Mesen_run=False,native_qualified=False)


def proposal(raw):
    _,spans,info=bindings(raw);out=bytearray(raw);allowed=set()
    for at,old,new in spans:
        assert raw[at:at+len(old)]==old
        out[at:at+len(new)]=new;allowed.update(range(at,at+len(old)))
    image=bytes(out);digest=sha256(image).hexdigest()
    assert digest==CANDIDATE
    assert len(image)==len(raw)
    changes={i for i,(a,b)in enumerate(zip(raw,image,strict=True))if a!=b}
    assert changes<=allowed
    for at,_,new in Cache.Parent.EDITS:assert image[at]==new
    for at,_,new in Cache.Parent.Owner.SPANS:assert image[at:at+len(new)]==new
    return image,dict(**info,ROM_SHA256=digest,changed_bytes=len(changes),
        granted_envelope_bytes=len(allowed),all_unowned_bytes_exact=True,
        repaired_cheat_owner_and_E037_exact=True)


def inverse(raw):
    assert sha256(raw).hexdigest()==CANDIDATE
    # Recover the exact retained probe from its owning assembly; inverse may
    # be called after this candidate becomes Downloads. No mutable nightly
    # image is an inverse dependency.
    resource=Cache.GRANT.read_bytes();assert sha256(resource).hexdigest()==Cache.GRANT_SHA
    grant=json.loads(resource)
    _,owned,_=Cache.Measure.Route.Current.Flag.source_recipe(raw)
    probe=owned['probe']
    assert len(probe)==174 and sha256(probe).hexdigest()==grant['spans'][0]['preimage_SHA256']
    out=bytearray(raw)
    for index,q in enumerate(grant['spans']):
        at,end=q['file_half_open'];old=probe if index==0 else bytes.fromhex(q['preimage_hex'])
        assert len(old)==end-at==q['bytes'];out[at:end]=old
    original=bytes(out);assert sha256(original).hexdigest()==PIN
    _,spans,_=bindings(original)
    for at,old,new in spans:
        assert raw[at:at+len(new)]==new
    assert proposal(original)[0]==raw
    return original


reverse=inverse


def load_current_image(path=None):
    """Explicit CLI boundary: only delivered fa66 or this exact successor."""
    path=Cache.Parent.Owner.D.C.Owner.NIGHTLY if path is None else Path(path)
    raw=path.read_bytes();digest=sha256(raw).hexdigest()
    if digest==PIN:return proposal(raw)[0]
    assert digest==CANDIDATE,'Current input must be exact fa66 or421379'
    assert proposal(inverse(raw))[0]==raw
    return raw


if __name__=='__main__':
    image=load_current_image();parent=inverse(image);_,q=proposal(parent)
    print(json.dumps(q,separators=(',',':')),flush=True)
