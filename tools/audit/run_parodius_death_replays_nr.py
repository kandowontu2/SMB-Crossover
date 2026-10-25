"""Replay six retained controller routes against the private death repair."""
from pathlib import Path
import subprocess,sys,json,hashlib,argparse
ROOT=Path(__file__).resolve().parents[2]
QA=ROOT/'build/verification/parodius-death-nr'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser();p.add_argument('--candidate',default='candidate-v1');p.add_argument('--tag',default='v2');a=p.parse_args()
 results={};rom=QA/(a.candidate+'.nes')
 for mode in('easy','hard'):
  for name in('octopus','twinbee','pentarou'):
   source=ROOT/f'build/verification/parodius-render-nq/replay-{name}-{mode}-v3/inputs.csv'
   discovery=QA/f'discover-{name}-{mode}-{a.tag}';out=QA/f'replay-{name}-{mode}-{a.tag}'
   result=subprocess.run([sys.executable,str(ROOT/'tools/playthroughs/new_roster_run_nd.py'),name,
    '--rom',str(rom),'--output',str(discovery),'--behavior',mode,'--prefix',str(source),
    '--capture','0','--chr-commit'],cwd=ROOT,capture_output=True,text=True)
   print(result.stdout.strip(),flush=True);assert result.returncode==0,result.stderr
   discovered=json.loads((discovery/'manifest.json').read_text())
   assert discovered['result']['cleared']and discovered['result']['deaths']==0 and discovered['result']['failure']is None
   frozen=discovery/'inputs.csv'
   result=subprocess.run([sys.executable,str(ROOT/'tools/playthroughs/new_roster_run_nd.py'),name,
    '--rom',str(rom),'--output',str(out),'--behavior',mode,'--replay',str(frozen),
    '--capture','0','--chr-commit','--parodius-render'],cwd=ROOT,capture_output=True,text=True)
   print(result.stdout.strip(),flush=True);assert result.returncode==0,result.stderr
   m=json.loads((out/'manifest.json').read_text());assert m['ROM_sha256']==sha(rom)
   assert m['controller_only']and not m['memory_writes']and m['fixed_replay']
   assert m['result']['cleared']and m['result']['deaths']==0 and m['result']['failure']is None
   assert frozen.read_bytes()==(out/'inputs.csv').read_bytes()
   result=subprocess.run([sys.executable,str(ROOT/'tools/audit/check_parodius_render.py'),str(out)],cwd=ROOT,capture_output=True,text=True)
   (out/'render-check.log').write_text(result.stdout+result.stderr);assert result.returncode==0
   results[name+'_'+mode]=dict(manifest_sha256=sha(out/'manifest.json'),discovery_sha256=sha(discovery/'manifest.json'),inputs_sha256=sha(frozen),retained_prefix_sha256=sha(source),
    frames=m['result']['frames'],result=m['result'],render=json.loads((out/'parodius-render-proof.json').read_text()))
   (QA/f'replays-{a.tag}.json').write_text(json.dumps(dict(passed=True,ROM_sha256=sha(rom),results=results),indent=2)+'\n')
 print('PASS six independent fixed 1-1 routes / zero deaths / movable1-2',flush=True)


if __name__=='__main__':main()
