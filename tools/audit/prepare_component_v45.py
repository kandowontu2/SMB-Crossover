"""Apply/freeze two source-backed weapon repairs, leaving acceptance separate."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'build/checkpoints/roster-audit-v44'
OUT = ROOT / 'build/checkpoints/roster-audit-v45-provisional-a'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--freeze-built', action='store_true', help='Freeze existing compiled pair after the separately preserved preparation guard failure')
args = parser.parse_args()
assert not OUT.exists(), 'Never overwrite a frozen candidate'
patches = {
    'build/verification/ryu-koopa-primary45-proposal-b/ryu-primary32-koopa-main-secondary.patch':
        '6d17060c38f56172649e9b9a35fec22291399d192f8d1c6f3daba2a43843c78f',
    'build/verification/bill-flare43-terrain-repair-proposal/flare-only-ground-filter.patch':
        '8dbc7a72af02ce94533319f3318e6b5e1e6a38ed3423ae36747af8b734d431e0',
}
assert all(sha(ROOT / n) == h for n, h in patches.items())
if not args.freeze_built:
    assert sha(ROOT / 'src/megaman_weapons.s') == 'd3de04482397c068a6a40bd9e54d14ecd91f64bae91c1729e11323e6c714c494'
control = json.loads((ROOT / 'build/verification/bill-flare-v1-observer-control44-first-a/report.json').read_text())
assert control['status'] == 'passed-neutrality' and len(control['runs']) == 2
for run in control['runs']:
    assert run['native_exit'] == run['check_exit'] == 0
    assert all(sha(ROOT / n) == h for n, h in run['files'].items())
    receipt = json.loads((ROOT / run['neutrality_receipt']).read_text())
    assert receipt['neutrality_passed'] and receipt['complete_original_csv_byte_identity']
    assert not receipt['actual_ground70_contacts'] and not receipt['qualified_case_slots']
with zipfile.ZipFile(OLD / 'source-v44.zip') as z:
    previous = json.loads(z.read('archived-file-hashes.json'))
if not args.freeze_built:
    assert {n for n, h in previous.items() if sha(ROOT / n) != h} == {'README.md'}
    patch_args = [str(ROOT / n) for n in patches]
    subprocess.run(['git', 'apply', '--check', *patch_args], cwd=ROOT, check=True)
    subprocess.run(['git', 'apply', *patch_args], cwd=ROOT, check=True)
proposal = ROOT / 'build/verification/ryu-koopa-primary45-proposal-b/megaman_weapons.proposed.s'
expected = proposal.read_text(encoding='utf8')
marker = 'Terrain:\n  ldy MmSlot\n  lda MmBulletType,y\n'
insertion = ('  ; Bill Flare requests Brick/Enemy, not GroundNonBrick. Brick/question\n'
    '  ; dispatch already occurred above; keep probing so later corners may hit.\n'
    '  cmp #70                       ; AV_FLARE43 after the +27 collision bridge.\n'
    '  bne :+\n    jmp ProbeNext\n  :\n')
assert expected.count(marker) == 1
assert (ROOT / 'src/megaman_weapons.s').read_text(encoding='utf8') == expected.replace(marker, marker + insertion, 1)
assert {n for n, h in previous.items() if sha(ROOT / n) != h} == {'README.md', 'src/megaman_weapons.s'}
if not args.freeze_built:
    for mapper in ('mmc3', 'mmc5'):
        with (ROOT / f'build/verification/roster-audit-v45a-build-{mapper}.log').open('w') as log:
            subprocess.run([sys.executable, 'tools/build.py', '--mapper', mapper], cwd=ROOT,
                stdout=log, stderr=subprocess.STDOUT, check=True)
OUT.mkdir()
roms = {}
for mapper in ('mmc3', 'mmc5'):
    for ext in ('.nes', '.dbg', '.lbl', '.map', '.lst'):
        p = ROOT / f'build/smb-crossover-{mapper}{ext}'
        shutil.copyfile(p, OUT / p.name)
        assert sha(p) == sha(OUT / p.name)
    rom = OUT / f'smb-crossover-{mapper}.nes'
    before, after = (OLD / rom.name).read_bytes(), rom.read_bytes()
    assert before[:16] == after[:16] and before[16 + 524288:] == after[16 + 524288:]
    dbg = rom.with_suffix('.dbg').read_text()
    seg = re.search(r'seg\s+[^\n]*name="GUEST",start=(0x[0-9A-Fa-f]+),size=(0x[0-9A-Fa-f]+),[^\n]*ooffs=(\d+)', dbg)
    assert seg and int(seg[1], 16) == 0xa000 and int(seg[2], 16) == 8017
    assert (int(seg[3]) - 16) // 8192 == 8
    roms[mapper] = dict(sha256=sha(rom), dbg_sha256=sha(rom.with_suffix('.dbg')),
        lbl_sha256=sha(rom.with_suffix('.lbl')), guest_bytes=8017, guest_free=175)
report = dict(status='provisional-not-accepted', checkpoint=OUT.name, parent=OLD.name,
    goal_complete=False, created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    runtime_sources={'src/megaman_weapons.s': sha(ROOT / 'src/megaman_weapons.s')},
    patches=patches, roms=roms, tests_complete=False,
    static_budget_note='Original8009-byte static prediction failed against actual8017 bytes; guard negative/code/log preserved separately. Eight-byte source of discrepancy requires independent classification before acceptance.',
    scope='Ryu type32 Character sword vs Koopa0/3 main+secondary admission, integer positions; Flare70 ignores nonbrick ground, retains brick/question/enemy dispatch. No shared fixture/golden changes.',
    limits=['Upgraded33/winged IDs/other Character and projectile source geometry remain separately qualified.',
        'Koopa walking-to-shell health/lifecycle, subpixel/current-cache phase and full roster routes/recordings remain open.'])
(OUT / 'candidate.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2), flush=True)
