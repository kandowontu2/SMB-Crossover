"""Qualify the player-only native PRG owner for Steve's live lift record."""

from itertools import product
import json

import check_steve_shatterhand_lift_art_1111 as A

C, W, N, H = A.C, A.W, A.N, A.Late.H
SOURCE = H.ROOT / 'tools/reference/steve_shatterhand_pose_owner_1111.s'
ORIGIN = 0xb79d
OLD = bytes.fromhex('0848203daf900d6828a9de8da17da9de8d16516068284cb6b7c000d01aad0260f016c901d011addd73f004a9c1d002a9a18da17d8d165160ad0a73c904d0f8a9e2d0ee')


def plan(raw):
    bundle = W.Symbols.bundle()
    fields = {name: W.address(bundle, name) for name in ('SelectedCharacter', 'SmPosePtr')}
    fields.update(ProtoVariant=0x73dd, MarioVariant=0x730a)
    source = ''.join(f'{name}=${value:04x}\n' for name, value in fields.items()) + SOURCE.read_text()
    linked = H.assemble(source, {'POSE_OWNER': (ORIGIN, 67)})
    assert len(OLD) == 67
    at = C.offset(95, ORIGIN)
    assert raw[at:at+67] == OLD, raw[at:at+67].hex()
    # The sole literal entry into the displaced fallback is the JMP inside
    # this very envelope. No independent direct caller is retired.
    prg = raw[16+95*8192:16+96*8192]
    assert prg.count(b'\x4c\xb6\xb7') == 1 and prg.count(b'\x20\xb6\xb7') == 0
    gate = C.offset(4, 0xbf61)
    assert raw[gate-7:gate+7] == bytes.fromhex('c000d019ad0260c903b0128d6a01')
    continuation = C.offset(4, 0xa422)
    assert raw[continuation] == 0xb9 and raw[continuation+3] == 0x38
    return ((at, OLD, linked['images']['POSE_OWNER'].ljust(67, b'\xea')),
            (gate+1, b'\x03', b'\x11'))


def compare(raw, candidate):
    bundle = W.Symbols.bundle()
    count = 0
    for character, form, high, status in product(range(17), (0, 1, 4), (0xc1, 0xc8), (0x20, 0x61)):
        results = []
        for image in (raw, candidate):
            m = C.Common.blank(dict(bundle, raw=image))
            m.raw_page(1, 0xdf)
            m.raw_page(2, 0xe1)
            N.put(m, SelectedCharacter=character, SmPosePtr=0xc0)
            m[W.address(bundle, 'SmPosePtr')+1] = high
            m[0x73dd], m[0x730a] = form, form
            m[0x7da1] = 0xe1
            cpu = N.NesMPU(memory=m, pc=ORIGIN)
            cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = character, 11, 0, status, 240
            cpu.stPushWord(0x4fff)
            for _ in range(500):
                if cpu.pc == 0x5000:
                    break
                assert m[cpu.pc], hex(cpu.pc)
                cpu.step()
            else:
                raise AssertionError('owner instruction bound')
            assert cpu.sp == 240 and cpu.x == 11 and cpu.y == 0
            # Native continuation begins LDA abs,Y / SEC, replacing N/Z/C
            # before any consumer. Preserve the remaining status bits.
            results.append((cpu.a, cpu.p & 0x7c, tuple(m.rawtags), m[0x7da1]))
        if character == 16 and high == 0xc8:
            assert results[1][2][2] == results[1][3] == 2
        elif character == 16:
            assert results[0][1:] == results[1][1:]
        else:
            assert results[0] == results[1], (character, form, high, status, results)
        count += 1
    return count


def main():
    raw = A.D.HOST.read_bytes()
    edits = plan(raw)
    candidate = bytearray(raw)
    for at, old, new in edits:
        candidate[at:at+len(old)] = new
    print(json.dumps(dict(owner_cases=compare(raw, bytes(candidate)), output_files=0)))


if __name__ == '__main__':
    main()
