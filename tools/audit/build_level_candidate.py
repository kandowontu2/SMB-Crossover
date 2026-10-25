"""Build private level candidates with frozen inputs and retained per-run outputs."""
from pathlib import Path
import argparse
import configparser
import hashlib
import json
import shutil
import subprocess

R = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--tag', required=True)
    parser.add_argument('--mapper', choices=('mmc3', 'mmc5'), required=True)
    parser.add_argument('--baseline', action='store_true')
    args = parser.parse_args()
    source = args.source.resolve()
    assert source.is_relative_to(R / 'build/verification')
    assert args.tag.replace('-', '').isalnum()
    output = source.parent / args.tag
    assert not output.exists()
    output.mkdir()
    stem = 'smb-crossover-' + args.mapper + ('-baseline' if args.baseline else '')
    obj = output / 'objects'
    obj.mkdir()
    for name in ('entrypoint.s', 'main.c'):
        shutil.copyfile(source / 'src' / name, obj / name)
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(source / 'build_options.ini')
    options = {n: v for sec in config.values() for n, v in sec.items()}
    options.update(MAPPER_MMC3=str(int(args.mapper == 'mmc3')),
        MAPPER_MMC5=str(int(args.mapper == 'mmc5')), ENABLE_CROSSOVER=str(int(not args.baseline)))
    command = [str(R / 'tools/Windows/cc65/bin/cl65.exe'), '--cpu', '6502x', '-t', 'nes', '-g', '-Oisr', '-vm', '-T',
        '-C', 'smb1base.cfg', '--ld-args', f'--dbgfile,{output / (stem + ".dbg")}',
        '--include-dir', '.', '--asm-include-dir', '.', '--asm-include-dir', 'src', '--bin-include-dir', '.',
        '-m', str(output / (stem + '.map')), '-Ln', str(output / (stem + '.lbl')), '-o', str(output / (stem + '.nes'))]
    for n, v in options.items():
        command += ['--asm-define', f'{n}={v}', '-D', f'{n}={v}']
    command += [str(obj / 'main.c'), str(obj / 'entrypoint.s')]
    with (output / 'build.log').open('wb') as f:
        result = subprocess.run(command, cwd=source, stdout=f, stderr=subprocess.STDOUT)
    report = dict(exit=result.returncode, command=command,
        source_hashes={p.relative_to(source).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in source.rglob('*') if p.is_file() and 'build' not in p.relative_to(source).parts},
        outputs={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir() if p.is_file()},
        installed=False, goal_complete=False)
    (output / 'build.json').write_text(json.dumps(report, indent=2) + '\n')
    if result.returncode:
        print((output / 'build.log').read_text()[-10000:])
    print(output, result.returncode)
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
