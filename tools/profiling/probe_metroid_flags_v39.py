"""Seeded CPU experiment only: a same-size native Metroid flag scanner.

This patches private CPU-unit code memory, never a traversal ROM or build input.
It compares the actual linked original for every flag value and valid table,
plus all incoming P values on the empty path, on all five imported song banks.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, random, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/profiling'))
from verify_expansion_flush_v38 import bank
spec = importlib.util.spec_from_file_location('native_unit', ROOT/'tools/audit/verify_native_relocation.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


def candidate(original):
    """B4BD..B4FA only; B4EE remains the externally referenced default RTS."""
    assert len(original) == 62
    assert original[32:45] == bytes.fromhex('48 0e') + original[1:3] + bytes.fromhex('b0 0c c8 c8 98 c9 10 d0 f4')
    assert original[45:50] == bytes([0x68, 0x8d, *original[1:3], 0x60])
    assert original[59:] == bytes.fromhex('4c ea b4')
    out = bytearray(original)
    # A shifts instead of the private memory flag; retain its original byte.
    # At least one bit is set on the active loop, so it needs no zero limit.
    # Empty return still has Y=16, C=1, A=0/NZ from the original flag.
    out[32:50] = bytes.fromhex('f0 07 0a b0 0d c8 c8 d0 f9 a0 10 38 ea ad') + original[1:3] + bytes.fromhex('ea 60')
    out[59:] = bytes.fromhex('4c ea b4')
    assert len(out) == 62 and out[49] == 0x60
    return bytes(out)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('rom', type=Path)
    p.add_argument('--after', type=Path, help='Compare an actual compiled candidate instead of injected unit code')
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    b, B = native.load(a.rom)
    c, C = native.load(a.after or a.rom)
    assert all(C[n] == v for n,v in B.items() if v < 0x8000 and n in C), 'Private/native RAM ABI'
    rng = random.Random(0x20239)
    table_offsets = (0x89, 0x8e, 0x93, 0x98, 0x9d, 0xa2, 0xa7, 0xac, 0xb1, 0xb6)
    stats, count, patches = {}, 0, {}
    for song in (0, 1, 2, 4, 5):
        physical = bank(a.rom, f'MetroidAudio{song}')
        b.memory.switch(physical)
        c.memory.switch(bank(a.after, f'MetroidAudio{song}') if a.after else physical)
        original = bytes(b.memory[0xb4bd:0xb4fb])
        modified = candidate(original)
        if a.after:
            assert bytes(c.memory[0xb4bd:0xb4fb]) == modified
        else:
            c.memory[0xb4bd:0xb4fb] = modified
        patches[song] = {'physical_bank': physical, 'before': original.hex(), 'after': modified.hex()}
        specs = [(x, flags, (flags*73+x*19+pattern*51)&255)
                 for x in table_offsets for flags in range(256) for pattern in range(4)]
        specs += [(x, 0, status) for x in table_offsets for status in range(256)]
        for x, flags, status in specs:
            ram = rng.randbytes(0x8000)
            outputs, clocks = [], []
            for cpu in (b, c):
                cpu.memory[:0x8000] = ram
                cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = flags, x, (count*29)&255, status, 0xfd
                cpu.stPushWord(0x7eff)
                cpu.pc, cpu.processorCycles = 0xb4bd, 0
                steps = 0
                while cpu.pc != 0x7f00:
                    cpu.step()
                    steps += 1
                    assert steps < 200, (song, x, flags, hex(cpu.pc))
                outputs.append((cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp,
                                bytes(cpu.memory[:0x100])+bytes(cpu.memory[0x200:0x8000])))
                clocks.append(cpu.processorCycles)
            assert outputs[0] == outputs[1], {
                'song': song, 'table': x, 'flags': flags, 'P': status,
                'registers': [o[:5] for o in outputs],
                'memory_differences': [(hex(i), b.memory[i], c.memory[i]) for i in range(0x8000)
                    if not 0x100 <= i < 0x200 and b.memory[i] != c.memory[i]][:12]}
            st = stats.setdefault('empty' if flags == 0 else 'active', {'cases': 0, 'min_delta': 10000, 'max_delta': -10000})
            st['cases'] += 1
            st['min_delta'] = min(st['min_delta'], clocks[1]-clocks[0])
            st['max_delta'] = max(st['max_delta'], clocks[1]-clocks[0])
            count += 1
    report = {'result': 'passed', 'cases': count, 'stats': stats, 'patches': patches,
              'rom_sha256': hashlib.sha256(a.rom.read_bytes()).hexdigest(),
              'after_sha256': hashlib.sha256(a.after.read_bytes()).hexdigest() if a.after else None,
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'compared': 'A/X/Y/allP/SP and every byte below8000 except discarded stack',
              'scope': 'Actual compiled scanner comparison' if a.after else 'CPU-memory injection experiment',
              'limits': ['Seeded CPU units only; no music lifecycle, interrupts, PPU, waveform or traversal.',
                         'Intermediate private flag writes differ; post-state is identical. This unit does not establish interrupt visibility.']}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2)+'\n')
    print('PASS', count, stats, flush=True)


if __name__ == '__main__':
    main()
