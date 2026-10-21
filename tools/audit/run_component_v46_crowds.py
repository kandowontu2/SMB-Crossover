"""Matched unchanged twenty-scene controls for all thirteen character IDs."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
source = ROOT / 'build/profiling/plain-walking-v45b-crowd-retention-a/profile-source.lua'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source) == '240e35a03fadb0adc785e43b07a0b643c44179b6e9ea6b56b360968a15eb43cb'
out = ROOT / 'build/verification/component46-all-character-crowds-a'
out.mkdir(exist_ok=False)
report = dict(result='running', seeded_arenas_not_routes=True, source_sha256=sha(source), runs=[])
rp = out / 'report.json'
for version, checkpoint, tag in (
    ('v45', 'roster-audit-v45', 'samus46-all-before-a'),
    ('v46a', 'roster-audit-v46-provisional-a', 'samus46-all-after-a'),
):
    log = out / f'{version}.log'
    cmd = [sys.executable, 'tools/profiling/profile_plain_walking.py', version, '--tag', tag,
           '--characters', ','.join(map(str, range(13))), '--mappers', 'mmc3,mmc5',
           '--source', str(source), '--checkpoint', str(ROOT / 'build/checkpoints' / checkpoint)]
    with log.open('w') as f:
        result = subprocess.run(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT)
    report['runs'].append(dict(version=version, command=cmd, exit=result.returncode, log_sha256=sha(log)))
    rp.write_text(json.dumps(report, indent=2) + '\n')
    assert result.returncode == 0
    print('PASS', version, 'twenty scenes x13 characters x2 mappers', flush=True)
comparison = out / 'comparison.json'
result = subprocess.run([sys.executable, 'tools/profiling/compare_plain_walking.py',
    'build/profiling/plain-walking-v45-samus46-all-before-a',
    'build/profiling/plain-walking-v46a-samus46-all-after-a', '--output', str(comparison)], cwd=ROOT)
report.update(result='compared-preserved' if result.returncode == 0 else 'comparison-negative-preserved',
              compare_exit=result.returncode, comparison_sha256=sha(comparison) if comparison.exists() else None)
rp.write_text(json.dumps(report, indent=2) + '\n')
raise SystemExit(result.returncode)
