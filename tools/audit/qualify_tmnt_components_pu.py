"""Run unchanged four native equipment suites, using one worker."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 f=ROOT/'tools/audit/run_tmnt_components_ny.py';s=f.read_text();assert s.count('max_workers=2')==1
 s=s.replace('max_workers=2','max_workers=1').replace('ROOT = Path(__file__).resolve().parents[2]','ROOT = Path('+repr(str(ROOT))+')')
 driver=a.output/'runner.py';driver.write_text(s);q=dict(passed=False,complete=False,ROM_sha256=sha(a.rom),original_runner_sha256=sha(f),bound_runner_sha256=sha(driver),native_workers=1,runs=[])
 for suite in ['equipment','primary','boss','ammo']:
  with(a.output/(suite+'.log')).open('w')as log:r=subprocess.run([sys.executable,str(driver),'--rom',str(a.rom.resolve()),'--output',str(a.output),'--suite',suite],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
  path=a.output/(suite+'-results.json');result=json.loads(path.read_text())if path.exists()else None
  q['runs'].append(dict(suite=suite,exit=r.returncode,passed=r.returncode==0 and result and result['passed'],proof_sha256=sha(path)if path.exists()else None));(a.output/'progress.json').write_text(json.dumps(q,indent=2)+'\n');print(suite,q['runs'][-1]['passed'],flush=True)
 q.update(complete=True,passed=all(r['passed']for r in q['runs']));(a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');return 0 if q['passed']else 1
if __name__=='__main__':raise SystemExit(main())
