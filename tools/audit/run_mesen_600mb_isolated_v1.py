"""Run a 512 MiB container capture with a stricter 600 MB total run budget.

The existing workspace/archive caps, file limit, free-space floor, one-process
lease and live watchdog remain enforced. No settings or guard files change.
"""
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[2]
RUN_BYTES = 600_000_000


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('script', type=Path)
    parser.add_argument('rom', type=Path)
    parser.add_argument('--emulator')
    parser.add_argument('--timeout', type=int, default=30)
    parser.add_argument('--option', action='append', default=None)
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT / 'tools'))
    from audit import capture_budget as budget
    assert budget.WORKSPACE_BYTES == 70_000_000_000
    assert budget.ARCHIVE_BYTES == 30_000_000_000
    assert budget.RUN_FILES == 64 and budget.RUN_BYTES >= RUN_BYTES
    original_preflight = budget.preflight
    budget.RUN_BYTES = RUN_BYTES
    budget.PAYLOAD_BYTES = RUN_BYTES - 1_000_000

    def preflight(output):
        return original_preflight(output, reserved_bytes=RUN_BYTES,
                                  reserved_files=budget.RUN_FILES)

    budget.preflight = preflight
    original = ROOT / 'tools/run_mesen.py'
    source = original.read_text()
    anchor = "    output = ROOT / 'build/verification'\n"
    assert source.count(anchor) == 1, 'Review the driver before rebinding its output'
    source = source.replace(anchor, '    output = ISOLATED_OUTPUT\n')
    namespace = dict(__file__=str(original), __name__='_bounded_isolated_mesen_driver',
                     ISOLATED_OUTPUT=args.output.resolve())
    exec(compile(source, str(original), 'exec'), namespace)
    return namespace['run'](args.script, args.rom, args.emulator, args.timeout,
                            emulator_options=args.option)


if __name__ == '__main__':
    raise SystemExit(main())
