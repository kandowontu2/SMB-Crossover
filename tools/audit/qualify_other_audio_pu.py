"""One-worker native regressions for the shared MMC5 mixer change."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 q=dict(passed=False,complete=False,ROM_sha256=sha(a.rom),native_workers=1,runs=[])
 for name in ['samus-audio-cold-ob','samus-beam-rendering','megaman-charged-scrolling','bass-water-audio','bill-audio-isolation','link-audio-isolation','simon-audio-isolation']:
  folder=a.output/name;folder.mkdir();fixture=ROOT/'tests'/(name+'.lua')
  args=[sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(folder),str(fixture),str(a.rom.resolve()),'--timeout','90','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
  with(folder/'host.log').open('w')as log:r=subprocess.run(args,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
  q['runs'].append(dict(name=name,exit=r.returncode,passed=r.returncode==0,fixture_sha256=sha(fixture)));(a.output/'progress.json').write_text(json.dumps(q,indent=2)+'\n');print(name,r.returncode,flush=True)
 q.update(complete=True,passed=all(r['passed']for r in q['runs']));(a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');return 0 if q['passed']else 1
if __name__=='__main__':raise SystemExit(main())
