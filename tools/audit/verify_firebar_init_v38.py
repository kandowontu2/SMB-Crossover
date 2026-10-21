"""Native short/long firebar initialization with arbitrary stale cache counts."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, re

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('native_unit', ROOT/'tools/audit/verify_native_relocation.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


def linked_bank(path, entry):
    debug = path.with_suffix('.dbg').read_text()
    s = re.search(r'sym\s+[^\n]*name="'+entry+r'",[^\n]*seg=(\d+)', debug)
    assert s
    segment = re.search(r'seg\s+id='+s[1]+r',name="[^"]+",start=(0x[0-9a-fA-F]+),[^\n]*ooffs=(\d+)', debug)
    assert segment and 0xa000 <= int(segment[1], 16) < 0xc000
    return (int(segment[2])-(int(segment[1], 16)-0xa000)-16)//8192


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('before', type=Path)
    p.add_argument('after', type=Path)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    b, B = native.load(a.before)
    c, C = native.load(a.after)
    assert all(C[n] == v for n, v in B.items() if v < 0x8000 and n in C)
    stats = {}
    count = 0
    banks = {entry: linked_bank(a.before, entry) for entry in ('InitShortFirebar', 'InitLongFirebar')}
    assert banks == {entry: linked_bank(a.after, entry) for entry in banks}
    for entry in ('InitShortFirebar', 'InitLongFirebar'):
        for slot in range(6):
            for stale in range(256):
                ram = [0]*0x8000
                ram[B['CurrentBank']] = banks[entry] | (128 if b.memory.rom[6]>>4 == 5 else 0)
                ram[B['ObjectOffset']] = slot
                ram[B['Enemy_ID']+slot] = 0x1b+stale%4 if entry == 'InitShortFirebar' else 0x1f
                ram[B['Enemy_Flag']+slot] = 1
                ram[B['Enemy_X_Position']+slot] = stale
                ram[B['Enemy_Y_Position']+slot] = (stale*13)&255
                ram[B['Enemy_PageLoc']+slot] = stale%3
                ram[B['FirebarPartCount']:B['FirebarPartCount']+6] = [(stale+i*29)&255 for i in range(6)]
                ram[B['FirebarPartCount']+slot] = stale
                for i in range(8):
                    ram[B['R0']+i] = (stale*17+i*23)&255
                # Include a completely occupied native duplicate pool.
                if stale&1:
                    ram[B['Enemy_Flag']:B['Enemy_Flag']+6] = [1]*6
                results, clocks = [], []
                for cpu, L, corrected in ((b, B, False), (c, C, True)):
                    cpu.memory[:0x8000] = ram
                    cpu.memory.switch(banks[entry])
                    cpu.memory[L['SMCCODE']:L['SMCCODE']+len(cpu.memory.smc)] = cpu.memory.smc
                    cpu.a, cpu.x, cpu.y, cpu.p = stale, slot, (stale*31)&255, (stale*59)&255
                    cpu.sp = 0xfd
                    cpu.stPushWord(0x7eff)
                    cpu.pc = L[entry]
                    cpu.processorCycles = 0
                    steps = 0
                    while cpu.pc != 0x7f00:
                        cpu.step()
                        steps += 1
                        assert steps < 3000, (entry, slot, stale, hex(cpu.pc))
                    assert cpu.memory[L['FirebarPartCount']+slot] == (0 if corrected else stale)
                    snapshot = bytearray(cpu.memory[:0x8000])
                    snapshot[0x100:0x200] = bytes(256)
                    snapshot[L['FirebarPartCount']+slot] = 0
                    results.append((cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp, bytes(snapshot)))
                    clocks.append(cpu.processorCycles)
                assert results[0] == results[1], (entry, slot, stale, [r[:5] for r in results])
                st = stats.setdefault(entry, {'cases': 0, 'min_delta': 1000, 'max_delta': -1000})
                st['cases'] += 1
                st['min_delta'] = min(st['min_delta'], clocks[1]-clocks[0])
                st['max_delta'] = max(st['max_delta'], clocks[1]-clocks[0])
                count += 1
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    report = {'result': 'passed', 'cases': count, 'entries': stats,
              'actual_entry_banks': banks,
              'before_sha256': sha(a.before), 'after_sha256': sha(a.after), 'script_sha256': sha(Path(__file__)),
              'compared': 'A/X/Y/allP/SP and every byte below8000 except discarded stack and the one intentionally cleared owner count',
              'independent_oracle': 'Newly initialized owner count is0 for every stale byte0..255; no other cache slot/native state changes',
              'scope': 'Actual compiled short/long native initializer units, six owner slots, free/full duplicate pools; no interrupts/PPU/traversal'}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2)+'\n')
    print('PASS', count, stats)


if __name__ == '__main__':
    main()
