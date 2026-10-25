"""Run Mac's physical mushroom/star/stock/super fixture on an explicit ROM."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--hard', action='store_true')
    args = p.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    script = out / 'physical-powerups.lua'
    script.write_text('MAC_HARD='+str(args.hard).lower()+'\n'+(ROOT/'tests/little-mac-powerups.lua').read_text())
    spec = importlib.util.spec_from_file_location('mac_mesen', ROOT/'tools/run_mesen.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    runner.ROOT = out
    rom = args.rom.resolve()
    code = runner.run(script, rom, timeout=60, emulator_options=[
        '--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false',
        '--nes.randomizeMapperPowerOnState=false'])
    report = dict(rom_sha256=sha(rom), fixture_sha256=sha(ROOT/'tests/little-mac-powerups.lua'),
                  runner_sha256=sha(ROOT/'tools/run_mesen.py'), script_sha256=sha(script),
                  hard=args.hard, exit=code, passed=code == 0)
    proof = out/'build/verification/proof.json'
    if proof.exists():
        report['proof'] = json.loads(proof.read_text())
    (out/'result.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
