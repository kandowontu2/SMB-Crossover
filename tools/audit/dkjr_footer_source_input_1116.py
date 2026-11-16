"""Explicit readonly inputs for versioned historical6a3/f544 source fixtures."""
from hashlib import sha256
from pathlib import Path

import compose_dkjr_platform_footer_current_1116 as Footer
import compose_battletoads_mature8_1116 as BT

BT_SHA='6db3aa513aac81d022efdc881b01bdcb93a639ccd4f99e8671fed3f8986bb27c'
H=lambda value:sha256(value).hexdigest()


def normalize(raw,*,kind):
    assert isinstance(raw,bytes)
    actual=H(raw)
    if kind=='exact-6a3':
        assert actual==Footer.Camera.PIN
        reference=raw
    elif kind=='bt91dc-reference-only':
        assert actual==BT.CANDIDATE
        assert H(Path(BT.__file__).read_bytes())==BT_SHA
        assert BT.PIN==Footer.Camera.PIN
        reference=BT.inverse(raw)
        owned=set()
        for at,old,new in BT.spans():
            assert raw[at:at+len(new)]==new and reference[at:at+len(old)]==old
            owned.update(range(at,at+len(old)))
        assert len(owned)==27
        assert all(a==b or i in owned for i,(a,b)in enumerate(zip(raw,reference,strict=True)))
    else:raise ValueError('Explicit exact-6a3 or bt91dc-reference-only kind required')
    assert H(reference)==Footer.Camera.PIN
    return reference,dict(actual_input_SHA256=actual,explicit_kind=kind,
        reference6a3_SHA256=Footer.Camera.PIN,
        CPU_execution_SHA256=Footer.CANDIDATE,
        actual_current91dc_execution_claim=False,BT27_join_composed=False,
        scope='Reconstructed strict historical ancestor for the already leased privatef544 source fixture; no current rebase or preserved-BT candidate')
