"""Run frozen read-only AV observers on45a, preserving all native outcomes."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import run_mesen

BASE = ROOT / 'build/verification/bill-flare-v1-golden-observer-preparation'
CP = ROOT / 'build/checkpoints/roster-audit-v45-provisional-a'
OUT = ROOT / 'build/verification/bill-flare-v1-observer-candidate45a-first-a'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(BASE / 'observer.lua') == '9af09ea52d34bd93917d324fa5a1a5ca0503aaf7b8e9e7e2be1b983faeb19f58'
assert sha(BASE / 'check.py') == 'e4e9f33cd61b79d23fbbf54e5496ebc593b76cc811a9828b10ed4470fba4fb69'
candidate = json.loads((CP / 'candidate.json').read_text())
OUT.mkdir(exist_ok=False)
report = dict(status='running', runs=[], goal_complete=False)
rp = OUT / 'report.json'
rp.write_text(json.dumps(report, indent=2) + '\n')
for mapper in ('mmc3', 'mmc5'):
    rom = CP / f'smb-crossover-{mapper}.nes'
    assert sha(rom) == candidate['roms'][mapper]['sha256']
    tag = 'candidate45a-first-a-' + mapper
    control = BASE / 'bindings' / ('control44-' + mapper) / 'neutrality-receipt.json'
    subprocess.run([sys.executable, str(BASE / 'bind.py'), '--rom', str(rom), '--tag', tag,
        '--purpose', 'candidate', '--neutrality', str(control)], check=True)
    binding = BASE / 'bindings' / tag
    wrapper = binding / f'bill-flare-v1-observer-{tag}.lua'
    code = run_mesen.run(wrapper, rom, timeout=180)
    log = ROOT / f'build/verification/{rom.stem}-{wrapper.stem}.log'
    frozen_log = binding / 'native.log'
    shutil.copyfile(log, frozen_log)
    check = subprocess.run([sys.executable, str(BASE / 'check.py'), '--binding', str(binding / 'binding.json'),
        '--native-log', str(frozen_log), '--exit-code', str(code)], capture_output=True, text=True)
    (binding / 'check.log').write_text(check.stdout + check.stderr)
    inspection = binding / 'candidate-contact-inspection.json'
    report['runs'].append(dict(mapper=mapper, native_exit=code, check_exit=check.returncode,
        rom_sha256=sha(rom), binding_sha256=sha(binding / 'binding.json'), native_log_sha256=sha(frozen_log),
        inspection=str(inspection.relative_to(ROOT)) if inspection.exists() else None,
        inspection_sha256=sha(inspection) if inspection.exists() else None,
        files={str(p.relative_to(ROOT)): sha(p) for p in binding.rglob('*') if p.is_file()}))
    rp.write_text(json.dumps(report, indent=2) + '\n')
    print(mapper, 'native', code, 'checker', check.returncode, flush=True)
    print(check.stdout + check.stderr, flush=True)
report['status'] = 'passed-observer-inspection' if all(q['native_exit'] == q['check_exit'] == 0 for q in report['runs']) else 'failed-preserved-for-classification'
rp.write_text(json.dumps(report, indent=2) + '\n')
raise SystemExit(0 if report['status'] == 'passed-observer-inspection' else 1)
