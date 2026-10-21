"""Full unchanged fixture suite on the privately bound current-P optimization."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time

ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/'build/verification/root49p-sophia-integrated-private-r'
SOURCE=BUILD/'source'
OUT=BUILD/'qa-suite-a'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sys.dont_write_bytecode=True;assert not OUT.exists()
    built=json.loads((BUILD/'report.json').read_text())
    assert sha(BUILD/'report.json')=='51eb15b3a2a00bb050990cf8c7ceadd4538583e4311b2e97c29621bc9f574f63'
    assert built['status']=='PASS_PRIVATE_BUILD_EXACT_WHOLE_ROM_TEMPLATE_ONLY'
    bind=json.loads((BUILD/'actual-integration-binding.json').read_text())
    assert bind['status']=='PASS_HOST_BOUND_ACTUAL_INTEGRATED_CANDIDATE_NOT_RELEASE'
    cat=built['source409_hashes'];assert len(cat)==409 and all(sha(SOURCE/n)==h for n,h in cat.items())
    cp=ROOT/'build/checkpoints/roster-audit-v49-provisional-pit-wings-p/manifest.json'
    shared=json.loads(cp.read_text())['source_hashes'];assert all(sha(ROOT/n)==h for n,h in shared.items())
    copies=[p.relative_to(ROOT).as_posix()for p in (ROOT/'tests').rglob('*')if p.is_file()]
    copies+=['tools/verify.py','tools/run_mesen.py','tools/luigi_native_review.py','tools/playthroughs/roster_audit.lua']
    original={n:sha(ROOT/n)for n in copies}
    for n in copies:
        dst=SOURCE/n;dst.parent.mkdir(parents=True,exist_ok=True)
        if dst.exists():assert sha(dst)==original[n],n
        else:shutil.copyfile(ROOT/n,dst)
    compiled={}
    for row in built['builds']:
        for p in row['outputs'].values():assert sha(Path(p['path']))==p['sha256'];compiled[p['path']]=p['sha256']
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(ROOT);assert used+275_000_000<50_000_000_000
    OUT.mkdir();command=[sys.executable,'tools/verify.py','--mmc5','--checkpoint','build','--jobs','2']
    report=dict(status='RUNNING_FULL_UNCHANGED_INTEGRATED_R_REGRESSIONS',command=command,cwd=str(SOURCE),
                script_sha256=sha(Path(__file__)),build_report_sha256=sha(BUILD/'report.json'),binding_sha256=sha(BUILD/'actual-integration-binding.json'),
                fixture_and_runner_hashes=original,compiled_hashes=compiled,workspace_before=used,reserved_bytes=275_000_000,
                accepted_release=False,goal_complete=False)
    def save():(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save();start=time.monotonic()
    with (OUT/'full-suite.log').open('wb')as f:p=subprocess.run(command,cwd=SOURCE,stdout=f,stderr=subprocess.STDOUT)
    report.update(exit=p.returncode,elapsed_seconds=time.monotonic()-start)
    summary=SOURCE/'build/verification/summary-build.json'
    data=json.loads(summary.read_text())if summary.exists()else{}
    report.update(cases=len(data.get('cases',[])),failures=data.get('failures'),summary_result=data.get('result'),
                  summary_sha256=sha(summary)if summary.exists()else None,full_suite_log_sha256=sha(OUT/'full-suite.log'))
    exact=all(sha(SOURCE/n)==h and sha(ROOT/n)==h for n,h in original.items())
    exact=exact and all(sha(SOURCE/n)==h for n,h in cat.items())and all(sha(ROOT/n)==h for n,h in shared.items())
    exact=exact and all(sha(Path(n))==h for n,h in compiled.items())
    passed=p.returncode==0 and data.get('result')=='passed'and exact
    report.update(status='PASS_FULL_UNCHANGED_INTEGRATED_R_REGRESSIONS'if passed else'FAIL_RETAINED_INTEGRATED_R_REGRESSIONS',
                  source409_and_original_fixtures_compiled_exact_after=exact,workspace_after=workspace_bytes(ROOT),
                  qualification='Full unchanged existing fixture suite on exact bound integrated candidate. Separate native performance smoke and root promotion decision remain; ordinary all-character routes/weapons/final recordings are still open.')
    save();print(json.dumps(dict(status=report['status'],cases=report['cases'],elapsed_seconds=report['elapsed_seconds'],report_sha256=sha(OUT/'report.json'))),flush=True)
    raise SystemExit(not passed)

if __name__=='__main__':main()
