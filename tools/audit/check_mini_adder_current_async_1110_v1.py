"""Rebind the qualified Mini collision interrupt checks to the current nightly."""

import argparse
import hashlib
import json
from pathlib import Path

from check_mini_native_collision_routes_async_1109_v1 import check
from check_mini_native_side_single_map_1109_v1 import R, sha


BASE=R/'build/mini-contact-render-typed-1109/candidate.nes'
PIN='84d372ef9b6cea58918454fbea0ab2f5433fe051bd17c99fd86cc8e94a6da3aa'
CANDIDATE='d7a91c05b27d080e89ff60c0e1420e23eb07d762a386ff6a28a81117d8d87c3c'
PRIOR=R/'build/mini-native-side-single-map-1109'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--candidate',type=Path)
    args=parser.parse_args()
    raw=BASE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==PIN
    receipt_paths=[PRIOR/name for name in ('proof.json','head-proof.json','adder-proof.json','adder-async-proof.json')]
    side,head,adder,old_irq=(json.loads(path.read_text()) for path in receipt_paths)
    assert all(q['passed'] for q in (side,head,adder,old_irq))
    assert old_irq['include_adder'] and adder['parent_SHA256']==side['expected_memory_only_SHA256']

    image=bytearray(raw)
    for q in (side,head,adder):
        for patch in q['patches']:
            site=patch['file_offset']
            before=bytes.fromhex(patch['old_hex'])
            after=bytes.fromhex(patch['new_hex'])
            assert len(before)==len(after)
            expected=before if q is adder else after
            assert raw[site:site+len(expected)]==expected,patch
            if q is adder:
                image[site:site+len(after)]=after
    digest=hashlib.sha256(image).hexdigest()
    assert digest==CANDIDATE
    if args.candidate:
        assert args.candidate.read_bytes()==image

    results=check(bytes(image),head=True,adder=True)
    sources=[Path(__file__),R/'tools/audit/check_mini_native_collision_routes_async_1109_v1.py',
             R/'tools/audit/check_mini_native_collision_adder_1109_v1.py',
             R/'tools/audit/check_mini_lift_admission_async_1108_v1.py',
             R/'tools/audit/check_mini_floor_pair_fast_1108_v1.py',
             R/'tools/reference/mini_native_collision_adder_1109_v1.s',BASE,*receipt_paths]
    if args.candidate:
        sources.append(args.candidate.resolve())
    output=args.output.resolve()
    output.mkdir(exist_ok=True)
    q=dict(passed=True,source_CPU_only=True,ROM_written=False,parent_SHA256=PIN,
           memory_only_SHA256=digest,exact_disk_candidate=bool(args.candidate),
           patches=adder['patches'],**results,bindings={str(path):sha(path) for path in sources})
    (output/'irq.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items() if k not in ('bindings','patches')}))


if __name__=='__main__':
    main()
