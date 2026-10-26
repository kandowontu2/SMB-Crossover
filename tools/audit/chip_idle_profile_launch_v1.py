"""One-shot launcher for the separately granted frozen Chip profiler only."""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--readiness',type=Path,required=True);p.add_argument('--expected-readiness-sha256',required=True);a=p.parse_args();assert sha(a.readiness)==a.expected_readiness_sha256;r=json.loads(a.readiness.read_text())
 for path,h in r['all_frozen_bindings'].items():assert sha(path)==h,('Frozen input/runtime drift',path)
 fixture=Path(r['fixture']);marker=fixture/'profile-launch-started.json';assert not marker.exists(),'No retry';start=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),readiness_sha256=sha(a.readiness),ROM_sha256=r['candidate']['sha256'],command=r['future_command_NOT_GRANTED'],retries=0,launcher_sha256=sha(__file__));marker.write_text(json.dumps(start,indent=2)+'\n')
 with(fixture/'profile-host.log').open('w')as log:z=subprocess.run(start['command'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 result=dict(start,exit_code=z.returncode,native_completed=z.returncode==0,optimization_accepted=False)
 if not z.returncode:
  cmd=[sys.executable,str(ROOT/'tools/audit/chip_idle_profile_verify_v1.py'),'--fixture',str(fixture),'--output',str(fixture/'profile-verification')];v=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);(fixture/'profile-verify.stdout.txt').write_text(v.stdout);(fixture/'profile-verify.stderr.txt').write_text(v.stderr);result['verification_exit']=v.returncode
 for path,h in r['all_frozen_bindings'].items():assert sha(path)==h,('Frozen input/runtime changed after capture',path)
 (fixture/'profile-launch-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(z.returncode or result.get('verification_exit',0))
if __name__=='__main__':main()
