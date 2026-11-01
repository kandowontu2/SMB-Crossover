"""Reject sidecar patches that silently change a delivered ROM in Mesen."""
from pathlib import Path
import argparse
import hashlib
import json

PATCH_SUFFIXES = {'.ips', '.bps', '.ups'}


def check(rom):
    rom = Path(rom).resolve(strict=True)
    patches = sorted(p for p in rom.parent.iterdir()
                     if p.is_file() and p.stem.casefold() == rom.stem.casefold()
                     and p.suffix.casefold() in PATCH_SUFFIXES)
    if patches:
        raise RuntimeError('Nightly would load with a sidecar patch: ' +
                           ', '.join(str(p) for p in patches))
    return {'passed': True, 'ROM': str(rom),
            'ROM_sha256': hashlib.sha256(rom.read_bytes()).hexdigest(),
            'matching_patch_files': []}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('rom', type=Path)
    print(json.dumps(check(parser.parse_args().rom)))
