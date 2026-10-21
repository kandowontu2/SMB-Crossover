"""Run the unchanged suite in K's isolated source checkout; retain old outputs."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
K = ROOT / 'build/verification/root49-integrated-private-build-k'
OWN = K / 'qa-suite-b'
FRESH = K / 'source'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not OWN.exists()
    built = json.loads((K / 'report.json').read_text())
    assert built['status'] == 'PASS-integrated-build-only-not-accepted'
    assert all(sha(FRESH / n) == h for n, h in built['source407_hashes'].items())
    sys.path.insert(0, str(ROOT / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    assert used + 300_000_000 < 30_000_000_000, used
    OWN.mkdir()
    for path in (ROOT / 'tests').rglob('*'):
        if not path.is_file():
            continue
        target = FRESH / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            assert sha(target) == sha(path), target
        else:
            shutil.copyfile(path, target)
    copies = ['tools/verify.py', 'tools/run_mesen.py', 'tools/luigi_native_review.py', 'tools/playthroughs/roster_audit.lua']
    copies += [f'build/smb-crossover-mmc3-baseline{ext}' for ext in ('.nes', '.lbl', '.dbg')]
    for name in copies:
        target = FRESH / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            assert sha(target) == sha(ROOT / name), name
        else:
            shutil.copyfile(ROOT / name, target)
    inputs = {p.relative_to(FRESH).as_posix(): sha(p) for p in (FRESH / 'tests').rglob('*') if p.is_file()}
    inputs.update({n: sha(FRESH / n) for n in copies})
    argv = [sys.executable, 'tools/verify.py', '--mmc5', '--checkpoint', 'build', '--jobs', '2']
    report = dict(status='running', goal_complete=False, argv=argv, cwd=str(FRESH),
                  compiled_report_sha256=sha(K / 'report.json'), fixture_and_runner_hashes=inputs,
                  workspace_before_bytes=used, reserve_bytes=300_000_000,
                  old_global_verification_outputs_touched=False, source407_exact_before=True)
    path = OWN / 'report.json'
    path.write_text(json.dumps(report, indent=2) + '\n')
    with (OWN / 'full-suite.log').open('w', encoding='utf-8') as output:
        result = subprocess.run(argv, cwd=FRESH, stdout=output, stderr=subprocess.STDOUT)
    assert all(sha(FRESH / n) == h for n, h in inputs.items()), 'QA inputs changed during suite'
    assert all(sha(FRESH / n) == h for n, h in built['source407_hashes'].items()), 'Compiler sources changed during suite'
    summary = FRESH / 'build/verification/summary-build.json'
    data = json.loads(summary.read_text())
    report.update(status='PASS' if result.returncode == 0 and data['result'] == 'passed' else 'FAIL-retained',
                  exit=result.returncode, cases=len(data['cases']), failures=data['failures'],
                  source407_exact_after=True, fixtures_exact_after=True, summary_sha256=sha(summary),
                  full_suite_log_sha256=sha(OWN / 'full-suite.log'), workspace_after_bytes=workspace_bytes(ROOT))
    path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'fixture_and_runner_hashes'}), flush=True)
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
