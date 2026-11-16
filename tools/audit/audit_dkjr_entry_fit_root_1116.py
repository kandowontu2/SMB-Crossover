"""Independent detached review of the visible, VY-qualified DK entry fit."""
from hashlib import sha256
import json
from pathlib import Path

import measure_dkjr_forced_entry_fit_v2_1116 as Plan

H = lambda data: sha256(data).hexdigest()
PLAN_SHA = '67da40a7d69632b98d1a04070c247cd099e34eac7a43594f53ed5a06936a2745'
J = lambda value: H(json.dumps(value, sort_keys=True, separators=(',', ':')).encode())


def main():
    assert H(Path(Plan.__file__).read_bytes()) == PLAN_SHA
    parent = Plan.C.BT.ROM.read_bytes()
    alpha, composition = Plan.C.proposal(parent)
    fit = Plan.measure(parent)
    consumers = Plan.consumers(parent)
    physical = Plan.physical(parent)
    assert J(fit) == 'e8de1ab6f825b9c3eb303ff4793c5cef68bbc808d929c12c95d5b7f16f21371b'
    assert J(consumers) == 'c620552abd0c0ac9d6e257220458420fba7f0cbd728d91db5c1950440feaa6eb'
    assert J(physical) == 'd0fda62840d282147a72bcaedb2a83445877b8b1a87acd351a884b00941175eb'
    assert fit['logical_bytes'] == 1070 and len(fit['fragments']) == 4
    assert fit['native_VY_negative_explicitly_rejected'] and fit['initial_VY_zero_preserved']
    assert fit['visible_native_states_exactly_zero_or_two'] and not fit['source_physics_or_fall_limits_changed']
    assert fit['spare'] == dict(fruit=1, draw=1, anchor=12)
    chunks = physical['physical']
    assert [q['file_half_open'] for q in chunks] == [[1902482,1902608],[1915920,1916109],
        [1916708,1916944],[1925136,1925614],[1952924,1952934],[1953745,1953776],[534485,534501]]
    updated = {}
    for row in chunks:
        lo, hi = row['file_half_open']
        old, new = bytes.fromhex(row['old_hex']), bytes.fromhex(row['new_hex'])
        assert hi-lo == len(old) == len(new) and alpha[lo:hi] == old
        assert not set(updated).intersection(range(lo, hi))
        updated.update((lo+i, b) for i, b in enumerate(new))
    assert len(updated) == 1086
    for label, lo, size in (('BT-code', Plan.C.BT.CACHE, 8192), ('BT-header', Plan.C.BT.HEADER, 487)):
        assert not set(updated).intersection(range(lo, lo+size)), label
    body = Plan.C.Camera.payload(alpha)
    digest = sha256()
    cursor = 0
    for row in sorted(fit['fragments'], key=lambda q:q['payload_offset']):
        lo = row['payload_offset']
        old, new = bytes.fromhex(row['old_hex']), bytes.fromhex(row['new_hex'])
        assert body[lo:lo+len(old)] == old and len(old) == len(new)
        digest.update(body[cursor:lo]); digest.update(new); cursor = lo+len(old)
    digest.update(body[cursor:])
    assert digest.hexdigest() == physical['predicted_packet_SHA256'] == 'bbdb7d84eb2485d69d23df750ce08a3ed703b2b4de495aa08aa8c6806b7cb3e1'
    cookie = alpha[534485:534488]+digest.digest()[:13]
    assert bytes(updated[534485+i] for i in range(16)) == cookie
    rom = sha256(); cursor = 0
    for row in sorted(chunks, key=lambda q:q['file_half_open'][0]):
        lo, hi = row['file_half_open']; rom.update(alpha[cursor:lo]); rom.update(bytes.fromhex(row['new_hex'])); cursor=hi
    rom.update(alpha[cursor:])
    assert rom.hexdigest() == physical['predicted_ROM_SHA256'] == '7c0f7902e5ef17ff552c2ce36ba08534fdd48f00fddc62a54834df18e68f3c98'
    result = dict(passed=True, actual_parent_SHA256=H(parent), intermediate_private_a3fb_SHA256=H(alpha),
                  plan_SHA256=PLAN_SHA, fit_receipt=J(fit), consumers_receipt=J(consumers), physical_receipt=J(physical),
                  predicted_candidate_SHA256=rom.hexdigest(), predicted_packet_SHA256=digest.hexdigest(),
                  cookie_hex=cookie.hex(), logical_code_bytes=1070, entry_owned_with_cookie=1086,
                  physical_spans=[dict(file_half_open=q['file_half_open'],bytes=q['bytes'],
                    old_SHA256=H(bytes.fromhex(q['old_hex'])),new_SHA256=H(bytes.fromhex(q['new_hex'])))for q in chunks],
                  original_fall_limit_and_helpers_unchanged=True, BT8192_and_header487_unowned=True,
                  unexecuted='No proposed instruction or new whole ROM executed/composed; component, lifecycle, flags, SMC, renderer, ISR and full-route gates remain.',
                  outputs=0)
    result['receipt_SHA256'] = J(result)
    print('RESULT '+json.dumps(result,separators=(',',':')),flush=True)


if __name__ == '__main__':
    main()
