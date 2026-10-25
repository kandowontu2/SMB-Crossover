"""Observe real Grant replays for native NMI/IRQ/stack/SMC safety."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--routes', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    report = dict(passed=False, goal_complete=False, ROM_sha256=sha(a.rom), cases=[],
        driver_sha256=sha(Path(__file__)), native_workers=1,
        scope='Read-only exact independent cold-menu Grant Easy/Hard replay through movable1-2. Actual NMI/IRQ activity, live-stack floor, immutable SMC write and invalid-code-execution guards; completed-loop movement and raw controls/trace unchanged. This is real-route stack/audio-NMI evidence, not a universal every-ability interrupt proof.')
    for mode in ('easy', 'hard'):
        route = a.routes / ('discover-grant-' + mode + '-v1')
        target = a.output / mode
        with (a.output / (mode + '.log')).open('w') as log:
            code = subprocess.run([sys.executable, str(ROOT / 'tools/audit/reproduce_sophia_lock_og.py'),
                '--rom', str(a.rom), '--route', str(route), '--output', str(target),
                '--expect', 'repaired', '--until-clear', '--movement'], cwd=ROOT,
                stdout=log, stderr=subprocess.STDOUT).returncode
        result = dict(mode=mode, exit=code, passed=False, folder=str(target))
        if code == 0:
            proof = json.loads((target / 'proof.json').read_text())
            assert proof['passed'] and proof['ROM_sha256'] == report['ROM_sha256']
            observed = proof['observed']
            assert observed['repaired'] and observed['observed_minimum_SP'] >= 0x7a
            assert observed['nmis'] > 4000 and observed['irqs'] > 4000
            result.update(passed=True, observed=observed, proof_sha256=sha(target / 'proof.json'))
        report['cases'].append(result)
        (a.output / 'progress.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(result), flush=True)
    report['passed'] = all(case['passed'] for case in report['cases'])
    (a.output / 'proof.json').write_text(json.dumps(report, indent=2) + '\n')
    return 0 if report['passed'] else 1


if __name__ == '__main__': main()
