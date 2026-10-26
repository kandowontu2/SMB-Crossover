"""One granted sequential eight-case pipeline; preserve every native failure."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,time
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--native-grant',action='store_true',required=True);a=p.parse_args()
 ready=a.packet/'readiness.json';q=json.loads(ready.read_text());assert q['native_workers']==1 and not q['native_executed']
 assert all(sha(f)==h for f,h in q['bindings'].items());assert not(a.packet/'native').exists()and not(a.packet/'launch.json').exists()
 launch=dict(readiness_sha256=sha(ready),tool_sha256=sha(Path(__file__)),native_grant_explicit=True,native_workers=1,command=q['command'])
 (a.packet/'launch.json').write_text(json.dumps(launch,indent=2)+'\n');print(json.dumps(dict(starting=True,cases=q['cases'],readiness_sha256=sha(ready))),flush=True)
 with(a.packet/'coordinator-host.log').open('w')as log:
  child=subprocess.Popen(q['command'],stdout=log,stderr=subprocess.STDOUT)
  previous=None
  while child.poll()is None:
   progress=a.packet/'native/progress.json'
   if progress.exists():
    try:
     z=json.loads(progress.read_text());state=[dict(identity=r['identity'],passed=r['passed'],replay=r.get('replay'))for r in z['runs']]
    except (OSError,json.JSONDecodeError):state=None
    if state is not None and state!=previous:print(json.dumps(dict(progress=state)),flush=True);previous=state
   time.sleep(5)
  rc=child.returncode
 result=a.packet/'native/proof.json';z=json.loads(result.read_text())if result.exists()else{}
 finish=dict(exit=rc,passed=rc==0 and z.get('passed',False),native_workers_released=True,proof=str(result),proof_sha256=sha(result)if result.exists()else None)
 (a.packet/'execution.json').write_text(json.dumps(finish,indent=2)+'\n');print(json.dumps(finish),flush=True);return rc or(0 if finish['passed']else 1)
if __name__=='__main__':raise SystemExit(main())
