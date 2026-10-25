"""Pin the old checker, replacing only its obsolete graphics entry name."""
from pathlib import Path
import argparse,hashlib,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 f=ROOT/'tools/audit/check_tmnt_front_gates_oc.py';s=f.read_text();assert s.count("[('RlGraphicsDispatch','TnFastGraphicsGate')")==1
 s=s.replace("[('RlGraphicsDispatch','TnFastGraphicsGate')","[('HotPlayerGraphics','TnFastGraphicsGate')")
 target=a.output/'checker.py';target.write_text(s);args=[sys.executable,str(target),'--rom',str(a.rom),'--baseline',str(a.baseline),'--output',str(a.output/'checks')]
 import os
 env=os.environ.copy();env['PYTHONPATH']=str(ROOT/'tools/audit')
 z=subprocess.run(args,cwd=ROOT,env=env,capture_output=True,text=True);(a.output/'host.log').write_text(z.stdout+z.stderr);print((z.stdout+z.stderr)[-2500:]);assert z.returncode==0
if __name__=='__main__':main()
