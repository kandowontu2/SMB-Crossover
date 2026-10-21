"""Apply the privately verified, mode-explicit test/tool migration."""
from pathlib import Path
import hashlib,json,shutil,sys
R=Path(__file__).resolve().parents[2]
A=R/'build/verification/agent49-menu-regression-migration-a'
B=R/'build/verification/agent49-menu-regression-migration-b'
CP=R/'build/checkpoints/roster-audit-v49-menu-options-s2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert sha(A/'freeze.json')=='9320dc63f97c975e1d979e14a8798604e8d1bc689535a70bc135730efb49d233'
    assert sha(B/'freeze.json')=='daed763861f09e4263950b0073a400b69b4837c0dd9b29b445262e2b31926366'
    cp=json.loads((CP/'manifest.json').read_text());assert cp['status']=='PASS_WORKING_MENU_OPTIONS_BOTH_MAPPERS'
    a=json.loads((A/'contract.json').read_text());b=json.loads((B/'contract.json').read_text())
    positive=json.loads((R/'build/verification/root-menu-migration-targeted-a/root-native-summary.json').read_text())
    accepted=[q for q in positive['cases']if q['test']not in('player-outlines','player-outlines-render')]
    assert len(accepted)==12 and all(q['passed']for q in accepted)
    corrected=R/'build/verification/root-menu-migration-targeted-b/root-native-summary.json'
    c=json.loads(corrected.read_text());assert c['status']=='PASS_CORRECTED_OUTLINE_TESTS'and len(c['cases'])==4
    out=CP/'test-migration';assert not out.exists()
    sources={n:A/'candidate'/n for n in a['candidate_files']}
    for n in b['candidate_files']:sources[n]=B/'candidate'/n
    assert len(sources)==7
    for n,p in sources.items():
        assert sha(R/n)==a['parent_files'][n]['sha256'],n
        pin=(b if n in b['candidate_files']else a)['candidate_files'][n]
        assert sha(p)==pin['sha256'],n
    out.mkdir()
    report=dict(status='APPLYING_VERIFIED_MODE_EXPLICIT_TEST_MIGRATION',files={},script_sha256=sha(__file__),targeted_cases=16,original_golden_data_modified=False)
    for n,p in sources.items():
        old=out/'before'/n;old.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,old)
        new=out/'after'/n;new.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,new)
        shutil.copyfile(p,R/n)
        report['files'][n]=dict(before_sha256=sha(old),after_sha256=sha(R/n))
    assert all(sha(R/n)==sha(p)for n,p in sources.items())
    report['status']='PASS_APPLIED_VERIFIED_MODE_EXPLICIT_TEST_MIGRATION'
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],sha(out/'report.json'))
if __name__=='__main__':main()
