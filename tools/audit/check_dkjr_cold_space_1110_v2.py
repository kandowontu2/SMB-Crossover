"""Verify the 102-byte private DK cold leaf, derivative of the 105-byte proof."""
from hashlib import sha256
import json

import check_dkjr_cold_space_1110 as V1


SOURCE = V1.SOURCE.with_name('dkjr_cold_compact_1110_v2.s')


def main():
    raw = V1.Gap.NIGHTLY.read_bytes()
    digest = sha256(raw).hexdigest()
    assert digest in (V1.Gap.PIN,V1.Gap.SECOND)
    carrier = 1048592+960*1024
    old = raw[carrier+V1.START-0xd000:carrier+V1.END-0xd000]
    assert sha256(old).hexdigest()==V1.PREIMAGE
    linked = V1.assemble(SOURCE.read_text(encoding='utf-8'),{'DK_COLD':(V1.START,V1.END-V1.START)})
    new = linked['images']['DK_COLD']
    assert len(new)==102 and linked['symbols']['DkColdEnd']==0xd2c4
    assert sha256(new).hexdigest()=='c47ddf12e6df4f8abf189ab9c78c58ffdcd5f80c3ade8e610f51d977f45889d7'
    seed = V1.C.cold(raw,raw[534485:534501])
    witnesses = []
    for fault in (None,1027,2050,16400):
        before,after = [V1.invoke(seed,worker,fault) for worker in (old,new)]
        assert before[:-1]==after[:-1]
        assert bool(after[0][3]&1)==(fault is None)
        witnesses.append(dict(fault=fault,reads=after[1],regs=after[0],mapper_writes=len(after[4]),
                              steps=[before[-1],after[-1]]))
    assert witnesses[0]['reads']==16400 and witnesses[0]['mapper_writes']==80
    print(json.dumps(dict(image_SHA256=digest,old_bytes=len(old),new_bytes=len(new),
                          assembled_SHA256=sha256(new).hexdigest(),free=[0xd2c4,V1.END],
                          witnesses=witnesses),separators=(',',':')),flush=True)


if __name__=='__main__':
    main()
