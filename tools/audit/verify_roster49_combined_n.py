"""One full current-fixture run on private combined N; retain every result."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
N = ROOT / 'build/verification/root49-combined-private-build-n'
SOURCE = N / 'source'
OWN = N / 'qa-suite-a'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not OWN.exists()
    built = json.loads((N / 'report.json').read_text())
    assert built['status'] == 'PASS-private-exact-disjoint-combination-build-only'
    assert all(sha(SOURCE / n) == h for n, h in built['source408_hashes'].items())
    vine = ROOT / 'build/verification/ryu49k-vine-abi-component-a/root-cache-full-b/report.json'
    v = json.loads(vine.read_text())
    assert v['status'] == 'PASS_EXPLICIT_COMPILED_VINE_ABI_OAM_SMC_STACK_COMPONENT'
    assert all(x['passed'] == 13568 for x in v['cases'].values())
    sys.path.insert(0, str(ROOT / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    assert used + 300_000_000 < 30_000_000_000
    OWN.mkdir()
    copies = [p.relative_to(ROOT).as_posix() for p in (ROOT / 'tests').rglob('*') if p.is_file()]
    copies += ['tools/verify.py', 'tools/run_mesen.py', 'tools/luigi_native_review.py', 'tools/playthroughs/roster_audit.lua']
    for n in copies:
        target = SOURCE / n
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            assert sha(target) == sha(ROOT / n), n
        else:
            shutil.copyfile(ROOT / n, target)
    baseline = [f'build/smb-crossover-mmc3-baseline{x}' for x in ('.nes', '.lbl', '.dbg')]
    assert sha(SOURCE / baseline[0]) == built['original_baseline_sha256']
    inputs = {n: sha(SOURCE / n) for n in copies + baseline}
    argv = [sys.executable, 'tools/verify.py', '--mmc5', '--checkpoint', 'build', '--jobs', '2']
    report = dict(status='running', goal_complete=False, accepted_release=False,
                  argv=argv, cwd=str(SOURCE), compiled_report_sha256=sha(N / 'report.json'),
                  full_vine_report_sha256=sha(vine), fixture_and_runner_hashes=inputs,
                  workspace_before_bytes=used, reserve_bytes=300_000_000,
                  original_global_verification_outputs_touched=False)
    def save():
        (OWN / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    with (OWN / 'full-suite.log').open('w', encoding='utf-8') as log:
        done = subprocess.run(argv, cwd=SOURCE, stdout=log, stderr=subprocess.STDOUT)
    assert all(sha(SOURCE / n) == h for n, h in inputs.items())
    assert all(sha(SOURCE / n) == h for n, h in built['source408_hashes'].items())
    summary = SOURCE / 'build/verification/summary-build.json'
    data = json.loads(summary.read_text())
    passed = done.returncode == 0 and data['result'] == 'passed'
    report.update(status='PASS-full-current-fixture-run' if passed else 'FAIL-retained',
                  exit=done.returncode, cases=len(data['cases']), failures=data['failures'],
                  source408_exact_after=True, fixtures_exact_after=True, summary_sha256=sha(summary),
                  full_suite_log_sha256=sha(OWN / 'full-suite.log'), workspace_after_bytes=workspace_bytes(ROOT))
    save()
    print(json.dumps({k: v for k, v in report.items() if k != 'fixture_and_runner_hashes'}), flush=True)
    raise SystemExit(not passed)

if __name__ == '__main__':
    main()
