"""Keep the v2 comparison unchanged, and fail the command when its verdict is false."""
from pathlib import Path
import argparse
import json
import subprocess
import sys


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fixture', type=Path, required=True)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    result = subprocess.run([sys.executable, '-B', str(Path(__file__).with_name('cv3_remaining_sfx_lifecycle_verify_v2.py')),
                             '--fixture', str(a.fixture), '--baseline', str(a.baseline), '--output', str(a.output)])
    if result.returncode:
        return result.returncode
    return 0 if json.loads((a.output / 'proof.json').read_text())['passed'] is True else 1


if __name__ == '__main__':
    raise SystemExit(main())
