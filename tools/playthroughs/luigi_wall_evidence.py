"""Pin the genuine Luigi33 negative and separately labeled native0 unit control."""
from pathlib import Path
import csv
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
routes = ROOT / 'build/roster-through-2-2'
negative = routes / 'mls-v33-luigi-water-write-probe-a-8-v0-mmc3'
control = routes / 'mls-v33-luigi-water-native-contact-control-a-8-v0-mmc3'
verification = ROOT / 'build/verification'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def rows(p):
    with p.open(newline='') as f:
        return list(csv.DictReader(f))

# The standard route runner cannot infer a diagnostic policy's explicit writes.
# Correct its generated metadata so this unit control is never a route proof.
manifest_path = control / 'manifest.json'
manifest = json.loads(manifest_path.read_text())
manifest.update(controller_only=False, memory_or_register_writes=True,
                synthetic_fixture=True, verified_through_2_2=False,
                fixture_override='SelectedCharacter=0 only inside SamusStopAtWall; restored8 at actual caller return',
                fixture_positions_velocities_terrain_written=False)
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')

ntrace, ctrace = rows(negative / 'trace.csv'), rows(control / 'trace.csv')
projection = ('frame', 'poll', 'world', 'level', 'x', 'y', 'yHigh', 'vx', 'vy', 'state', 'buttons', 'camera')
assert [[r[k] for k in projection] for r in ntrace if int(r['frame']) <= 15257] == [
    [r[k] for k in projection] for r in ctrace if int(r['frame']) <= 15257]
assert (negative / 'inputs.csv').read_bytes() == (control / 'inputs.csv').read_bytes()
nr, cr = rows(negative / 'position-writes.csv'), rows(control / 'position-writes.csv')

def receipt(source, frame, pc, old, value):
    matching = [r for r in source if r['event'] == 'Player_X_Position'
                and (r['frame'], r['pc'], r['old'], r['value']) == tuple(map(str, (frame, pc, old, value)))]
    assert len(matching) == 1
    return matching[0]

receipts = {
    'ordinary_guest_15258': receipt(nr, 15258, 0xea11, 0x3e, 0x31),
    'ordinary_guest_15259': receipt(nr, 15259, 0xea11, 0x31, 0x21),
    'native_control_15258': receipt(cr, 15258, 0x9cd7, 0x3e, 0x3d),
    'native_control_15259': receipt(cr, 15259, 0x9cd7, 0x3d, 0x3c),
}
files = {}
for directory in (negative, control):
    for name in ('manifest.json', 'inputs.csv', 'trace.csv', 'position-writes.csv', 'policy.lua'):
        p = directory / name
        files[p.relative_to(ROOT).as_posix()] = sha(p)
files[(control / 'synthetic-contact-overrides.csv').relative_to(ROOT).as_posix()] = sha(control / 'synthetic-contact-overrides.csv')
for mapper in ('mmc3', 'mmc5'):
    rom = ROOT / f'build/checkpoints/roster-audit-v33/smb-crossover-{mapper}.nes'
    files[rom.relative_to(ROOT).as_posix()] = sha(rom)
    for extension in ('csv', 'log'):
        p = verification / f'smb-crossover-{mapper}-native-wall-corner.{extension}'
        copy = verification / f'mls-v33-{mapper}-native-wall-corner-negative.{extension}'
        if not copy.exists():
            # Standard output names may now contain a newer positive run.
            # Validate the negative before preserving it, and never replace
            # an already archived receipt with another checkpoint's output.
            candidate = rows(verification / f'smb-crossover-{mapper}-native-wall-corner.csv')
            assert len(candidate) == 2 and candidate[1]['character'] == '8' and candidate[1]['dx'] == '-13'
            shutil.copyfile(p, copy)
        files[copy.relative_to(ROOT).as_posix()] = sha(copy)
    fixture_rows = rows(verification / f'mls-v33-{mapper}-native-wall-corner-negative.csv')
    assert fixture_rows[0]['character'] == '0' and fixture_rows[0]['dx'] == '-1' and fixture_rows[0]['nativeCalls'] == '1'
    assert fixture_rows[1]['character'] == '8' and fixture_rows[1]['dx'] == '-13' and fixture_rows[1]['nativeCalls'] == '0'
    control_file = verification / f'mls-v33-{mapper}-native-wall-corner-mario-control.csv'
    native_rows = rows(control_file)
    assert len(native_rows) == 324 and all(r['character'] == '0' and r['nativeCalls'] == '1' for r in native_rows)
    files[control_file.relative_to(ROOT).as_posix()] = sha(control_file)
files['tests/native-wall-corner.lua'] = sha(ROOT / 'tests/native-wall-corner.lua')
fixture_snapshot = verification / 'mls-v33-native-wall-corner-fixture.lua'
if fixture_snapshot.exists():
    assert sha(fixture_snapshot) == sha(ROOT / 'tests/native-wall-corner.lua'), 'Archived negative fixture must remain immutable'
else:
    shutil.copyfile(ROOT / 'tests/native-wall-corner.lua', fixture_snapshot)
files[fixture_snapshot.relative_to(ROOT).as_posix()] = sha(fixture_snapshot)
packet = {
    'checkpoint': 'roster-audit-v33', 'confirmed_dispatch_defect': True,
    'ordinary_negative_memory_writes': False, 'native_control_is_synthetic_not_clear': True,
    'identical_input_csv': True, 'identical_position_motion_input_projection_through_frame': 15257,
    'receipts': receipts,
    'unit_negative_both_mappers': 'case1 native0 exact-1; case2 Luigi8 wrong-13/no native ImpedePlayerMove',
    'independent_native0_matrix_both_mappers': '324 cases each, all pass with exact expected native direction/velocity/flags/remainder preservation',
    'proposed_fix': 'SamusStopAtWall: native Luigi8 must join native Mario0 clc/rts bypass; all other guest paths retained',
    'files_sha256': files,
}
out = verification / 'luigi-v33-native-wall-negative.json'
out.write_text(json.dumps(packet, indent=2) + '\n')
print(json.dumps({'packet': str(out), 'sha256': sha(out), 'checks': 'passed'}))
