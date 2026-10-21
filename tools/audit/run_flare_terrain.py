"""Bind/run the frozen26-case Flare terrain oracle; never revise goldens."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import run_mesen
BASE = ROOT / 'build/verification/bill-flare43-terrain-preparation'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('checkpoint', type=Path)
p.add_argument('--tag', required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output.resolve()
assert out.is_relative_to(ROOT) and not out.exists()
out.mkdir(parents=True)
assert sha(BASE / 'core.lua') == 'b1b90f2317df65bf5af583085d1e18c5a4ce26cde04a650375e2ddfe4e5ad847'
report = dict(status='running', core_sha256=sha(BASE / 'core.lua'), traversal_proof=False, runs=[])
rp = out / 'report.json'
rp.write_text(json.dumps(report, indent=2) + '\n')
for mapper in ('mmc3', 'mmc5'):
    rom = a.checkpoint.resolve() / f'smb-crossover-{mapper}.nes'
    tag = a.tag + '-' + mapper
    subprocess.run([sys.executable, str(BASE / 'bind.py'), '--rom', str(rom), '--tag', tag], check=True)
    binding = BASE / 'bindings' / tag
    wrapper = binding / f'bill-flare-terrain-{tag}.lua'
    meta = json.loads((binding / 'binding.json').read_text())
    assert meta['rom']['sha256'] == sha(rom) and meta['core']['sha256'] == report['core_sha256']
    code = run_mesen.run(wrapper, rom, timeout=180)
    target = binding / 'run'
    shutil.copyfile(ROOT / f'build/verification/{rom.stem}-{wrapper.stem}.log', target / 'native.log')
    completion = json.loads((target / 'completion.json').read_text())
    with (target / 'cases.csv').open(newline='') as f:
        cases = list(csv.DictReader(f))
    report['runs'].append(dict(mapper=mapper, exit=code, rom_sha256=sha(rom),
        binding=str((binding / 'binding.json').relative_to(ROOT)), binding_sha256=sha(binding / 'binding.json'),
        completion=completion, cases=cases,
        files={str(f.relative_to(ROOT)): sha(f) for f in target.iterdir() if f.is_file()}))
    rp.write_text(json.dumps(report, indent=2) + '\n')
    assert sha(BASE / 'core.lua') == report['core_sha256']
    assert code == 0 and completion['cases'] == 26 and completion['passed'] is True
    assert completion['rom_sha256'] == sha(rom)
    assert len(cases) == 26 and all(c['result'] == 'PASS' for c in cases)
    print(mapper, 'PASS26 unchanged Flare source cases', flush=True)
report.update(status='passed-frozen-source-component', total_cases=52, source_disagreements=0, coverage_failures=0)
rp.write_text(json.dumps(report, indent=2) + '\n')
