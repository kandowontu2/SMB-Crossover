"""Independent read-only ceiling hook/funding review; no successor CPU."""
from pathlib import Path
from hashlib import sha256
import json
import plan_sonic_ceiling_hold_cancel_1327_1116 as P
import audit_sonic_metadata_tail_root_1116 as Tail


def review(raw):
    assert P.H(Path(P.__file__).read_bytes()) == 'dcd6c04b09fc5e5052088d67fd12273788bde250a91a0367d6aed6ce0f381aa3'
    assert P.H(Path(Tail.__file__).read_bytes()) == '4db00b7eb423439bd331c1cbc6f975e877e3e970a5dfba6d52bbd3d9b9cdfe1b'
    capacity = Tail.review(raw)
    d = P.descriptor(raw)
    assert d['receipt_SHA256'] == '94bbe428efd3ee02efd10a688cdcaf30e93392798524a0b0e6dc3f03fc261e89'
    assert (d['owned_bytes'], d['changed_bytes']) == (94, 91)
    assert d['predicted_candidate_SHA256'] == 'a2d9d1218504dedf186cfe352ee4c927160529af4f8d09fe6e2aafccfae477c7'
    page = lambda n: raw[P.CHR+n*1024:P.CHR+(n+1)*1024]
    kernel = b''.join(page(n) for n in (*range(321, 328), 330))
    meta = page(328)
    assert meta[0x86:0x95] == bytes.fromhex('adb6c0c904d032a9018d22c1ad04c1')
    assert d['new_hook_hex'] == '2071d3' and d['helper_hex'] == '8d22c1a9008d58c0a90160'
    assert bytes.fromhex(d['physical_spans'][2]['new_hex'])[:45] == P.Previous.HELPER
    assert (d['JumpTimer_existing'], d['HeadPending_existing']) == (0xc058, 0xc122)
    domains = ((3, 0xa000, kernel), (2, 0xd000, meta),
               (2, 0xd400, page(333)), (2, 0xd800, page(334)))
    hook_controls, writers = [], []
    direct = {0x8d, 0x8e, 0x8c, 0xee, 0xce, 0x0e, 0x4e, 0x2e, 0x6e}
    indexed = {0x9d, 0x99, 0xfe, 0xde, 0x1e, 0x5e, 0x3e, 0x7e}
    for bank, base, data in domains:
        for i in range(len(data)-2):
            op = data[i]
            at = int.from_bytes(data[i+1:i+3], 'little')
            if op in (0x20, 0x4c, 0x6c) and 0xd08f <= at < 0xd092:
                hook_controls.append((bank, base+i, at))
            if op in direct|indexed and at < 0xd37c and at+(256 if op in indexed else 1) > 0xd371:
                writers.append((bank, base+i, op, at))
    assert not hook_controls and not writers
    assert not d['tail_words'] and not d['tail_controls'] and not d['tail_relative']
    report = dict(passed=True, source_SHA256=P.H(Path(__file__).read_bytes()),
                  parent_SHA256=P.PIN, plan_receipt_SHA256=d['receipt_SHA256'],
                  candidate_SHA256=d['predicted_candidate_SHA256'], owned_bytes=94, changed_bytes=91,
                  exact_kind4_A1_domination=True, original5526_motor_preserved=True,
                  classifier45_bytes_exact=True, new11B_helper_tail=[0xd371, 0xd37c],
                  declared_tail_capacity_receipt=capacity['receipt_SHA256'],
                  new_tail_literal_controls_and_writers=[], old_hook_literal_controls=[],
                  stack_change='One genuine JSR/RTS, two transient bytes; caller ABI/ISR tests still required',
                  scope='Source-bound static review only. No arbitrary-pointer theorem, '
                      'successor CPU, physical ROM or delivery qualification.',
                  CPU_executed=False, outputs=0)
    report['receipt_SHA256'] = P.H(json.dumps(report, sort_keys=True, separators=(',', ':')).encode())
    return report


if __name__ == '__main__':
    print('RESULT '+json.dumps(review(P.ROM.read_bytes()), separators=(',', ':')), flush=True)
