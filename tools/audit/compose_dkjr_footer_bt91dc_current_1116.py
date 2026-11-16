"""Strict leased current91dc camera/footer join; in-memory bytes only."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import plan_dkjr_footer_bt91dc_join_root_1116 as Plan

BT,Footer=Plan.BT,Plan.Footer
Camera=Footer.Camera
R=Camera.R
PIN='91dc4ac58ae749bc81f1ef91953c7c3e5aba73dd07e4b6ea2cd3059d1cdb41cc'
CANDIDATE='a3fb2dd448961ca1f7b7abc1c82175f3177da62207271c18ad87819d0dddda1a'
GRANT=R/'docs/qa/allocations/dkjr-footer-bt91dc-join-source-root-1116.json'
GRANT_SHA='fdd6336128691992e75e593c1898dccb044dea14bf89ccb14796d8cd83f86306'
PLAN_SHA='0489d5f32582f26e2511abe7bda0f80bcff0095fc51f18771e2ec57854cdd340'
H=lambda value:sha256(value).hexdigest()


@lru_cache(maxsize=1)
def lease():
    assert H(GRANT.read_bytes())==GRANT_SHA
    assert H(Path(Plan.__file__).read_bytes())==PLAN_SHA
    grant=json.loads(GRANT.read_text())
    assert grant['owning_parent_SHA256']==PIN and grant['candidate_SHA256']==CANDIDATE
    assert grant['source_in_memory_composition_and_mounts_authorized']
    assert not any(grant[k]for k in('physical_ROM_file_writes_authorized','native_Mesen_authorized','Downloads_delivery_authorized'))
    return grant


@lru_cache(maxsize=1)
def spans(parent):
    assert isinstance(parent,bytes)and H(parent)==PIN
    grant=lease();descriptor=Plan.detached(parent);rows=[]
    assert descriptor['proposed_join_SHA256']==CANDIDATE
    for extent,row in zip(grant['spans'],descriptor['spans'],strict=True):
        lo,hi=row['file_half_open'];old,new=bytes.fromhex(row['old_hex']),bytes.fromhex(row['new_hex'])
        assert extent==[lo,hi]and hi-lo==len(old)==len(new)
        assert parent[lo:hi]==old and H(old)==row['old_SHA256']and H(new)==row['new_SHA256']
        rows.append((lo,old,new))
    return tuple(rows)


@lru_cache(maxsize=1)
def proposal(parent):
    assert isinstance(parent,bytes)and H(parent)==PIN
    out=bytearray(parent);owned=set()
    for at,old,new in spans(parent):
        domain=set(range(at,at+len(old)));assert not domain&owned
        owned|=domain;out[at:at+len(old)]=new
    result=bytes(out);changed={i for i,(a,b)in enumerate(zip(parent,result,strict=True))if a!=b}
    assert len(owned)==383 and len(changed)==281 and changed<=owned and H(result)==CANDIDATE
    protected=[]
    for label,at,size in(('BT8192',BT.CACHE,8192),('BT487header-cookie',BT.HEADER,487)):
        assert not owned.intersection(range(at,at+size))and result[at:at+size]==parent[at:at+size]
        protected.append(dict(role=label,offset=at,bytes=size,SHA256=H(result[at:at+size])))
    body=Camera.payload(result);cookie=result[534485:534501]
    assert cookie==bytes.fromhex('a72801')+sha256(body).digest()[:13]
    report=dict(parent_SHA256=PIN,candidate_SHA256=CANDIDATE,grant_SHA256=GRANT_SHA,plan_SHA256=PLAN_SHA,
        owned_bytes=len(owned),changed_bytes=len(changed),spans=[dict(offset=at,bytes=len(a),old_SHA256=H(a),new_SHA256=H(b))for at,a,b in spans(parent)],
        all_unowned_current91dc_exact=True,whole_BT_envelopes=protected,
        packet_SHA256=H(body),cookie=cookie.hex(),source_only=True,CPU_executed=False,ROM_written=False,outputs=0)
    return result,report


def inverse(raw):
    assert isinstance(raw,bytes)and H(raw)==CANDIDATE
    lease();q=Camera.lease();out=bytearray(raw)
    # Restore only the seven granted spans from their pinned source preimages.
    _,labels=Camera.Plan.source_inputs()
    source=Camera.Plan.SOURCE_PATH.read_text().replace('\r\n','\n')
    fragment=source[source.index('DkjrNativeCarryEvent:'):source.index('DkjrNativeLifeReset:')]
    labels['DkCarryPendingTransition']=0xb7bb
    fragment=Camera.Plan.Source.once(fragment,' jsr DkjrFallDistance\n',' jsr DkCarryPendingTransition\n')
    old=Camera.Plan.assemble_fragment(fragment,source,labels)['images']['CARRY']
    assert H(old)==q['code']['old_SHA256']
    lo,hi=q['code']['file_half_open'];assert H(raw[lo:hi])==q['code']['new_SHA256'];out[lo:hi]=old
    out[534485:534501]=bytes.fromhex(q['cookie']['old_hex'])
    import recover_dkjr_current_identity_67_1115 as Identity
    old_native=dict(Identity.PUBLIC_NATIVE)
    for row in Footer.lease()['spans']:
        lo,hi=row['file_half_open'];old=old_native[lo]
        assert H(old)==row['old_SHA256']and H(raw[lo:hi])==row['new_SHA256'];out[lo:hi]=old
    parent=bytes(out);assert H(parent)==PIN
    assert proposal(parent)[0]==raw
    return parent


def historical_reference(raw):
    """Strict metadata/control reference; callers must execute owning raw."""
    parent=inverse(raw);six=BT.inverse(parent)
    camera,_=Camera.proposal(six);historical,_=Footer.proposal(camera)
    assert H(historical)==Footer.CANDIDATE
    return historical
