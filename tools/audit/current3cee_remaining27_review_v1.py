"""Offline incremental review preparation for completed27route replays."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.resolve().is_relative_to(ROOT);a.output.mkdir(parents=True,exist_ok=True)
 q=json.loads((a.packet/'readiness.json').read_text());done=[];pending=[]
 for case in q['cases']:
  case=case.replace(':','-');direct=a.packet/'native'/(case+'-direct');proof=direct/'proof.json';dest=a.output/case
  if not proof.exists():pending.append(case);continue
  z=json.loads(proof.read_text());assert z['passed']
  if not dest.exists():
   cmd=[sys.executable,'-B',str(ROOT/'tools/audit/current3cee_eight_routes_review_v2.py'),'--native',str(a.packet/'native'),'--case',case,'--output',str(dest)]
   r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
   if r.returncode:
    (a.output/(case+'-review-failure.txt')).write_text(r.stdout+'\n'+r.stderr,encoding='utf-8');raise AssertionError((case,r.returncode,r.stderr))
  v=json.loads((dest/'proof.json').read_text());assert v['passed'];done.append(dict(case=case,proof_sha256=sha(dest/'proof.json'),power_status_transitions=v['power_status_transitions'],direct_frames=v['direct_PPU_frames']))
 print(json.dumps(dict(offline_only=True,prepared=len(done),pending=len(pending),routes=done),indent=2))
if __name__=='__main__':main()
