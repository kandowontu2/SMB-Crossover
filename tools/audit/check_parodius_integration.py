"""Run the real-menu Parodius component arenas against a private candidate."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json

ROOT=Path(__file__).resolve().parents[2]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--variants',nargs='+',type=int,default=[1,2,3])
    args=parser.parse_args();rom=args.rom.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    spec=importlib.util.spec_from_file_location('pn_mesen',ROOT/'tools/run_mesen.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    results={}
    for variant in args.variants:
        folder=out/str(variant);folder.mkdir(exist_ok=True)
        script=folder/'components.lua';script.write_text(f'PN_VARIANT={variant}\n'+(ROOT/'tests/parodius-integration.lua').read_text())
        runner.ROOT=folder
        code=runner.run(script,rom,timeout=45,
                        emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
        results[str(variant)]=dict(exit=code)
        (out/'results.json').write_text(json.dumps(dict(ROM_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),results=results),indent=2)+'\n')
        if code:return code
    return 0


if __name__=='__main__':raise SystemExit(main())
