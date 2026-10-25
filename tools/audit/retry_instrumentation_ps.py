"""Retry one retained Lua instrumentation timeout without relaxing checks."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[2]
BASE=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-vram-status-ps')
EXPECTED='646baef6cbcbe9ebc3c0a57c182592b3e777970c13b9c89eda6765f446915bb6'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def record(p):return dict(path=str(p),sha256=sha(p))
def main():
    report=BASE/'qualification-final-v4.json';assert not report.exists()
    while True:
        q=json.loads((BASE/'qualification-v4/progress.json').read_text())
        if q['complete']:break
        time.sleep(2)
    assert q['ROM_sha256']==EXPECTED and len(q['routes'])==10
    failed=[r for r in q['routes']if not r['passed']]
    assert {(r['identity'],r['mode'])for r in failed}=={('meta','hard'),('sypha','hard')},failed
    assert all(j['exit']==0 for j in q['jobs']if j['name']not in ['replay-meta-hard','replay-sypha-hard'])
    for row in failed:
        key=row['identity']+'-'+row['mode'];old=BASE/('qualification-v4/replay-'+key)
        host=old/('direct-'+key+'/host.log');log=host.read_text()
        assert 'audit.lua:157: Maximum execution time (1 seconds) exceeded.'in log
        assert 'MMC5 write-time latch model matches actual hardware window'not in log
        retry=BASE/('replay-'+key+'-retry-v4')
        args=[sys.executable,str(ROOT/'tools/audit/replay_roster_pf.py'),'--rom',str(BASE/'candidate-v4/candidate.nes'),
          '--discoveries',str(BASE/('qualification-v4/discovery-index-'+key+'.json')),'--output',str(retry)]
        z=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);(BASE/(key+'-retry-v4.log')).write_text(z.stdout+z.stderr)
        assert z.returncode==0,(z.stdout+z.stderr)[-1400:]
        proof=json.loads((retry/'proof.json').read_text());assert proof['passed']and proof['complete']and proof['ROM_sha256']==EXPECTED
        row['retained_failed_replay']=record(old/'proof.json');row['instrumentation_timeout']=record(host)
        row.update(passed=True,replay_exit=0,replay_folder=str(retry),retry_proof=record(retry/'proof.json'))
        q['jobs'].append(dict(name='replay-'+key+'-retry',exit=0))
        (BASE/'retry-progress-v4.json').write_text(json.dumps(q,indent=2)+'\n');print(key,'PASS',flush=True)
    q['original_qualification']=record(BASE/'qualification-v4/progress.json')
    q.update(passed=True,instrumentation_timeout_retried=True,checks_relaxed=False,aggregation_driver=record(Path(__file__)))
    report.write_text(json.dumps(q,indent=2)+'\n');print('PASS ten current-hash pairs; original measurement timeout retained',flush=True)
if __name__=='__main__':main()
