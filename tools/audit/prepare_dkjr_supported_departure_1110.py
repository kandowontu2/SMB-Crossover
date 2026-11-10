"""Observe actual source/native lift support instead of a transient SMB state."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from prepare_selected_native_packet_v1 import prepare, sha, R
from prepare_dkjr_edge_departure_1110 import ROM, PIN, once

OLD = R / 'build/dkjr-edge-departure-1110'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert sha(ROM) == PIN
    previous = json.loads((OLD / 'capture/result.json').read_text())
    assert not previous['passed'] and previous['first_pipe']['phase'] == 'step-down'
    assert previous['first_pipe']['carries']['480']['count'] == 359
    source = (OLD / 'controller.lua').read_text()
    old = """ local grounded=private(2,0x6b)==1 and read(C.ram.Player_State)==0
 local up,down=liftAt(416),liftAt(480)"""
    new = """ local up,down=liftAt(416),liftAt(480)
 local function carried(left,top)
  local event=pipe.carries[tostring(left)]
  return top and event and event.last.Main<=updates and updates-event.last.Main<=1
    and y+32==top and private(2,0x210)==y+15
 end
 -- PlayerBGCollision can publish falling before the platform pass. Only
 -- actual matching carry events can substitute for that transient state.
 local grounded=private(2,0x6b)==1 and (read(C.ram.Player_State)==0 or carried(416,up) or carried(480,down))"""
    source = once(source, old, new)
    source = once(source, "pipe.world==0 and pipe.level==0 and pipe.area==5 and pipe.engine==8 and pipe.scroll.qualified and",
                  "pipe.world==0 and pipe.level==0 and pipe.area==5 and pipe.engine==8 and read(C.ram.Player_State)==0 and pipe.scroll.qualified and")
    assert 'emu.write' not in source
    labels = R / 'build/dkjr-camera-native-1110/dkjr-private.lbl'
    prepare(args.output, ROM, source,
            {Path(__file__), OLD / 'controller.lua', OLD / 'capture/result.json',
             R / 'build/complete-roster-native-1110/combined-proof.json'},
            expected=PIN, timeout=240, allow_interactive=True,
            rom_symbols=(labels, labels.with_suffix('.dbg')),
            scope='Same controller-only edge departure on unchanged c10 ROM. Intermediate support admits only a current/prior actual native carry with matching native/source feet and source grounded state. Final far-floor requires ordinary native grounded state, both lifts/carries and lives. One retained PNG.')
    run = subprocess.run([sys.executable, '-B', str(R / 'tools/audit/run_small_mesen_packet_1110.py'),
                          '--files', '6', str(args.output / 'run.py')])
    result = json.loads((args.output / 'capture/result.json').read_text())
    print(json.dumps(dict(exit=run.returncode, passed=result['passed'],
                          first_pipe={k: result['first_pipe'][k] for k in ('phase', 'reason', 'x', 'y', 'source_state')})), flush=True)
    raise SystemExit(run.returncode)


if __name__ == '__main__':
    main()
