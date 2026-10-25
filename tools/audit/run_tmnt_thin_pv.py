"""Bind the actual thin-brick/native-recoil component to old/new ROMs."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,re
from check_tmnt_render_oa import load,address
ROOT=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--expect-bad',action='store_true');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 fixture=ROOT/'tests/tmnt-thin-side-pv.lua';bundle=load(a.rom)
 aliases=''.join('L.'+n+'='+str(address(bundle,n))+'\n'for n in sorted(set(re.findall("'(Tn\\w+)'",fixture.read_text()))))
 script=a.output/'run.lua';script.write_text(aliases+'THIN_CFG={expect_bad='+str(a.expect_bad).lower()+'}\ndofile('+json.dumps(fixture.as_posix())+')\n')
 z=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output),str(script),str(a.rom.resolve()),'--timeout','90','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],capture_output=True,text=True,cwd=ROOT);(a.output/'host.log').write_text(z.stdout+z.stderr)
 q=dict(passed=z.returncode==0,ROM_sha256=hashlib.sha256(a.rom.read_bytes()).hexdigest(),fixture_sha256=hashlib.sha256(fixture.read_bytes()).hexdigest(),exit=z.returncode)
 if(a.output/'result.json').exists():q['result']=json.loads((a.output/'result.json').read_text())
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q));return z.returncode
if __name__=='__main__':raise SystemExit(main())
