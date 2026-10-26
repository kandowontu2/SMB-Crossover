"""Continue only the exact frozen lifecycle grant, never rerun an attempted cell."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
READY='e7102d428cd5a872853094c2d2e3c2651afef092f70432aa8bbfc7d8ae1ebc42'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--readiness',type=Path,required=True);p.add_argument('--receipts',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert sha(a.readiness)==READY;r=json.loads(a.readiness.read_text());a.output.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,a.output/'frozen-batch.py');rows=[]
 for cell in r['future_launches']:
  dest=a.receipts/cell['name']
  if(dest/'launch.json').exists():
   assert(dest/'proof.json').exists(),'Prior attempted cell has no completed receipt: manual diagnosis required';z=json.loads((dest/'proof.json').read_text());assert z['readiness_sha256']==READY and z['retries']==0
   rows.append(dict(name=cell['name'],previously_attempted=True,receipt=str(dest/'proof.json'),receipt_sha256=sha(dest/'proof.json'),native_guard_passed=z['native_guard_passed'],comparison_passed=z.get('comparison',{}).get('passed')));continue
  cmd=[sys.executable,str(ROOT/'tools/audit/cv3_remaining_sfx_lifecycle_launch_v1.py'),'--readiness',str(a.readiness),'--expected-readiness-sha256',READY,'--cell',cell['name'],'--receipt',str(dest)]
  z=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);(a.output/(cell['name']+'.stdout.txt')).write_text(z.stdout);(a.output/(cell['name']+'.stderr.txt')).write_text(z.stderr)
  row=dict(name=cell['name'],exit_code=z.returncode,receipt=str(dest/'proof.json'));rows.append(row)
  if(dest/'proof.json').exists():q=json.loads((dest/'proof.json').read_text());row.update(receipt_sha256=sha(dest/'proof.json'),native_guard_passed=q['native_guard_passed'],comparison_passed=q.get('comparison',{}).get('passed'))
  (a.output/'progress.json').write_text(json.dumps(dict(completed=False,readiness_sha256=READY,rows=rows,tool_sha256=sha(__file__)),indent=2)+'\n');print(json.dumps(row),flush=True)
  if z.returncode:print('STOP_FOR_MANUAL_DIAGNOSIS_NO_RETRY',flush=True);raise SystemExit(z.returncode)
 (a.output/'proof.json').write_text(json.dumps(dict(completed=True,native_launches=20,retries=0,accepted=False,readiness_sha256=READY,rows=rows,tool_sha256=sha(__file__)),indent=2)+'\n')
if __name__=='__main__':main()
