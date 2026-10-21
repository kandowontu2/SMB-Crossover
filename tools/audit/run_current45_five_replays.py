"""Fresh ordinary-input replay attempts; historical proofs are inputs only."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
inputs = ROOT / 'build/verification/current45-five-character-replay-inputs.json'
assert sha(inputs) == '73bec78806068640978ac5857b8fdeef6546f5279aecb4c658503ad79f952ca6'
plan = json.loads(inputs.read_text())
out = ROOT / 'build/verification/current45-five-character-replay-results-a'
out.mkdir(exist_ok=False)
runner = ROOT / 'tools/playthroughs/roster_run.py'
report = dict(classification='Fresh current45 controller-only full-audit attempts; no recordings',
              plan_sha256=sha(inputs), runner_sha256=sha(runner), runs=[], result='running')
rp = out / 'report.json'

def save():
    rp.write_text(json.dumps(report, indent=2) + '\n')

save()
for row in plan:
    p = row['current45_proposal']
    rom = Path(p['ROM'])
    fixed = Path(row['source_inputs'])
    assert sha(rom) == p['ROM_sha256'] and sha(fixed) == row['inputs_sha256']
    assert not Path(p['output']).exists()
    log = out / (row['character'].lower() + '.log')
    cmd = [sys.executable, str(runner), '--character', str(row['character_id']),
           '--variant', str(row['variant']), '--mapper', row['mapper'], '--rom', str(rom),
           '--tag', p['tag'], '--replay', str(fixed), '--frames', str(row['frame_bound'] + 10),
           '--timeout', '300']
    print('START', row['character'], flush=True)
    with log.open('w') as stream:
        result = subprocess.run(cmd, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
    manifest = Path(p['output']) / 'manifest.json'
    actual = json.loads(manifest.read_text()) if manifest.exists() else {}
    report['runs'].append(dict(character=row['character'], command=cmd, exit=result.returncode,
        log=str(log.relative_to(ROOT)), log_sha256=sha(log),
        manifest_sha256=sha(manifest) if manifest.exists() else None,
        verified_through_2_2=actual.get('verified_through_2_2', False), result=actual.get('result')))
    save()
    print('END', row['character'], result.returncode, actual.get('verified_through_2_2', False), flush=True)
report['result'] = 'all-five-current45-pass' if all(q['verified_through_2_2'] for q in report['runs']) else 'partial-results-preserved'
save()
print(report['result'], flush=True)
