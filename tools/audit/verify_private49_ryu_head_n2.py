"""Run current unchanged fixtures on the frozen private Ryu head candidate."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = ROOT / 'build/verification/agent-lsr-s2-head-n2-a'
SOURCE = PRIVATE / 'source'
OUT = PRIVATE / 'root-qa-suite-a'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    sys.dont_write_bytecode = True
    assert not OUT.exists(), 'Fresh suite only'
    frozen = PRIVATE / 'implementation-publication-freeze.json'
    assert sha(frozen) == 'b9777225aa4026bf598b0a7418ed193ca4877eab8461456d647b388d7f8d5e17'
    binding = json.loads(frozen.read_text())
    review = PRIVATE / 'actual-review-b.json'
    assert sha(review) == binding['review_sha256']
    assert json.loads(review.read_text())['behavior_native']['passed_cases'] == 196
    build = PRIVATE / 'report-b.json'
    assert sha(build) == '3d2f3f3841958b945ddbd05727e14263031a66c8aae0e0d31d6befddcad58c51'
    cat = json.loads(build.read_text())['source_catalog']
    assert len(cat) == 412 and all(sha(SOURCE / n) == h for n, h in cat.items())
    checkpoint = ROOT / 'build/checkpoints/roster-audit-v49-menu-options-s2/manifest.json'
    main_cat = json.loads(checkpoint.read_text())['source_hashes']
    assert len(main_cat) == 410 and all(sha(ROOT / n) == h for n, h in main_cat.items())
    fixtures = [p.relative_to(ROOT).as_posix() for p in (ROOT / 'tests').rglob('*') if p.is_file()]
    fixtures += ['tools/verify.py', 'tools/run_mesen.py', 'tools/luigi_native_review.py',
                 'tools/playthroughs/roster_audit.lua']
    pins = {n: sha(ROOT / n) for n in fixtures}
    for n, h in pins.items():
        target = SOURCE / n
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            assert sha(target) == h, ('Do not replace divergent private fixture', n)
        else:
            shutil.copyfile(ROOT / n, target)
    compiled = {}
    for mapper in ['mmc3', 'mmc5']:
        for ext in ['nes', 'dbg', 'lbl', 'map']:
            p = SOURCE / f'build/smb-crossover-{mapper}.{ext}'
            compiled[str(p)] = sha(p)
    # Baseline has no crossover code. Copy the existing immutable baseline;
    # this suite does not claim a new baseline build.
    assert sha(ROOT / 'build/smb-crossover-mmc3-baseline.nes') == '0511c6844d0e9fa61f4b4fbc34e6f9c67d8247d3ca964ebbb0c9c2718cdc5146'
    baseline = {}
    for ext in ['nes', 'dbg', 'lbl', 'map']:
        p = ROOT / f'build/smb-crossover-mmc3-baseline.{ext}'
        q = SOURCE / 'build' / p.name
        assert not q.exists()
        shutil.copyfile(p, q)
        baseline[str(q)] = sha(q)
    sys.path.insert(0, str(ROOT / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    assert used + 500_000_000 < 50_000_000_000
    OUT.mkdir()
    command = [sys.executable, 'tools/verify.py', '--mmc5', '--checkpoint', 'build', '--jobs', '2']
    report = dict(status='RUNNING_CURRENT_UNCHANGED_PRIVATE_HEAD_REGRESSIONS',
        command=command, cwd=str(SOURCE), script_sha256=sha(__file__),
        implementation_freeze_sha256=sha(frozen), actual_review_sha256=sha(review),
        fixture_and_runner_hashes=pins, candidate_compiled_hashes=compiled,
        copied_existing_baseline_hashes=baseline, source412_hashes=cat,
        main_S2_source410_hashes=main_cat, workspace_before=used,
        root_reserved_bytes=500_000_000, accepted_release=False, goal_complete=False)

    def save():
        (OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    start = time.monotonic()
    with (OUT / 'full-suite.log').open('wb') as log:
        p = subprocess.Popen(command, cwd=SOURCE, stdout=log, stderr=subprocess.STDOUT)
        report['driver_pid'] = p.pid
        save()
        code = p.wait()
    summary = SOURCE / 'build/verification/summary-build.json'
    data = json.loads(summary.read_text()) if summary.exists() else {}
    exact = all(sha(ROOT / n) == h and sha(SOURCE / n) == h for n, h in pins.items())
    exact = exact and all(sha(SOURCE / n) == h for n, h in cat.items())
    exact = exact and all(sha(ROOT / n) == h for n, h in main_cat.items())
    exact = exact and all(sha(n) == h for n, h in (compiled | baseline).items())
    passed = code == 0 and data.get('result') == 'passed' and exact
    report.update(status='PASS_CURRENT_UNCHANGED_PRIVATE_HEAD_REGRESSIONS' if passed else 'FAIL_RETAINED_PRIVATE_HEAD_REGRESSIONS',
        exit=code, elapsed_seconds=time.monotonic() - start,
        cases=len(data.get('cases', [])), failures=data.get('failures'),
        summary_result=data.get('result'), summary_sha256=sha(summary) if summary.exists() else None,
        log_sha256=sha(OUT / 'full-suite.log'), source_fixtures_and_compiled_exact_after=exact,
        workspace_after=workspace_bytes(ROOT),
        limits='Broader native regression coverage of the private candidate. Full-roster routes/weapons/final recordings remain open; no main promotion performed.')
    save()
    print(json.dumps({k: report[k] for k in ['status', 'cases', 'exit', 'elapsed_seconds']}), flush=True)
    raise SystemExit(not passed)


if __name__ == '__main__':
    main()
