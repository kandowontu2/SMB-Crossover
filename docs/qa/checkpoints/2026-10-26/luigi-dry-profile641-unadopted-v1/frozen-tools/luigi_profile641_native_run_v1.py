"""Run only a separately granted two-profile Luigi dry-candidate batch; stop first failure."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,q):
    assert not p.exists(),p
    p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True)
    p.add_argument('--expected-readiness-sha256',required=True);p.add_argument('--native-grant',action='store_true',required=True);a=p.parse_args()
    ready=a.packet/'readiness.json';assert sha(ready)==a.expected_readiness_sha256;q=json.loads(ready.read_text())
    assert [(v['name'],v['character'],v['variant'],v['mode'])for v in q['profiles']]==[('luigi-easy',8,1,0),('luigi-hard',8,1,1)]
    assert q['native_workers']==1 and q['stop_first_failure'] and q['automatic_retries']==0
    for f,h in q['bindings'].items():assert sha(f)==h,f
    put(a.packet/'launch.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),explicit_grant=True,readiness_sha256=sha(ready),retries=0))
    results=[]
    for profile in q['profiles']:
        for f,h in q['bindings'].items():assert sha(f)==h,f
        out=Path(profile['fixture']);assert not(out/'result.json').exists()
        with(out/'native-host.log').open('x',encoding='utf-8')as log:z=subprocess.run(profile['command'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        get=lambda n:json.loads((out/n).read_text())if(out/n).exists()else{}
        result=get('result.json');item=get('flower-component.json');chr_result=get('chr-commit.json')
        for n in ['worker_settings','user_settings']:assert sha(q['environment'][n])==q['environment'][n+'_sha256']
        passed=z.returncode==0 and result.get('component_complete')is True and result.get('deaths')==0
        passed=passed and item.get('passed')is True and item.get('actual_mode')==profile['mode'] and item.get('character')==8 and item.get('variant')==1 and chr_result.get('passed')is True
        row=dict(name=profile['name'],passed=bool(passed),actual_expected_numeric_mode=profile['mode'],exit=z.returncode,result=result,component=item,CHR=chr_result,retries=0)
        put(out/'native-receipt.json',row);results.append(row)
        put(a.packet/('progress-'+str(len(results))+'.json'),dict(results=results))
        print(json.dumps(dict(name=profile['name'],passed=bool(passed),exit=z.returncode)),flush=True)
        if not passed:break
    proof=dict(passed=len(results)==2 and all(r['passed']for r in results),ROM_sha256=q['ROM_sha256'],profiles_run=len(results),profiles=results,native_worker_released=True,retries=0,fullroute_adoption_claim=False)
    put(a.packet/'native-proof.json',proof);return 0 if proof['passed']else 1


if __name__=='__main__':raise SystemExit(main())
