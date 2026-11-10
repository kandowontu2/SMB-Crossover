"""Controller-only current-ROM reproduction with a bounded in-memory carry trace."""
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

TRACE = '''
local carryTrace={}
local function traceCarry(event,value)
 if not active() or phase~='first-pipe' or xpos()<430 then return end
 local state=emu.getState()
 local row={event=event,value=value,frame=frame,Main=updates,pc=state['cpu.pc'],
  x=xpos(),y=read(C.ram.Player_Y_Position),dy=read(0x8e),native_state=read(C.ram.Player_State),
  source_state=private(2,0x6b),pending=private(2,0x6c),source_y=private(2,0x210),
  origin=private(2,0x76),jump=private(2,0x54),frac=private(2,0x56),
  carry_phase=private(2,0x8f7),top=liftAt(416),keys=inputKeys}
 if #carryTrace>=128 then table.remove(carryTrace,1)end
 carryTrace[#carryTrace+1]=row
end
emu.addMemoryCallback(function()traceCarry('phase-write')end,emu.callbackType.write,0xc06b)
emu.addMemoryCallback(function()
 if inram(0xb6a5,3,0xa000)then traceCarry('carry-entry')end
end,emu.callbackType.exec,0xb6a5)
emu.addMemoryCallback(function()
 if inram(C.main,2,0xc000)then traceCarry('main-entry')end
end,emu.callbackType.exec,C.main)
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert sha(ROM) == PIN
    old_ready = json.loads((OLD / 'ready.json').read_text())
    assert old_ready['ROM_sha256'] == OLD_PIN
    assert old_ready['bindings'][str((OLD / 'controller.lua').resolve())] == sha(OLD / 'controller.lua')
    old_result = json.loads((OLD / 'capture/result.json').read_text())
    assert not old_result['passed'] and old_result['first_pipe']['x'] == 450
    # The current public ROM retained the exact DK private code and header.
    old_rom = Path(old_ready['ROM']).read_bytes()
    raw = ROM.read_bytes()
    for page in (817, 833, 847, 856, 867, 881, 882, 883, 959, 960, 961):
        at = 16 + 1048576 + page * 1024
        assert raw[at:at + 1024] == old_rom[at:at + 1024], page
    assert raw[534485:534501] == old_rom[534485:534501]
    source = (OLD / 'controller.lua').read_text()
    assert source.count(OLD_PIN) == 1
    source = source.replace(OLD_PIN, PIN)
    marker = 'local function finishPipe(ok,reason)'
    assert source.count(marker) == 1
    source = source.replace(marker, TRACE + '\n' + marker)
    marker = ' pipe.reason=reason;pipe.x=x;'
    assert source.count(marker) == 1
    # The retained observer's JSON formatter quotes string keys only. Its
    # numeric array keys produce invalid JSON, so publish a string-key map.
    source = source.replace(marker, " pipe.trace={};for i,row in ipairs(carryTrace)do pipe.trace[tostring(i)]=row end;pipe.reason=reason;pipe.x=x;")
    assert 'emu.write' not in source
    labels = R / 'build/dkjr-camera-native-1110/dkjr-private.lbl'
    prepare(args.output, ROM, source,
            {Path(__file__), OLD / 'controller.lua', OLD / 'capture/result.json',
             R / 'build/complete-roster-native-1110/combined-proof.json'},
            expected=PIN, timeout=240, allow_interactive=True,
            rom_symbols=(labels, labels.with_suffix('.dbg')),
            scope='Current exact ROM, unchanged prior first-pipe controller with 128-entry in-memory trace. Expected genuine carry/detach failure retained; no script state writes, three PNG maximum.')
    run = subprocess.run([sys.executable, '-B', str(R / 'tools/audit/run_small_mesen_packet_1110.py'),
                          '--files', '8', str(args.output / 'run.py')])
    result = json.loads((args.output / 'capture/result.json').read_text())
    assert result['ROM_sha256'] == PIN and result['first_pipe']['trace']
    print(json.dumps(dict(emulator_exit=run.returncode, passed=result['passed'],
                          first_pipe={k: result['first_pipe'][k] for k in ('reason', 'x', 'y', 'source_state')},
                          trace_events=len(result['first_pipe']['trace']))), flush=True)


if __name__ == '__main__':
    main()
