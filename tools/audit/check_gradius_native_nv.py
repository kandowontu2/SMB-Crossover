"""Compare the relocated Gradius driver with original NSF/Mesen APU events."""
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json
import re
from py65.devices.mpu6502 import MPU

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-roster-audio-nv')


class Bus(list):
    def __init__(self, body):
        super().__init__([0] * 65536)
        self[0xa000:0xa000 + len(body)] = body
        self.events = []; self.ram_writes = set()

    def __setitem__(self, key, value):
        if isinstance(key, int):
            if 0x4000 <= key <= 0x4017: self.events.append([key - 0x4000, value])
            elif key < 0xa000 and not 0x100 <= key < 0x200: self.ram_writes.add(key)
        super().__setitem__(key, value)


def main():
    packet = ARCHIVE / 'gradius-relocated-v2'
    source = ARCHIVE / 'gradius-native-v2'
    coverage = json.loads((source / 'coverage.json').read_text())
    labels = {name: int(address, 16) for address, name in re.findall(
        r'^al ([0-9A-Fa-f]+) \.([\w]+)$', (packet / 'raw-test.lbl').read_text(), re.M)}
    body = (packet / 'raw-test.bin').read_bytes()
    manifest = json.loads((ROOT / 'reference/new-roster-audio/captures-manifest.json').read_text())
    calls_manifest_path = ARCHIVE / 'gradius-call-captures-v1/manifest.json'
    calls_manifest = json.loads(calls_manifest_path.read_text())
    assert {int(k) for k in calls_manifest} == set(coverage['source']['tracks'].values())
    events = frames = matched_mesen = 0; summaries = {}
    for song, record in coverage['results'].items():
        song = int(song)
        original_raw = gzip.decompress((source / f'source-{song:02d}.json.gz').read_bytes())
        assert hashlib.sha256(original_raw).hexdigest() == record['sha256']
        original = json.loads(original_raw)
        bus = Bus(body); cpu = MPU(memory=bus)
        def call(address, a=None):
            if a is not None: cpu.a = a; cpu.x = cpu.y = 0
            cpu.sp = 0xfd; bus[0x1fe] = 255; bus[0x1ff] = 1; cpu.pc = address
            for _ in range(30000):
                if cpu.pc == 0x200: return
                assert 0xa000 <= cpu.pc < 0xc000, (song, hex(cpu.pc))
                cpu.step()
            raise AssertionError(('driver call did not return', song, hex(cpu.pc)))
        call(labels['GradiusNativeInit'], song - 1)
        assert bus.events == original[0], (song, 'init', bus.events, original[0])
        bus.events.clear()
        for frame in range(record['frames']):
            call(labels['GradiusNativePlay'])
            assert bus.events == original[frame + 1], (song, frame, bus.events, original[frame + 1])
            events += len(bus.events); bus.events.clear(); frames += 1
        assert all(a in {0xdd, 0xde, 0xf6, 0xf7, 0xfa, 0xfb} or 0x7000 <= a < 0x7050
                   for a in bus.ram_writes), (song, sorted(bus.ram_writes))
        key = f'vic-{song:02d}'
        capture = calls_manifest.get(str(song))
        if capture:
            raw = gzip.decompress(Path(capture['path']).read_bytes())
            assert hashlib.sha256(raw).hexdigest() == capture['capture_sha256']
            expected = [[] for _ in range(capture['result']['calls'] + 1)]
            for row in csv.DictReader(io.StringIO(raw.decode())):
                f, reg, val = (int(row[field]) for field in ('call', 'register', 'value'))
                if f < len(expected): expected[f].append([reg, val])
            assert original[:len(expected)] == expected, key
            matched_mesen += len(expected)
        old_first_difference = None
        if key in manifest:
            old = manifest[key]
            raw = gzip.decompress(Path(old['path']).read_bytes())
            assert hashlib.sha256(raw).hexdigest() == old['capture_sha256']
            old_frames = [[] for _ in range(old['frames'])]
            for row in csv.DictReader(io.StringIO(raw.decode())):
                f, reg, val = map(int, row.values())
                if f < len(old_frames): old_frames[f].append([reg, val])
            candidate = [[[reg, val] for reg, val in frame if reg <= 21]
                         for frame in original[:len(old_frames)]]
            old_first_difference = next((i for i, (a, b) in enumerate(zip(candidate, old_frames)) if a != b), None)
        summaries[song] = dict(frames=record['frames'], relocated_APU_events_equal_original=True,
                               bounded_state_writes=True,
                               independent_mesen_calls=0 if not capture else capture['result']['calls'],
                               old_endFrame_capture_first_difference=old_first_difference)
        print('PASS track', song, record['frames'], flush=True)
    report = dict(passed=True, native_songs=len(summaries), relocated_source_frames=frames,
                  ordered_APU_events=events, independent_original_Mesen_calls_including_init=matched_mesen,
                  raw_test_binary_sha256=hashlib.sha256(body).hexdigest(),
                  preparation_sha256=hashlib.sha256((packet / 'preparation.json').read_bytes()).hexdigest(),
                  coverage_sha256=hashlib.sha256((source / 'coverage.json').read_bytes()).hexdigest(), songs=summaries,
                  new_original_Mesen_capture_manifest_sha256=hashlib.sha256(calls_manifest_path.read_bytes()).hexdigest(),
                  scope='Standalone original-engine relocation and channel RAM isolation. Not installed or linked game/mixer/NMI validation.')
    (packet / 'golden-proof.json').write_text(json.dumps(report, indent=2) + '\n')
    local = ROOT / 'build/verification/roster-audio-nv'
    (local / 'gradius-native-location.json').write_text(json.dumps(dict(
        path=str(packet / 'golden-proof.json'), sha256=hashlib.sha256((packet / 'golden-proof.json').read_bytes()).hexdigest(),
        passed=True, native_songs=len(summaries), source_frames=frames, mesen_driver_calls_including_init=matched_mesen), indent=2) + '\n')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
