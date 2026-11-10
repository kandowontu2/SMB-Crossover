"""Test an ordinary walking departure from the existing native first-pipe lift."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from prepare_selected_native_packet_v1 import prepare, sha, R

ROM = R / 'build/complete-roster-native-1110/candidate.nes'
PIN = 'c10b7d87f466bf028096bddd33b7ac2baee242870ee83ccc4eebd529af57bd7f'
OLD = R / 'build/dkjr-getsu-native-1110/first-pipe'
OLD_PIN = '88e62d81df92282f0515bc78a0bcf0cc4a2048f1aecf73bab13f36b7b86c183a'


def once(source, old, new):
    assert source.count(old) == 1, old
    return source.replace(old, new)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert sha(ROM) == PIN
    source = once((OLD / 'controller.lua').read_text(), OLD_PIN, PIN)
    old = """ if pipe.phase=='rise' and up then
  right=x<439
  if x>=439 and grounded and up-32==y and up>=170 and up<=176 then holdA=updates+8;setPhase('cross',up) end
 end"""
    new = """ if pipe.phase=='rise' and up then
  -- Stay on the last observed supported pixel until level with the cap.
  -- No new A: the original slow jump is caught by the rising lift.
  right=x<449
  if x>=449 and grounded and up-32==y and up>=170 and up<=176 then setPhase('cross',up) end
 end"""
    source = once(source, old, new)
    source = once(source, "OUTPUT..name..'.png'", "OUTPUT..'terminal.png'")
    assert 'emu.write' not in source
    labels = R / 'build/dkjr-camera-native-1110/dkjr-private.lbl'
    prepare(args.output, ROM, source,
            {Path(__file__), OLD / 'controller.lua', OLD / 'capture/result.json',
             R / 'build/complete-roster-native-1110/combined-proof.json',
             R / 'build/dkjr-current-carry-trace-1110/capture/result.json'},
            expected=PIN, timeout=240, allow_interactive=True,
            rom_symbols=(labels, labels.with_suffix('.dbg')),
            scope='Controller-only native first pipe: same original physics, two authored girders, both carries/far-ground assertions retained. Walk to proven supported X449, then depart level without a new jump. One retained PNG; body/OAM checks remain active.')
    run = subprocess.run([sys.executable, '-B', str(R / 'tools/audit/run_small_mesen_packet_1110.py'),
                          '--files', '6', str(args.output / 'run.py')])
    result = json.loads((args.output / 'capture/result.json').read_text())
    print(json.dumps(dict(exit=run.returncode, passed=result['passed'],
                          first_pipe={k: result['first_pipe'][k] for k in ('reason', 'x', 'y', 'source_state')})), flush=True)
    raise SystemExit(run.returncode)


if __name__ == '__main__':
    main()
