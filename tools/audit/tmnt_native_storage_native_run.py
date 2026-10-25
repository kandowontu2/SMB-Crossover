"""Run one already frozen native TMNT pilot, preserving its first failure."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
from tmnt_native_storage_driver import ROOT, CURRENT, sha


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prepared', type=Path, required=True)
    p.add_argument('--timeout', type=int, default=180)
    a = p.parse_args()
    out = a.prepared.resolve()
    assert not out.is_relative_to(ROOT)
    assert not (out / 'native-result.json').exists() and not (out / 'host.log').exists()
    bind = json.loads((out / 'binding.json').read_text())
    rom, script, emulator = Path(bind['ROM']), out / 'run.lua', Path('C:/mesen2/Mesen.exe')
    assert sha(rom) == bind['ROM_sha256'] and sha(script) == bind['script_sha256']
    assert sha(emulator) == bind['emulator_sha256']
    assert all(sha(Path(name)) == value for name, value in bind['dependencies'].items())
    assert sha(ROOT / 'build/smb-crossover-mmc5-expanded.nes') == CURRENT
    with (out / 'host.log').open('w') as log:
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'tools/audit/run_mesen_isolated.py'), '--output', str(out),
                                 '--emulator', str(emulator), str(script), str(rom), '--timeout', str(a.timeout),
                                 '--option=--doNotSaveSettings', '--option=--nes.ramPowerOnState=AllZeros',
                                 '--option=--nes.randomizeCpuPpuAlignment=false', '--option=--nes.randomizeMapperPowerOnState=false'],
                                cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    report = bind | dict(passed=False, exit=result.returncode, runner_sha256=sha(Path(__file__)))
    for name in ['result.json', 'ownership-guards.json', 'chr-commit.json', 'mode-readback.json',
                 'first-hardware-failure.json', 'native-source-hardware.json']:
        if (out / name).exists(): report[name] = json.loads((out / name).read_text())
    report['passed'] = result.returncode == 0 and all(report.get(name, {}).get('passed') for name in ['result.json', 'ownership-guards.json', 'chr-commit.json', 'native-source-hardware.json']) and report.get('mode-readback.json', {}).get('actual') == bind['behavior']
    (out / 'native-result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(passed=report['passed'], exit=result.returncode, ROM_sha256=bind['ROM_sha256'],
                          behavior=bind['behavior'], failure=report.get('first-hardware-failure.json'))))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
