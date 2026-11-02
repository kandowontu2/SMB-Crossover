"""Keep Thomas's original jump and detect gaps under his current feet."""
from pathlib import Path
import json
from prepare_selected_native_packet_v1 import R, prepare, sha

O = R / 'build/thomas-full11-1102-v1'
PIN = 'f5c30ceaa36894f3e814ef277081ecd9cf434a934c0f7b3f514c2291be0e1cfc'


def main():
    source = R / 'build/bub-menu-candidate-1102-v2/native-thomas-step-probe/controller.lua'
    text = source.read_text()
    old = '   if not solid(x+12,216) or foot then pad.up=updates%8<3 end'
    assert text.count(old) == 1
    text = text.replace(old, '''   local support,supportTile=solid(x+12,py+32)
   if not support or foot then pad.up=updates%8<3 end
   if py<176 and not support and not counters.elevated_support_probe then
    counters.elevated_support_probe=1
    local f=assert(io.open(OUTPUT..'elevated-support.json','w'))
    f:write(json({frame=frame,Main=updates,x=x,y=py,probe_x=x+12,probe_y=py+32,
     tile=supportTile,old_ground_probe=solid(x+12,216),up=pad.up}));f:close()
   end''')
    rom = R / 'build/wwf-helper-stable-1102-v2/candidate2.nes'
    assert sha(rom) == PIN
    prepare(O / 'native-elevated-support', rom, text, [Path(__file__), source],
            expected=PIN, timeout=240, allow_interactive=True,
            scope='Controller-only elevated support probe at actual body bottom. Original Up pulse, native motion, four-pipe route, software/hardware RTI checks and full1-1 assertions retained. Prior240s run reached3900Main then stalled after missing elevated takeoff;450s permits full route with unchanged12000Main/24000physical bounds. No ROM or RAM changes; four PNG maximum.')
    # Per-packet host-time allowance, supported by the prior measured runtime.
    # Leave the shared preparer and all storage/emulated-frame limits unchanged.
    ready = O / 'native-elevated-support/ready.json'
    q = json.loads(ready.read_text())
    q['timeout'] = 450
    q['host_timeout_evidence'] = 'Prior 240s observer replay completed only3900Main; full route requires additional updates. Same12000Main/24000physical and capture limits.'
    ready.write_text(json.dumps(q, indent=2) + '\n')


if __name__ == '__main__':
    main()
