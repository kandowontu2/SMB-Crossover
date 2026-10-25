"""Run the same600-update native performance arenas on representative turtles."""
from pathlib import Path
import argparse, concurrent.futures, hashlib, json, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output;out.mkdir(parents=True,exist_ok=False)
 driver=ROOT/'tests/tmnt-performance.lua';observer=ROOT/'tools/audit/tmnt_performance_observer.lua'
 def run(c):
  name,variant,mode=c;d=out/name;d.mkdir();s=d/'run.lua';s.write_text('TMNT_CFG={variant='+str(variant)+',mode='+json.dumps(mode)+',observer='+json.dumps(observer.as_posix())+'}\ndofile('+json.dumps(driver.as_posix())+')\n')
  z=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(d),str(s),str(a.rom.resolve()),'--timeout','90','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],cwd=ROOT,capture_output=True,text=True);(d/'host.log').write_text(z.stdout+z.stderr)
  return dict(identity=name,variant=variant,mode=mode,exit=z.returncode,result=json.loads((d/'result.json').read_text())if(d/'result.json').exists()else None)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(run,[('leonardo',0,'easy'),('donatello',3,'hard')]))
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();report=dict(passed=all(x['exit']==0 and x['result']and x['result']['passed']for x in results),ROM_sha256=sha(a.rom),driver_sha256=sha(driver),observer_sha256=sha(observer),runs=results)
 (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return 0 if report['passed']else 1
if __name__=='__main__':raise SystemExit(main())
