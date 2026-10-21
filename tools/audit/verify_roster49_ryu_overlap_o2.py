"""One complete unchanged current-fixture run on private O2 after targeted passes."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT/'build/verification/root49n-ryu-overlap-private-build-o2'
SOURCE = BUILD/'source'
OWN = BUILD/'qa-suite-a'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not OWN.exists()
    built = json.loads((BUILD/'report.json').read_text())
    assert built['status'] == 'PASS-private-Ryu-overlap-build-only'
    assert len(built['source409_hashes']) == 409
    assert all(sha(SOURCE/n) == h for n,h in built['source409_hashes'].items())
    target = ROOT/'build/verification/ryu49n-platform-source-component-a'
    targeted = {}
    for mapper in ('mmc3','mmc5'):
        p = target/f'binding-o2-{mapper}-root-a/native-output/result.json'
        r = json.loads(p.read_text())
        assert r['cases'] == r['completed'] == 24 and r['failures'] == 0
        targeted[mapper] = dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p))
    vine = ROOT/'build/verification/ryu49k-vine-abi-component-a/root-cache-full-b/report.json'
    v = json.loads(vine.read_text())
    assert v['status'] == 'PASS_EXPLICIT_COMPILED_VINE_ABI_OAM_SMC_STACK_COMPONENT'
    assert all(x['passed'] == 13568 for x in v['cases'].values())
    old_outputs = ROOT/'build/verification/root49-combined-private-build-n/source/build/verification'
    old_bytes = sum(p.stat().st_size for p in old_outputs.rglob('*') if p.is_file())
    # The exact unchanged suite produced47,385,477 bytes on N. Reserve exceeds
    # twice that measured total; no source/route/native evidence is removed.
    reserve = 100_000_000
    assert old_bytes*2 < reserve
    sys.path.insert(0,str(ROOT/'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    assert used + reserve < 30_000_000_000
    OWN.mkdir()
    copies = [p.relative_to(ROOT).as_posix() for p in (ROOT/'tests').rglob('*') if p.is_file()]
    copies += ['tools/verify.py','tools/run_mesen.py','tools/luigi_native_review.py','tools/playthroughs/roster_audit.lua']
    for n in copies:
        dst = SOURCE/n
        dst.parent.mkdir(parents=True,exist_ok=True)
        if dst.exists():
            assert sha(dst) == sha(ROOT/n),n
        else:
            shutil.copyfile(ROOT/n,dst)
    baseline = [f'build/smb-crossover-mmc3-baseline{x}' for x in ('.nes','.lbl','.dbg')]
    assert sha(SOURCE/baseline[0]) == built['original_baseline_sha256']
    inputs = {n:sha(SOURCE/n) for n in copies+baseline}
    argv = [sys.executable,'tools/verify.py','--mmc5','--checkpoint','build','--jobs','2']
    report = dict(status='running',accepted_release=False,goal_complete=False,
                  argv=argv,cwd=str(SOURCE),script_sha256=sha(Path(__file__)),
                  compiled_report_sha256=sha(BUILD/'report.json'),
                  targeted_native_result_pins=targeted,full_vine_report_sha256=sha(vine),
                  fixture_and_runner_hashes=inputs,workspace_before_bytes=used,
                  measured_N_suite_output_bytes=old_bytes,reserve_bytes=reserve,
                  original_global_verification_outputs_touched=False)
    def save():
        (OWN/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    with (OWN/'full-suite.log').open('w',encoding='utf-8') as log:
        result = subprocess.run(argv,cwd=SOURCE,stdout=log,stderr=subprocess.STDOUT)
    assert all(sha(SOURCE/n) == h for n,h in inputs.items())
    assert all(sha(SOURCE/n) == h for n,h in built['source409_hashes'].items())
    summary = SOURCE/'build/verification/summary-build.json'
    data = json.loads(summary.read_text())
    passed = result.returncode == 0 and data['result'] == 'passed'
    used_after = workspace_bytes(ROOT)
    assert used_after < 30_000_000_000
    report.update(status='PASS-full-current-fixture-run' if passed else 'FAIL-retained',
                  exit=result.returncode,cases=len(data['cases']),failures=data['failures'],
                  source409_exact_after=True,fixtures_exact_after=True,
                  summary_sha256=sha(summary),full_suite_log_sha256=sha(OWN/'full-suite.log'),
                  workspace_after_bytes=used_after,
                  qualification='Complete existing fixture run. Separate target-ABI/route/AV/release acceptance remains pending.')
    save()
    print(json.dumps({k:v for k,v in report.items() if k!='fixture_and_runner_hashes'}),flush=True)
    raise SystemExit(not passed)


if __name__=='__main__':
    main()
