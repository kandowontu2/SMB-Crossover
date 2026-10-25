"""Bind native Mesen audio arenas to independently captured original song events."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-roster-audio-nv')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); out = args.output
    out.mkdir(parents=True, exist_ok=False)
    fixture = ROOT / 'tests/gradius-native-audio.lua'
    prefix = ['GRADIUS_GOLDEN={}']
    for song in (1, 3, 4, 5, 6, 9, 10, 13, 14):
        original = json.loads(gzip.decompress((ARCHIVE / f'gradius-native-v2/source-{song:02d}.json.gz').read_bytes()))
        image = bytearray(16); values = []
        for frame in original[:1501]:
            for reg, value in frame:
                if reg < 16: image[reg] = value
            values.append('"' + ''.join(f'\\{v:03d}' for v in image) + '"')
        prefix.append(f'GRADIUS_GOLDEN[{song}]={{' + ','.join(values) + '}')
    script = out / 'fixture.lua'; script.write_text('\n'.join(prefix) + '\n' + fixture.read_text())
    command = [sys.executable, str(ROOT / 'tools/audit/run_mesen_isolated.py'), '--output', str(out),
               str(script), str(args.rom), '--timeout', '60', '--option=--nes.ramPowerOnState=AllZeros',
               '--option=--nes.randomizeCpuPpuAlignment=false', '--option=--nes.randomizeMapperPowerOnState=false']
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    (out / 'runner.log').write_text(result.stdout + result.stderr)
    report = dict(ROM_SHA256=hashlib.sha256(args.rom.read_bytes()).hexdigest(),
                  fixture_sha256=hashlib.sha256(fixture.read_bytes()).hexdigest(),
                  bound_script_sha256=hashlib.sha256(script.read_bytes()).hexdigest(),
                  exit=result.returncode, passed=result.returncode == 0)
    if (out / 'proof.json').exists(): report['proof'] = json.loads((out / 'proof.json').read_text())
    (out / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report), flush=True)
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
