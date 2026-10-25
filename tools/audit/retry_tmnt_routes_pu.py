"""Retain failed controls, retry their real gap with legal inputs, strict replay."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];ARC=Path('C:/Users/kando/Videos/SMB Crossover Archive')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--original',type=Path,required=True);p.add_argument('--policy',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--existing-leonardo',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 source=json.loads(a.original.read_text());assert source['complete']and source['ROM_sha256']==sha(a.rom)
 driver=ARC/'2026-10-24-roster-pe/matrix-v1/bound-runner.py';assert sha(driver)=='d6ab9cc1e938923797525704cf6d0e99e16fda6f007b98da1024cb167f00f167'
 q=dict(passed=False,complete=False,ROM_sha256=sha(a.rom),original_failed_batch_sha256=sha(a.original),policy_sha256=sha(a.policy),native_workers=1,checks_relaxed=False,runs=[])
 def save():(a.output/'progress.json').write_text(json.dumps(q,indent=2)+'\n')
 def run(key,args):
  with(a.output/(key+'.log')).open('w')as log:return subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT).returncode
 for old in source['runs']:
  if old['passed']:continue
  name,mode=old['identity'],old['mode'];key=name+'-'+mode;entry=dict(identity=name,mode=mode,passed=False,original_failure=old);q['runs'].append(entry)
  if key=='leonardo-hard':folder=a.existing_leonardo;rc=0
  else:
   folder=a.output/('discover-'+key);rc=run('discover-'+key,[driver,name,'--rom',a.rom.resolve(),'--output',folder,'--behavior',mode,'--frames','10000','--capture','12','--chr-commit','--policy',a.policy,'--timeout','180'])
  f=folder/'manifest.json';m=json.loads(f.read_text())if f.exists()else {};entry.update(discovery_exit=rc,folder=str(folder),frames=(m.get('result')or {}).get('frames'))
  if rc==0 and m.get('result',{}).get('cleared')and m['result']['deaths']==0 and m['chr_commit']['passed']:
   assert m['ROM_sha256']==q['ROM_sha256']and m['policy_sha256']==q['policy_sha256']and not m['fixed_replay']
   index=a.output/('index-'+key+'.json');index.write_text(json.dumps(dict(ROM_sha256=q['ROM_sha256'],phase='discover',runs=[dict(identity=name,mode=mode,passed=True,folder=str(folder),manifest_sha256=sha(f))]),indent=2)+'\n')
   replay=a.output/('replay-'+key);rr=run('replay-'+key,[ROOT/'tools/audit/replay_roster_pf.py','--rom',a.rom.resolve(),'--discoveries',index,'--output',replay]);entry.update(replay_exit=rr,replay_folder=str(replay),passed=rr==0)
  save();print(key,entry['passed'],flush=True)
 q.update(complete=True,passed=all(r['passed']for r in q['runs']));save();(a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');return 0 if q['passed']else 1
if __name__=='__main__':raise SystemExit(main())
