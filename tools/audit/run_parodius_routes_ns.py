"""Fresh discoveries and independent fixed Parodius replays on the private NS build."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];QA=ROOT/'build/verification/parodius-performance-ns';ROM=QA/'candidate-v4.nes'
ARCHIVE=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-22-workspace-cleanup')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 digest=sha(ROM);assert digest=='214b39daacdb0fb29590625f83912994fc73fb090235ac9f0f058bb938167f0c';results={}
 for char in ('octopus','twinbee','pentarou'):
  for mode in ('easy','hard'):
   key=char+'-'+mode
   for kind in ('discover','replay'):
    out=QA/(kind+'-'+key+'-v4')
    if not out.exists():
     prefix=ARCHIVE/f'build/verification/parodius-death-nr/replay-{key}-v3/inputs.csv'
     commands=[sys.executable,str(ROOT/'tools/playthroughs/new_roster_run_nd.py'),char,'--rom',str(ROM),'--output',str(out),'--behavior',mode,'--capture','0','--chr-commit','--parodius-render','--timeout','90']
     commands+=['--prefix',str(prefix)]if kind=='discover'else['--replay',str(QA/('discover-'+key+'-v4')/'inputs.csv')]
     r=subprocess.run(commands,cwd=ROOT,capture_output=True,text=True);(QA/(kind+'-'+key+'-runner.log')).write_text(r.stdout+r.stderr)
     assert r.returncode==0,(kind,key,r.stdout[-1200:],r.stderr[-1200:])
    m=json.loads((out/'manifest.json').read_text());assert m['ROM_sha256']==digest and m['exit']==0 and m['result']['cleared']and m['result']['deaths']==0 and m['chr_commit']['passed']
    assert m['policy_sha256']==sha(out/'policy.lua')and m['harness_sha256']==sha(out/'harness.lua')and m['inputs_sha256']==sha(out/'inputs.csv')
    results[kind+'-'+key]=dict(frames=m['result']['frames'],deaths=0,input_sha256=m['inputs_sha256'],chr=m['chr_commit'])
    (QA/'route-results.json').write_text(json.dumps(dict(passed=False,rom_sha256=digest,results=results),indent=2)+'\n');print(kind,key,m['result']['frames'],flush=True)
   assert sha(QA/('discover-'+key+'-v4')/'inputs.csv')==sha(QA/('replay-'+key+'-v4')/'inputs.csv'),'Independent replay uses exactly the retained controller stream'
 (QA/'route-results.json').write_text(json.dumps(dict(passed=True,rom_sha256=digest,results=results),indent=2)+'\n')
if __name__=='__main__':main()
