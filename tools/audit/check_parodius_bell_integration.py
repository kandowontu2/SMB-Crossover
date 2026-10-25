"""Run native-boundary physical Bell arenas through the real front end."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json

ROOT=Path(__file__).resolve().parents[2]
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--variants',nargs='+',type=int,default=[1,2,3]);a=p.parse_args()
    rom=a.rom.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    s=importlib.util.spec_from_file_location('bell_mesen',ROOT/'tools/run_mesen.py');runner=importlib.util.module_from_spec(s);s.loader.exec_module(runner)
    prelude=(ROOT/'tests/parodius-integration.lua').read_text().split('local pulses=')[0];body=(ROOT/'tests/parodius-bells.lua').read_text();results={}
    for variant in a.variants:
        folder=out/str(variant);folder.mkdir(exist_ok=True);script=folder/'bells.lua';script.write_text(f'PN_VARIANT={variant}\n'+prelude+body);runner.ROOT=folder
        code=runner.run(script,rom,timeout=60,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
        results[str(variant)]=dict(exit=code,script_sha256=hashlib.sha256(script.read_bytes()).hexdigest())
        (out/'results.json').write_text(json.dumps(dict(ROM_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),results=results),indent=2)+'\n')
        if code:return code
    return 0
if __name__=='__main__':raise SystemExit(main())
