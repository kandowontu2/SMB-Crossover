"""Compare the private DK Jr. loop changes through the ordinary linked opening."""

import json
from pathlib import Path

from py65.devices.mpu6502 import MPU

import check_dkjr_rect_read_current_1123 as Check
import compose_dkjr_scene_hot_1123 as Scene


# Only these instruction operands can be self-modified by the original or
# replacement code. Their backing descriptor and all gameplay RAM are compared.
MUTABLE_OPERANDS = (0xA87C, 0xAD7F, 0xAC0B, 0xAC30)
INPUT = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')


def check_tiles(raw, candidate):
    old, new = (Scene.Head.payload(image)[:8192] for image in (raw, candidate))
    for value in range(256):
        for body in (old, new):
            cpu = MPU()
            cpu.memory[0xA000:0xC000] = body
            cpu.pc = 0xBEC4
            cpu.a = cpu.memory[0xC8EC] = value
            cpu.x = 0x34
            cpu.p &= ~cpu.DECIMAL
            Check.finish(cpu, (0xBED7 if value in (0x5E, *range(0xF1, 0xF8)) else 0xBEF3, cpu.sp))
            assert cpu.x == 0x34 and cpu.memory[0xC8EC] == value
            if cpu.pc == 0xBED7:
                assert not cpu.p & cpu.CARRY
                expected = 0x74 if value == 0x5E else 0x70 + (value - 0xF1 + (value >= 0xF3)) * 2
                assert cpu.a == expected


def comparator(raw, candidate):
    patches, old_rect, new_rect = Scene.program(raw)

    def normalize(rows):
        for pc, before, after in patches[1:]:
            offset = pc & 8191
            for bank, expected in ((rows[0][3], before), (rows[1][3], after)):
                for index, byte in enumerate(expected):
                    addr = pc + index
                    if not any(at <= addr < at + 2 for at in MUTABLE_OPERANDS):
                        assert bank[offset + index] == byte, ('Scene code owner', hex(addr))
                bank[offset:offset + len(expected)] = bytes(len(expected))
        for row in rows:
            for pc in MUTABLE_OPERANDS:
                offset = pc & 8191
                row[3][offset:offset + 2] = b'\x00\x00'

    def compare(a, b):
        Check.compare(a, b, raw, candidate, old_rect, new_rect, normalize)

    return compare


def main():
    raw = INPUT.read_bytes()
    candidate = Scene.compose(raw)
    check_tiles(raw, candidate)
    compare = comparator(raw, candidate)
    pair = [Check.P.Old.boot(rom) for rom in (raw, candidate)]
    compare(*pair)
    schedule = (
        ('standing', 0, 24), ('walking', 1, 24), ('walk-left', 2, 16),
        ('release', 0, 4), ('jump', 128, 1), ('steer-right-in-air', 1, 16),
        ('landing', 0, 32), ('right-jump', 129, 1), ('moving-landing', 1, 56),
    )
    for phase, pad, count in schedule:
        totals = [0, 0]
        before = Check.state(pair[0])
        for _ in range(count):
            for index, memory in enumerate(pair):
                assert not any(Check.B.flags(memory))
                elapsed, _ = Check.B.main_step(memory, pad)
                totals[index] += elapsed
            compare(*pair)
        result = dict(phase=phase, updates=count, before=before, after=Check.state(pair[0]),
                      mean_Main=[time / count for time in totals],
                      saved_per_Main=(totals[0] - totals[1]) / count)
        print(json.dumps(result, separators=(',', ':')), flush=True)
    print(json.dumps(dict(candidate=Scene.sha256(candidate).hexdigest(),
                          checked_display_tiles=256, linked_updates=sum(row[2] for row in schedule),
                          physical_cadence_qualified=False)), flush=True)


if __name__ == '__main__':
    main()
