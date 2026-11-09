"""Capture bounded, controller-only observations from the original Getsu Fūma ROM."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from audit.mesen_session_guard_v1 import require_free_workspace
from run_mesen import run


ROM = Path('C:/NES/Getsu Fuuma Den (Japan).nes')
PIN = 'a413567542aab4cf27ff835fd390773455bb61f2af9711ad85043e0a9196033e'
TRACE = ROOT / 'tools/playthroughs/getsu_fuma_donor_1110.lua'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(ROOT / 'build')
    assert digest(ROM) == PIN
    untouched = require_free_workspace(ROOT, ROM, allow_interactive=True)
    os.environ['SMB_RUN_OUTPUT'] = str(output / 'capture')
    code = run(TRACE, ROM, timeout=45,
               emulator_options=['--doNotSaveSettings', '--nes.removeSpriteLimit=false',
                                 '--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false',
                                 '--nes.randomizeMapperPowerOnState=false'])
    assert digest(ROM) == PIN
    receipt = dict(ROM_SHA256=PIN, controller_sha256=digest(TRACE), emulator_exit=code,
                   untouched_process_ids=[p['ProcessId'] for p in untouched], controller_only=True)
    (output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    raise SystemExit(code)


if __name__ == '__main__':
    main()
