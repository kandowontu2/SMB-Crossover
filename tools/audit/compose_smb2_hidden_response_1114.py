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
    parent=Cache.parent_image();_,spans,_=bindings(parent);out=bytearray(raw)
    for at,old,new in spans:
        assert raw[at:at+len(new)]==new;out[at:at+len(old)]=old
    original=bytes(out)
    assert sha256(original).hexdigest()==PIN and proposal(original)[0]==raw
    return original


reverse=inverse


if __name__=='__main__':
    parent=Cache.parent_image();image,q=proposal(parent);assert inverse(image)==parent
    print(json.dumps(q,separators=(',',':')),flush=True)
