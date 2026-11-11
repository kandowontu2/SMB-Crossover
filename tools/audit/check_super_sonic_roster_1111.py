"""Compose the fifth Mr. Gimmick alternate and qualify the compiled menu."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

from audit_bub_menu_frontend_1102_v1 import commands, invoke
from check_remaining_roster_starts_1110 import I, W, inventory, menu_name
from check_tmnt_render_oa import address, location
from prepare_sonic_vol2_art_1111 import NIGHTLY, SHEET, apply_art, transport_cookie


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/reference'))
from sonic_sms_compact_cold_worker_1110 import assemble


SOURCE = ROOT / 'tools/reference/super_sonic_roster_1111.s'
LAYOUT = {
    'NAME_GATE': (0xac7d, 40),
    'SUPER_NAME': (0xbeed, 22),
    'SUPER_TITLE': (0xbf03, 22),
    'PORTRAIT': (0xbc77, 51),
    'PALETTE': (0xb4d0, 62),
    'ACTIVE_PAGE': (0xda31, 11),
}


def prg(bank, pc):
    return 16 + 8192 * bank + (pc & 8191)


def chr_offset(page, pc):
    return 1048592 + 1024 * page + (pc & 1023)


def selector_spans():
    """Return exact offset, prior bytes, and proposed bytes for every selector edit."""
    code = assemble(SOURCE.read_text(encoding='ascii'), LAYOUT)['images']
    spans = []

    def patch(offset, original, replacement):
        assert len(original) == len(replacement)
        spans.append((offset, original, replacement))

    def write(segment, offset, old):
        payload = code[segment]
        assert len(payload) <= len(old), (segment, len(payload), len(old))
        patch(offset, old, payload.ljust(len(old), b'\xea'))

    patch(prg(66, 0xb054), b'\xe0\x04', b'\xe0\x05')
    patch(prg(76, 0xbcf9), bytes.fromhex('c903f00b'), bytes.fromhex('c903b00b'))
    # The indexed clear already excludes $5FFF. Preserve the title's explicitly
    # initialized $5FFE selection across starts and clear the same other bytes.
    patch(prg(78, 0xa00c), bytes.fromhex('9dff5e'), bytes.fromhex('9dfe5e'))

    write('NAME_GATE', prg(66, 0xac7d), bytes.fromhex(
        '08ad0260c92bd00ea9008d6a0128a958a2a3a0e1d00728a90ea2a8a0bf4cc6ac') + b'\xea'*8)
    # The Rogue donor raw-bank view stays intact. Its compiled control-flow
    # view has 44 unused bytes after the last copied table at $BEED.
    prior_name = bytes.fromhex('003700340031002e0027ff03030202020101ffbc0200')
    patch(prg(97, 0xbeed), prior_name, code['SUPER_NAME'].ljust(len(prior_name), b'\xff'))
    patch(prg(97, 0xbf03), b'\xff'*22, code['SUPER_TITLE'].ljust(22, b'\xff'))

    write('PORTRAIT', prg(9, 0xbc77), bytes.fromhex(
        '08c92bf013288d6a01a9288d6c01a9a58d6d01a9dd4c5a0128a9018de1068dee73'
        '8d4601a9858de073a9108d470160') + b'\xea'*4)
    palette = bytes.fromhex('6828aeae04e04eb012a000b9ecb49daf04e8c8c007d0f4ca8eae04603f110316123000')
    vanilla = bytes.fromhex('01a9cb8d6c01a9a68d6d01a986205a010a0a1865036920a84c3fb5')
    write('PALETTE', prg(3, 0xb4d0), palette + vanilla)

    patch(chr_offset(330, 0xbfc3), bytes.fromhex('a9108d4701'), bytes.fromhex('2031daeaea'))
    patch(chr_offset(334, 0xda31), b'\xff'*11, code['ACTIVE_PAGE'])
    return tuple(spans)


def apply_spans(image, *, reverse):
    result = bytearray(image)
    for offset, original, replacement in selector_spans():
        expected, new = (replacement, original) if reverse else (original, replacement)
        assert image[offset:offset+len(expected)] == expected, (hex(offset), expected.hex())
        result[offset:offset+len(new)] = new
    return bytes(result)


def proposal(stock):
    """Return the selector/runtime image before art and cookie rebinding."""
    assert stock[1034472:1034488] == transport_cookie(stock)
    return apply_spans(stock, reverse=False)


def recover_selector(image):
    """Undo selector and runtime changes, leaving art and cookie for the caller."""
    return apply_spans(image, reverse=True)


def rogue_audio_domains(stock):
    """Bind the actual relocated audio readers and original dispatch graph."""
    closure = ROOT / 'docs/qa/rogue-dawn-audio-source-closure-2026-10-28.json'
    graph = json.loads(closure.read_text(encoding='utf-8'))['graph']
    gap = range(0xbeed, 0xbf19)
    assert not any(row['pc'] in gap for row in graph['instructions'])
    assert not any(target in gap for _, target in graph['static_edges'])
    assert not any(pc in gap for pc in graph['roots'])

    audio = ROOT / 'src/rogue_dawn_audio_reader_native_v6.inc'
    compiled = re.findall(r'^ lda RdaUpperStart\+\$([0-9a-f]+)(,y)? ;49:([A-F0-9]{4}) [0-9a-f]+$',
                          audio.read_text(encoding='ascii'), re.M)
    assert len(compiled) == 25
    highest = 0
    for offset, indexed, pc in compiled:
        destination = 0xc480 + int(offset, 16)
        instruction = bytes((0xb9 if indexed else 0xad,)) + destination.to_bytes(2, 'little')
        where = prg(97, int(pc, 16))
        assert stock[where:where+3] == instruction, pc
        highest = max(highest, destination + (255 if indexed else 0))
    assert highest == 0xdeec

    # The indirect read paths use separate raw-bank maps through the A window.
    # Bind the actual lower and upper reader operands before testing the maps.
    lower = prg(97, 0xc429)
    upper = prg(97, 0xc44c)
    assert stock[lower:lower+3] == bytes.fromhex('bda7bb')
    assert stock[upper:upper+3] == bytes.fromhex('bd3fbe')
    lower_map = prg(62, 0xbba7)
    upper_map = prg(62, 0xbe3f)
    indirect_banks = stock[lower_map:lower_map+192] + stock[upper_map:upper_map+32]
    assert all((bank & 127) != 97 for bank in indirect_banks)
    return dict(compiled_direct_readers=len(compiled), highest_address=hex(highest),
                indirect_map_rows=len(indirect_banks), code_view_cave=[hex(gap.start+0x2000), hex(gap.stop+0x2000)])


def family(bundle):
    model = I.UI.seed(bundle, 25)
    results = []
    for step in range(6):
        title, _ = menu_name(model)
        body = tuple(model[0x201 + i*4] for i in range(4))
        palette = [tuple(c['bytes']) for c in commands(model) if c['address'] == 0x3f11]
        results.append((title, model[0x6002], model[0x5ffe], model[0x0147], body, palette))
        for button in (16, 128):
            selected = I.N.fork(model)
            I.UI.key(selected, button)
            assert I.N.get(selected, 'CrossoverMenuState') == 0
            if title in ('SONIC', 'SUPER SONIC'):
                invoke(selected, 'X5InventoryInit')
                assert selected[0x6002] == 43 and selected[0x5ffe] == step
        I.UI.key(model, 32)
    return results


def qualify(stock, image):
    parent, candidate = W.bundle(stock), W.bundle(image)
    before = inventory(stock)
    after = inventory(image)
    assert before['distinct_named_entries'] == 100 and after['distinct_named_entries'] == 101
    assert [row for row in after['rows'] if row['name'] != 'SUPER SONIC'] == before['rows']
    assert not after['locked']
    choices = family(candidate)
    assert [r[0] for r in choices] == ['MR GIMMICK', 'BUB', 'BOB', 'SONIC', 'SUPER SONIC', 'MR GIMMICK']
    assert [r[:3] for r in choices[:4]] == [r[:3] for r in family_parent(parent)]
    assert [r[3] for r in choices[3:5]] == [16, 17]
    assert [sorted(r[4]) for r in choices[3:5]] == [[0, 2, 32, 34]]*2
    assert [r[5] for r in choices[3:5]] == [[(22, 18, 48)], [(22, 40, 48)]]
    for choice in range(5):
        for bundle, expected in ((parent, 0), (candidate, choice)):
            model = I.UI.seed(bundle, 25)
            model[0x5c00:0x6000] = bytes([0xa5])*1024
            model[0x5ffe] = choice
            invoke(model, 'X5ProfilesNewGame')
            assert bytes(model[0x5c00:0x6000]) == bytes(1022) + bytes((expected, 0xa5))
    return dict(named=after['distinct_named_entries'], confirmable=after['confirmable_named_entries'],
                family=choices, cookie=transport_cookie(image, super_sonic=True).hex(),
                rogue_audio=rogue_audio_domains(stock), exram_clear_pairs=5)


def family_parent(bundle):
    model = I.UI.seed(bundle, 25)
    for _ in range(4):
        yield menu_name(model)[0], model[0x6002], model[0x5ffe]
        I.UI.key(model, 32)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, default=NIGHTLY)
    args = parser.parse_args()
    stock = args.rom.read_bytes()
    selector = proposal(stock)
    assert recover_selector(selector) == stock
    image = apply_art(stock, SHEET.read_bytes(), candidate=selector, super_sonic=True)
    print(json.dumps(dict(passed=True, parent_SHA256=sha256(stock).hexdigest(),
                          candidate_SHA256=sha256(image).hexdigest(),
                          result=qualify(stock, image), output_files=0)), flush=True)


if __name__ == '__main__':
    main()
