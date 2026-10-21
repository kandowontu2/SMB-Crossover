"""Compiled native flush and Samus audio lifecycle before/after CPU receipts."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, random, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/profiling'))
from verify_expansion_flush_v38 import TraceMemory, bank
spec = importlib.util.spec_from_file_location('native_unit', ROOT/'tools/audit/verify_native_relocation.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


class AudioMemory(TraceMemory):
    def __setitem__(self, key, value):
        if isinstance(key, int) and 0x4000 <= key <= 0x4015:
            self.writes.append((key, value))
        super().__setitem__(key, value)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('before', type=Path)
    p.add_argument('after', type=Path)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    b, B = native.load(a.before)
    c, C = native.load(a.after)
    assert all(C[n] == v for n, v in B.items() if v < 0x8000 and n in C)
    for cpu in (b, c):
        cpu.memory = AudioMemory(cpu.memory)
    flush_banks = [bank(path, 'GuestAudioNativeFlush') for path in (a.before, a.after)]
    stats = {}
    count = 0

    def call(entry, physical, number):
        nonlocal count
        results, clocks = [], []
        for cpu, L in ((b, B), (c, C)):
            if physical is not None:
                cpu.memory.switch(physical)
            cpu.memory.writes.clear()
            cpu.a, cpu.x, cpu.y, cpu.p = number&255, (number*17)&255, (number*31)&255, (number*59)&255
            cpu.sp = 0xfd
            cpu.stPushWord(0x7eff)
            cpu.pc = L[entry]
            cpu.processorCycles = 0
            steps = 0
            while cpu.pc != 0x7f00:
                cpu.step()
                steps += 1
                assert steps < 15000, (entry, number, hex(cpu.pc))
            results.append((cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp,
                            bytes(cpu.memory[:0x100])+bytes(cpu.memory[0x200:0x8000]),
                            list(cpu.memory.writes)))
            clocks.append(cpu.processorCycles)
        assert results[0] == results[1], {'entry': entry, 'case': number, 'registers': [r[:5] for r in results],
            'writes': [r[-1] for r in results], 'memory_differences': [(hex(i), b.memory[i], c.memory[i]) for i in range(0x8000)
                if not 0x100 <= i < 0x200 and b.memory[i] != c.memory[i]][:12]}
        s = stats.setdefault(entry, {'cases': 0, 'min_delta': 10000, 'max_delta': -10000})
        s['cases'] += 1
        s['min_delta'] = min(s['min_delta'], clocks[1]-clocks[0])
        s['max_delta'] = max(s['max_delta'], clocks[1]-clocks[0])
        count += 1

    rng = random.Random(0x20238a)
    for number in range(1024):
        ram = [0]*0x8000
        for n in ('GuestNativeApu', 'GuestApuLast', 'GuestNativeDirty', 'GuestFxDirty'):
            ram[B[n]:B[n]+16] = [rng.randrange(256) for _ in range(16)]
        if number%4 == 0:
            ram[B['GuestApuLast']:B['GuestApuLast']+16] = ram[B['GuestNativeApu']:B['GuestNativeApu']+16]
        if number%4 == 1:
            ram[B['GuestNativeDirty']:B['GuestNativeDirty']+16] = [0]*16
        for cpu in (b, c):
            cpu.memory[:0x8000] = ram
        assert flush_banks[0] == flush_banks[1]
        call('GuestAudioNativeFlush', flush_banks[0], number)

    for stream in range(8):
        for cpu, L in ((b, B), (c, C)):
            cpu.memory[:0x8000] = [0]*0x8000
            for n, v in (('SelectedCharacter', 2), ('OperMode', 1), ('CurrentBank', 128), ('BankShadow', 0x47), ('CurrentBankC', 13)):
                if n in L:
                    cpu.memory[L[n]] = v
            for i in range(12):
                cpu.memory[0xe0+i] = (stream*53+i*17)&255
        call('SamusAudioInit', 0, stream)
        for tick in range(112):
            for cpu, L in ((b, B), (c, C)):
                put = lambda n, v: cpu.memory.__setitem__(L[n], v)
                put('FrameCounter', tick)
                put('PlayerStatus', stream%3)
                put('AreaMusicQueue', (1, 2, 4, 8, 16, 32, 64, 128)[stream] if tick in (0, 48, 80) else 0)
                put('EventMusicQueue', (1, 2, 4, 8, 16, 32, 64, 128)[stream] if tick in (32, 64) else 0)
                put('Square1SoundQueue', (1 << ((tick+stream)%8)) if tick%5 == 0 else 0)
                put('SmSfx', (1 << ((tick//3+stream)%7)) if tick%3 == 0 else 0)
                put('GamePauseStatus', 1 if 72 <= tick < 76 else 0)
                put('OperMode', 0 if tick == 96 else 1)
            call('SamusAudioUpdate', None, stream*112+tick)
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    report = {'result': 'passed', 'cases': count, 'entries': stats,
              'before_sha256': sha(a.before), 'after_sha256': sha(a.after), 'script_sha256': sha(Path(__file__)),
              'compared': 'A/X/Y/allP/SP, every byte below8000 except discarded stack, and ordered4000..4015/5000..5015 writes',
              'scope': 'Initialized actual RP2A03 native-flush units and eight coherent Samus music/effect/pause/mute/restart lifecycles',
              'limits': ['No PPU, interrupts, sampled waveform, DMC playback or ordinary-input traversal.', 'The C000 mapper is not executed by these fixed/A000 entry paths; actual IRQ/CHR timing needs emulator checks.']}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2)+'\n')
    print('PASS', count, stats)


if __name__ == '__main__':
    main()
