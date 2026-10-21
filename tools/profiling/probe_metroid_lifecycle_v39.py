"""CPU-only native music lifecycle experiment; changes no build/traversal ROM.

Candidate memory uses the fixed-size flag scanner and bypasses the eight SFX
scans only when every scanned init/continue flag is zero. All three original
scan roots remain on the active path. Music always runs, including repeat/init.
"""
from pathlib import Path
import argparse, hashlib, json, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/profiling'))
from verify_audio_copies_v38 import AudioMemory, native
from verify_expansion_flush_v38 import bank
from probe_metroid_flags_v39 import candidate


class ExperimentMemory(AudioMemory):
    def __init__(self, original, enabled, banks, ram):
        super().__init__(original)
        self.enabled, self.banks = enabled, set(banks)
        self.stub = bytearray()
        for i, offset in enumerate((0x80, 0x88, 0x84, 0x8c, 0x81, 0x89, 0x83, 0x8b)):
            self.stub += bytes([0xad if i == 0 else 0x0d, (ram+offset)&255, (ram+offset)>>8])
        # Even an empty Multi scan does ADC FF+08 in Add8, clearing V.
        # Active scans retain every original call and its resulting flags.
        self.stub += bytes.fromhex('f0 0a 20 1b b3 20 4b b3 20 3d b3 60 b8 60')
        assert len(self.stub) == 38
        if enabled:
            # A CPU-unit injection into an unused fixed-code gap, not an edit
            # of the original ROM file. A compiled candidate is still required.
            # Current sample ends FF80 and vectors start FFFA. Never inject
            # at F100: that is live BASS_DPCM data in this checkpoint.
            assert bytes(self[0xff81:0xffa7]) == bytes([0xff])*38
            self[0xff81:0xffa7] = self.stub

    def switch(self, physical):
        super().switch(physical)
        if self.enabled and (physical&0x7f) in self.banks:
            before = bytes(self[0xb4bd:0xb4fb])
            self[0xb4bd:0xb4fb] = candidate(before)
            assert bytes(self[0xb3ca:0xb3d3]) == bytes.fromhex('20 1b b3 20 4b b3 20 3d b3')
            self[0xb3ca:0xb3d3] = bytes.fromhex('20 81 ff ea ea ea ea ea ea')

    def __setitem__(self, key, value):
        if isinstance(key, int) and key == 0x4017:
            self.writes.append((key, value))
        super().__setitem__(key, value)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('rom', type=Path)
    p.add_argument('--after', type=Path, help='Actual compiled candidate; disables all code injection')
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    b, B = native.load(a.rom)
    c, C = native.load(a.after or a.rom)
    assert all(C[n] == v for n,v in B.items() if v < 0x8000 and n in C), 'Unchanged private/native RAM ABI'
    banks = [bank(a.rom, f'MetroidAudio{s}') for s in (0, 1, 2, 4, 5)]
    for cpu, enabled in ((b, False), (c, True)):
        cpu.memory = ExperimentMemory(cpu.memory, enabled and a.after is None, banks, B['SmAudioRam'])
    stats, count = {}, 0

    def call(entry, number):
        nonlocal count
        results, clocks = [], []
        for cpu, L in ((b, B), (c, C)):
            cpu.memory.writes.clear()
            cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = number&255, (number*17)&255, (number*31)&255, (number*59)&255, 0xfd
            cpu.stPushWord(0x7eff)
            cpu.pc, cpu.processorCycles = L[entry], 0
            steps = 0
            while cpu.pc != 0x7f00:
                cpu.step()
                steps += 1
                assert steps < 15000, (entry, number, hex(cpu.pc))
            results.append((cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp,
                            bytes(cpu.memory[:0x100])+bytes(cpu.memory[0x200:0x8000]), list(cpu.memory.writes)))
            clocks.append(cpu.processorCycles)
        assert results[0] == results[1], {
            'entry': entry, 'case': number, 'registers': [r[:5] for r in results],
            'writes': [r[-1] for r in results],
            'memory_differences': [(hex(i), b.memory[i], c.memory[i]) for i in range(0x8000)
                if not 0x100 <= i < 0x200 and b.memory[i] != c.memory[i]][:12]}
        st = stats.setdefault(entry, {'cases': 0, 'min_delta': 10000, 'max_delta': -10000})
        st['cases'] += 1
        st['min_delta'] = min(st['min_delta'], clocks[1]-clocks[0])
        st['max_delta'] = max(st['max_delta'], clocks[1]-clocks[0])
        count += 1

    for stream in range(8):
        for cpu, L in ((b, B), (c, C)):
            cpu.memory[:0x8000] = [0]*0x8000
            for n, v in (('SelectedCharacter', 2), ('OperMode', 1), ('CurrentBank', 128), ('BankShadow', 0x47), ('CurrentBankC', 13)):
                if n in L:
                    cpu.memory[L[n]] = v
            for i in range(12):
                cpu.memory[0xe0+i] = (stream*53+i*17)&255
        call('SamusAudioInit', stream)
        for tick in range(2000):
            for cpu, L in ((b, B), (c, C)):
                put = lambda n, v: cpu.memory.__setitem__(L[n], v)
                put('FrameCounter', tick&255)
                put('PlayerStatus', stream%3)
                put('AreaMusicQueue', (1, 2, 4, 8, 16, 32, 64, 128)[stream] if tick in (0, 768, 1408) else 0)
                put('EventMusicQueue', (1, 2, 4, 8, 16, 32, 64, 128)[stream] if tick in (512, 1024) else 0)
                # Alternating long idle periods and dense actual effect flags.
                active = (tick//128)&1
                put('Square1SoundQueue', (1 << ((tick+stream)%8)) if active and tick%5 == 0 else 0)
                put('SmSfx', (1 << ((tick//3+stream)%7)) if active and tick%3 == 0 else 0)
                put('GamePauseStatus', 1 if 1600 <= tick < 1604 else 0)
                put('OperMode', 0 if tick == 1800 else 1)
            call('SamusAudioUpdate', stream*2000+tick)
    report = {'result': 'passed', 'cases': count, 'stats': stats,
              'rom_sha256': hashlib.sha256(a.rom.read_bytes()).hexdigest(),
              'after_sha256': hashlib.sha256(a.after.read_bytes()).hexdigest() if a.after else None,
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'compared': 'A/X/Y/allP/SP, every byte below8000 except discarded stack, ordered4000..4015/4017/5000..5015 writes',
              'scope': ('Actual compiled driver comparison' if a.after else 'CPU-memory-only scanner/empty-SFX prototype')+' across eight2000-update coherent music/effect/pause/mute/restart streams',
              'limits': ['CPU units only; no interrupts, PPU, waveform, DMC or traversal.',
                         'Private intermediate write sequences differ; complete final private memory and hardware writes match.']}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2)+'\n')
    print('PASS', count, stats, flush=True)


if __name__ == '__main__':
    main()
