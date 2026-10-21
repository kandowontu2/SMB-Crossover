"""Execute the real MMC5 expansion mixer: exact ABI/RAM/ordered hardware writes."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, random, re

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('native_unit', ROOT/'tools/audit/verify_native_relocation.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


class TraceMemory(native.NesMemory):
    def __init__(self, original):
        super().__init__(list(original), original.rom, original.smc)
        self.writes = []

    def __setitem__(self, key, value):
        if isinstance(key, int) and 0x5000 <= key <= 0x5015:
            self.writes.append((key, value))
        super().__setitem__(key, value)


def bank(path, entry):
    debug = path.with_suffix('.dbg').read_text()
    s = re.search(r'sym\s+[^\n]*name="'+entry+r'",[^\n]*val=(0x[0-9a-fA-F]+),seg=(\d+)', debug)
    assert s
    seg = re.search(r'seg\s+id='+s[2]+r',name="[^"]+",start=(0x[0-9a-fA-F]+),[^\n]*ooffs=(\d+)', debug)
    assert seg and int(seg[1], 16) == 0xa000
    return (int(seg[2])-16)//8192


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('before', type=Path)
    p.add_argument('after', type=Path)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    b, B = native.load(a.before)
    c, C = native.load(a.after)
    assert all(C[n] == v for n, v in B.items() if v < 0x8000 and n in C), 'Unchanged RAM ABI'
    assert all(cpu.memory.rom[6] >> 4 == 5 for cpu in (b, c))
    banks = [bank(path, 'GuestExpansionFlush') for path in (a.before, a.after)]
    for cpu in (b, c):
        cpu.memory = TraceMemory(cpu.memory)
    rng = random.Random(0x20238)
    stats = {}
    count = 0
    for mask in range(256):
        for pattern in range(16):
            ram = [0]*0x8000
            for n in ('GuestExpansionApu', 'GuestExpansionLast', 'GuestFxApu', 'GuestFxDirty'):
                ram[B[n]:B[n]+8] = [rng.randrange(256) for _ in range(8)]
            ram[B['GuestMixMask']] = mask
            ram[B['GuestMixChanged']] = (0, 1, 2, 3, 255, mask, mask^3, rng.randrange(256))[pattern%8]
            if pattern & 1:
                ram[B['GuestExpansionLast']:B['GuestExpansionLast']+8] = ram[B['GuestFxApu']:B['GuestFxApu']+8]
            if pattern & 2:
                ram[B['GuestFxDirty']:B['GuestFxDirty']+8] = [0]*8
            for n, size in (('GuestSweepPeriod', 2), ('GuestSweepDelta', 2), ('GuestSweepControl', 1), ('GuestSweepDivider', 1), ('GuestSweepReload', 1), ('GuestSweepTicks', 1)):
                ram[B[n]:B[n]+size] = [rng.randrange(256) for _ in range(size)]
            # Explicit sub-eight, valid, overflow and negative sweep targets.
            if pattern < 8:
                period = (0, 7, 8, 255, 256, 1023, 2047, 2048)[pattern]
                ram[B['GuestSweepPeriod']:B['GuestSweepPeriod']+2] = [period&255, period>>8]
                ram[B['GuestSweepControl']] = (pattern*17)&255
            results, clocks = [], []
            for cpu, L, physical in ((b, B, banks[0]), (c, C, banks[1])):
                cpu.memory[:0x8000] = ram
                cpu.memory.switch(physical)
                cpu.memory.writes.clear()
                cpu.a, cpu.x, cpu.y, cpu.p = count&255, (count*17)&255, (count*31)&255, (count*59)&255
                cpu.sp = 0xfd
                cpu.stPushWord(0x7eff)
                cpu.pc = L['GuestExpansionFlush']
                cpu.processorCycles = 0
                steps = 0
                while cpu.pc != 0x7f00:
                    cpu.step()
                    steps += 1
                    assert steps < 4000, (count, hex(cpu.pc))
                results.append((cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp,
                                bytes(cpu.memory[:0x100])+bytes(cpu.memory[0x200:0x8000]),
                                list(cpu.memory.writes)))
                clocks.append(cpu.processorCycles)
            assert results[0] == results[1], {
                'mask': mask, 'pattern': pattern, 'registers': [r[:5] for r in results],
                'writes': [r[-1] for r in results],
                'memory_differences': [(hex(i), b.memory[i], c.memory[i]) for i in range(0x8000)
                                       if not 0x100 <= i < 0x200 and b.memory[i] != c.memory[i]][:12],
            }
            group = 'silent-expansion' if mask&3 == 0 else 'active-pulse'
            st = stats.setdefault(group, {'cases': 0, 'min_delta': 10000, 'max_delta': -10000})
            st['cases'] += 1
            st['min_delta'] = min(st['min_delta'], clocks[1]-clocks[0])
            st['max_delta'] = max(st['max_delta'], clocks[1]-clocks[0])
            count += 1
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    report = {'result': 'passed', 'cases': count, 'stats': stats,
              'before_sha256': sha(a.before), 'after_sha256': sha(a.after), 'script_sha256': sha(Path(__file__)),
              'actual_entry_banks': banks,
              'compared': 'A/X/Y/allP/SP, every byte below8000 except discarded stack, and ordered5000..5015 writes',
              'scope': 'Initialized compiled RP2A03 MMC5 mixer units; all256 masks, dirty/changed/equal image cases, sweep boundary/arbitrary state',
              'limits': ['No PPU, interrupts, rendered pixels, audio waveform or ordinary-input traversal. Separate emulator tests remain required.']}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2)+'\n')
    print('PASS', count, stats)


if __name__ == '__main__':
    main()
