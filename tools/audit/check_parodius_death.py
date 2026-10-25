"""Verify real terrain-triggered ship death in a labeled component arena."""
from pathlib import Path
import argparse,hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parents[2]


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--variants',nargs='+',type=int,default=[1,2,3]);p.add_argument('--script',type=Path,default=ROOT/'tests/parodius-native-death.lua');a=p.parse_args()
 out,rom=a.output.resolve(),a.rom.resolve();out.mkdir(parents=True,exist_ok=False)
 spec=importlib.util.spec_from_file_location('pn_death_mesen',ROOT/'tools/run_mesen.py');runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
 results={};sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 for variant in a.variants:
  folder=out/str(variant);folder.mkdir();script=folder/'death.lua';script.write_text(f'PN_VARIANT={variant}\n'+a.script.read_text());runner.ROOT=folder
  code=runner.run(script,rom,timeout=45,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
  results[str(variant)]=dict(exit=code,script_sha256=sha(script))
  proof=folder/'build/verification/death-proof.json'
  if proof.exists():results[str(variant)]['proof']=json.loads(proof.read_text())
  (out/'results.json').write_text(json.dumps(dict(rom_sha256=sha(rom),passed=all(v['exit']==0 for v in results.values()),fixture_sha256=sha(a.script),results=results),indent=2)+'\n')
 return int(any(v['exit']for v in results.values()))


if __name__=='__main__':raise SystemExit(main())
