"""Compare Karnov's cache side probe with the native block-buffer worker."""

from collections import Counter
from itertools import product
import json

import check_karnov_foreground_cookie_1123 as Karnov
from profile_dkjr_empty_current_1123 import Old


def call(model, address, y, flags, registers):
    cpu = Karnov.N.NesMPU(memory=model, pc=address)
    cpu.sp, cpu.p, cpu.a, cpu.x, cpu.y = 0xF6, flags, 0xB0, 5, y
    cpu.stPushWord(0x1FF)
    Karnov.CPU.run(cpu, lambda c: (c.pc, c.sp) == (0x200, 0xF6))
    return (cpu.a, cpu.x, cpu.y, cpu.p & 0xC3), bytes(model[i] for i in registers), cpu.processorCycles


def main():
    raw = Old.ROM.read_bytes()
    if Karnov.Cookie.sha256(raw).hexdigest() == Karnov.Side.CANDIDATE:
        raw = Karnov.Side.inverse(raw)
    assert Karnov.Cookie.sha256(raw).hexdigest() == Karnov.Cookie.PIN
    model = Karnov.start(raw, 'KARNOV')
    model.raw_page(1, 3)
    model.raw_page(2, 2)
    address = lambda name: Karnov.W.address(model.bundle, name)
    native = address('BlockBufferColli_Side')
    source = 0xA02A
    assert native == 0x958B and bytes(model[source + i] for i in range(3)) == bytes.fromhex('4c8cb3')
    x_pos, y_pos, page, crouch = map(address, ('Player_X_Position', 'Player_Y_Position',
                                            'Player_PageLoc', 'CrouchingFlag'))
    registers = tuple(address(f'R{i}') for i in range(8))
    for bank, name in enumerate(('Block_Buffer_1', 'Block_Buffer_2')):
        start = address(name)
        for i in range(208):
            model[start + i] = (i * 17 + 83 * bank) & 255

    scratch = bytes.fromhex('8291deadbeef5768')
    results = Counter()
    costs = Counter()
    x_positions = (0, 13, 14, 15, 16, 110, 111, 112, 241, 242, 253, 254, 255)
    positions = product((0, 1), (0, 1, 254, 255), x_positions, (33, 34, 35, 36))
    for is_crouch, page_number, x, probe in positions:
        native_probe = probe + (14 if is_crouch else 0)
        low, high = (20, 28) if is_crouch else (12, 24)
        dy = low if probe & 1 else high
        for y in range(256):
            model[x_pos], model[y_pos], model[page], model[crouch] = x, y, page_number, is_crouch
            for i, v in zip(registers, scratch):
                model[i] = v
            source_regs, source_ram, source_cost = call(model, source, probe, 0x75, registers)
            for i, v in zip(registers, scratch):
                model[i] = v
            native_regs, native_ram, native_cost = call(model, native, native_probe, 0x75, registers)
            if 32 <= ((y + dy) & 255) < 240:
                assert source_regs[:2] == native_regs[:2] and source_regs[2] == probe
                assert native_regs[2] == native_probe and source_regs[3] == native_regs[3]
                assert source_ram == native_ram, (is_crouch, page_number, x, y, probe)
                costs['karnov_worker'] += source_cost
                costs['native_worker'] += native_cost
                results['ordinary_matches'] += 1
            else:
                assert source_regs[:3] == (0, 0, probe)
                assert source_ram[2:5] == bytes((scratch[2], 0, scratch[4])), (registers, source_ram.hex())
                results['outside_playfield_requires_guard'] += 1
                results['unguarded_native_nonzero'] += bool(native_regs[0])

    assert results['unguarded_native_nonzero'] and results['ordinary_matches']
    print(json.dumps(dict(ROM=Karnov.Cookie.PIN, cases=dict(results),
                          mean_worker_cycles={k: v / results['ordinary_matches'] for k, v in costs.items()},
                          captures=0), separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
