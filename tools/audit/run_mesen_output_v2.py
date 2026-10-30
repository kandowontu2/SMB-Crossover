"""Run the current Mesen driver using its supported per-run output setting."""
from pathlib import Path
import argparse
import os
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
from run_mesen import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('script', type=Path)
    parser.add_argument('rom', type=Path)
    parser.add_argument('--emulator')
    parser.add_argument('--timeout', type=int, default=30)
    parser.add_argument('--option', action='append', default=None)
    args = parser.parse_args()
    previous = os.environ.get('SMB_RUN_OUTPUT')
    os.environ['SMB_RUN_OUTPUT'] = str(args.output.resolve())
    try:
        return run(args.script, args.rom, args.emulator, args.timeout,
                   emulator_options=args.option)
    finally:
        if previous is None:
            os.environ.pop('SMB_RUN_OUTPUT', None)
        else:
            os.environ['SMB_RUN_OUTPUT'] = previous


if __name__ == '__main__':
    raise SystemExit(main())
