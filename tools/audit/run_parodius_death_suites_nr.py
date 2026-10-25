"""Run the affected live-pool suites and unchanged ordinary mapper builds."""
from pathlib import Path
import subprocess,sys,json,gzip,hashlib,argparse
ROOT=Path(__file__).resolve().parents[2]
QA=ROOT/'build/verification/parodius-death-nr'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
 global QA
 p=argparse.ArgumentParser();p.add_argument('--candidate',default='candidate-v1');p.add_argument('--tag');a=p.parse_args()
 rom=QA/(a.candidate+'.nes');results={}
 if a.tag:QA=QA/('regressions-'+a.tag);QA.mkdir(exist_ok=False)
 for name,tool in [('components','check_parodius_integration.py'),('bells','check_parodius_bell_integration.py'),('pickups','check_parodius_pickups.py')]:
  result=subprocess.run([sys.executable,str(ROOT/'tools/audit'/tool),'--rom',str(rom),'--output',str(QA/name)],cwd=ROOT,capture_output=True,text=True)
  (QA/(name+'-host.log')).write_text(result.stdout+result.stderr);assert result.returncode==0,name
  r=json.loads((QA/name/'results.json').read_text());assert r['ROM_sha256']==sha(rom)and set(r['results'])=={'1','2','3'}and all(v['exit']==0 for v in r['results'].values())
  results[name]=dict(passed=True,receipt_sha256=sha(QA/name/'results.json'));print('PASS '+name,flush=True)
 for mapper,wanted in [('mmc3','97913a42a48b1d48c0dfde61fcc6f9eb406ec325f749dc439b96af85ba3108b4'),('mmc5','7982aed6838e7c56e15390c67b7ddc05bd3acaab7a59bd5e2d3a91eb5bf07128')]:
  out=QA/f'standard-{mapper}.nes'
  result=subprocess.run([sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),'--flag-off',mapper,'--output',str(out)],cwd=ROOT,capture_output=True,text=True)
  (QA/(mapper+'-build-host.log')).write_text(result.stdout+result.stderr);assert result.returncode==0 and sha(out)==wanted
  debug=out.with_suffix('.dbg');raw=debug.read_bytes();packed=debug.with_suffix('.dbg.gz');packed.write_bytes(gzip.compress(raw,mtime=0));assert gzip.decompress(packed.read_bytes())==raw
  debug.unlink();results[mapper]=dict(passed=True,rom_sha256=sha(out),debug_sha256=hashlib.sha256(raw).hexdigest());print('PASS unchanged '+mapper,flush=True)
 (QA/'suites.json').write_text(json.dumps(dict(passed=True,rom_sha256=sha(rom),results=results),indent=2)+'\n')


if __name__=='__main__':main()
