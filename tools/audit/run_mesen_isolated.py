"""Run the existing Mesen fixture driver with a separate evidence directory."""
from pathlib import Path
import argparse
import sys

R = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('script', type=Path)
    parser.add_argument('rom', type=Path)
    parser.add_argument('--emulator')
    parser.add_argument('--timeout', type=int, default=30)
    args = parser.parse_args()
    original = R / 'tools/run_mesen.py'
    text = original.read_text()
    anchor = "    output = ROOT / 'build/verification'\n"
    assert text.count(anchor) == 1, 'Review the driver before rebinding its output.'
    text = text.replace(anchor, '    output = ISOLATED_OUTPUT\n')
    sys.path.insert(0, str(R / 'tools'))
    namespace = dict(__file__=str(original), __name__='_isolated_mesen_driver', ISOLATED_OUTPUT=args.output.resolve())
    exec(compile(text, str(original), 'exec'), namespace)
    return namespace['run'](args.script, args.rom, args.emulator, args.timeout)


if __name__ == '__main__':
    raise SystemExit(main())
