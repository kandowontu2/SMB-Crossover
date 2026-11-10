"""Source-funded FF head-corner derivative; CPU/ROM data stays in memory.

The old 80-byte EffectPalettePointer has no remaining current caller. Its
source-retirement proof is separate. Snapshot extends existing pre-render
descriptor scratch from eight bytes to ten, within the same 61-byte buffer.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / 'tools/reference'))
import sonic_sms_compact_cold_worker_1110 as Asm
import check_ff_white_mushroom_current_1110 as W
from check_tmnt_render_oa import address, location

SOURCE = R / 'tools/reference/ff_head_corner_1110.s'
BASE = R / 'build/complete-roster-native-1110/candidate.nes'
PIN = W.PIN
KERNEL_PIN = '14f1ac6330109b1e6ab77710c8491b8ba1b706a524b133a7c9542d6b51910b3b'
RETIRED_PIN = 'a76c5f9a9e202f66dcdc7fbcd85b34f9257260a145b63bd85bf720cae9b35cc6'
CHR, FIRST, COUNT = 1048592, 893, 8
COOKIE = 511774


def digest(data):
    return sha256(data).hexdigest()


def program(b):
    names = ('FfHostRead', 'FfEnsure', 'Player_Y_Speed', 'Player_X_Position',
             'Player_PageLoc', 'MTileAttribute', 'R3', 'R5')
    definitions = {name: address(b, name) for name in names}
    definitions.update(FfHostReadReturn=address(b, 'FfHostRead::Return'),
                       FfTerrainPage=address(b, 'FfRenderBuffer') + 6,
                       FfCornerPreviousX=address(b, 'FfRenderBuffer') + 8,
                       FfCornerPreviousPage=address(b, 'FfRenderBuffer') + 9)
    source = '\n'.join(f'{name}=${value:04x}' for name, value in definitions.items())
    compiled = Asm.assemble(source + '\n' + SOURCE.read_text(),
                            {'HEAD': (0xb620, 80), 'SNAPSHOT': (0xbb47, 25)})
    assert compiled['used'] == {'HEAD': 71, 'SNAPSHOT': 14}, compiled['used']
    return compiled, definitions


def proposal(raw):
    assert digest(raw) == PIN
    b = W.Symbols.bundle(); b['raw'] = raw
    code, definitions = program(b)
    start = CHR + FIRST * 1024
    original = raw[start:start + COUNT * 1024]
    assert digest(original) == KERNEL_PIN and original[0x1fe0:0x1ff0] == b'\xff' * 16
    assert digest(original[0x1620:0x1670]) == RETIRED_PIN
    assert original[0x1b47:0x1b60] == b'\xff' * 25
    # The following class palette pointer and live portrait remain intact.
    image, kernel = bytearray(raw), bytearray(original)
    patches = []

    def put(pc, old, new, role):
        a = pc - 0xa000
        assert kernel[a:a + len(old)] == old and len(old) == len(new), (role, hex(pc))
        kernel[a:a + len(new)] = new
        patches.append(dict(RAM3=pc, bytes=len(new), old_hex=old.hex(), new_hex=new.hex(), role=role))

    for segment, pc, size in (('HEAD', 0xb620, 80), ('SNAPSHOT', 0xbb47, 25)):
        data = code['images'][segment]
        put(pc, original[pc - 0xa000:pc - 0xa000 + size], data.ljust(size, b'\xff'),
            'Source-retired effect pointer' if segment == 'HEAD' else 'Declared FF terrain linker padding')
    for pc in (0xb996, 0xb9a0, 0xb9aa):
        put(pc, b'\x20' + definitions['FfHostRead'].to_bytes(2, 'little'),
            b'\x20' + code['symbols']['FfCornerHeadRead'].to_bytes(2, 'little'),
            'Only the three head candidates use the previous-world-body filter')
    put(0xb907, b'\x20' + definitions['FfEnsure'].to_bytes(2, 'little'),
        b'\x20' + code['symbols']['FfCornerCapture'].to_bytes(2, 'little'),
        'Capture original worldX/page at the existing Ensure boundary')
    assert kernel[0x1613:0x1620] == original[0x1613:0x1620]
    assert kernel[0x1670:0x168b] == original[0x1670:0x168b]
    assert kernel[0x1fe0:0x1ff0] == b'\xff' * 16
    cookie = bytes((0xa7, 22, 0, 10)) + sha256(kernel).digest()[:12]
    old_cookie = bytes((0xa7, 22, 0, 9)) + sha256(original).digest()[:12]
    assert raw[COOKIE:COOKIE + 16] == old_cookie
    image[start:start + len(kernel)] = kernel
    image[COOKIE:COOKIE + 16] = cookie
    return bytes(image), bytes(kernel), cookie, code, definitions, patches


def unit(raw, kernel, code, definitions):
    # Isolated exact current native cell reader with the new derivative.
    # Fixtures here are explicit; natural controller/cold qualification is
    # separate and must not be inferred from this geometry matrix.
    b = W.Symbols.bundle(); b['raw'] = raw
    m = W.N.fresh(b)
    m.raw_page(1, 3); m.raw_page(2, 2)
    W.N.put(m, CurrentBank=3, CurrentBankC=2, SelectedCharacter=22, Player_Y_HighPos=1)
    m.ram[3][:] = kernel
    counts = Counter()
    reader = code['symbols']['FfCornerHeadRead']
    frame = address(b, 'FfRenderBuffer')
    for direction in (-1, 0, 1):
        for previous in (0, 1, 13, 14, 15, 16, 239, 240, 241, 254, 255, 256, 510, 511, 65535):
            current = (previous + direction) & 65535
            for dx in (1, 8, 14):
                for tile in (0, 0x61, 0xc1):
                    for vy in (0, 1, 255):
                        for a in range(0x300, 0x4a0):
                            m[a] = 0
                        point = (current + dx) & 65535
                        cell = point & 65520
                        index = 0x300 + ((point >> 8) & 1) * 208 + 7 * 16 + ((point >> 4) & 15)
                        m[index] = tile
                        W.N.put(m, Player_X_Position=current & 255, Player_PageLoc=current >> 8,
                                Player_Y_Position=144, Player_Y_Speed=vy)
                        m[frame + 3], m[frame + 4], m[frame + 5] = dx, 0, 0
                        m[frame + 8], m[frame + 9] = previous & 255, previous >> 8
                        m[3], m[4] = 85, 166
                        c = W.N.NesMPU(memory=m, pc=reader)
                        c.a, c.x, c.y, c.p, c.sp = 83, 71, 0, 0x21, 224
                        c.stPushWord(0x5aff)
                        for _ in range(2048):
                            if c.pc == 0x5b00:
                                break
                            assert m[c.pc], ('Geometry BRK', hex(c.pc))
                            c.step()
                        else:
                            raise AssertionError('Geometry call bound')
                        endpoints = ((previous + 1) & 65535, (previous + 14) & 65535)
                        overlaps = any((p & 65520) == cell for p in endpoints)
                        solid = bool(m[address(b, 'MTileAttribute') + tile] & 1)
                        climb = bool(m[address(b, 'MTileAttribute') + tile] & 2)
                        filtered = vy >= 128 and solid and not climb and not overlaps
                        expected = 0 if filtered else tile
                        assert (c.a, c.x, c.y, c.sp) == (expected, 0, 0, 224), (previous, current, dx, tile, vy, overlaps, c.a)
                        assert (m[3], m[4]) == (85, 166)
                        assert m[frame + 8] == previous & 255 and m[frame + 9] == previous >> 8
                        assert W.N.get(m, 'Player_X_Position') == current & 255
                        counts['geometry_calls'] += 1
                        counts['new_side_only_candidates_filtered'] += int(filtered and tile != 0)
    return dict(counts)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--static-only', action='store_true')
    args = p.parse_args()
    raw = BASE.read_bytes()
    image, kernel, cookie, code, definitions, patches = proposal(raw)
    result = dict(passed=True, source_only=True, outputs_written=0, ROM_written=False,
                  parent_SHA256=PIN, in_memory_SHA256=digest(image), kernel_SHA256=digest(kernel),
                  cookie=cookie.hex(), code_bytes=code['used'], patches=patches,
                  separate_retirement_header_cold_lifecycle_and_native_qualification_required=True)
    if not args.static_only:
        result['isolated_geometry'] = unit(raw, kernel, code, definitions)
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
