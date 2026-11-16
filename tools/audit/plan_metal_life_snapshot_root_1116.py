"""Detached two-byte Metal repair; no ROM overlay or proposed-code CPU."""
from hashlib import sha256
import json
from pathlib import Path

import current_metal_stock_7c0f_1116 as Current

R = Current.R
H = lambda value: sha256(value).hexdigest()
CURRENT_SHA = '6bd911e82b9891ce1c9ae39d4f8c3acdf2492731c83edf23612f27d76a857956'


def measure(raw):
    assert H(Path(Current.__file__).read_bytes()) == CURRENT_SHA
    assert H(raw) == Current.PIN
    actor, renderer, extra, proof = Current.payload(raw)
    labels = Current.labels()
    life, branch, store = 0xd4a7, 0xd4ad, 0xd4e5
    origin = 0xcd00
    assert labels['Ms12Movement'] == 0xd476
    assert labels['Ms12NeedConstructor'] == branch+2
    assert labels['Ms12BeforeStep'] == store+3
    assert renderer[life-origin:branch+2-origin] == bytes.fromhex('ad5f07cd3ec8f039')
    assert renderer[store-3-origin:store+3-origin] == bytes.fromhex('ad5f078d3ec8')
    assert branch+2+renderer[branch+1-origin] == labels['Ms12BeforeStep']
    old, new = bytes.fromhex('f039'), bytes((0x10, store-(branch+2)))
    assert new == bytes.fromhex('1036')
    revised = bytearray(renderer)
    revised[branch-origin:branch+2-origin] = new
    pages = Current.Previous.Inventory.RENDER_PAGES
    page, offset = divmod(branch-origin, 1024)
    file = 1048592+pages[page]*1024+offset
    assert raw[file:file+2] == old
    previous_cookie = Current.COOKIE
    cookie = bytes((0xa7, 35, 47))+sha256(
        b'Metal earned-life snapshot 1116\0'+previous_cookie+actor+revised+extra).digest()[:13]
    spans = [dict(role='signed life comparison branch', file=file, bytes=2,
                  old_hex=old.hex(), new_hex=new.hex(), old_SHA256=H(old), new_SHA256=H(new))]
    for resident in proof['residents_exact_bc5']:
        at = resident['cookie_file']
        assert raw[at:at+16] == previous_cookie
        spans.append(dict(role=resident['role']+' full existing cookie', file=at, bytes=16,
                          old_hex=previous_cookie.hex(), new_hex=cookie.hex(),
                          old_SHA256=H(previous_cookie), new_SHA256=H(cookie)))
    digest = sha256()
    cursor = 0
    owned = set()
    for span in sorted(spans, key=lambda row: row['file']):
        lo, size = span['file'], span['bytes']
        assert lo >= cursor
        digest.update(raw[cursor:lo]); digest.update(bytes.fromhex(span['new_hex']))
        cursor = lo+size
        owned.update(range(lo, cursor))
    digest.update(raw[cursor:])
    assert len(owned) == 34
    report = dict(detached=True, parent_SHA256=H(raw), owning_Metal_facade_SHA256=CURRENT_SHA,
                  branch_PC=branch, previous_equal_target=labels['Ms12BeforeStep'], new_target_existing_STA=store,
                  old_cookie=previous_cookie.hex(), proposed_cookie=cookie.hex(),
                  owning_actor_SHA256=H(actor), owning_renderer_SHA256=H(renderer), full_extra499_SHA256=H(extra),
                  proposed_renderer_SHA256=H(revised), predicted_candidate_SHA256=digest.hexdigest(),
                  source_code_bytes=2, existing_cookie_bytes=32, owned_bytes=34, physical_spans=spans,
                  semantics='After valid ready and same-player guards, CMP life-snapshot BPL stores current life at existing STA. Equal and positive modulo deltas retain earned state; negative deltas follow original constructor. Every +/-1 transition, including wrapping255->0 and0->255, has the intended sign. Header/player/Fresh construction guards unchanged.',
                  ordinary_equal_delta_cost='One existing absolute STA, +4cycles; no new stack/frame/storage',
                  scope='Detached exact preimages/targets/streamed digest. Current.payload validates installed metadata with compiled menu CPU; no proposed instruction or ROM overlay is executed. Proposed ABI, life boundaries, lifecycle/IRQ and frozen genuine L route remain unexecuted.',
                  retained_pre_correction_receipt_SHA256='4af89b242f62d88dd6582e8ab93560c40a0bce40719b1ad8cda8f3b38312a527',
                  new_RAM_or_carrier_or_helper_bytes=0, ROM_composed=False, CPU_executed=True,
                  CPU_scope='Installed compiled menu metadata only', proposed_CPU_executed=False, outputs=0)
    report['receipt_SHA256'] = H(json.dumps(report, sort_keys=True, separators=(',', ':')).encode())
    return report


if __name__ == '__main__':
    raw = Current.ROM.read_bytes()
    print('RESULT '+json.dumps(measure(raw), separators=(',', ':')), flush=True)
