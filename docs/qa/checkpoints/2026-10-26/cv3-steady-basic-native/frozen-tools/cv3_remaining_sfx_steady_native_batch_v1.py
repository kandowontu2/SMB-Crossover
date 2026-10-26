"""Exactly14 remaining granted launches; Hard-ice pilot is not rerun."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
READY='e56d43409453ea54cd898637078498aa6d5d9b7ad3e08d46f4347ef9ed7b15cb'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--readiness',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert sha(a.readiness)==READY;r=json.loads(a.readiness.read_text());a.output.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,a.output/'frozen-batch.py');cells=[c for c in r['future_launches']if c['name']!='hard-ice'];assert len(cells)==14 and cells[0]['name']=='fresh-baseline-easy-lightning';rows=[]
 hard=next(c for c in r['future_launches']if c['name']=='hard-ice');pilot=Path(hard['fixture']).parent/'native-hard-ice-v1/proof.json';p0=json.loads(pilot.read_text());assert p0['native_guard_passed']and p0['comparison']['passed']and p0['retries']==0;assert sha(p0['complete_GAMEproof']['path'])==p0['complete_GAMEproof']['sha256']=='57f990d194f12b1b00edad662f875922a9b472d83b08749b450d6637e937d0ae';assert sha(p0['comparison']['path'])==p0['comparison']['sha256']=='6b4533f250c355bcb53388fe7aa1f63a0c316298db39a21643d36ceb65580320'
 def save(stopped=False,reason=None):
  (a.output/'proof.json').write_text(json.dumps(dict(completed=not stopped,native_executed=bool(rows),remaining_granted_launches=len(rows),original_pilot_launches=1,total_new_native_launches=1+len(rows),retries=0,worker_released=True,accepted=False,early_stop=stopped,stop_reason=reason,readiness_sha256=READY,original_pilot=dict(path=str(pilot),sha256=sha(pilot)),cells=rows,tool_sha256=sha(__file__)),indent=2)+'\n')
 for c in cells:
  receipt=a.output/c['name'];cmd=[sys.executable,str(ROOT/'tools/audit/cv3_remaining_sfx_steady_native_launch_v1.py'),'--readiness',str(a.readiness),'--expected-readiness-sha256',READY,'--cell',c['name'],'--receipt',str(receipt)];z=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);(a.output/(c['name']+'.stdout.txt')).write_text(z.stdout);(a.output/(c['name']+'.stderr.txt')).write_text(z.stderr)
  row=dict(name=c['name'],exit_code=z.returncode,receipt=str(receipt/'proof.json'));rows.append(row)
  if z.returncode:save(True,'Shared input/settings/host/observer/source/hardware failure: stop without retry');print(json.dumps(dict(stopped=True,cell=c['name'],exit=z.returncode)),flush=True);raise SystemExit(1)
  out=json.loads((receipt/'proof.json').read_text());assert out['native_guard_passed']and out['retries']==0;row['receipt_sha256']=sha(receipt/'proof.json');row['native_guard_passed']=True
  if 'comparison'in out:row['strict_cadence_passed']=out['comparison']['passed']
  save();print(json.dumps(row),flush=True)
 assert len(rows)==14;save();print(json.dumps(dict(completed=True,native_launches=15,retries=0,worker_released=True,cadence_passes_in_remaining=sum(row.get('strict_cadence_passed',False)for row in rows)),indent=2))
if __name__=='__main__':main()
