"""Run the byte-frozen Bill AV observer controls; preserve every outcome."""
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
OUT = ROOT / 'build/verification/bill-flare-v1-observer-control44-first-a'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(BASE / 'preparation-receipt.json') == 'a95c57036e77f8402edf89b600b368751c3e669f11e77b19a0b5fa85236aca0e'
assert sha(BASE / 'observer.lua') == '9af09ea52d34bd93917d324fa5a1a5ca0503aaf7b8e9e7e2be1b983faeb19f58'
assert sha(BASE / 'check.py') == 'e4e9f33cd61b79d23fbbf54e5496ebc593b76cc811a9828b10ed4470fba4fb69'
OUT.mkdir(exist_ok=False)
report = dict(status='running', runs=[], observer_sha256=sha(BASE / 'observer.lua'), checker_sha256=sha(BASE / 'check.py'))
rp = OUT / 'report.json'
rp.write_text(json.dumps(report, indent=2) + '\n')
for mapper in ('mmc3', 'mmc5'):
    tag = 'control44-' + mapper
    binding = BASE / 'bindings' / tag
    meta = json.loads((binding / 'binding.json').read_text())
    rom = ROOT / meta['rom']['path']
    assert sha(rom) == meta['rom']['sha256']
    wrapper = binding / f'bill-flare-v1-observer-{tag}.lua'
    assert not any((binding / 'run').iterdir()), 'Do not overwrite native observations'
    code = run_mesen.run(wrapper, rom, timeout=180)
    log = ROOT / f'build/verification/{rom.stem}-{wrapper.stem}.log'
    frozen_log = binding / 'native.log'
    shutil.copyfile(log, frozen_log)
    check = subprocess.run([sys.executable, str(BASE / 'check.py'), '--binding', str(binding / 'binding.json'),
        '--native-log', str(frozen_log), '--exit-code', str(code)], capture_output=True, text=True)
    (binding / 'check.log').write_text(check.stdout + check.stderr)
    receipt = binding / 'neutrality-receipt.json'
    report['runs'].append(dict(mapper=mapper, native_exit=code, check_exit=check.returncode,
        rom_sha256=sha(rom), binding_sha256=sha(binding / 'binding.json'), native_log_sha256=sha(frozen_log),
        neutrality_receipt=str(receipt.relative_to(ROOT)) if receipt.exists() else None,
        neutrality_receipt_sha256=sha(receipt) if receipt.exists() else None,
        files={str(p.relative_to(ROOT)): sha(p) for p in binding.rglob('*') if p.is_file()}))
    rp.write_text(json.dumps(report, indent=2) + '\n')
    print(mapper, 'native', code, 'checker', check.returncode, flush=True)
    print(check.stdout + check.stderr, flush=True)
report['status'] = 'passed-neutrality' if all(q['native_exit'] == q['check_exit'] == 0 for q in report['runs']) else 'failed-preserved-for-classification'
rp.write_text(json.dumps(report, indent=2) + '\n')
raise SystemExit(0 if report['status'] == 'passed-neutrality' else 1)
