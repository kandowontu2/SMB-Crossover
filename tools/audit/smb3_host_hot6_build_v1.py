"""Independent staged build and ordinary flag-off controls; no installation."""
from pathlib import Path
import argparse,json,subprocess,sys,traceback
from smb3_host_current3b_cpu_v1 import D,R,sha,put
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);rows=[]
 try:
  def call(cmd):
   r=subprocess.run(cmd,cwd=R,capture_output=True,text=True);rows.append(dict(command=cmd,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));put(a.output/f'command-{len(rows)}.json',rows[-1]);assert r.returncode==0,r.stdout+r.stderr
  target=a.output/'canonical.nes';base=[sys.executable,str(R/'tools/build_mmc5_expanded.py'),'--source-overlay',str(a.packet/'source')]
  call(base+['--output',str(target)])
  call([sys.executable,str(R/'tools/prepare_smb3_dmc_mirrors.py'),'--source',str(a.packet/'source'),'--rom',str(target)])
  assert sha(target)==sha(a.packet/'candidate.nes')
  ordinary={}
  for mapper,expected in [('mmc3','d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),('mmc5','f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
   target=a.output/(mapper+'.nes');call(base+['--flag-off',mapper,'--output',str(target)]);assert sha(target)==expected;ordinary[mapper]=expected
  put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,ROM_sha256=sha(a.packet/'candidate.nes'),fresh_canonical_exact=True,ordinary_flagoffs=ordinary,commands=rows,checker_sha256=sha(__file__),no_production_default_settings_or_installation_mutation=True))
  print(json.dumps(dict(passed=True,ROM_sha256=sha(a.packet/'candidate.nes'),ordinary_flagoffs=ordinary)))
 except Exception as e:put(a.output/'failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc(),commands_done=len(rows)));raise
if __name__=='__main__':main()
