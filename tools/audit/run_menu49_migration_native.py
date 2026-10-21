"""Execute the small staged test migration against immutable S2 ROMs."""
from pathlib import Path
import concurrent.futures,hashlib,json,subprocess,sys,time
R=Path(__file__).resolve().parents[2]
H=R/'build/verification/root-menu-migration-targeted-a'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    receipt=H/'root-native-summary.json';assert not receipt.exists()
    stage=json.loads((H/'stage.json').read_text())
    assert stage['status']=='HOST_STAGED_PRIVATE_FIXTURE_MIGRATION_NO_NATIVE'
    assert stage['proposal_freeze_sha256']=='9320dc63f97c975e1d979e14a8798604e8d1bc689535a70bc135730efb49d233'
    def exact():
        assert all(sha(H/n)==p['sha256'] for n,p in stage['files'].items())
        for target in stage['target_roms']:
            assert sha(Path(target['path']))==target['sha256']
    exact()
    result=dict(status='RUNNING_TARGETED_MENU_MIGRATION',stage_sha256=sha(H/'stage.json'),script_sha256=sha(Path(__file__)),cases=[])
    def save():receipt.write_text(json.dumps(result,indent=2)+'\n')
    save()
    def one(target,name):
        mapper=Path(target['path']).stem;tag=mapper+'-'+name;log=H/(tag+'-root.log');t=time.monotonic()
        with log.open('wb') as f:
            p=subprocess.run([sys.executable,str(H/'tools/run_mesen.py'),str(H/'tests'/(name+'.lua')),target['path'],'--timeout','90'],cwd=R,stdout=f,stderr=subprocess.STDOUT)
        raw=log.read_text(encoding='utf8',errors='replace')
        good=p.returncode==0 and 'PASS 'in raw and 'FAIL 'not in raw
        return dict(mapper=mapper,test=name,exit=p.returncode,passed=good,elapsed_seconds=time.monotonic()-t,log=str(log),log_sha256=sha(log))
    with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
        pending=[pool.submit(one,target,name)for target in stage['target_roms'] for name in stage['targeted_tests']]
        for future in concurrent.futures.as_completed(pending):
            row=future.result();result['cases'].append(row);save();print(row['mapper'],row['test'],'PASS'if row['passed']else'FAIL',flush=True)
    exact();good=len(result['cases'])==16 and all(q['passed']for q in result['cases'])
    result['status']='PASS_TARGETED_MENU_MIGRATION'if good else'NEGATIVE_TARGETED_MENU_MIGRATION';save()
    print(result['status'],sha(receipt),flush=True);return 0 if good else 1
if __name__=='__main__':raise SystemExit(main())
