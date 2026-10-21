"""Classify every retained suite failure without converting any to a pass."""
from pathlib import Path
import collections
import hashlib
import json
import re

R=Path(__file__).resolve().parents[2]
V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out=V/'root49-full-suite-admission-a.json';assert not out.exists()
    suitepath=V/'root49-combined-full-suite-c/summary.json'
    assert sha(suitepath)=='97327df36f999f5da9c6c69d370a5482df261181e72b2c9e7f2b45a272516225'
    suite=json.loads(suitepath.read_text())
    D=V/'root49-full-failure-parent-e-a'
    assert sha(D/'freeze.json')=='d231e72facce7a0aa2fc6204a256ac692ea7ed852ee511a03770fb4e07f51447'
    assert sha(D/'report.json')=='487f7c6c2f3c16ef9e4eb4879ce60dedb9e3ab47eeb6ad083d9df1c36fbbef89'
    frozen=json.loads((D/'freeze.json').read_text())
    checked=set()
    def walk(value):
        if isinstance(value,dict):
            if 'path' in value and 'sha256' in value:
                p=Path(value['path']);p=p if p.is_absolute() else R/p
                assert p.is_file() and sha(p)==value['sha256'],str(p)
                if 'bytes' in value:assert p.stat().st_size==value['bytes']
                checked.add(str(p))
            for child in value.values():walk(child)
        elif isinstance(value,list):
            for child in value:walk(child)
    walk(frozen)
    report=json.loads((D/'report.json').read_text());walk(report)
    # Also rehash the freeze's relative retained-file catalog.
    catalogs=[v for v in frozen.values() if isinstance(v,dict) and len(v)==295]
    assert len(catalogs)==1
    for n,h in catalogs[0].items():
        p=D/n;digest=h if isinstance(h,str) else h['sha256']
        assert sha(p)==digest,n
    assert suite['result']=='failed' and len(suite['cases'])==688 and len(suite['failures'])==74
    pairs=set()
    for message in suite['failures']:
        m=re.fullmatch(r'(.+) failed for smb-crossover-(mmc[35])',message)
        if m:pairs.add((m[1],m[2]))
        else:assert message=='Mario state diverged from the baseline input replay.'
    assert len(pairs)==73 and not suite['changed_fixtures']
    assert {(z['test'],z['mapper']) for z in report['results']}==pairs
    assert collections.Counter(z['classification'] for z in report['results'])=={'PREEXISTING_E_SAME_FAILURE':73}
    assert report['fixtures_unchanged'] and report['parent_sources_unchanged'] and not report['active']
    for n,h in suite['fixture_hashes_after'].items():assert sha(R/n)==h,n
    trace=V/'root49-combined-full-suite-b/smb-crossover-mmc3-mario-trace.csv'
    mario={}
    for name in ['gq','audio-e']:
        p=V/f'root49-mario-trace-investigation-b/{name}/smb-crossover-mmc3-mario-trace.csv'
        assert p.read_bytes()==trace.read_bytes();mario[name]=sha(p)
    result=dict(status='REVIEWED_WORKING_CANDIDATE_SCOPE_WITH_ALL_LEGACY_FAILURES_RETAINED',
        script_sha256=sha(__file__),suite_sha256=sha(suitepath),comparison_freeze_sha256=sha(D/'freeze.json'),
        comparison_report_sha256=sha(D/'report.json'),rehashed_catalog_files=295,rehashed_reference_records=len(checked),
        passed_native_slots=688,failed_native_slots=73,separate_stock_Mario_comparison_failed=True,
        all_failed_native_slots_reproduce_on_E=True,fixtures_unchanged=True,mario_prior_trace_identity=mario,
        qualifies_provisional_working_adoption=True,full_suite_passed=False,
        qualifications=['Equality is of each actual first failure, not the unexecuted remainder of a failed fixture.',
            'Pre-existing failure classification does not prove the runtime or fixture is correct; all73 remain open failures.',
            'The suite executes combined B. C adds only the literal nine-byte tested armor correction and passes12 targeted native fixtures.',
            'Full roster routes, remaining Ice behavior, broader lag/source fidelity and final recordings remain incomplete.'],
        accepted_release=False,goal_complete=False)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','rehashed_catalog_files','passed_native_slots','failed_native_slots','full_suite_passed']}))


if __name__=='__main__':main()
