"""Run one frozen Mac physical-resource profile only when a worker is granted."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--packet', type=Path, required=True)
    p.add_argument('--mode', choices=['easy', 'hard'], required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--emulator', type=Path, required=True)
    p.add_argument('--timeout', type=int, default=300)
    a = p.parse_args()
    z = json.loads((a.packet/'preparation.json').read_text())
    profile = next(q for q in z['profiles'] if q['mode'] == a.mode)
    frozen = a.packet/'frozen-current'
    assert sha(frozen/'candidate.nes') == z['ROM_sha256']
    assert sha(Path(profile['script'])) == profile['script_sha256']
    assert sha(frozen/'final_mac_items_native.lua') == z['fixture_sha256']
    ledger = json.loads((frozen/'bindings.json').read_text())
    assert all(sha(frozen/n) == h for n, h in ledger.items())
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    for ext in ['.nes', '.dbg', '.lbl', '.map']:
        shutil.copy2(frozen/('candidate'+ext), out/('candidate'+ext))
    shutil.copy2(profile['script'], out/'run.lua')
    with (out/'host.log').open('w') as log:
        run = subprocess.run([sys.executable, str(ROOT/'tools/audit/run_mesen_isolated.py'),
            '--output', str(out), '--emulator', str(a.emulator), str(out/'run.lua'),
            str(out/'candidate.nes'), '--timeout', str(a.timeout), '--option=--doNotSaveSettings',
            '--option=--nes.ramPowerOnState=AllZeros', '--option=--nes.randomizeCpuPpuAlignment=false',
            '--option=--nes.randomizeMapperPowerOnState=false'], stdout=log, stderr=subprocess.STDOUT)
    def read(n):
        return json.loads((out/n).read_text()) if (out/n).exists() else {}
    native, guards, chr_result = [read(n) for n in ['native-result.json', 'ownership-guards.json', 'chr-commit.json']]
    result = dict(passed=run.returncode == 0 and all(q.get('passed', False) for q in [native, guards, chr_result])
                  and native.get('actual_mode_readback') == profile['numeric_mode'],
                  ROM_sha256=z['ROM_sha256'], mode=a.mode, exit=run.returncode,
                  emulator_sha256=sha(a.emulator), runner_sha256=sha(Path(__file__)),
                  preparation_sha256=sha(a.packet/'preparation.json'), fixture_sha256=z['fixture_sha256'],
                  script_sha256=sha(out/'run.lua'), native=native, guards=guards, CHR=chr_result,
                  first_failure=read('first-failure.json'), goal_complete=False)
    (out/'proof.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(passed=result['passed'], mode=a.mode, first_failure=result['first_failure'], output=str(out))))
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
