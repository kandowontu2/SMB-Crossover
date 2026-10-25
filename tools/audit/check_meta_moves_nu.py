"""Run source-based Meta Knight move component arenas on an explicit ROM."""
from pathlib import Path
import argparse
import gzip
import hashlib
import importlib.util
import json
import re

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--hard', action='store_true')
    p.add_argument('--physical', action='store_true', help='Run real food emergence, block effects and health lifecycle')
    args = p.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    fixture = ROOT/('tests/meta-knight-food-blocks.lua' if args.physical else 'tests/meta-knight-nes-moves.lua')
    rom = args.rom.resolve()
    debug=(rom.with_suffix('.dbg').read_text() if rom.with_suffix('.dbg').exists()
           else gzip.decompress(rom.with_suffix('.dbg.gz').read_bytes()).decode())
    constants={}
    for name in ('KbFoodKind','KbJumpPhase'):
        values=set()
        for line in debug.splitlines():
            if 'type=equ' in line and f'name="{name}"' in line:
                match=re.search(r'(?:^|,)val=(0x[0-9A-Fa-f]+)(?:,|$)',line)
                if match:values.add(int(match[1],16))
        assert len(values)==1,(name,'Unambiguous linked debug constant')
        constants[name]=values.pop()
    script = out/('physical.lua' if args.physical else 'native-moves.lua')
    script.write_text('META_HARD='+str(args.hard).lower()+'\n'+
                      ''.join(f'L.{n}={v}\n'for n,v in constants.items())+fixture.read_text())
    spec = importlib.util.spec_from_file_location('meta_mesen', ROOT/'tools/run_mesen.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    runner.ROOT = out
    code = runner.run(script, rom, timeout=60, emulator_options=[
        '--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false',
        '--nes.randomizeMapperPowerOnState=false'])
    report = dict(rom_sha256=sha(rom), fixture_sha256=sha(fixture),
                  runner_sha256=sha(ROOT/'tools/run_mesen.py'), script_sha256=sha(script),
                  hard=args.hard, physical=args.physical, debug_constants=constants,
                  exit=code, passed=code == 0)
    proof = out/'build/verification/proof.json'
    if proof.exists():
        report['proof'] = json.loads(proof.read_text())
    (out/'result.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
