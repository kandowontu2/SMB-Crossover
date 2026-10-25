"""Compile both ordinary mapper targets from frozen before/after inputs."""
from pathlib import Path
import argparse,concurrent.futures,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 a.output.mkdir(parents=True,exist_ok=False)
 def check(mapper):
  hashes={};commands=[]
  for name,folder in [('baseline','baseline-source'),('candidate','source')]:
   out=a.output/(name+'-'+mapper+'.nes')
   command=[sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),'--workspace',str(a.prepared/folder),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--flag-off',mapper,'--output',str(out)]
   with out.with_suffix('.host.log').open('w')as log:result=subprocess.run(command,cwd=a.prepared/folder,stdout=log,stderr=subprocess.STDOUT)
   assert result.returncode==0,out.with_suffix('.host.log').read_text()[-5000:]
   hashes[name]=sha(out);commands.append(command)
  assert hashes['baseline']==hashes['candidate'],'Guarded feature changes ordinary '+mapper+' ROM'
  return dict(mapper=mapper,passed=True,byte_identical=True,hashes=hashes,commands=commands)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(check,['mmc3','mmc5']))
 report=dict(passed=True,driver_sha256=sha(Path(__file__)),prepared_receipt_sha256=sha(a.prepared/'prepare.json'),results=results,scope='Actual fresh before/after ordinary MMC3/MMC5 compilation and byte comparison. No native ordinary-mapper gameplay claim.')
 (a.output/'proof.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
