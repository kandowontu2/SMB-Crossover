"""Run only the four corrected outline navigation/pixel cases."""
from pathlib import Path
import concurrent.futures,hashlib,json,subprocess,sys,time
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root-menu-migration-targeted-b'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=H/'root-native-summary.json';assert not out.exists()
    stage=json.loads((H/'stage.json').read_text())
    pins={str(p):sha(p)for p in H.rglob('*')if p.is_file()}
    result=dict(status='RUNNING_CORRECTED_OUTLINE_TESTS',stage_sha256=sha(H/'stage.json'),cases=[],script_sha256=sha(Path(__file__)))
    def save():out.write_text(json.dumps(result,indent=2)+'\n')
    def run(mapper,name):
        rom=R/f'build/verification/root49-menu-options-private-s2/source/build/smb-crossover-{mapper}.nes'
        log=H/(mapper+'-'+name+'-root.log');t=time.monotonic()
        with log.open('wb')as f:p=subprocess.run([sys.executable,str(H/'tools/run_mesen.py'),str(H/'tests'/(name+'.lua')),str(rom),'--timeout','90'],cwd=R,stdout=f,stderr=subprocess.STDOUT)
        raw=log.read_text(errors='replace');return dict(mapper=mapper,test=name,exit=p.returncode,passed=p.returncode==0 and 'PASS 'in raw and 'FAIL 'not in raw,log=str(log),log_sha256=sha(log),elapsed_seconds=time.monotonic()-t)
    save()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
        futures=[pool.submit(run,m,n)for m in ('mmc3','mmc5')for n in ('player-outlines','player-outlines-render')]
        for f in concurrent.futures.as_completed(futures):
            row=f.result();result['cases'].append(row);save();print(row['mapper'],row['test'],'PASS'if row['passed']else'FAIL',flush=True)
    assert all(sha(Path(n))==h for n,h in pins.items())
    good=all(q['passed']for q in result['cases']);result['status']='PASS_CORRECTED_OUTLINE_TESTS'if good else'NEGATIVE_CORRECTED_OUTLINE_TESTS';save();print(result['status'],sha(out),flush=True);return 0 if good else 1
if __name__=='__main__':raise SystemExit(main())
