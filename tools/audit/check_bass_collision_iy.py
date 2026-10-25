"""Reexecute unchanged HR terrain calls captured during ordinary Bass play.

The diagnostic runner observes the real emulator; this separate CPU component
check consumes its immutable entry states. It does not manufacture a replay or
change the emulator. Every final RAM byte, physical register, mapper selector,
and ordered write must match; no interrupt occurred inside these 34 calls.
"""
from pathlib import Path
import csv
import hashlib
import importlib.util
import json
import struct
import traceback

R = Path(__file__).resolve().parents[2]
D = R / 'build/roster-through-2-2/root-bass-collision-ix-9-v0-mmc3'
O = R / 'build/verification/bass-collision-cpu-iz'
MODEL = R / 'build/verification/agent49-samus-bill-arsenal-a/palette_native_model_cu.py'
ROM = R / 'build/checkpoints/ryu-overlap-hr/build/smb-crossover-mmc3.nes'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    O.mkdir()
    spec = importlib.util.spec_from_file_location('bass_terrain_cpu', MODEL)
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    im = model.q.Image(ROM)
    rows = list(csv.DictReader((D / 'bass-collision-calls.csv').open()))
    events = {}
    for row in rows:
        if row['event'] in ('entry', 'return'):
            events.setdefault(int(row['call']), {})[row['event']] = row
    writes = {}
    for call, address, value, depth, pc in struct.iter_unpack('<IHBBH', (D / 'bass-collision-writes.bin').read_bytes()):
        assert depth == 0, 'An interrupted call requires its actual ISR input tape'
        writes.setdefault(call, []).append((pc, address, value))
    assert set(events) == set(writes) == set(range(1, 35))
    report = dict(status='RUNNING', ROM_sha256=sha(ROM), model_sha256=sha(MODEL),
                  script_sha256=sha(__file__), calls=[], game_changed=False,
                  goal_complete=False, scope='Unchanged MMC3 HR complete native PlayerBGCollision calls; no ISR or external hardware reads in this captured window. Not a fix, full route, MMC5 or arbitrary-contact certification.')
    try:
        for call, pair in events.items():
            entry, end = pair['entry'], pair['return']
            initial = (D / f'bg-{call}-entry-ram.bin').read_bytes()
            final = (D / f'bg-{call}-return-ram.bin').read_bytes()
            assert len(initial) == len(final) == 10240
            banks = {address: int(entry[name]) for address, name in (
                (0x8000, 'bank8000'), (0xa000, 'bankA000'),
                (0xc000, 'bankC000'), (0xe000, 'bankE000'))}
            bus = model.Bus(im, initial, banks, ())
            bus.selector = int(entry['mapperSelect'])
            cpu = model.q.core.NesMPU(memory=bus)
            cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = [int(entry[n]) for n in ('a', 'x', 'y', 'p', 'sp')]
            cpu.pc = int(entry['pc'])
            cpu.processorCycles = 0
            stop = [int(end[n]) for n in ('pc', 'sp')]
            steps = 0
            while [cpu.pc, cpu.sp] != stop or not steps:
                bus.pc, bus.op = cpu.pc, bus.data[cpu.pc]
                popped = bus.data[0x100 + ((cpu.sp + 1) & 255)] if bus.op in (0x28, 0x40) else None
                cpu.step()
                if popped is not None:
                    assert cpu.p == popped | 0x30
                    cpu.p = popped & 0xcf
                steps += 1
                assert steps < 300000
            regs = [cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp, cpu.pc]
            expected = [int(end[n]) for n in ('a', 'x', 'y', 'p', 'sp', 'pc')]
            assert regs == expected, ('physical return registers', call, regs, expected)
            assert bus.ram() == final, ('all 10240 final RAM bytes', call)
            expected_banks = {address: int(end[name]) for address, name in (
                (0x8000, 'bank8000'), (0xa000, 'bankA000'),
                (0xc000, 'bankC000'), (0xe000, 'bankE000'))}
            assert bus.banks == expected_banks
            assert bus.selector == int(end['mapperSelect'])
            # Mesen's write callback exposes the CPU's already-fetched PC.
            # Bind it to the actual executed producer and its addressing mode;
            # JSR pushes before fetching its final operand (PC+2, not PC+3).
            lengths = dict(imp=1, acc=1, imm=2, zpg=2, zpx=2, zpy=2,
                           rel=2, inx=2, iny=2, abs=3, abx=3, aby=3, ind=3)
            actual_writes = []
            for pc, opcode, address, physical, value in bus.trace:
                mode = cpu.disassemble[opcode][1]
                callback_pc = (pc + (2 if opcode == 0x20 else lengths[mode])) & 65535
                actual_writes.append((callback_pc, address, value))
            assert actual_writes == writes[call], ('every ordered writer PC/address/value', call, actual_writes, writes[call])
            native_cycles = int(end['cycle']) - int(entry['cycle'])
            assert cpu.processorCycles == native_cycles, ('complete instruction cycles', call, cpu.processorCycles, native_cycles)
            report['calls'].append(dict(call=call, frame=int(entry['frame']),
                cycles=cpu.processorCycles, instructions=steps, ordered_writes=len(bus.trace),
                entry_sha256=hashlib.sha256(initial).hexdigest(),
                return_sha256=hashlib.sha256(final).hexdigest(),
                x_before=int(entry['playerX']), x_after=int(end['playerX'])))
        report['status'] = 'PASS_34_EXACT_NATIVE_WHOLE_TERRAIN_CALLS'
    except Exception as exc:
        report.update(status='FAIL_RETAINED', call=call, error=repr(exc), traceback=traceback.format_exc())
        raise
    finally:
        (O / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], sha(O / 'summary.json'))


if __name__ == '__main__':
    main()
