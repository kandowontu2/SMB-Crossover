"""Run an existing packet with a smaller, explicit capture file allowance."""
import argparse
from functools import partial
from pathlib import Path
import runpy
import sys


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('packet',type=Path)
    cli.add_argument('--files',type=int,default=8,choices=range(3,65))
    args=cli.parse_args()
    root=Path(__file__).resolve().parents[2]
    script=args.packet.resolve()
    assert script.is_relative_to(root/'build') and script.name=='run.py'
    sys.path[:0]=[str(root/'tools'),str(root/'tools/audit')]
    from audit import capture_budget
    # Narrow this isolated process only. The shared runner and its historical
    # source bindings stay unchanged; the byte and PNG caps are unchanged too.
    capture_budget.preflight=partial(capture_budget.preflight,reserved_files=args.files)
    capture_budget.PAYLOAD_FILES=args.files-2  # Budget receipt and final log.
    print(f'Capture reservation and watchdog narrowed to {args.files} files.',flush=True)
    runpy.run_path(str(script),run_name='__main__')


if __name__=='__main__':
    main()
