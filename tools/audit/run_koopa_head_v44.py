"""Execute frozen Koopa Character-sword arenas without assuming the outcome."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import run_mesen
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('checkpoint', type=Path)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--component', choices=('a', 'b'), default='a')
a = p.parse_args()
out = a.output.resolve()
assert out.is_relative_to(ROOT) and not out.exists()
out.mkdir(parents=True)
core = ROOT / f'build/verification/koopa-head-admission44-component-{a.component}/component-{a.component}.lua'
binder = core.parent / 'bind_candidate.py'
assert sha(core) == dict(a='cf8d8a73b039415ed9da97c106c4180f75545aaca244c60ea29ab6c2f9e85e6d',
    b='694deb25b4961742736830f5310334e6feba744536577877f7a8da5c39255321')[a.component]
report = dict(status='running', completed=False, traversal_proof=False,
    core_sha256=sha(core), binder_sha256=sha(binder), runner_sha256=sha(Path(__file__)), runs=[])
rp = out / 'report.json'
rp.write_text(json.dumps(report, indent=2) + '\n')
for mapper in ('mmc3', 'mmc5'):
    rom = a.checkpoint.resolve() / f'smb-crossover-{mapper}.nes'
    bind = out / mapper
    subprocess.run([sys.executable, str(binder), '--rom', str(rom),
        '--expected-rom-sha256', sha(rom), '--out', str(bind)], check=True)
    meta = json.loads((bind / 'binding.json').read_text())
    wrapper = Path(meta['wrapper'])
    assert meta['rom_sha256'] == sha(rom) and meta['core_sha256'] == sha(core)
    code = run_mesen.run(wrapper, rom, timeout=180)
    target = bind / 'future-emulator-output'
    shutil.copyfile(ROOT / f'build/verification/{rom.stem}-{wrapper.stem}.log', target / 'native.log')
    result = json.loads((target / 'result.json').read_text()) if (target / 'result.json').exists() else None
    report['runs'].append(dict(mapper=mapper, exit=code, rom_sha256=sha(rom),
        binding_sha256=sha(bind / 'binding.json'), result=result,
        files={str(f.relative_to(out)): sha(f) for f in target.iterdir() if f.is_file()}))
    rp.write_text(json.dumps(report, indent=2) + '\n')
    assert sha(core) == report['core_sha256'] and sha(binder) == report['binder_sha256']
    assert result and result['cases'] == result['completed'] == 28, (mapper, code, result)
    print(mapper, 'COMPLETED', result['completed'], 'setup', result['setup_failures'],
        'source assertions', result['source_disagreements'], flush=True)
report.update(status='executed-component-needs-classification', completed=True,
    total_cases=sum(q['result']['completed'] for q in report['runs']),
    setup_failures=sum(q['result']['setup_failures'] for q in report['runs']),
    source_disagreements=sum(q['result']['source_disagreements'] for q in report['runs']))
rp.write_text(json.dumps(report, indent=2) + '\n')
print('PRESERVED all original observations; classify coverage before drawing conclusions', flush=True)
