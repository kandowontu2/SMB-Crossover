"""Read three live platform descriptors from the already-reached Mini peak."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from prepare_selected_native_packet_v1 import prepare, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path('build/mini-lane-peak-1110')
    controller = root/'controller.lua'
    rom = Path('build/mini-lane-audio-native-1110/candidate.nes')
    assert sha(rom) == 'a226894c4f6b97f1b9df248cf1465f1a36037fcc256d8ec703e05d0f077d6746'
    sample = json.loads((root/'capture/instruction-sample.json').read_text())
    assert sample['scene']['frame'] == 1475 and sample['scene']['x'] == 695
    source = controller.read_text()

    def replace(old, new):
        nonlocal source
        assert source.count(old) == 1, old
        source = source.replace(old, new)

    replace('local lastInstruction', 'local rendererEntries={}\nlocal lastInstruction')
    replace(" if state['cpu.sp']<minimumSampleSP.sp then", """ if not instructionIsISR and bank=='4' and pc==0xa5ba then
  check(#rendererEntries<8,'Bounded renderer witness count')
  local ptr=read(3)+256*read(4)
  local header=read(ptr)
  check(header<=32,'Bounded complete native descriptor')
  local descriptor={header}
  for i=1,header do descriptor[i+1]=read(ptr+i) end
  local slot=read(0x0d)
  rendererEntries[#rendererEntries+1]={pointer=ptr,descriptor=descriptor,
   slot=slot,enemy_id=read(0x17+slot),enemy_state=read(0x1f+slot),
   attribute=read(6),x_low=read(7),x_high=read(8),y_low=read(9),y_high=read(10),
   oam_cursor=r('CurrentOAMOffset'),rotation_active=r('GuestOamRotationActive'),
   rotation=r('RgOamRotation'),sp=state['cpu.sp']}
 end
 if state['cpu.sp']<minimumSampleSP.sp then""")
    replace('floor_probes=floorSamples,', 'floor_probes=floorSamples,renderer_entries=rendererEntries,')
    assert all(token not in source for token in ('emu.write(', 'emu.reset(', 'emu.loadSavestate('))
    prepare(args.output, rom, source, {controller, Path(__file__)}, expected=sha(rom),
            timeout=140, allow_interactive=True,
            scope='Read-only renderer descriptor witnesses in exact frame1475, no game changes.')
    subprocess.run([sys.executable, '-B', str(args.output/'run.py')], check=True)
    result = json.loads((args.output/'capture/instruction-sample.json').read_text())
    assert len(result['renderer_entries']) == 3
    assert all(row['enemy_id'] == 0x25 for row in result['renderer_entries'])
    print(json.dumps(result['renderer_entries']), flush=True)


if __name__ == '__main__':
    main()
