"""Build SMB Crossover using the bundled Windows cc65 or a cl65 on PATH."""
from __future__ import annotations

import argparse
import configparser
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mapper', choices=('mmc3', 'mmc5'), default='mmc3')
    parser.add_argument('--baseline', action='store_true', help='Disable the Crossover additions')
    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(ROOT / 'build_options.ini')
    options = {name: value for section in config.values() for name, value in section.items()}
    options['MAPPER_MMC3'] = str(int(args.mapper == 'mmc3'))
    options['MAPPER_MMC5'] = str(int(args.mapper == 'mmc5'))
    options['ENABLE_CROSSOVER'] = str(int(not args.baseline))
    if not args.baseline:
        subprocess.run([sys.executable,str(ROOT/'tools/prepare_guest_audio.py')],cwd=ROOT,check=True)
        subprocess.run([sys.executable,str(ROOT/'tools/reference/pack_chr.py')],cwd=ROOT,check=True)
        subprocess.run([sys.executable,str(ROOT/'tools/reference/tag_player_outlines.py')],cwd=ROOT,check=True)
    bundled = ROOT / 'tools/Windows/cc65/bin/cl65.exe'
    compiler = str(bundled) if sys.platform == 'win32' else shutil.which('cl65')
    if not compiler:
        parser.error('Install cc65 and put cl65 on PATH.')
    name = f'smb-crossover-{args.mapper}' + ('-baseline' if args.baseline else '')
    output = ROOT / 'build' / name
    output.parent.mkdir(exist_ok=True)
    # cl65 writes intermediates beside its inputs. Give every target its own
    # entrypoints so baseline/mapper builds cannot overwrite each other's .s/.o.
    objects = ROOT / 'build/objects' / name
    objects.mkdir(parents=True, exist_ok=True)
    for filename in ('main.c', 'entrypoint.s'):
        shutil.copyfile(ROOT / 'src' / filename, objects / filename)
    command = [
        compiler, '--cpu', '6502x', '-t', 'nes', '-g', '-Oisr', '-vm', '-T',
        '-C', 'smb1base.cfg', '--ld-args', f'--dbgfile,build/{name}.dbg',
        '--include-dir', '.', '--asm-include-dir', '.', '--asm-include-dir', 'src', '--bin-include-dir', '.',
        '-l', f'build/{name}.lst', '-m', f'build/{name}.map',
        '-Ln', f'build/{name}.lbl', '-o', f'build/{name}.nes',
    ]
    for key, value in options.items():
        command.extend(('--asm-define', f'{key}={value}', '-D', f'{key}={value}'))
    command.extend((str(objects/'main.c'), str(objects/'entrypoint.s')))
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode:
        return result.returncode
    rom = output.with_suffix('.nes').read_bytes()
    mapper = (rom[6] >> 4) | (rom[7] & 0xf0) | ((rom[8] & 0xf) << 8)
    expected = 4 if args.mapper == 'mmc3' else 5
    if mapper != expected or len(rom) != 16 + rom[4]*16384 + rom[5]*8192:
        raise RuntimeError('Output header/size does not match the selected mapper.')
    print(f'Built {output.with_suffix(".nes")} ({len(rom):,} bytes; mapper {mapper})')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
