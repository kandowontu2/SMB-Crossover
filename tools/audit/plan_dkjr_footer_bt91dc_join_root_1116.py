"""Detached current-nightly DK Jr join descriptor; no new image or CPU mount."""
from hashlib import sha256
import json
from pathlib import Path

import compose_battletoads_mature8_1116 as BT
import compose_dkjr_platform_footer_current_1116 as Footer

H=lambda value:sha256(value).hexdigest()
PINS={BT:'6db3aa513aac81d022efdc881b01bdcb93a639ccd4f99e8671fed3f8986bb27c',
    Footer:'6692bf58e2189dde8289a094d3d816352cb5a67e43f3f18ae3259f9ee53b7a47',
    Footer.Camera:'9776402784a0b199b3055a75ab10a6f01cd382094d13d736a46ac7ee453fa5b3'}


def detached(actual):
    assert isinstance(actual,bytes) and H(actual)==BT.CANDIDATE
    for module,pin in PINS.items():assert H(Path(module.__file__).read_bytes())==pin
    historical=BT.inverse(actual)
    camera,camera_report=Footer.Camera.proposal(historical)
    assert Footer.Camera.inverse(camera)==historical
    oldrows=Footer.Camera.spans(historical)+Footer.spans(camera)
    rows=sorted(oldrows,key=lambda q:q[0]);bt_owned=set();owned=set();changed=0
    for at,old,new in BT.spans():
        assert actual[at:at+len(new)]==new
        bt_owned.update(range(at,at+len(new)))
    digest=sha256();end=0;spans=[]
    for at,old,new in rows:
        assert at>=end and len(old)==len(new) and actual[at:at+len(old)]==old
        indexes=set(range(at,at+len(old)))
        assert not indexes&owned and not indexes&bt_owned
        owned|=indexes
        digest.update(actual[end:at]);digest.update(new);end=at+len(new)
        n=sum(a!=b for a,b in zip(old,new,strict=True));changed+=n
        spans.append(dict(file_half_open=[at,end],bytes=len(old),changed_bytes=n,
            old_SHA256=H(old),new_SHA256=H(new),old_hex=old.hex(),new_hex=new.hex()))
    digest.update(actual[end:])
    assert len(owned)==383 and changed==281 and len(bt_owned)==27
    # Entire updated BT payload and native-header/cookie envelope stay outside
    # this proposal, not only the 27 bytes that changed in its last delivery.
    protected=[('BT private payload',BT.CACHE,8192),('BT native header and full cookie',BT.HEADER,487)]
    protected_rows=[]
    for label,at,size in protected:
        assert not owned.intersection(range(at,at+size))
        protected_rows.append(dict(role=label,file_half_open=[at,at+size],SHA256=H(actual[at:at+size])))
    return dict(parent_SHA256=BT.CANDIDATE,historical_reference_SHA256=BT.PIN,
        historical_camera_SHA256=camera_report['candidate_SHA256'],historical_footer_SHA256=Footer.CANDIDATE,
        proposed_join_SHA256=digest.hexdigest(),ROM_bytes=len(actual),owned_bytes=len(owned),changed_bytes=changed,
        BT27_disjoint=True,complete_BT_envelopes_untouched=protected_rows,spans=spans,
        dependency_SHA256={Path(k.__file__).name:v for k,v in PINS.items()},
        scope='Detached hash streaming only. Historical leased camera composition supplies exact span preimages; no new current-nightly image composed or mounted.',
        current_join_image_composed=False,new_code_executed=False,ROM_file_written=False,native_Mesen=False,
        source_mount_grant_required=True,physical_native_delivery_authorized=False,outputs=0)


if __name__=='__main__':
    report=detached(BT.ROM.read_bytes())
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_BT_JOIN_PLAN '+encoded,flush=True)
    print('DKJR_BT_JOIN_PLAN_SHA256 '+H(encoded.encode()),flush=True)
