"""TMNT actual-menu native component matrix with declared RAM arrangements."""
from pathlib import Path
import argparse
import concurrent.futures
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
NAMES = ('leonardo', 'raphael', 'michelangelo', 'donatello')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--suite', choices=('equipment', 'primary', 'boss', 'ammo'), required=True)
    a = p.parse_args()
    out = a.output.resolve(); assert out.exists()
    driver = ROOT / f'tests/tmnt-{a.suite}.lua'
    observer = ROOT / 'tests/tmnt-equipment-observer.lua'
    assert not (out / f'{a.suite}-results.json').exists()

    def run(case):
        variant, name, mode = case
        folder = out / f'{a.suite}-{name}-{mode}-v1'
        folder.mkdir(exist_ok=False)
        cfg = dict(mode=mode, variant=variant, observer=observer.as_posix())
        script = folder / 'run.lua'
        script.write_text('TMNT_CFG={' + ','.join(k + '=' + json.dumps(v) for k, v in cfg.items())
                          + '}\ndofile(' + json.dumps(driver.as_posix()) + ')\n')
        command = [sys.executable, str(ROOT / 'tools/audit/run_mesen_isolated.py'),
                   '--output', str(folder), str(script), str(a.rom.resolve()), '--timeout', '60',
                   '--option=--nes.ramPowerOnState=AllZeros',
                   '--option=--nes.randomizeCpuPpuAlignment=false',
                   '--option=--nes.randomizeMapperPowerOnState=false']
        r = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        (folder / 'host.log').write_text(r.stdout + r.stderr)
        result = json.loads((folder / 'result.json').read_text()) if (folder / 'result.json').exists() else None
        return dict(identity=name, variant=variant, mode=mode, exit=r.returncode,
                    passed=r.returncode == 0 and result is not None and result.get('passed') is True,
                    folder=str(folder), result=result, script_sha256=sha(script))

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(run, [(v, n, m) for v, n in enumerate(NAMES) for m in ('easy', 'hard')]))
    report = dict(passed=all(r['passed'] for r in results), ROM_sha256=sha(a.rom),
                  suite=a.suite, native_actual_menu_entry=True, component_RAM_writes=True,
                  equipment_granted_only_by_physical_collision=a.suite == 'equipment',
                  driver_sha256=sha(driver), observer_sha256=sha(observer), runs=results,
                  scope='Explicit native component arrangements, not untouched natural campaign reward delivery.')
    (out / f'{a.suite}-results.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
