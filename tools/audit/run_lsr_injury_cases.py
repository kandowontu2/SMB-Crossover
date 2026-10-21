"""Run isolated LSR injury fixtures against copied immutable ROMs, sequentially."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--checkpoint', type=Path, required=True)
    p.add_argument('--tag', required=True)
    p.add_argument('--tests', nargs='+', default=['link-injury-source', 'simon-injury-source', 'ryu-injury-source'])
    p.add_argument('--mappers', nargs='+', type=int, choices=(3, 5), default=[3, 5])
    p.add_argument('--timeout', type=int, default=90)
    p.add_argument('--case-subset', choices=('ceiling', 'wall'), help='Explicit diagnostic subset for source motion fixture only')
    args = p.parse_args()
    out = ROOT/'build/verification'/args.tag
    out.mkdir(exist_ok=False)
    fixture_dir = out/'fixtures'
    fixture_dir.mkdir()
    for source in (ROOT/'tests').glob('*.lua'):
        shutil.copy2(source, fixture_dir/source.name)
    shutil.copytree(ROOT/'tests/fixtures', fixture_dir/'fixtures')
    tool = ROOT/'tools/run_mesen.py'
    shutil.copy2(tool, out/'run_mesen-source.py')
    report = {'checkpoint': str(args.checkpoint.resolve()), 'tool_sha256': digest(tool),
              'fixture_sha256': {n: digest(ROOT/'tests'/f'{n}.lua') for n in args.tests}, 'case_subset': args.case_subset, 'cases': []}
    for mapper in args.mappers:
        src = args.checkpoint/f'smb-crossover-mmc{mapper}.nes'
        dst = out/f'{args.tag}-mmc{mapper}.nes'
        for ext in ('.nes', '.lbl', '.dbg', '.dbg.gz'):
            if src.with_suffix(ext).exists():
                shutil.copy2(src.with_suffix(ext), dst.with_suffix(ext))
        for name in args.tests:
            script = fixture_dir/f'{name}.lua'
            original = script.read_text()
            config = f'HURT_CASE_SUBSET={json.dumps(args.case_subset)}\n' if args.case_subset else ''
            script.write_text("dofile(TEST_DIR..'menu-bootstrap.lua')\n" + config + original)
            command = [sys.executable, str(tool), str(script), str(dst), '--timeout', str(args.timeout)]
            run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            log = out/f'{name}-mmc{mapper}-runner.log'
            log.write_text(run.stdout + run.stderr)
            report['cases'].append({'test': name, 'mapper': mapper, 'rom_sha256': digest(dst),
                                    'exit': run.returncode, 'runner_log': str(log.relative_to(ROOT))})
            script.write_text(original)
            print(name, mapper, run.returncode, flush=True)
            (out/'summary.json').write_text(json.dumps(report, indent=2)+'\n')
    print(out/'summary.json')


if __name__ == '__main__':
    main()
