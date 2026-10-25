"""Bounded cold-menu TMNT routes and independent exact-input verification."""
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
    p.add_argument('--phase', choices=('discover', 'replay'), required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert out.exists()
    runner = ROOT / 'tools/playthroughs/new_roster_run_nd.py'
    policy = ROOT / 'tools/playthroughs/new_roster_policy_nd.lua'
    assert not (out / f'{a.phase}-results.json').exists()

    def run(case):
        name, mode = case
        folder = out / f'{a.phase}-{name}-{mode}-v1'
        command = [sys.executable, str(runner), name, '--rom', str(a.rom.resolve()),
                   '--output', str(folder), '--behavior', mode, '--frames', '8000',
                   '--capture', '1' if a.phase == 'replay' else '12',
                   '--chr-commit', '--policy', str(policy), '--timeout', '90']
        discovery = out / f'discover-{name}-{mode}-v1'
        if a.phase == 'replay':
            command += ['--replay', str(discovery / 'inputs.csv')]
        r = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        (out / f'{a.phase}-{name}-{mode}-host.log').write_text(r.stdout + r.stderr)
        manifest = json.loads((folder / 'manifest.json').read_text()) if (folder / 'manifest.json').exists() else {}
        result = manifest.get('result', {})
        passed = (r.returncode == 0 and result.get('cleared') and result.get('deaths') == 0
                  and manifest.get('chr_commit', {}).get('passed') is True)
        comparisons = {}
        if a.phase == 'replay' and r.returncode == 0:
            for n in ('inputs.csv', 'trace.csv'):
                comparisons[n] = (folder / n).read_bytes() == (discovery / n).read_bytes()
            passed = passed and all(comparisons.values())
        return dict(identity=name, mode=mode, exit=r.returncode, passed=bool(passed),
                    frames=result.get('frames'), deaths=result.get('deaths'),
                    stage_entries=result.get('stage_entries'),
                    exact_discovery_bytes=comparisons, manifest_sha256=sha(folder / 'manifest.json'),
                    folder=str(folder), failure=result.get('failure'))

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(run, [(n, m) for n in NAMES for m in ('easy', 'hard')]))
    report = dict(passed=all(r['passed'] for r in results), ROM_sha256=sha(a.rom),
                  runner_sha256=sha(runner), policy_sha256=sha(policy), phase=a.phase,
                  controller_only=True, memory_writes=False, runs=results)
    (out / f'{a.phase}-results.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
