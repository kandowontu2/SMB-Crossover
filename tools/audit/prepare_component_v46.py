"""Freeze a provisional MMC5 Samus idle optimization; acceptance is separate."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'build/checkpoints/roster-audit-v45'
OUT = ROOT / 'build/checkpoints/roster-audit-v46-provisional-a'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert not OUT.exists(), 'Never replace frozen candidate evidence'
with zipfile.ZipFile(OLD / 'source-v45.zip') as z:
    previous = json.loads(z.read('archived-file-hashes.json'))
assert len(previous) == 401
assert {n for n, h in previous.items() if sha(ROOT / n) != h} == {'README.md'}
target = ROOT / 'src/samus_weapons.s'
assert sha(target) == '592a3473c22a0bdf2f740b792f57542e62c349b01f1fd1d793acbe7f95a537cd'
patch = ROOT / 'build/verification/samus-idle-v44-readonly-proposal/samus-idle-unapplied.patch'
OUT.mkdir()
report = dict(status='preparation-running-not-accepted', parent=OLD.name,
    created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    patch=dict(path=patch.relative_to(ROOT).as_posix(), sha256=sha(patch)),
    goal_complete=False, tests_complete=False, roms={})
rp = OUT / 'candidate.json'

def save():
    rp.write_text(json.dumps(report, indent=2) + '\n')

save()
subprocess.run(['git', 'apply', '--check', str(patch)], cwd=ROOT, check=True)
subprocess.run(['git', 'apply', str(patch)], cwd=ROOT, check=True)
for mapper, expected_size in (('mmc3', 8172), ('mmc5', 8177)):
    log = OUT / f'build-{mapper}.log'
    with log.open('w') as f:
        subprocess.run([sys.executable, 'tools/build.py', '--mapper', mapper], cwd=ROOT,
                       stdout=f, stderr=subprocess.STDOUT, check=True)
    for ext in ('.nes', '.dbg', '.lbl', '.map', '.lst'):
        src = ROOT / f'build/smb-crossover-{mapper}{ext}'
        shutil.copyfile(src, OUT / src.name)
    rom = OUT / f'smb-crossover-{mapper}.nes'
    before, after = (OLD / rom.name).read_bytes(), rom.read_bytes()
    assert before[:16] == after[:16] and before[16 + 524288:] == after[16 + 524288:]
    if mapper == 'mmc3':
        assert before == after, 'MMC3 must remain byte identical'
    dbg = rom.with_suffix('.dbg').read_text()
    seg = re.search(r'seg\s+[^\n]*name="SAMUS",start=(0x[0-9A-Fa-f]+),size=(0x[0-9A-Fa-f]+),[^\n]*ooffs=(\d+)', dbg)
    assert seg and int(seg[1], 16) == 0xa000 and int(seg[2], 16) == expected_size
    report['roms'][mapper] = dict(sha256=sha(rom), dbg_sha256=sha(rom.with_suffix('.dbg')),
        lbl_sha256=sha(rom.with_suffix('.lbl')), samus_bytes=expected_size, samus_free=8192-expected_size,
        byte_identical_to_parent=before == after, chr_identical=True)
    save()
files = {n: sha(ROOT / n) for n in previous}
assert {n for n, h in previous.items() if files[n] != h} == {'README.md', 'src/samus_weapons.s'}
archive = OUT / 'source-v46a.zip'
with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for n in files:
        z.writestr(n, (ROOT / n).read_bytes())
    z.writestr('archived-file-hashes.json', json.dumps(files, indent=2) + '\n')
report.update(status='provisional-not-accepted', runtime_sources={'src/samus_weapons.s':sha(target)},
    archive_sha256=sha(archive), source_count=len(files),
    scope='MMC5 active SamusWeapons with six empty slots and B released only; preserve pose/cleanup/return ABI.',
    limits=['No measured speedup or redraw improvement yet.', 'CPU/native/weapon/interrupt/crowd/full-suite controls pending.',
            'Broader roster, special-weapon, final recording and dense-scene lag work remains incomplete.'])
save()
print(json.dumps(report, indent=2), flush=True)
