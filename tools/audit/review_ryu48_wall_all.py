"""Classify the native origin of all nine retained Ryu horizontal snaps."""
from pathlib import Path
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
PROBE = ROOT / 'build/roster-through-2-2/root48-ryu-wall-passive-all-a-10-v0-mmc3'
CONTROL = PROBE.parent / 'root48-ryu-fixed-a-10-v0-mmc3'
OUT = ROOT / 'build/verification/root48-ryu-wall-passive-all-a-review.json'
FILES = ('audio-events.csv', 'chr.csv', 'events.csv', 'inputs.csv', 'oam.csv',
         'render.csv', 'scroll-writes.csv', 'stomp-events.csv', 'trace.csv')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not OUT.exists(), 'Never overwrite observed evidence'
    manifest = json.loads((PROBE / 'manifest.json').read_text())
    assert manifest['verified_through_2_2'] and manifest['full_frame_audit']
    assert manifest['controller_only'] and not manifest['memory_or_register_writes']
    assert manifest['rom_sha256'] == 'e9c1a98961d26389bc54eefc4c63e725f8ddd91c0e801cf9c553bdf774ece1f1'
    assert manifest['result']['frames'] == 23432 and manifest['result']['deaths'] == 0
    streams = {}
    for name in FILES:
        assert (PROBE / name).read_bytes() == (CONTROL / name).read_bytes(), name
        streams[name] = dict(sha256=sha(PROBE / name), bytes=(PROBE / name).stat().st_size, literal_equal=True)
    with (PROBE / 'native-wall-receipts.csv').open(newline='') as file:
        rows = list(csv.DictReader(file))
    assert len(rows) == 4751 and all(row['nmi'] == row['irq'] == '0' for row in rows)
    earlier = ROOT / 'build/verification/ryu48-full-route-review-fixed-a/report.json'
    steps = json.loads(earlier.read_text())['normal_movement_large_steps']
    assert len(steps) == 9
    cases = []
    for step in steps:
        frame = step['frame']
        selected = [row for row in rows if int(row['frame']) == frame]
        entry = [row for row in selected if row['event'] == 'SamusStopAtWallBanked']
        leave = [row for row in selected if row['event'] == 'WallClampRTS']
        feet = [row for row in selected if row['event'] == 'GuestFootContactSide']
        assert len(entry) == len(leave) == len(feet) == 1
        entry, leave, feet = entry[0], leave[0], feet[0]
        assert step['dx'] == -9 and entry['R0'] == '1'
        assert int(entry['playerX']) == int(step['before']['x']) + 1
        assert entry['playerX'] == feet['playerX']
        assert int(leave['playerX']) == int(step['after']['x'])
        assert int(leave['playerX']) - int(entry['playerX']) == -10
        assert int(feet['cycle']) < int(entry['cycle']) < int(leave['cycle'])
        bad_velocity = [row for row in rows if frame-12 <= int(row['frame']) < frame
            and row['event'] == 'ExpandedMovement::Integrate' and row['wall'] == '1'
            and int(row['qVX']) == 101035]
        assert bad_velocity, frame
        cases.append(dict(frame=frame, world=step['after']['world'], level=step['after']['level'],
            trace_dx=-9, native_clamp_dx=-10, foot=feet, clamp_entry=entry,
            clamp_return=leave, attached_walking_velocity_receipts=bad_velocity))
    report = dict(result='all-nine-native-foot-clamp-origins-confirmed', script_sha256=sha(Path(__file__)),
        controller_only=True, emulated_memory_or_register_writes=False,
        observer_neutrality_streams=streams, manifest_sha256=sha(PROBE / 'manifest.json'),
        control_manifest_sha256=sha(CONTROL / 'manifest.json'), earlier_review_sha256=sha(earlier),
        hook_metadata_sha256=sha(ROOT / 'build/verification/ryu48-wall-drift-readonly-a/hooks.json'),
        observer_sha256=sha(PROBE / 'policy.lua'), native_receipts=len(rows),
        native_receipts_sha256=sha(PROBE / 'native-wall-receipts.csv'), cases=cases,
        movement_clean=False, runtime_patch_applied=False, final_recording=False,
        qualification='Every candidate has actual guarded GuestFootContactSide -> wall-clamp -> RTS receipts, preceded by nonzero walking velocity during wall attachment. Only the first grab has separately classified normal-air source admission geometry. This does not establish exact source rectangles/cache phase for all nine, supply a completed repair, or certify full audiovisual fidelity.')
    OUT.write_text(json.dumps(report, indent=2) + '\n')
    print(report['result'], '9 exact audit streams;', len(rows), 'native receipts')


if __name__ == '__main__':
    main()
