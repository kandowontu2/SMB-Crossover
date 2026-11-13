"""In-memory refactor trial for the Ladder funding; no equipment enabled."""

from hashlib import sha256

import karnov_equipment_1113 as Audit

Bomb,Scene=Audit.Bomb,Audit.Scene
OLD_COOKIE=bytes.fromhex('a7070112fd9d8e091d29e8be18360c27')
SOURCE_HASH='de34c6db8c92a61b59eaf0ef66c5d96ef309e525cf64cd33a6ee0f411611ab10'
COMPACT_HASH='59e57a8503d42834fc88a12f8755650c177ffe2f1192c5a60a4efd6a05043592'
ISLANDS=dict(ACTOR_CORE=(0xa087,0xac06),WEAPON_CORE=(0xac06,0xafa4),CLEAR_CORE=(0xafa4,0xafbb))


def digest(data):return sha256(data).hexdigest()


def original_binding(raw):
    parent=Scene.inverse(raw)
    assert Scene.transform(parent)[0]==raw
    assert raw[Scene.RESIDENT:Scene.RESIDENT+16]==OLD_COOKIE
    assert raw[Scene.ACTOR+0x1fe0:Scene.ACTOR+0x1ff0]==OLD_COOKIE and raw.count(OLD_COOKIE)==2


def trial(raw):
    original_binding(raw)
    old,base=Audit.relink_core(raw)
    code,report=Audit.relink_core(raw,compact=True)
    assert base['source_SHA256']==SOURCE_HASH and report['source_SHA256']==COMPACT_HASH
    result=bytearray(raw)
    for segment,(lo,hi)in ISLANDS.items():
        at=Scene.ACTOR+lo-0xa000
        assert raw[at:at+hi-lo]==old['images'][segment]
        result[at:at+hi-lo]=code['images'][segment].ljust(hi-lo,b'\xea')
    # No Ladder routine occupies the recovered tails in this refactor trial.
    before=result[Scene.ACTOR:Scene.ACTOR+8192]
    cookie=bytes.fromhex('a7070113')+sha256(b'Karnov source branch islands 1113\0'+OLD_COOKIE+before).digest()[:12]
    for at in(Scene.RESIDENT,Scene.ACTOR+0x1fe0):result[at:at+16]=cookie
    image=bytes(result)
    allowed=set(range(Scene.ACTOR+0x87,Scene.ACTOR+0xfbb))|set(range(Scene.ACTOR+0x1fe0,Scene.ACTOR+0x1ff0))|set(range(Scene.RESIDENT,Scene.RESIDENT+16))
    assert all(a==b or i in allowed for i,(a,b)in enumerate(zip(raw,image)))
    assert raw[Scene.ACTOR:Scene.ACTOR+0x87]==image[Scene.ACTOR:Scene.ACTOR+0x87]
    return image,dict(parent_SHA256=digest(raw),trial_SHA256=digest(image),cookie=cookie,
        actor_SHA256=digest(image[Scene.ACTOR:Scene.ACTOR+8192]),
        no_equipment_enabled=True,no_new_code_allocation=True,allocation_qualified=False,
        recovered_unused_bytes=624,code=code,baseline=old,source=report)


def inverse(raw):
    assert len(raw)==2097168
    cookie=raw[Scene.RESIDENT:Scene.RESIDENT+16]
    assert cookie[:4]==bytes.fromhex('a7070113')and raw.count(cookie)==2
    old,base=Audit.relink_core(raw,verify_baseline=False)
    code,report=Audit.relink_core(raw,compact=True,verify_baseline=False)
    assert base['source_SHA256']==SOURCE_HASH and report['source_SHA256']==COMPACT_HASH
    result=bytearray(raw)
    for segment,(lo,hi)in ISLANDS.items():
        at=Scene.ACTOR+lo-0xa000
        assert raw[at:at+hi-lo]==code['images'][segment].ljust(hi-lo,b'\xea')
        result[at:at+hi-lo]=old['images'][segment]
    for at in(Scene.RESIDENT,Scene.ACTOR+0x1fe0):result[at:at+16]=OLD_COOKIE
    parent=bytes(result);original_binding(parent)
    assert trial(parent)[0]==raw
    return parent


if __name__=='__main__':
    import json
    raw,_=Audit.inputs();image,report=trial(raw)
    assert inverse(image)==raw
    print(json.dumps({k:v.hex()if isinstance(v,bytes)else v for k,v in report.items()if k not in('code','baseline')},separators=(',',':')),flush=True)
