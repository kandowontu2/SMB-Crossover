"""Independent current-parent capacity/preimage review of the detached C2 plan."""
from hashlib import sha256
import json
from pathlib import Path

import plan_contra_force_checked_c2_direct_v2_1116 as Plan
import audit_contra_force_c2_tail_capacity_1116 as Capacity

H = lambda data: sha256(data).hexdigest()
PLAN_SHA = '0c2c3f37b326c6899ce261e4afca6fccab752eee8632422d74fa94080dfc5bce'
CAPACITY_SHA = 'e8c634a20c6a1cb9d3f1659daec9e0777f5a76ce249b932a0cc1ab0cbee381db'


def main():
    assert H(Path(Plan.__file__).read_bytes()) == PLAN_SHA
    assert H(Path(Capacity.__file__).read_bytes()) == CAPACITY_SHA
    raw = Plan.Base.load_current_image()
    q = Plan.descriptor(raw)
    assert q['receipt_SHA256'] == 'e93be9a4fb97384ff41e4158051f1f481726e2ecd701a3a297a04a3410de9232'
    c = Capacity.run(raw)
    assert c['receipt_SHA256'] == '151ae69089b1992db0959563e5ddc70f6fa8a15b767982e193765e93e30fd6db'
    for key in ('unclassified_tail_tuple_leads', 'unclassified_indexed_read_leads',
                'actual_standard_bank2_tail_ingress', 'actual_CF_RAM2_near_tail_control', 'structured_bank2_tail_targets'):
        assert not c[key], key
    reference, _ = Plan.Base.proposal(raw)
    updates = {}
    for at, pre in Plan.Base.PREIMAGES:
        old = bytes.fromhex(pre)
        assert raw[at:at+len(old)] == old
        updates.update((at+i, reference[at+i]) for i in range(len(old)))
    spans = []
    for row in q['additional_detached_fragments']:
        lo, hi = row['file_half_open']
        old, new = bytes.fromhex(row['old_hex']), bytes.fromhex(row['new_hex'])
        assert len(old) == len(new) == hi-lo
        assert reference[lo:hi] == old and H(old) == row['old_SHA256'] and H(new) == row['new_SHA256']
        updates.update((lo+i, b) for i, b in enumerate(new))
        spans.append(dict(file_half_open=[lo, hi], bytes=len(new), old_SHA256=H(old), new_SHA256=H(new)))
    assert len(updates) == q['proposed_total_owned_bytes'] == 661
    assert sum(raw[at] != value for at, value in updates.items()) == q['proposed_total_changed_bytes'] == 284
    at = Plan.Rejected.TAIL_FILE
    tail = bytes(updates[at+i] for i in range(58))
    assert raw[at:at+79] == bytes([255])*79
    assert tail[:5] == bytes.fromhex('ada17dc902')
    assert tail[-10:] == bytes.fromhex('a9978d6c01ad6a011860')
    assert at+58 <= c['tail_file_half_open'][1]
    payload = bytearray(raw[2006032:2030608])
    payload[at-2006032:at-2006032+58] = tail
    assert H(payload) == q['new_CF_payload_SHA256']
    cookie = bytes.fromhex('a71f0005') + bytes.fromhex(H(payload))[:12]
    for loc in (573373, 642966):
        assert bytes(updates[loc+i] for i in range(16)) == cookie
    assert bytes(payload[8192+0x1e00:8192+0x1f91]) == raw[2006032+8192+0x1e00:2006032+8192+0x1f91]
    result = dict(passed=True, parent_SHA256=H(raw), source_plan_SHA256=PLAN_SHA,
                  source_capacity_SHA256=CAPACITY_SHA, plan_receipt=q['receipt_SHA256'], capacity_receipt=c['receipt_SHA256'],
                  owned_bytes=661, changed_bytes=284, additional_fragments=spans,
                  new_payload_SHA256=H(payload), cookie_hex=cookie.hex(),
                  old401_API_exact=True, remaining_tail_bytes=21,
                  unexecuted='All runtime/public/ISR/SMC/ArgA-P/state parity and actual Main cost gates remain required.',
                  new_whole_ROM_or_CPU_or_files=0, outputs=0)
    result['receipt_SHA256'] = H(json.dumps(result, sort_keys=True, separators=(',', ':')).encode())
    print('RESULT '+json.dumps(result, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
