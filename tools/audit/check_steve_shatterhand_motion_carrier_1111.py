"""Test a fourth metadata row for Steve's movement in the pinned live ROM."""

from collections import Counter
import json
from unittest.mock import patch

import check_jay_silius_shotgun_transport_1111 as T
import check_steve_shatterhand_live_1111 as Live
import compose_steve_shatterhand_1111 as S
import trace_steve_shatterhand_motion_1111 as Motion


PAGE = 167
ORIGIN = 0xdc00
METADATA_SIZE = 0x3e0
ORIGINAL_COOKIE = bytes.fromhex('a7102009d541d456ddb444f69f81a4f1')
ORIGINAL_DESCRIPTOR = bytes((7, 4)) + T.FULL_DESCRIPTOR[2:] + bytes((220, 0))
DESCRIPTOR = bytes((8, 4)) + ORIGINAL_DESCRIPTOR[2:] + bytes((PAGE, 0))
MOVEMENT_FALLBACK = 0xbf22


def pinned_parent():
    raw = S.Donor.HOST.read_bytes()
    pin = S.C.digest(raw)
    if pin == S.LIVE_PIN:
        return raw
    from deliver_steve_move_1111 import PIN as MOVED, recover_parent as without_movement
    from deliver_prince_exposed_brick_idle_1111 import recover_parent

    if pin == MOVED:
        raw = without_movement(raw)
    raw = recover_parent(raw)
    assert S.C.digest(raw) == S.LIVE_PIN
    return raw


def ownership(raw):
    """Reuse the current all-roster CHR selector audit without its mirror requirement."""
    assert S.C.digest(raw) == S.LIVE_PIN and S.page(raw, PAGE) == bytes(1024)
    physical_page = T.page

    def only_as_carrier_preimage(image, index):
        return physical_page(image, 2 if index == PAGE else index)

    with patch.multiple(T, PIN=S.LIVE_PIN, EXTRA_PAGE=PAGE, page=only_as_carrier_preimage):
        proof = T.carrier_ownership(raw, PAGE)
    assert proof['candidate_page'] == PAGE
    return proof


def cold_program(descriptor, cookie):
    template = T.cold_program(descriptor, cookie)['source']
    source = S.changed(template, ' and #$60\n cmp #$20\n beq ReturnIdentity\n',
                       ' adc #$1f\n and #$40\n cmp #$40\n rts\n')
    return S.H.assemble(source, {'COLD65': (T.COLD, T.COLD_SIZE)})


def proposal(raw, *, worker=None, residents=None):
    assert S.C.digest(raw) == S.LIVE_PIN
    old_cold = cold_program(ORIGINAL_DESCRIPTOR, ORIGINAL_COOKIE)
    assert S.code(raw, 65, T.COLD, T.COLD_SIZE) == old_cold['images']['COLD65'].ljust(T.COLD_SIZE, b'\xea')
    assert S.code(raw, 65, 0xaf00, 3) == b'\x4c' + S.address_bytes(old_cold['symbols']['JaySelect'])
    assert S.code(raw, 94, 0xb2ef, 16) == ORIGINAL_COOKIE
    if worker is None:
        worker = Motion.link(ORIGIN)['images']['MOTION']
    assert len(worker) <= METADATA_SIZE
    row = worker.ljust(1024, b'\xea')
    assert S.page(raw, PAGE) == bytes(1024)
    residents = residents or {}
    cookie = bytes((0xa7, 16, 32, 10)) + bytes.fromhex(S.C.digest(
        ORIGINAL_COOKIE + DESCRIPTOR + row + b''.join(residents[name] for name in sorted(residents))))[:12]
    cold = cold_program(DESCRIPTOR, cookie)
    assert len(old_cold['images']['COLD65']) == 157 and len(cold['images']['COLD65']) == 159
    edits = (
        (S.C.offset(65, T.COLD), cold['images']['COLD65'].ljust(T.COLD_SIZE, b'\xea')),
        (S.C.offset(65, 0xaf01), S.address_bytes(cold['symbols']['JaySelect'])),
        (S.C.offset(94, 0xb2ef), cookie),
        (S.C.CHR + 1024 * PAGE, row),
    )
    candidate = bytearray(raw)
    for start, data in edits:
        candidate[start:start+len(data)] = data
    if residents:
        original = S.link(S.W.Symbols.bundle())['images']
        placement = {'COMBAT': (234, 0xbc00), 'BIRTH': (222, 0xb400)}
        for name, code in residents.items():
            origin, capacity = S.LAYOUT[name]
            page, page_origin = placement[name]
            assert len(code) == capacity
            at = S.C.CHR + 1024 * page + origin - page_origin
            assert raw[at:at+capacity] == original[name].ljust(capacity, b'\xea')
            candidate[at:at+capacity] = code
    return bytes(candidate), cookie, row


def controller_parity(raw, candidate, cookie, row):
    result = {}
    assert S.page(raw, 234)[MOVEMENT_FALLBACK - 0xbc00:][:2] == b'\x18\x60'
    for variant, name in enumerate(('Mike', 'Jay', 'Steve')):
        before, old_open = Live.opening(raw, variant)
        after, new_open = Live.opening(candidate, variant)
        assert old_open == new_open == 167
        if variant:
            assert before.ppu_reads == 14350 and after.ppu_reads == 16400
            assert S.C.Common.headers(before) == (ORIGINAL_COOKIE,) * 2
            assert S.C.Common.headers(after) == (cookie,) * 2
            assert bytes(after.ram[2][0x1c00:0x1fe0]) == row[:METADATA_SIZE]
            assert bytes(before.ram[2][:0x1c00]) == bytes(after.ram[2][:0x1c00])
        else:
            assert before.ppu_reads == after.ppu_reads == 0
        old_cold_reads, new_cold_reads = before.ppu_reads, after.ppu_reads
        pads = [0] * 4 + [1] * 12 + [129] * 6 + [2] * 6 + [0] * 10 + [64] * 12
        entries = []
        callers = Counter()

        def observe(memory, cpu):
            if (memory.rawtags[1], cpu.pc) == (3, MOVEMENT_FALLBACK):
                assert cpu.y in (0xd6, 0xe0) and memory.rawtags[2] == 2
                callers[f'{cpu.y:02x}'] += 1
                if cpu.y == 0xe0:
                    entries.append(S.N.get(memory, 'SavedJoypadBits'))

        for update, pad in enumerate(pads, 1):
            before.controller_pad = after.controller_pad = pad
            S.C.Game.frame(before)
            S.C.Game.frame(after, observe)
            old, new = S.C.Vector.app(before), S.C.Vector.app(after)
            if variant:
                assert old[:3] + old[4:] == new[:3] + new[4:], (name, update)
            else:
                assert old == new, (name, update)
            assert before.vram == after.vram and before.chr_latches == after.chr_latches
            assert before.ppu_reads == old_cold_reads and after.ppu_reads == new_cold_reads
        assert entries == (pads if variant == 2 else []), (name, entries)
        result[name] = dict(opening=new_open, updates=len(pads), ppu_reads=new_cold_reads,
                            resident_fallback_callers=dict(callers), player=Live.player(after),
                            lives=S.N.get(after, 'NumberofLives'))
    return result


def main():
    raw = pinned_parent()
    print('Physical CHR selector census', json.dumps(ownership(raw), sort_keys=True), flush=True)
    candidate, cookie, row = proposal(raw)
    print(json.dumps(dict(passed=True, parent_SHA256=S.C.digest(raw), candidate_SHA256=S.C.digest(candidate),
                          cookie=cookie.hex(), CHR_page=PAGE, metadata_start=hex(ORIGIN),
                          callable_carrier=False, controller_parity=controller_parity(raw, candidate, cookie, row),
                          output_files=0), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
