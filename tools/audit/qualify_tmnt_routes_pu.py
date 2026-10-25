"""Fresh turtle discoveries and strict physical-frame replays, one worker."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];ARC=Path('C:/Users/kando/Videos/SMB Crossover Archive')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--gap-controls',type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 prior=ARC/'2026-10-24-roster-pn/known-pairs-v1/proof.json';old=json.loads(prior.read_text());driver=ARC/'2026-10-24-roster-pe/matrix-v1/bound-runner.py'
 assert sha(driver)=='d6ab9cc1e938923797525704cf6d0e99e16fda6f007b98da1024cb167f00f167'
 selected=[r for r in old['runs']if r['identity']in ['leonardo','raphael','michelangelo','donatello']];assert len(selected)==8 and all(r['passed']for r in selected)
 report=dict(passed=False,complete=False,goal_complete=False,ROM_sha256=sha(a.rom),prior_policy_selection_proof_sha256=sha(prior),bound_driver_sha256=sha(driver),native_workers=1,runs=[])
 def save():(a.output/'progress.json').write_text(json.dumps(report,indent=2)+'\n')
 def invoke(key,args):
  assert sha(a.rom)==report['ROM_sha256']
  with(a.output/(key+'.log')).open('w')as log:return subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT).returncode
 save()
 for row in selected:
  name,mode=row['identity'],row['mode'];key=name+'-'+mode;before=Path(row['folder']);oldm=json.loads((before/'manifest.json').read_text());policy=before/'policy.lua';assert sha(policy)==oldm['policy_sha256'];assert sha(before/'manifest.json')==row['manifest_sha256']
  if a.gap_controls:policy=a.gap_controls
  folder=a.output/('discover-'+key);rc=invoke('discover-'+key,[driver,name,'--rom',a.rom.resolve(),'--output',folder,'--behavior',mode,'--frames',str(oldm['config']['limit']),'--capture','12','--chr-commit','--policy',policy,'--timeout','180'])
  entry=dict(identity=name,mode=mode,passed=False,folder=str(folder),discovery_exit=rc,policy_sha256=sha(policy));report['runs'].append(entry)
  f=folder/'manifest.json';m=json.loads(f.read_text())if f.exists()else {};result=m.get('result')or {};entry.update(frames=result.get('frames'),failure=result.get('failure'))
  if rc==0 and result.get('cleared')and result.get('deaths')==0 and m.get('chr_commit',{}).get('passed'):
   assert m['ROM_sha256']==report['ROM_sha256']and not m['fixed_replay']
   index=a.output/('index-'+key+'.json');index.write_text(json.dumps(dict(ROM_sha256=report['ROM_sha256'],phase='discover',runs=[dict(identity=name,mode=mode,passed=True,folder=str(folder),manifest_sha256=sha(f))]),indent=2)+'\n')
   replay=a.output/('replay-'+key);rr=invoke('replay-'+key,[ROOT/'tools/audit/replay_roster_pf.py','--rom',a.rom.resolve(),'--discoveries',index,'--output',replay]);entry.update(replay_exit=rr,replay_folder=str(replay),passed=rr==0)
  save();print(key,entry['passed'],flush=True)
 report.update(complete=True,passed=all(r['passed']for r in report['runs']));save();(a.output/'proof.json').write_text(json.dumps(report,indent=2)+'\n');return 0 if report['passed']else 1
if __name__=='__main__':raise SystemExit(main())
