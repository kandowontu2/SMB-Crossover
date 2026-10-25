"""Execute the actual linked original music code and buffering helpers."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import re
from py65.devices.mpu6502 import MPU

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-roster-audio-nv')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); out = args.output
    out.mkdir(parents=True, exist_ok=False)
    rom = args.rom.read_bytes(); prg = rom[16:16 + 1024 * 1024]
    labels = {name: int(address, 16) for address, name in re.findall(
        r'^al ([0-9A-Fa-f]+) \.([\w]+)$', args.rom.with_suffix('.lbl').read_text(), re.M)}
    expected_root = ARCHIVE / 'gradius-native-v2'
    source = json.loads((expected_root / 'coverage.json').read_text())
    apu, dirty, history = [labels[name] for name in ('GuestNativeApu', 'GuestNativeDirty', 'XgLzHistory')]
    class Bus(list):
        def __init__(self):
            super().__init__([0] * 65536)
            self[0xa000:0xc000] = prg[0x7a * 8192:0x7b * 8192]
            self[0xe000:0x10000] = prg[0x7f * 8192:0x80 * 8192]
            self.events = []; self.writes = set()
        def __setitem__(self, key, value):
            if isinstance(key, int):
                if apu <= key < apu + 16: self.events.append([key - apu, value])
                elif 0x4000 <= key <= 0x4017: self.events.append([key - 0x4000, value])
                if key < 0xa000 and not 0x100 <= key < 0x200: self.writes.add(key)
            super().__setitem__(key, value)
    results = {}; frames = events = cycles = 0
    for song, record in source['results'].items():
        song = int(song)
        expected_raw = gzip.decompress((expected_root / f'source-{song:02d}.json.gz').read_bytes())
        assert hashlib.sha256(expected_raw).hexdigest() == record['sha256']
        expected = json.loads(expected_raw)
        bus = Bus(); cpu = MPU(memory=bus); peak = 0
        def call(address, a=None):
            nonlocal peak
            if a is not None: cpu.a = a; cpu.x = cpu.y = 0
            cpu.sp = 0xfd; bus[0x1fe] = 255; bus[0x1ff] = 1; cpu.pc = address
            start = cpu.processorCycles
            for _ in range(30000):
                if cpu.pc == 0x200:
                    peak = max(peak, cpu.processorCycles - start)
                    return
                assert 0xa000 <= cpu.pc < 0xc000 or 0xe000 <= cpu.pc <= 65535, (song, hex(cpu.pc))
                cpu.step()
            raise AssertionError(('native call did not return', song, hex(cpu.pc)))
        call(labels['VgEC48'], song - 1)
        assert bus.events == expected[0], (song, 'init')
        bus.events.clear()
        for frame in range(record['frames']):
            call(labels['VgED30'])
            assert bus.events == expected[frame + 1], (song, frame, bus.events, expected[frame + 1])
            events += len(bus.events); frames += 1; bus.events.clear()
        assert all(address in {0xdd, 0xde, 0xf6, 0xf7, 0xfa, 0xfb, 0x4017} or
                   history <= address < history + 80 or apu <= address < apu + 16 or dirty <= address < dirty + 16
                   for address in bus.writes), (song, sorted(bus.writes))
        cycles += cpu.processorCycles
        results[song] = dict(frames=record['frames'], ordered_source_APU_equal=True,
                             cycles=cpu.processorCycles, peak_call_cycles=peak,
                             bounded_RAM_writes=True)
        print('PASS linked track', song, record['frames'], peak, flush=True)
    report = dict(passed=True, ROM_SHA256=hashlib.sha256(rom).hexdigest(), source_songs=len(results),
                  source_frames=frames, ordered_source_APU_events=events, total_driver_cycles=cycles,
                  mean_driver_cycles_per_frame=cycles / frames, tracks=results,
                  scope='Actual linked music code plus actual linked flag-preserving APU buffering helpers, executed against original NSF events. Native NMI/mixer/gameplay validation is separate.')
    (out / 'proof.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'tracks'}), flush=True)


if __name__ == '__main__':
    main()
