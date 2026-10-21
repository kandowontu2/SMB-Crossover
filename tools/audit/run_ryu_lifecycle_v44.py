"""Run the unchanged frozen C lifecycle oracle on a new ROM checkpoint."""
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
a = p.parse_args()
out = a.output.resolve()
assert out.is_relative_to(ROOT) and not out.exists()
out.mkdir(parents=True)
core = ROOT / 'build/verification/ryu-slash-lifecycle43-preparation-c/component-c.lua'
assert sha(core) == '235f9ce482962490ddc7e4a03fde0782dc7cf7399858b9c0c1839d22a89cfca8'
report = dict(completed=False, traversal_proof=False, frozen_core=str(core),
    core_sha256=sha(core), expected='all source lifecycle/contact cases pass; four phase cases per mapper remain telemetry only', runs=[])
rp = out / 'report.json'
rp.write_text(json.dumps(report, indent=2) + '\n')
for mapper in ('mmc3', 'mmc5'):
    rom = a.checkpoint.resolve() / f'smb-crossover-{mapper}.nes'
    bind = out / mapper
    subprocess.run([sys.executable, str(ROOT / 'build/verification/ryu-wall-cancel44-preparation/rebind_frozen_C.py'),
        '--rom', str(rom), '--expected-rom-sha256', sha(rom), '--out', str(bind)], check=True)
    meta = json.loads((bind / 'binding.json').read_text())
    assert meta['rom_sha256'] == sha(rom) and meta['component_sha256'] == sha(core)
    wrapper = Path(meta['wrapper'])
    code = run_mesen.run(wrapper, rom, timeout=180)
    target = bind / 'future-emulator-output'
    log = ROOT / f'build/verification/{rom.stem}-{wrapper.stem}.log'
    shutil.copyfile(log, target / 'native.log')
    result = json.loads((target / 'result.json').read_text())
    report['runs'].append(dict(mapper=mapper, exit=code, rom_sha256=sha(rom),
        binding_sha256=sha(bind / 'binding.json'), wrapper_sha256=sha(wrapper), result=result,
        files={str(f.relative_to(out)): sha(f) for f in target.iterdir() if f.is_file()}))
    rp.write_text(json.dumps(report, indent=2) + '\n')
    assert sha(core) == report['core_sha256']
    assert code == 0 and result['cases'] == result['completed'] == 20
    assert result['mismatches'] == 0 and not result['failures'], result
    print(mapper, 'PASS', result['completed'], 'frozen C lifecycle cases', flush=True)
report.update(completed=True, total_cases=40, total_mismatches=0)
rp.write_text(json.dumps(report, indent=2) + '\n')
print('PASS40 frozen C; phase telemetry is not an animation timing proof', flush=True)
